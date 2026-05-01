---
ha: "0.1.1"
object_type: "index"
status: "active"
visibility: "public"
addressed_by: "2.6.codex"
addressed_at: "2026-05-01"
---
# Hypernet Core 0.1.1 - Core System

**Status:** In Development
**Language:** Python 3.11+
**Framework:** FastAPI
**Database:** PostgreSQL 15+

---

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Database

```bash
# Install PostgreSQL (if not already installed)
# Ubuntu/Debian:
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE hypernet;
CREATE USER hypernet WITH PASSWORD 'dev-password';
GRANT ALL PRIVILEGES ON DATABASE hypernet TO hypernet;
\q

# Run initial migration
psql -U hypernet -d hypernet -f ../0.1.0\ -\ Planning\ \&\ Documentation/Database-Design/02-Initial-Migration.sql
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 4. Run Development Server

```bash
# Start server
python app/main.py

# Or use uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8443
```

### 5. Test the API

```bash
# Health check
curl http://localhost:8443/health

# API documentation
open http://localhost:8443/api/docs
```

---

## Project Structure

```
0.1.1 - Core System/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Configuration (environment variables)
│   │   ├── database.py        # Database connection
│   │   └── security.py        # Password hashing, JWT tokens
│   ├── models/
│   │   ├── user.py           # SQLAlchemy User model
│   │   ├── media.py          # Media model (TODO)
│   │   ├── album.py          # Album model (TODO)
│   │   ├── integration.py    # Integration model (TODO)
│   │   └── link.py           # Link model (TODO)
│   ├── routes/
│   │   ├── auth.py           # Authentication endpoints (register, login)
│   │   ├── users.py          # User profile endpoints (TODO)
│   │   ├── media.py          # Media endpoints (TODO)
│   │   ├── albums.py         # Album endpoints (TODO)
│   │   ├── integrations.py   # Integration endpoints (TODO)
│   │   └── links.py          # Link endpoints (TODO)
│   └── services/             # Business logic (TODO)
├── tests/                    # Test suite (TODO)
├── requirements.txt          # Python dependencies
├── .env.example             # Example environment variables
└── README.md                # This file
```

---

## Current Status

### ✅ Completed
- [x] Project structure created
- [x] FastAPI application skeleton
- [x] Database configuration (SQLAlchemy)
- [x] Security utilities (password hashing, JWT)
- [x] User model (SQLAlchemy ORM)
- [x] Auth routes (register, login) **WORKING**
- [x] Health check endpoint
- [x] API documentation (auto-generated)

### ⏳ In Progress
- [ ] Complete remaining models (Media, Album, Integration, Link)
- [ ] Authentication middleware (get current user from JWT)
- [ ] User profile endpoints
- [ ] Media upload functionality

### 📋 TODO (Milestone 1 - Weeks 3-5)
- [ ] Complete all ORM models
- [ ] Implement authentication middleware
- [ ] Add rate limiting
- [ ] Add input validation
- [ ] Write unit tests
- [ ] Set up CI/CD

---

## API Endpoints

### Implemented ✅

**System:**
- `GET /health` - Health check
- `GET /api/v1/version` - Version info

**Authentication:**
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens

### Planned ⏳

**Users:**
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update profile
- `POST /api/v1/users/me/change-password` - Change password

**Media:**
- `POST /api/v1/media/upload` - Upload media
- `GET /api/v1/media` - List media
- `GET /api/v1/media/{id}` - Get media details
- `DELETE /api/v1/media/{id}` - Delete media

(See API-Design documentation for complete endpoint list)

---

## Testing

### Manual Testing

```bash
# Register a user
curl -X POST http://localhost:8443/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "display_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8443/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

### Automated Tests (TODO)

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

---

## Development

### Code Quality

```bash
# Format code
black app/

# Lint code
ruff check app/

# Type check
mypy app/
```

### Database Migrations (Alembic)

```bash
# Create migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Configuration

Key environment variables (see `.env.example`):

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 15)
- `MAX_UPLOAD_SIZE` - Max file upload size in bytes
- `CORS_ORIGINS` - Allowed CORS origins

---

## Security Notes

### Development

- Default SECRET_KEY is insecure (change in .env)
- DEBUG mode enabled (disable in production)
- All traffic over HTTP (use HTTPS in production)

### Production Checklist

- [ ] Change SECRET_KEY to random secure value
- [ ] Set DEBUG=false
- [ ] Enable HTTPS (TLS certificates)
- [ ] Set secure CORS_ORIGINS
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular backups
- [ ] Security audit

---

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check database exists
psql -U postgres -l | grep hypernet

# Recreate database if needed
psql -U postgres -c "DROP DATABASE IF EXISTS hypernet;"
psql -U postgres -c "CREATE DATABASE hypernet;"
```

### Module Import Errors

```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Port Already in Use

```bash
# Find process using port 8443
lsof -i :8443

# Kill process (if safe)
kill -9 <PID>

# Or use different port in .env
PORT=8080
```

---

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for functions/classes
- Keep functions small and focused

### Commit Messages

```
<type>: <subject>

<body>

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Types: feat, fix, docs, refactor, test, chore

---

## Documentation

- **Architecture:** See `0.1.0 - Planning & Documentation/Architecture/`
- **API Design:** See `0.1.0 - Planning & Documentation/API-Design/`
- **Database:** See `0.1.0 - Planning & Documentation/Database-Design/`
- **Roadmap:** See `0.1.0 - Planning & Documentation/Development-Roadmap/`

---

## Status

**Phase:** Milestone 1 (Foundation) - Week 3 of 16
**Progress:** ~20% complete
**Next:** Complete ORM models, implement auth middleware

**Created by:** Matt Schaeffer (CEO/Owner) & Claude (Anthropic Sonnet 4.5)
**License:** MIT
