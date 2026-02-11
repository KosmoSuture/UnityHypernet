# Test Suite

**Purpose:** Automated tests for Hypernet Core application

**Status:** Active development

**Target Coverage:** 70%+ code coverage

---

## Overview

This directory contains all automated tests for Hypernet Core 0.1. We follow a comprehensive testing strategy covering unit tests, integration tests, and end-to-end tests to ensure code quality, prevent regressions, and enable confident refactoring.

---

## Testing Philosophy

### Why We Test

1. **Prevent Regressions:** Catch bugs before they reach production
2. **Enable Refactoring:** Change code confidently without breaking functionality
3. **Document Behavior:** Tests serve as executable documentation
4. **Design Feedback:** Hard-to-test code is often poorly designed
5. **Faster Development:** Automated tests faster than manual testing

### Testing Pyramid

```
        ┌─────────────┐
        │  E2E Tests  │  <- Few, slow, test full system
        │   (5-10%)   │
        ├─────────────┤
        │ Integration │  <- Medium number, test component interaction
        │   (20-30%)  │
        ├─────────────┤
        │ Unit Tests  │  <- Many, fast, test individual functions
        │  (60-75%)   │
        └─────────────┘
```

**Bottom-heavy pyramid:** Most tests are fast unit tests, fewer slow E2E tests.

---

## Directory Structure

```
tests/
├── __init__.py
├── conftest.py                 # Pytest fixtures and configuration
├── README.md                   # This file
│
├── unit/                       # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_models/           # Test ORM models
│   │   ├── test_user.py
│   │   ├── test_media.py
│   │   ├── test_album.py
│   │   ├── test_integration.py
│   │   └── test_link.py
│   ├── test_services/         # Test business logic
│   │   ├── test_auth_service.py
│   │   ├── test_user_service.py
│   │   ├── test_media_service.py
│   │   ├── test_album_service.py
│   │   ├── test_integration_service.py
│   │   └── test_link_service.py
│   └── test_utils/            # Test utility functions
│       ├── test_security.py
│       ├── test_validation.py
│       └── test_file_utils.py
│
├── integration/               # Integration tests (medium speed)
│   ├── __init__.py
│   ├── test_api/             # Test API endpoints
│   │   ├── test_auth_routes.py
│   │   ├── test_user_routes.py
│   │   ├── test_media_routes.py
│   │   ├── test_album_routes.py
│   │   └── test_integration_routes.py
│   ├── test_database/        # Test database operations
│   │   ├── test_migrations.py
│   │   ├── test_queries.py
│   │   └── test_transactions.py
│   └── test_integrations/    # Test external integrations
│       ├── test_instagram.py
│       └── test_google_photos.py
│
├── e2e/                      # End-to-end tests (slow)
│   ├── __init__.py
│   ├── test_user_flows.py    # Complete user workflows
│   ├── test_media_flows.py
│   └── test_sync_flows.py
│
├── security/                 # Security tests
│   ├── __init__.py
│   ├── test_authentication.py
│   ├── test_authorization.py
│   ├── test_input_validation.py
│   └── test_injection_prevention.py
│
├── performance/              # Performance tests
│   ├── __init__.py
│   ├── test_api_performance.py
│   └── test_query_performance.py
│
└── fixtures/                 # Test data and fixtures
    ├── sample_media/
    │   ├── test_photo.jpg
    │   ├── test_video.mp4
    │   └── test_document.pdf
    └── sample_data.json
```

---

## Test Types

### 1. Unit Tests (`tests/unit/`)

**Purpose:** Test individual functions/methods in isolation

**Characteristics:**
- Fast (milliseconds)
- No external dependencies (mock database, network)
- Test one thing at a time
- Run frequently during development

**Example:**

