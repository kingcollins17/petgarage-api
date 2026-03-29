import pytest
from src.core.models.user import User, UserRole, CustomerProfile, VendorProfile

@pytest.mark.asyncio
async def test_get_me(client, mock_user_repo, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_user
    
    # Authenticated call
    response = await client.get("/api/v1/accounts/me", headers={"Authorization": "Bearer token"})
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
    assert response.json()["full_name"] == test_user.full_name

@pytest.mark.asyncio
async def test_update_me_success(client, mock_user_repo, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_user
    # Return updated user
    updated_user = test_user.model_copy()
    updated_user.full_name = "Jane Doe"
    mock_user_repo.update.return_value = updated_user
    
    # Request
    response = await client.patch(
        "/api/v1/accounts/me", 
        json={"full_name": "Jane Doe"},
        headers={"Authorization": "Bearer token"}
    )
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["full_name"] == "Jane Doe"
    mock_user_repo.update.assert_called_once()

@pytest.mark.asyncio
async def test_get_customer_profile_success(client, mock_user_repo, mock_customer_repo, test_user):
    # Setup - user must be a customer
    test_user.role = UserRole.CUSTOMER
    mock_user_repo.get_by_email.return_value = test_user
    mock_customer_repo.get_by_user_id.return_value = CustomerProfile(
        id=1, user_id=test_user.id, address="123 Customer St"
    )
    
    # Authenticated call
    response = await client.get("/api/v1/accounts/me/profile", headers={"Authorization": "Bearer token"})
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["address"] == "123 Customer St"

@pytest.mark.asyncio
async def test_update_customer_profile(client, mock_user_repo, mock_customer_repo, test_user):
    # Setup
    test_user.role = UserRole.CUSTOMER
    mock_user_repo.get_by_email.return_value = test_user
    mock_customer_repo.get_by_user_id.return_value = None
    mock_customer_repo.create.return_value = CustomerProfile(
        id=1, user_id=test_user.id, address="New Address"
    )
    
    # Authenticated call
    response = await client.patch(
        "/api/v1/accounts/me/customer-profile", 
        json={"address": "New Address"},
        headers={"Authorization": "Bearer token"}
    )
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["address"] == "New Address"
    mock_customer_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_update_vendor_profile_forbidden_for_customer(client, mock_user_repo, test_user):
    # Setup - user is a customer
    test_user.role = UserRole.CUSTOMER
    mock_user_repo.get_by_email.return_value = test_user
    
    # Request
    response = await client.patch(
        "/api/v1/accounts/me/vendor-profile", 
        json={"store_name": "My Store"},
        headers={"Authorization": "Bearer token"}
    )
    
    # Assertions
    assert response.status_code == 403
    assert "vendors" in response.json()["detail"]

@pytest.mark.asyncio
async def test_delete_account(client, mock_user_repo, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_user
    
    # Authenticated call
    response = await client.delete("/api/v1/accounts/me", headers={"Authorization": "Bearer token"})
    
    # Assertions
    assert response.status_code == 204
    mock_user_repo.delete.assert_called_once_with(test_user.id)
