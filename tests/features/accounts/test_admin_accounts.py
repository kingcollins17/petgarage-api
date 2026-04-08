import pytest
from src.core.models.user import User, UserRole, CustomerProfile, VendorProfile

@pytest.mark.asyncio
async def test_admin_list_users(client, mock_user_repo, test_admin):
    # Setup
    mock_user_repo.get_by_email.return_value = test_admin
    mock_user_repo.list.return_value = [test_admin]
    
    # Request
    response = await client.get("/api/v1/accounts/", headers={"Authorization": "Bearer token"})
    
    # Assertions
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
    assert "metadata" in response.json()
    assert response.json()["metadata"]["total"] == 1
    mock_user_repo.list.assert_called_once()

@pytest.mark.asyncio
async def test_admin_deactivate_user(client, mock_user_repo, test_admin, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_admin
    mock_user_repo.get.return_value = test_user
    
    updated_user = test_user.model_copy()
    updated_user.active = False
    mock_user_repo.update.return_value = updated_user
    
    # Request
    response = await client.post(
        f"/api/v1/accounts/{test_user.id}/deactivate", 
        headers={"Authorization": "Bearer token"}
    )
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["data"]["active"] is False
    mock_user_repo.update.assert_called_once()
    args, kwargs = mock_user_repo.update.call_args
    assert args[1]["active"] is False

@pytest.mark.asyncio
async def test_admin_verify_user(client, mock_user_repo, test_admin, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_admin
    mock_user_repo.get.return_value = test_user
    
    updated_user = test_user.model_copy()
    updated_user.verified = True
    mock_user_repo.update.return_value = updated_user
    
    # Request
    response = await client.post(
        f"/api/v1/accounts/{test_user.id}/verify", 
        headers={"Authorization": "Bearer token"}
    )
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["data"]["verified"] is True
    mock_user_repo.update.assert_called_once()

@pytest.mark.asyncio
async def test_admin_update_user_profile(client, mock_user_repo, mock_customer_repo, test_admin, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_admin
    mock_customer_repo.get_by_user_id.return_value = CustomerProfile(id=1, user_id=test_user.id, address="Old Address")
    
    updated_profile = CustomerProfile(id=1, user_id=test_user.id, address="Admin Updated Address")
    mock_customer_repo.update.return_value = updated_profile
    
    # Request
    response = await client.patch(
        f"/api/v1/accounts/{test_user.id}/customer-profile", 
        json={"address": "Admin Updated Address"},
        headers={"Authorization": "Bearer token"}
    )
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["data"]["address"] == "Admin Updated Address"
    mock_customer_repo.update.assert_called_once()

@pytest.mark.asyncio
async def test_admin_delete_user(client, mock_user_repo, test_admin, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_admin
    mock_user_repo.get.return_value = test_user
    
    # Request
    response = await client.delete(
        f"/api/v1/accounts/{test_user.id}", 
        headers={"Authorization": "Bearer token"}
    )
    
    # Assertions
    assert response.status_code == 204
    mock_user_repo.delete.assert_called_once_with(test_user.id)

@pytest.mark.asyncio
async def test_admin_get_user_detail(client, mock_user_repo, test_admin, test_user):
    # Setup
    mock_user_repo.get_by_email.return_value = test_admin
    mock_user_repo.get.return_value = test_user
    
    # Request
    response = await client.get(
        f"/api/v1/accounts/{test_user.id}", 
        headers={"Authorization": "Bearer token"}
    )
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["data"]["email"] == test_user.email