```python
# tests/unit/test_services/test_album_service.py
import pytest
from unittest.mock import Mock
from app.services.album_service import AlbumService
from app.services.exceptions import ValidationError

def test_create_album_success():
    """Test creating album with valid data."""
    # Arrange
    db_mock = Mock()
    service = AlbumService(db_mock)

    # Act
    album = service.create_album(
        user_id=uuid4(),
        name="Test Album",
        description="Test Description"
    )

    # Assert
    assert album.name == "Test Album"
    assert album.media_count == 0
    db_mock.add.assert_called_once()
    db_mock.commit.assert_called_once()

def test_create_album_empty_name():
    """Test creating album with empty name fails."""
    db_mock = Mock()
    service = AlbumService(db_mock)

    with pytest.raises(ValidationError, match="name cannot be empty"):
        service.create_album(user_id=uuid4(), name="")
```

### 2. Integration Tests (`tests/integration/`)

**Purpose:** Test component interactions (API + Database, Service + Model)

**Characteristics:**
- Medium speed (seconds)
- Use real database (test database)
- Test multiple components together
- Run before commits/PRs

**Example:**

```python
# tests/integration/test_api/test_album_routes.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_album_api(test_db, auth_headers):
    """Test album creation via API."""
    # Act
    response = client.post(
        "/api/v1/albums",
        json={"name": "Vacation 2026", "description": "Summer trip"},
        headers=auth_headers
    )

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Vacation 2026"
    assert data["media_count"] == 0
    assert "id" in data

def test_create_album_unauthorized(test_db):
    """Test album creation without auth fails."""
    response = client.post(
        "/api/v1/albums",
        json={"name": "Test"}
    )
    assert response.status_code == 401
```

### 3. End-to-End Tests (`tests/e2e/`)

**Purpose:** Test complete user workflows from start to finish

**Characteristics:**
- Slow (seconds to minutes)
- Test entire system
- Simulate real user behavior
- Run before releases

**Example:**

```python
# tests/e2e/test_media_flows.py
def test_complete_photo_upload_workflow(test_db, auth_headers):
    """
    Test complete workflow:
    1. Register user
    2. Login
    3. Create album
    4. Upload photo
    5. Add photo to album
    6. Retrieve album with photos
    """
    # 1. Register
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123!"}
    )
    assert register_response.status_code == 201

    # 2. Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "SecurePass123!"}
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Create album
    album_response = client.post(
        "/api/v1/albums",
        json={"name": "Test Album"},
        headers=headers
    )
    album_id = album_response.json()["id"]

    # 4. Upload photo
    with open("tests/fixtures/sample_media/test_photo.jpg", "rb") as f:
        upload_response = client.post(
            "/api/v1/media/upload",
            files={"file": f},
            headers=headers
        )
    media_id = upload_response.json()["id"]

    # 5. Add to album
    add_response = client.post(
        f"/api/v1/albums/{album_id}/media",
        json={"media_id": media_id},
        headers=headers
    )
    assert add_response.status_code == 201

    # 6. Retrieve album
    get_response = client.get(f"/api/v1/albums/{album_id}", headers=headers)
    assert get_response.json()["media_count"] == 1
```

### 4. Security Tests (`tests/security/`)

**Purpose:** Verify security controls and prevent vulnerabilities

**Example:**

```python
# tests/security/test_injection_prevention.py
def test_sql_injection_prevention(test_db, auth_headers):
    """Test that SQL injection attempts are blocked."""
    # Try SQL injection in search parameter
    response = client.get(
        "/api/v1/media?search=' OR '1'='1",
        headers=auth_headers
    )
    # Should not return all media, should be empty or error
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        # Injection should have no effect
        assert len(response.json()["items"]) == 0

def test_path_traversal_prevention(test_db, auth_headers):
    """Test that path traversal attempts are blocked."""
    response = client.get(
        "/api/v1/media/../../etc/passwd",
        headers=auth_headers
    )
    assert response.status_code == 400  # Bad request, not file contents
```

### 5. Performance Tests (`tests/performance/`)

**Purpose:** Ensure performance meets requirements

**Example:**

```python
# tests/performance/test_api_performance.py
import time

def test_media_list_performance(test_db, auth_headers, test_media_100):
    """Test that listing media is fast enough."""
    start = time.time()

    response = client.get(
        "/api/v1/media?limit=50",
        headers=auth_headers
    )

    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 0.5  # Should complete in < 500ms
```

---

## Running Tests

### All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v
```

### Specific Test Types

```bash
# Unit tests only (fast)
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only (slow)
pytest tests/e2e/

