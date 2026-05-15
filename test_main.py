import uuid
from fastapi.testclient import TestClient
from main import app
from database import Base, engine

# Recreate Database, only if not exists
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_create_user():
    global test_user_id
    unique_id = str(uuid.uuid4())[:8]    

    response = client.post(
            "/users/",
            json={
                "username": f"testuser_{unique_id}",
                "email": f"test_{unique_id}@testing.com",
                "first_name": "Test",
                "last_name": "User",
                "role": "user",
                "active": True
            },
        )
    assert response.status_code == 201

    data = response.json()
    assert "testuser_" in data["username"]
    
    # Save ID for next tests
    test_user_id = data["id"]

def test_read_user():
    global test_user_id
    # Using Dynamic ID
    response = client.get(f"/users/{test_user_id}")
    assert response.status_code == 200

def test_update_user():
    global test_user_id
    response = client.put(
        f"/users/{test_user_id}",
        json={"first_name": "UpdatedName"}
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "UpdatedName"

def test_delete_user():
    global test_user_id
    response = client.delete(f"/users/{test_user_id}")
    assert response.status_code == 204
    
    # Verify id already dont exists
    response_check = client.get(f"/users/{test_user_id}")
    assert response_check.status_code == 404