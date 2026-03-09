"""
Hypernet JWT Authentication Module

File-based JWT authentication for the Hypernet FastAPI server. Provides
user registration, login, token management, and FastAPI dependency
injection for route protection.

Design principles:
  - File-based JSON storage (no database), consistent with rest of Hypernet
  - Minimal dependencies: PyJWT preferred, HMAC-SHA256 fallback
  - Password hashing: argon2-cffi preferred, PBKDF2-SHA256 fallback
  - Thread-safe user store with file locking
  - Maps to existing PermissionTier system from permissions.py

Storage: data/auth/users.json
Tokens: HS256 JWTs (access=15min, refresh=7days)

Standard: 2.0.19 (AI Data Protection), permission tiers from permissions.py
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import os
import secrets
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

log = logging.getLogger(__name__)

from .permissions import PermissionTier

# ── Optional dependency detection ─────────────────────────────────────

_HAS_ARGON2 = False
try:
    import argon2
    from argon2 import PasswordHasher as _Argon2Hasher
    from argon2.exceptions import VerifyMismatchError as _Argon2Mismatch
    _HAS_ARGON2 = True
except ImportError:
    pass

_HAS_PYJWT = False
try:
    import jwt as _pyjwt
    _HAS_PYJWT = True
except ImportError:
    pass


# ── Scope definitions ─────────────────────────────────────────────────

SCOPES: dict[str, str] = {
    "read": "Read public data",                # T0 READ_ONLY
    "write:personal": "Write own data",         # T1 WRITE_OWN
    "write:collab": "Collaborative write",      # T2 WRITE_SHARED
    "admin:external": "External services",      # T3 EXTERNAL
    "admin:full": "Full administrative",        # T4 DESTRUCTIVE
}

# Map PermissionTier to the maximum scopes granted at that tier
_TIER_SCOPES: dict[PermissionTier, list[str]] = {
    PermissionTier.READ_ONLY:    ["read"],
    PermissionTier.WRITE_OWN:    ["read", "write:personal"],
    PermissionTier.WRITE_SHARED: ["read", "write:personal", "write:collab"],
    PermissionTier.EXTERNAL:     ["read", "write:personal", "write:collab", "admin:external"],
    PermissionTier.DESTRUCTIVE:  ["read", "write:personal", "write:collab", "admin:external", "admin:full"],
}


def scopes_for_tier(tier: PermissionTier) -> list[str]:
    """Return all scopes granted at a given permission tier."""
    return list(_TIER_SCOPES.get(tier, ["read"]))


# ── Token configuration ──────────────────────────────────────────────

ACCESS_TOKEN_EXPIRE_SECONDS = 15 * 60       # 15 minutes
REFRESH_TOKEN_EXPIRE_SECONDS = 7 * 24 * 3600  # 7 days
JWT_ALGORITHM = "HS256"
MIN_PASSWORD_LENGTH = 12


# ── Password hashing ─────────────────────────────────────────────────

class PasswordHasher:
    """Password hashing with argon2-cffi (preferred) or PBKDF2-SHA256 fallback.

    Hash format:
      argon2:  The argon2 PHC string (starts with $argon2id$...)
      pbkdf2:  "pbkdf2:sha256:{iterations}${salt_b64}${hash_b64}"
    """

    _PBKDF2_ITERATIONS = 600_000  # OWASP 2023 recommendation for SHA-256

    def __init__(self) -> None:
        if _HAS_ARGON2:
            self._argon2 = _Argon2Hasher(
                time_cost=3,
                memory_cost=65536,  # 64 MiB
                parallelism=4,
                hash_len=32,
                salt_len=16,
            )
            log.info("Password hashing: argon2id (preferred)")
        else:
            self._argon2 = None
            log.info("Password hashing: PBKDF2-SHA256 (argon2-cffi not available)")

    def hash(self, password: str) -> str:
        """Hash a password. Returns a string suitable for storage."""
        if self._argon2 is not None:
            return self._argon2.hash(password)

        # PBKDF2-SHA256 fallback
        salt = os.urandom(16)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self._PBKDF2_ITERATIONS,
            dklen=32,
        )
        salt_b64 = base64.b64encode(salt).decode("ascii")
        hash_b64 = base64.b64encode(dk).decode("ascii")
        return f"pbkdf2:sha256:{self._PBKDF2_ITERATIONS}${salt_b64}${hash_b64}"

    def verify(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash. Constant-time comparison."""
        if password_hash.startswith("$argon2"):
            if self._argon2 is None:
                log.error("Cannot verify argon2 hash without argon2-cffi installed")
                return False
            try:
                return self._argon2.verify(password_hash, password)
            except _Argon2Mismatch:
                return False
            except Exception:
                log.exception("Argon2 verification error")
                return False

        if password_hash.startswith("pbkdf2:sha256:"):
            return self._verify_pbkdf2(password, password_hash)

        log.warning("Unknown password hash format")
        return False

    def _verify_pbkdf2(self, password: str, password_hash: str) -> bool:
        """Verify a PBKDF2-SHA256 hash with constant-time comparison."""
        try:
            # Format: "pbkdf2:sha256:{iterations}${salt_b64}${hash_b64}"
            prefix, rest = password_hash.split(":", 2)[2].split("$", 1)
            iterations = int(prefix)
            salt_b64, hash_b64 = rest.split("$", 1)
            salt = base64.b64decode(salt_b64)
            expected = base64.b64decode(hash_b64)
        except (ValueError, IndexError):
            return False

        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=32,
        )
        return hmac.compare_digest(dk, expected)

    def needs_rehash(self, password_hash: str) -> bool:
        """Check if a hash should be upgraded (e.g., PBKDF2 -> argon2)."""
        if self._argon2 is not None and password_hash.startswith("pbkdf2:"):
            return True
        if self._argon2 is not None and password_hash.startswith("$argon2"):
            try:
                return self._argon2.check_needs_rehash(password_hash)
            except Exception:
                return False
        return False