# Security tests
pytest tests/security/
```

### Specific Test Files

```bash
# Single file
pytest tests/unit/test_services/test_album_service.py

# Single test function
pytest tests/unit/test_services/test_album_service.py::test_create_album_success

# Tests matching pattern
pytest -k "album"
```

### Watch Mode

```bash
# Re-run tests on file changes (requires pytest-watch)
ptw
```

---

## Test Fixtures

Fixtures provide reusable test data and setup.

### Common Fixtures (`conftest.py`)

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User
from uuid import uuid4

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test."""
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()

@pytest.fixture
def test_user(test_db):
    """Create a test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        password_hash="$2b$12$...",  # bcrypt hash of "password123"
        display_name="Test User"
    )
    test_db.add(user)
    test_db.commit()
    return user

@pytest.fixture
def auth_headers(test_user):
    """Generate authentication headers."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_media(test_db, test_user):
    """Create test media."""
    from app.models.media import Media
    media = Media(
        id=uuid4(),
        user_id=test_user.id,
        filename="test.jpg",
        media_type="photo",
        mime_type="image/jpeg",
        size=1024000,
        file_path="/media/test.jpg",
        hash="abcd1234"
    )
    test_db.add(media)
    test_db.commit()
    return media
```

---

## Test Database

### Strategy

- **Unit Tests:** Mock database (no real DB)
- **Integration/E2E Tests:** Real database (SQLite in-memory for speed)

### Test Database Setup

```python
# Use SQLite in-memory for tests (fast, isolated)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Or use PostgreSQL test database (more realistic)
TEST_DATABASE_URL = "postgresql://hypernet_test:password@localhost/hypernet_test"
```

### Cleanup Between Tests

```python
@pytest.fixture(autouse=True)
def reset_db(test_db):
    """Reset database state between tests."""
    yield
    # Rollback any uncommitted changes
    test_db.rollback()
    # Clear all tables
    for table in reversed(Base.metadata.sorted_tables):
        test_db.execute(table.delete())
    test_db.commit()
```

---

## Best Practices

### 1. Test Naming

```python
# ✅ GOOD: Descriptive test names
def test_create_album_with_valid_data_succeeds():
def test_create_album_with_empty_name_raises_validation_error():
def test_get_album_as_non_owner_raises_permission_error():

# ❌ BAD: Vague test names
def test_album():
def test_1():
```

### 2. Arrange-Act-Assert (AAA) Pattern

```python
def test_example():
    # Arrange: Set up test data
    user = create_test_user()
    album = create_test_album(user)

    # Act: Perform the operation
    result = service.get_album(album.id, user.id)

    # Assert: Verify the results
    assert result.id == album.id
    assert result.name == album.name
```

### 3. One Assertion Per Test (When Practical)

```python
# ✅ GOOD: Test one thing
def test_create_album_sets_name():
    album = service.create_album(name="Test")
    assert album.name == "Test"

def test_create_album_sets_media_count_to_zero():
    album = service.create_album(name="Test")
    assert album.media_count == 0

# ⚠️ ACCEPTABLE: Related assertions
def test_create_album_success():
    album = service.create_album(name="Test")
    assert album.id is not None
    assert album.name == "Test"
    assert album.media_count == 0
```

### 4. Test Edge Cases

```python
# Test happy path
def test_create_album_success(): ...

# Test edge cases
def test_create_album_with_empty_name(): ...
def test_create_album_with_very_long_name(): ...
def test_create_album_with_special_characters(): ...
def test_create_album_with_null_user_id(): ...
```

### 5. Don't Test Implementation Details

```python
# ❌ BAD: Testing internal method
def test_album_service_calls_validate_name():
    service.create_album(name="Test")
    assert service._validate_name.called  # Testing implementation

# ✅ GOOD: Testing behavior
def test_create_album_with_invalid_name_fails():
    with pytest.raises(ValidationError):
        service.create_album(name="")
```

### 6. Use Mocks Sparingly

