import pytest
import uuid
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

# Recreate Database, only if not exists
Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(scope="module")
def admin_auth_data():
    """
    Prepares an admin test user
    """
    unique_id = str(uuid.uuid4())[:8]    
    test_password = "TestPassword123"
    test_username = f"admin_{unique_id}"

    create_response = client.post(
            "/api/v1/users/",
            json={
                "username": test_username,
                "email": f"admin_{unique_id}@testing.com",
                "password": test_password,
                "first_name": "Admin",
                "last_name": "User",
                "role": "admin",
                "active": True
            },
        )
    assert create_response.status_code == 201
    
    user_id = create_response.json()["id"] 

    # Obtain access token
    login_response = client.post(
        "/api/v1/login",
        data={"username": test_username, "password": test_password} 
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]    

    return {
        "user_id": user_id,
        "headers": {"Authorization": f"Bearer {token}"}
    }
    # ---------------------------------

def test_create_user():
    unique_id = str(uuid.uuid4())[:8]    

    response = client.post(
        "/api/v1/users/",
        json={
            "username": f"testuser_{unique_id}",
            "email": f"test_{unique_id}@testing.com",
            "password": "TestPassword123",
            "first_name": "Test",
            "last_name": "User",
            "role": "user",
            "active": True
        },
    )

    assert response.status_code == 201
    assert "testuser_" in response.json()["username"]

def test_read_user(admin_auth_data):
    response = client.get(
        f"/api/v1/users/{admin_auth_data['user_id']}", 
        headers=admin_auth_data["headers"]
    )
    assert response.status_code == 200

def test_update_user(admin_auth_data):
    response = client.put(
        f"/api/v1/users/{admin_auth_data['user_id']}",
        json={"first_name": "UpdatedName"},
        headers=admin_auth_data["headers"]
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "UpdatedName"

def test_delete_user(admin_auth_data):
    response = client.delete(
        f"/api/v1/users/{admin_auth_data['user_id']}", 
        headers=admin_auth_data["headers"]
    )
    assert response.status_code == 204