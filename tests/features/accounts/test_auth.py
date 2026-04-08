import pytest
from src.core.models.user import User, UserRole

@pytest.mark.asyncio
async def test_signup_success(client, mock_user_repo):
    # Setup
    mock_user_repo.get_by_email.return_value = None
    mock_user_repo.create.return_value = User(
        id=1, email="new@example.com", full_name="New User", role=UserRole.CUSTOMER
    )
    
    # Request
    response = await client.post("/api/v1/auth/signup", json={
        "email": "new@example.com",
        "password": "securepassword",
        "full_name": "New User"
    })
    
    # Assertions
    assert response.status_code == 201
    assert response.json()["data"]["email"] == "new@example.com"
    mock_user_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_signup_already_exists(client, mock_user_repo, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_user
    
    # Request
    response = await client.post("/api/v1/auth/signup", json={
        "email": "test@example.com",
        "password": "securepassword",
        "full_name": "Test User"
    })
    
    # Assertions
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client, mock_user_repo, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_user
    
    # Request - form-data like Swagger UI
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    
    # Assertions
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(client, mock_user_repo, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_user
    
    # Request with wrong password (mock_security mocks password verify)
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    
    # Assertions
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

@pytest.mark.asyncio
async def test_send_otp(client):
    response = await client.post("/api/v1/auth/send-otp", json={"email": "test@example.com"})
    assert response.status_code == 200
    assert "success" in response.json()["message"]

@pytest.mark.asyncio
async def test_verify_otp_success(client):
    response = await client.post("/api/v1/auth/verify-otp", json={
        "email": "test@example.com",
        "otp": "123456"
    })
    assert response.status_code == 200
    assert "verified" in response.json()["message"]

@pytest.mark.asyncio
async def test_verify_otp_failure(client):
    response = await client.post("/api/v1/auth/verify-otp", json={
        "email": "test@example.com",
        "otp": "wrong_otp"
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_login_inactive_account(client, mock_user_repo, test_user):
    # Setup
    test_user.active = False
    mock_user_repo.get_by_email.return_value = test_user
    
    # Request
    response = await client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    
    # Assertions
    assert response.status_code == 403
    assert "inactive" in response.json()["detail"]