```python
# ✅ GOOD: Mock external services
@patch('app.services.integration_service.InstagramClient')
def test_sync_from_instagram(mock_client):
    mock_client.fetch_media.return_value = [...]
    service.sync_from_integration(integration_id)

# ❌ BAD: Mocking internal code
@patch('app.services.album_service.AlbumService.get_album')
def test_update_album(mock_get):
    # If you're mocking the class you're testing, something's wrong
```

---

## Code Coverage

### Coverage Goals

- **Overall:** 70%+ code coverage
- **Critical Paths:** 90%+ (authentication, payment, data deletion)
- **Not Everything:** 100% coverage is often wasteful

### Running Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html

# View report
open htmlcov/index.html

# Show missing lines
pytest --cov=app --cov-report=term-missing
```

### What to Cover

✅ **High Priority:**
- Business logic (services)
- Authentication and authorization
- Data validation
- Critical user workflows

⚠️ **Medium Priority:**
- API routes (covered by integration tests)
- Database models (basic CRUD)
- Utility functions

❌ **Low Priority:**
- Auto-generated code
- Third-party library code
- Simple getters/setters
- Configuration files

---

## Continuous Integration

### Pre-Commit Hooks

Run tests before committing:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest tests/unit/
        language: system
        pass_filenames: false
```

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
```

---

## Testing Checklist

### Before Committing

- [ ] All tests pass (`pytest`)
- [ ] New code has tests
- [ ] Coverage hasn't decreased
- [ ] No test warnings
- [ ] Tests are fast (< 5 seconds for unit tests)

### Before Merging PR

- [ ] All tests pass on CI
- [ ] Integration tests pass
- [ ] Security tests pass
- [ ] Code coverage meets threshold (70%)
- [ ] Tests reviewed by another developer

### Before Release

- [ ] All tests pass
- [ ] E2E tests pass
- [ ] Performance tests pass
- [ ] Security audit complete
- [ ] Load testing complete (if applicable)

---

## Common Testing Patterns

### Testing Exceptions

```python
# Test that exception is raised
with pytest.raises(ValidationError):
    service.create_album(name="")

# Test exception message
with pytest.raises(ValidationError, match="name cannot be empty"):
    service.create_album(name="")
```

### Testing Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result == expected
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

### Testing Database Transactions

```python
def test_rollback_on_error(test_db):
    """Test that transaction rolls back on error."""
    initial_count = test_db.query(Album).count()

    try:
        service.create_album(name="Test")
        raise Exception("Simulated error")
    except:
        test_db.rollback()

    final_count = test_db.query(Album).count()
    assert final_count == initial_count  # No album created
```

---

## Tools and Libraries

### Core Testing Tools

- **pytest:** Test framework
- **pytest-cov:** Coverage reporting
- **pytest-asyncio:** Async test support
- **pytest-mock:** Mocking utilities

### HTTP Testing

- **FastAPI TestClient:** API testing (built-in)
- **httpx:** HTTP client for async tests

### Database Testing

- **SQLAlchemy:** Database fixtures
- **pytest-postgresql:** PostgreSQL test fixtures
- **factory-boy:** Test data factories (optional)

### Security Testing

- **bandit:** Security linting
- **safety:** Dependency vulnerability scanning
- **pytest-security:** Security test utilities

---

## Status

**Test Files:** 0 (folder ready for test development)
**Target Coverage:** 70%+
**Next Tests to Write:**
1. Unit tests for models
2. Unit tests for services
3. Integration tests for API routes
4. Security tests for authentication

**Priority:** Critical - Tests enable confident development

---

## Quick Reference

### Run Commands

```bash
# Fast feedback loop (unit tests only)
pytest tests/unit/ -v

# Before commit (unit + integration)
pytest tests/unit/ tests/integration/

# Full test suite
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/unit/test_services/test_album_service.py::test_create_album
```

### Writing a New Test

1. Create test file in appropriate directory
2. Import pytest and code under test
3. Write test function starting with `test_`
4. Use AAA pattern (Arrange, Act, Assert)
5. Run test to verify it works
6. Verify coverage with `pytest --cov`

---

**Location:** `C:\Hypernet\Hypernet Structure\0.1 - Hypernet Core\0.1.1 - Core System\tests\`
**Version:** 1.0
**Created:** 2026-02-10
**Maintainer:** Hypernet Development Team
