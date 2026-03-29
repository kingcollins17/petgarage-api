import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from src.app import app
from src.core.repositories import (
    get_user_repository, 
    get_permission_repository, 
    get_customer_profile_repository, 
    get_vendor_profile_repository
)
from src.core.security import get_security
from src.core.models.user import User, UserRole

@pytest.fixture
def mock_user_repo():
    return AsyncMock()

@pytest.fixture
def mock_perm_repo():
    return AsyncMock()

@pytest.fixture
def mock_customer_repo():
    return AsyncMock()

@pytest.fixture
def mock_vendor_repo():
    return AsyncMock()

@pytest.fixture
def mock_security():
    mock = MagicMock()
    # Mock some basic security methods
    mock.hash_password.side_effect = lambda pw: f"hashed_{pw}"
    mock.verify_password.side_effect = lambda pw, hashed: hashed == f"hashed_{pw}"
    mock.create_jwt_token.return_value = "mock_token"
    mock.decode_jwt_token.return_value = {"sub": "test@example.com", "role": "CUSTOMER"}
    return mock

@pytest_asyncio.fixture
async def client(mock_user_repo, mock_perm_repo, mock_customer_repo, mock_vendor_repo, mock_security):
    # Override dependencies
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo
    app.dependency_overrides[get_permission_repository] = lambda: mock_perm_repo
    app.dependency_overrides[get_customer_profile_repository] = lambda: mock_customer_repo
    app.dependency_overrides[get_vendor_profile_repository] = lambda: mock_vendor_repo
    app.dependency_overrides[get_security] = lambda: mock_security
    
    # Use ASGITransport for newer httpx versions
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
def test_user():
    return User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.CUSTOMER,
        hashed_password="hashed_password123",
        is_active=True
    )
