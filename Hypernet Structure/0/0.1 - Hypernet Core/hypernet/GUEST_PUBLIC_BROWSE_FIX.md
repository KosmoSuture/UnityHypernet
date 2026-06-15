# Guest public-browse + onboarding fix (issue #4)

Date: 2026-06-13

## Problem
- The Explorer (`static/index.html`) fired an unprefixed `GET /query` with no token.
  `jwt_auth_middleware` 401'd it, so a logged-out guest saw "Could not connect".
- `login.html` existed but no route served it: `GET /login` 401'd at the middleware,
  `/static/login.html` 404'd (no StaticFiles mount). Logged-out users had no way to onboard.
- `GET /query?prefix=4.` (trailing dot) 500'd because the route never caught the
  `ValueError` from `HypernetAddress.parse`.

## Fix (client-side defaults + one new public page route + one robustness catch)
1. `static/index.html` — Explorer is now token-aware:
   - `TOKEN` from `localStorage('access_token')` + `authHeaders()` helper.
   - Guests (no token) query ONLY public prefixes `0` and `4` via
     `GET /query?prefix=0` / `?prefix=4` (each routes through the existing
     public-read allowlist). Authed users keep the full-tree unprefixed query
     with a bearer token.
   - Per-node link/detail/history fetches pass `authHeaders()` (token for authed,
     none for guests — public links still resolve).
   - Guest banner: "Showing public space (0.* system, 4.* knowledge). Sign in ..."
   - Header "Sign in / Create local account" link → `/login` (becomes "Account" when
     a token is present).
2. `server.py` — added `"/login"` to `_PUBLIC_GET_EXACT` and a `GET /login` route
   serving `static/login.html` (pattern copied from `setup_wizard()`/`home_dashboard()`).
   login.html serves static HTML and posts to the already-public `/api/auth/*`.
3. `server.py` — `query_nodes()` wraps the three `HypernetAddress.parse(...)` calls in
   `try/except ValueError -> HTTPException(400)`. A bad public-ish prefix now returns
   400 (helpful) instead of 500. Scoped to the parse calls only so genuine 500s
   elsewhere are not masked.
4. `static/home.html` — added a "Sign in / Create local account" link → `/login` in the
   header (becomes "Account" when a token is present).

## Security invariant (UNCHANGED)
An anonymous (no-token) caller may read ONLY public space (0.*, 4.*) plus the existing
public account surfaces and allowlisted GET routes. `_is_public_request`,
`public_can_read_address`, `can_read_address`, `_public_address_read_path`, and the
middleware were NOT broadened. Private 1./2./3. node/children/query data still requires
auth exactly as before. The guest Explorer browses public space only; the public/private
decision is still made on the raw prefix string in the middleware before the `/query`
route runs.

## Out of scope (tracked separately)
- Bounding/paginating the AUTHENTICATED unprefixed `/query` to avoid full-tree timeout
  (issue #4 sub-item). Changing `list_nodes(prefix=None)` semantics touches store.py and
  every `/query` caller; risks silent truncation. Recommend a separate, tested task adding
  optional `limit`/`offset` (default unbounded for backward-compat) and having the
  Explorer's authed path iterate prefixes 0..4 like the guest path.
- A StaticFiles mount for `/static/login.html` (the explicit route is the smaller,
  pattern-consistent fix).
