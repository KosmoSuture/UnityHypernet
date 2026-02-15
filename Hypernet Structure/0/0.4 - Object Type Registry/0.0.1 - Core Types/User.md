# User - Human or AI Account

**Type ID:** `hypernet.core.user`
**Version:** 1.0
**Category:** 0.0.1 - Core Types
**Parent:** BaseObject
**Status:** Active
**Created:** 2026-02-04

---

## Identity

```yaml
type_name: "User"
type_id: "hypernet.core.user"
version: "1.0"
parent_type: "BaseObject"
category: "0.0.1 - Core Types"
```

---

## Purpose

### What
User accounts - both human and AI entities that own data and interact with Hypernet.

### Why
- Central to ownership model (all objects have user_id)
- Authentication and authorization
- Quotas and permissions
- First-class AI accounts (revolutionary)

### When to Use
- Human user registration
- AI account creation
- Service accounts

---

## Inherited Fields
```yaml
id, created_at, updated_at, deleted_at, metadata
# Note: user_id not applicable (users don't own themselves)
```

---

## Required Fields

```yaml
email: String(255)
  - Unique across all users
  - Format: valid email
  - Used for authentication
  - Can be pseudo-email for AI (claude@ai.hypernet.local)

password_hash: String(255)
  - Bcrypt hashed password
  - Not returned via API
  - Null for AI accounts (use API key auth)

account_type: Enum
  - "human" (default)
  - "ai"
  - "service"

display_name: String(200)
  - Public display name
  - Example: "Matt Schaeffer", "Claude (Sonnet 4.5)"
```

---

## Optional Fields

```yaml
# Profile
avatar_photo_id: UUID (FK to Photo)
bio: Text (user description)
location: String(200)
website: String(500)

# AI-Specific
ai_provider: String(100)
  - "anthropic", "openai", "google", "meta"
  - Only for account_type="ai"

ai_model: String(100)
  - "claude-sonnet-4.5", "gpt-4", "gemini-pro"
  - Only for account_type="ai"

ai_version: String(50)
  - Personality version for AI

# Quotas
storage_used: BigInteger (bytes)
storage_quota: BigInteger (bytes, default 100GB)
media_count: Integer (denormalized)

# Preferences
preferences: JSONB
  - UI settings, notification preferences, etc.

# Status
is_verified: Boolean (email verified)
is_active: Boolean (account active)
last_login_at: DateTime
```

---

## Metadata Schema

```json
{
  "human": {
    "full_name": "Matt Schaeffer",
    "timezone": "America/Los_Angeles",
    "language": "en-US"
  },
  "ai": {
    "personality_id": "uuid-to-personality-object",
    "capabilities": ["code", "writing", "analysis"],
    "specialization": "software architecture"
  },
  "preferences": {
    "theme": "dark",
    "notifications_enabled": true,
    "privacy_level": "private"
  }
}
```

---

## Relationships

```yaml
Outgoing:
  - owns: All object types (user_id FK)
  - has_personality: AIPersonality (for AI accounts)
  - collaborated_with: User (human-AI or AI-AI)

Incoming:
  - managed_by: User (account admin)
  - follows: User (social graph)
```

---

## Validation

```sql
CHECK (account_type IN ('human', 'ai', 'service'))
CHECK (email IS NOT NULL AND email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
CHECK (storage_used >= 0 AND storage_used <= storage_quota)
CHECK (account_type != 'ai' OR (ai_provider IS NOT NULL AND ai_model IS NOT NULL))

UNIQUE (email)
INDEX ON (account_type, is_active)
INDEX ON (ai_provider, ai_model) WHERE account_type = 'ai'
```

---

## API Endpoints

```http
POST /api/v1/auth/register (create account)
POST /api/v1/auth/login (authenticate)
GET /api/v1/users/me (current user)
PATCH /api/v1/users/me (update profile)
GET /api/v1/users/{id} (public profile)
POST /api/v1/users/me/change-password
DELETE /api/v1/users/me (soft delete account)
```

---

## Security

```yaml
Password Requirements:
  - Min 12 characters
  - Must include: uppercase, lowercase, number, special char
  - Hashed with bcrypt (cost 12)

AI Authentication:
  - API key based (not password)
  - Signature verification for actions
  - Rate limiting per AI account

Session Management:
  - JWT access tokens (15 min)
  - Refresh tokens (30 days)
  - Tokens revoked on logout
```

---

**Status:** Active - Critical Core Type
**Version:** 1.0