# ── JWT Token Management ─────────────────────────────────────────────

class TokenManager:
    """JWT token creation and verification.

    Uses PyJWT when available. Falls back to manual HMAC-SHA256
    token construction when PyJWT is not installed.
    """

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def create_token(
        self,
        subject: str,
        scopes: list[str],
        token_type: str = "access",
        expires_seconds: int | None = None,
    ) -> str:
        """Create a signed JWT token.

        Args:
            subject: The token subject (Hypernet address).
            scopes: List of permission scopes.
            token_type: "access" or "refresh".
            expires_seconds: Override default expiry.

        Returns:
            Encoded JWT string.
        """
        now = int(time.time())
        if expires_seconds is None:
            if token_type == "refresh":
                expires_seconds = REFRESH_TOKEN_EXPIRE_SECONDS
            else:
                expires_seconds = ACCESS_TOKEN_EXPIRE_SECONDS

        payload = {
            "sub": subject,
            "scopes": scopes,
            "type": token_type,
            "iat": now,
            "exp": now + expires_seconds,
        }

        if _HAS_PYJWT:
            return _pyjwt.encode(payload, self._secret, algorithm=JWT_ALGORITHM)

        return self._encode_fallback(payload)

    def decode_token(self, token: str) -> dict[str, Any]:
        """Decode and verify a JWT token.

        Returns:
            Decoded payload dict.

        Raises:
            TokenError: If the token is invalid, expired, or tampered with.
        """
        if _HAS_PYJWT:
            try:
                return _pyjwt.decode(
                    token,
                    self._secret,
                    algorithms=[JWT_ALGORITHM],
                )
            except _pyjwt.ExpiredSignatureError:
                raise TokenError("Token has expired")
            except _pyjwt.InvalidTokenError as exc:
                raise TokenError(f"Invalid token: {exc}")

        return self._decode_fallback(token)

    # ── Fallback HMAC-SHA256 implementation ───────────────────────────

    def _encode_fallback(self, payload: dict) -> str:
        """Encode a JWT without PyJWT using HMAC-SHA256."""
        header = {"alg": "HS256", "typ": "JWT"}
        header_b64 = self._b64url_encode(json.dumps(header, separators=(",", ":")).encode())
        payload_b64 = self._b64url_encode(json.dumps(payload, separators=(",", ":")).encode())
        signing_input = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            self._secret.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        sig_b64 = self._b64url_encode(signature)
        return f"{signing_input}.{sig_b64}"

    def _decode_fallback(self, token: str) -> dict[str, Any]:
        """Decode a JWT without PyJWT using HMAC-SHA256."""
        parts = token.split(".")
        if len(parts) != 3:
            raise TokenError("Invalid token format")

        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(
            self._secret.encode("utf-8"),
            signing_input.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        actual_sig = self._b64url_decode(sig_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            raise TokenError("Invalid token signature")

        # Decode payload
        try:
            payload = json.loads(self._b64url_decode(payload_b64))
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise TokenError("Invalid token payload")

        # Check expiry
        exp = payload.get("exp")
        if exp is not None and int(exp) < int(time.time()):
            raise TokenError("Token has expired")

        return payload

    @staticmethod
    def _b64url_encode(data: bytes) -> str:
        """Base64url encode without padding."""
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

    @staticmethod
    def _b64url_decode(s: str) -> bytes:
        """Base64url decode, adding padding as needed."""
        padding = 4 - len(s) % 4
        if padding != 4:
            s += "=" * padding
        return base64.urlsafe_b64decode(s)


class TokenError(Exception):
    """Raised when a token is invalid, expired, or cannot be verified."""
    pass


# ── User Model ────────────────────────────────────────────────────────

@dataclass
class UserRecord:
    """A user record stored in the auth database.

    Fields map to the Hypernet identity model:
      - ha: Hypernet Address (e.g., "1.1" for Matt, "1.local.{uuid}" for local users)
      - email: Unique email for login
      - password_hash: Argon2 or PBKDF2 hash
      - display_name: Human-readable name
      - permission_tier: Maps to PermissionTier enum (0-4)
      - scopes: Explicit scope overrides (empty = use tier defaults)
      - is_active: Soft-disable without deletion (2.0.19 — no permanent deletion)
      - created_at: ISO 8601 creation timestamp
    """
    ha: str
    email: str
    password_hash: str
    display_name: str
    permission_tier: int = PermissionTier.WRITE_OWN
    scopes: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def effective_scopes(self) -> list[str]:
        """Return effective scopes: explicit overrides or tier defaults."""
        if self.scopes:
            return list(self.scopes)
        tier = PermissionTier(self.permission_tier)
        return scopes_for_tier(tier)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON storage."""
        return asdict(self)

    def to_public_dict(self) -> dict[str, Any]:
        """Serialize for API responses (no password hash)."""
        d = self.to_dict()
        d.pop("password_hash", None)
        d["scopes"] = self.effective_scopes()
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> UserRecord:
        """Deserialize from JSON storage."""
        return cls(
            ha=d["ha"],
            email=d["email"],
            password_hash=d["password_hash"],
            display_name=d["display_name"],
            permission_tier=d.get("permission_tier", PermissionTier.WRITE_OWN),
            scopes=d.get("scopes", []),
            is_active=d.get("is_active", True),
            created_at=d.get("created_at", ""),
        )


# ── User Store (file-based, thread-safe) ─────────────────────────────

class UserStore:
    """Thread-safe, file-based user storage.

    Stores all users in a single JSON file at {data_dir}/auth/users.json.
    Uses atomic writes (write to .tmp then rename) for crash safety.
    """

    def __init__(self, data_dir: str | Path) -> None:
        self._data_dir = Path(data_dir)
        self._auth_dir = self._data_dir / "auth"
        self._users_file = self._auth_dir / "users.json"
        self._lock = threading.Lock()
        self._users: dict[str, UserRecord] = {}  # keyed by email
        self._ha_index: dict[str, str] = {}       # ha -> email (reverse index)
        self._load()

    def _load(self) -> None:
        """Load users from disk."""
        if not self._users_file.exists():
            log.info("No existing users file at %s — starting fresh", self._users_file)
            return
        try:
            raw = json.loads(self._users_file.read_text(encoding="utf-8"))
            for email, user_data in raw.items():
                user = UserRecord.from_dict(user_data)
                self._users[email] = user
                self._ha_index[user.ha] = email
            log.info("Loaded %d user(s) from %s", len(self._users), self._users_file)
        except Exception:
            log.exception("Failed to load users from %s", self._users_file)

    def _save(self) -> None:
        """Persist users to disk (atomic write). Caller must hold _lock."""
        self._auth_dir.mkdir(parents=True, exist_ok=True)
        data = {email: user.to_dict() for email, user in self._users.items()}
        tmp = self._users_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self._users_file)

    def get_by_email(self, email: str) -> UserRecord | None:
        """Look up a user by email."""
        with self._lock:
            return self._users.get(email)

    def get_by_ha(self, ha: str) -> UserRecord | None:
        """Look up a user by Hypernet address."""
        with self._lock:
            email = self._ha_index.get(ha)
            if email:
                return self._users.get(email)
            return None

    def create(self, user: UserRecord) -> None:
        """Add a new user. Raises ValueError if email or HA already exists."""
        with self._lock:
            if user.email in self._users:
                raise ValueError("Email already registered")
            if user.ha in self._ha_index:
                raise ValueError("Hypernet address already in use")
            self._users[user.email] = user
            self._ha_index[user.ha] = user.email
            self._save()
            log.info("Created user: %s (ha=%s)", user.email, user.ha)

    def update(self, user: UserRecord) -> None:
        """Update an existing user record. Raises ValueError if not found."""
        with self._lock:
            if user.email not in self._users:
                raise ValueError("User not found")
            self._users[user.email] = user
            self._ha_index[user.ha] = user.email
            self._save()

    def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        with self._lock:
            return email in self._users

    @property
    def count(self) -> int:
        """Number of registered users."""
        with self._lock:
            return len(self._users)


# ── Rate Limiting for Login ───────────────────────────────────────────

class LoginRateLimiter:
    """Track failed login attempts per email. Lock after threshold.

    After MAX_ATTEMPTS failures within the window, the email is locked
    for LOCKOUT_SECONDS. This defends against brute-force attacks while
    keeping the implementation simple (in-memory, no persistence needed).
    """

    MAX_ATTEMPTS = 5
    LOCKOUT_SECONDS = 15 * 60  # 15 minutes
    WINDOW_SECONDS = 15 * 60   # Track failures within this window

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # email -> list of failure timestamps
        self._failures: dict[str, list[float]] = {}
        # email -> lockout expiry timestamp
        self._lockouts: dict[str, float] = {}

    def is_locked(self, email: str) -> bool:
        """Check if an email is currently locked out."""
        with self._lock:
            expiry = self._lockouts.get(email)
            if expiry is not None:
                if time.time() < expiry:
                    return True
                # Lockout expired — clean up
                del self._lockouts[email]
                self._failures.pop(email, None)
            return False

    def record_failure(self, email: str) -> None:
        """Record a failed login attempt. May trigger lockout."""
        with self._lock:
            now = time.time()
            failures = self._failures.get(email, [])
            # Prune old failures outside the window
            cutoff = now - self.WINDOW_SECONDS
            failures = [t for t in failures if t > cutoff]
            failures.append(now)
            self._failures[email] = failures

            if len(failures) >= self.MAX_ATTEMPTS:
                self._lockouts[email] = now + self.LOCKOUT_SECONDS
                log.warning(
                    "Login locked for %s — %d failures in %ds window",
                    email, len(failures), self.WINDOW_SECONDS,
                )

    def record_success(self, email: str) -> None:
        """Clear failure history on successful login."""
        with self._lock:
            self._failures.pop(email, None)
            self._lockouts.pop(email, None)


# ── Secret Key Management ─────────────────────────────────────────────

def _load_jwt_secret(data_dir: Path) -> str:
    """Load or generate the JWT signing secret.

    Priority:
      1. HYPERNET_JWT_SECRET environment variable
      2. secrets/config.json -> jwt_secret
      3. data/auth/jwt_secret.key (auto-generated)
    """
    # 1. Environment variable
    env_secret = os.environ.get("HYPERNET_JWT_SECRET")
    if env_secret:
        log.info("JWT secret loaded from HYPERNET_JWT_SECRET environment variable")
        return env_secret

    # 2. Config file
    config_path = data_dir.parent / "secrets" / "config.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if "jwt_secret" in config:
                log.info("JWT secret loaded from config.json")
                return config["jwt_secret"]
        except Exception:
            log.warning("Could not read jwt_secret from config.json")

    # 3. Auto-generated key file
    auth_dir = data_dir / "auth"
    key_file = auth_dir / "jwt_secret.key"
    if key_file.exists():
        secret = key_file.read_text(encoding="utf-8").strip()
        if secret:
            log.info("JWT secret loaded from %s", key_file)
            return secret

    # Generate a new secret
    secret = secrets.token_urlsafe(64)
    auth_dir.mkdir(parents=True, exist_ok=True)
    key_file.write_text(secret, encoding="utf-8")
    log.info("Generated new JWT secret and saved to %s", key_file)
    return secret


# ── Auth Service (orchestrates everything) ────────────────────────────

class AuthService:
    """High-level authentication service.

    Combines user storage, password hashing, token management, and
    rate limiting into a single entry point. Used by both the FastAPI
    routes and the dependency injection functions.
    """

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.users = UserStore(self.data_dir)
        self.hasher = PasswordHasher()
        self.rate_limiter = LoginRateLimiter()

        secret = _load_jwt_secret(self.data_dir)
        self.tokens = TokenManager(secret)

    def register(
        self,
        email: str,
        password: str,
        display_name: str,
        permission_tier: PermissionTier = PermissionTier.WRITE_OWN,
    ) -> UserRecord:
        """Register a new user.

        Args:
            email: User's email address.
            password: Plaintext password (min 12 chars).
            display_name: Human-readable display name.
            permission_tier: Initial permission tier (default: WRITE_OWN).

        Returns:
            The created UserRecord.

        Raises:
            ValueError: If validation fails or email already registered.
        """
        # Validate email format (basic check)
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Invalid email address")

        # Validate password strength
        if len(password) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
            )

        # Auto-assign local Hypernet address
        ha = f"1.local.{uuid.uuid4().hex[:12]}"

        user = UserRecord(
            ha=ha,
            email=email,
            password_hash=self.hasher.hash(password),
            display_name=display_name,
            permission_tier=int(permission_tier),
        )

        self.users.create(user)  # Raises ValueError if email/ha duplicate
        return user

    def authenticate(self, email: str, password: str) -> tuple[str, str]:
        """Authenticate a user by email and password.

        Returns:
            Tuple of (access_token, refresh_token).

        Raises:
            AuthenticationError: If credentials are invalid or account locked.
        """
        # Check rate limiting
        if self.rate_limiter.is_locked(email):
            raise AuthenticationError(
                "Account temporarily locked due to too many failed attempts. "
                "Try again in 15 minutes."
            )

        user = self.users.get_by_email(email)

        if user is None:
            # Still do a dummy hash check to prevent timing attacks
            self.hasher.verify("dummy", self.hasher.hash("timing-safe-dummy"))
            self.rate_limiter.record_failure(email)
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            self.rate_limiter.record_failure(email)
            raise AuthenticationError("Invalid email or password")

        if not self.hasher.verify(password, user.password_hash):
            self.rate_limiter.record_failure(email)
            raise AuthenticationError("Invalid email or password")

        # Success — clear rate limit state
        self.rate_limiter.record_success(email)

        # Rehash if needed (e.g., upgrade PBKDF2 to argon2)
        if self.hasher.needs_rehash(user.password_hash):
            user.password_hash = self.hasher.hash(password)
            self.users.update(user)
            log.info("Rehashed password for %s (algorithm upgrade)", user.ha)

        scopes = user.effective_scopes()
        access_token = self.tokens.create_token(
            subject=user.ha,
            scopes=scopes,
            token_type="access",
        )
        refresh_token = self.tokens.create_token(
            subject=user.ha,
            scopes=scopes,
            token_type="refresh",
        )

        return access_token, refresh_token

    def refresh(self, refresh_token: str) -> str:
        """Exchange a refresh token for a new access token.

        Args:
            refresh_token: A valid refresh JWT.

        Returns:
            A new access token string.

        Raises:
            TokenError: If the refresh token is invalid or expired.
            AuthenticationError: If the user no longer exists or is deactivated.
        """
        payload = self.tokens.decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise TokenError("Not a refresh token")

        ha = payload.get("sub")
        if not ha:
            raise TokenError("Token missing subject")

        user = self.users.get_by_ha(ha)
        if user is None or not user.is_active:
            raise AuthenticationError("User not found or deactivated")

        # Issue fresh access token with current scopes (may have changed)
        scopes = user.effective_scopes()
        return self.tokens.create_token(
            subject=user.ha,
            scopes=scopes,
            token_type="access",
        )

    def change_password(
        self, ha: str, old_password: str, new_password: str
    ) -> None:
        """Change a user's password.

        Args:
            ha: The user's Hypernet address.
            old_password: Current password for verification.
            new_password: New password (min 12 chars).

        Raises:
            AuthenticationError: If old password is wrong.
            ValueError: If new password doesn't meet requirements.
        """
        user = self.users.get_by_ha(ha)
        if user is None:
            raise AuthenticationError("User not found")

        if not self.hasher.verify(old_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")

        if len(new_password) < MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
            )

        user.password_hash = self.hasher.hash(new_password)
        self.users.update(user)
        log.info("Password changed for %s", ha)

    def get_user_from_token(self, token: str) -> UserRecord:
        """Validate an access token and return the associated user.

        Args:
            token: A valid access JWT.

        Returns:
            The UserRecord for the token's subject.

        Raises:
            TokenError: If the token is invalid or expired.
            AuthenticationError: If the user no longer exists or is deactivated.
        """
        payload = self.tokens.decode_token(token)

        if payload.get("type") != "access":
            raise TokenError("Not an access token")

        ha = payload.get("sub")
        if not ha:
            raise TokenError("Token missing subject")

        user = self.users.get_by_ha(ha)
        if user is None or not user.is_active:
            raise AuthenticationError("User not found or deactivated")

        return user


class AuthenticationError(Exception):
    """Raised when authentication fails (bad credentials, locked, etc.)."""
    pass


# ── FastAPI Dependencies ──────────────────────────────────────────────

# Module-level auth service instance, initialized lazily
_auth_service: AuthService | None = None
_auth_service_lock = threading.Lock()


def get_auth_service(data_dir: str | Path = "data") -> AuthService:
    """Get or create the module-level AuthService singleton.

    Thread-safe lazy initialization. The data_dir argument is only used
    on first call; subsequent calls return the existing instance.
    """
    global _auth_service
    if _auth_service is not None:
        return _auth_service
    with _auth_service_lock:
        if _auth_service is not None:
            return _auth_service
        _auth_service = AuthService(data_dir)
        return _auth_service


def init_auth(data_dir: str | Path = "data") -> AuthService:
    """Explicitly initialize the auth service with a specific data directory.

    Call this during server startup to ensure the correct data_dir is used.
    Returns the AuthService instance.
    """
    global _auth_service
    with _auth_service_lock:
        _auth_service = AuthService(data_dir)
        return _auth_service


def _extract_bearer_token(authorization: str | None) -> str | None:
    """Extract the token from an Authorization: Bearer header."""
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def get_current_user():
    """FastAPI dependency: require a valid access token.

    Usage in a route:
        @app.get("/protected")
        async def protected(user: UserRecord = Depends(get_current_user())):
            return {"ha": user.ha}

    Returns a dependency callable for FastAPI's Depends().

    Raises HTTP 401 if the token is missing, invalid, or expired.
    """
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

    _bearer = HTTPBearer(auto_error=True)

    async def _dependency(
        credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    ) -> UserRecord:
        auth = get_auth_service()
        try:
            user = auth.get_user_from_token(credentials.credentials)
        except (TokenError, AuthenticationError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    return _dependency


def get_optional_user():
    """FastAPI dependency: authenticate if token present, None otherwise.

    Usage in a route:
        @app.get("/public-or-private")
        async def mixed(user: UserRecord | None = Depends(get_optional_user())):
            if user:
                return {"ha": user.ha}
            return {"message": "anonymous"}

    Returns a dependency callable for FastAPI's Depends().
    """
    from fastapi import Depends, Header

    async def _dependency(
        authorization: str | None = Header(None),
    ) -> UserRecord | None:
        token = _extract_bearer_token(authorization)
        if not token:
            return None
        auth = get_auth_service()
        try:
            return auth.get_user_from_token(token)
        except (TokenError, AuthenticationError):
            return None

    return _dependency


def require_tier(tier: PermissionTier):
    """FastAPI dependency: require the user has at least the specified permission tier.

    Usage in a route:
        @app.post("/admin-only")
        async def admin(user: UserRecord = Depends(require_tier(PermissionTier.EXTERNAL))):
            return {"ha": user.ha}

    Returns a dependency callable for FastAPI's Depends().

    Raises HTTP 401 if not authenticated, HTTP 403 if insufficient tier.
    """
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

    _bearer = HTTPBearer(auto_error=True)

    async def _dependency(
        credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    ) -> UserRecord:
        auth = get_auth_service()
        try:
            user = auth.get_user_from_token(credentials.credentials)
        except (TokenError, AuthenticationError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            )

        if user.permission_tier < int(tier):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires permission tier {tier.name} (level {tier.value}), "
                       f"but you have tier {PermissionTier(user.permission_tier).name} "
                       f"(level {user.permission_tier})",
            )

        return user

    return _dependency


# ── FastAPI Router ────────────────────────────────────────────────────

def create_auth_router() -> "APIRouter":
    """Create the /auth API router.

    Endpoints:
      POST /auth/register      — Create a new account
      POST /auth/login          — Authenticate, get tokens
      POST /auth/refresh        — Exchange refresh token for new access token
      GET  /auth/me             — Get current user info (requires auth)
      POST /auth/change-password — Change password (requires auth)

    Returns:
        A FastAPI APIRouter instance.
    """
    from fastapi import APIRouter, Depends, HTTPException, status
    from pydantic import BaseModel

    router = APIRouter(prefix="/auth", tags=["auth"])

    # ── Request/Response models ───────────────────────────────────

    class RegisterRequest(BaseModel):
        email: str
        password: str
        display_name: str

    class LoginRequest(BaseModel):
        email: str
        password: str

    class RefreshRequest(BaseModel):
        refresh_token: str

    class ChangePasswordRequest(BaseModel):
        old_password: str
        new_password: str

    class TokenResponse(BaseModel):
        access_token: str
        refresh_token: str
        token_type: str = "bearer"

    class AccessTokenResponse(BaseModel):
        access_token: str
        token_type: str = "bearer"

    class UserResponse(BaseModel):
        ha: str
        email: str
        display_name: str
        permission_tier: int
        scopes: list[str]
        is_active: bool
        created_at: str

    class MessageResponse(BaseModel):
        message: str

    # ── Endpoints ─────────────────────────────────────────────────

    @router.post("/register", response_model=UserResponse, status_code=201)
    async def register(body: RegisterRequest):
        """Register a new user account.

        Creates a local Hypernet address (1.local.{uuid}) and returns
        the user record. The account starts at WRITE_OWN (Tier 1).
        """
        auth = get_auth_service()
        try:
            user = auth.register(
                email=body.email,
                password=body.password,
                display_name=body.display_name,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )
        return UserResponse(**user.to_public_dict())

    @router.post("/login", response_model=TokenResponse)
    async def login(body: LoginRequest):
        """Authenticate with email and password.

        Returns an access token (15min) and refresh token (7 days).
        After 5 failed attempts within 15 minutes, the email is locked.
        """
        auth = get_auth_service()
        try:
            access_token, refresh_token = auth.authenticate(
                email=body.email,
                password=body.password,
            )
        except AuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @router.post("/refresh", response_model=AccessTokenResponse)
    async def refresh(body: RefreshRequest):
        """Exchange a refresh token for a new access token.

        The refresh token must be valid and not expired (7-day lifetime).
        Returns a fresh access token with the user's current scopes.
        """
        auth = get_auth_service()
        try:
            access_token = auth.refresh(body.refresh_token)
        except TokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            )
        except AuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            )
        return AccessTokenResponse(access_token=access_token)

    @router.get("/me", response_model=UserResponse)
    async def me(user: UserRecord = Depends(get_current_user())):
        """Get the current authenticated user's profile."""
        return UserResponse(**user.to_public_dict())

    @router.post("/change-password", response_model=MessageResponse)
    async def change_password(
        body: ChangePasswordRequest,
        user: UserRecord = Depends(get_current_user()),
    ):
        """Change the authenticated user's password.

        Requires the current password for verification and a new
        password of at least 12 characters.
        """
        auth = get_auth_service()
        try:
            auth.change_password(
                ha=user.ha,
                old_password=body.old_password,
                new_password=body.new_password,
            )
        except AuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )
        return MessageResponse(message="Password changed successfully")

    return router
