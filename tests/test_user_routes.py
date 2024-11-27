import json
import pytest
from app import create_app
from models.user import User
from services.user_services import users, active_sessions


def test_register_success(client):
    """Test successful user registration"""
    data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "role": "User",
    }
    response = client.post(
        "/register", data=json.dumps(data), content_type="application/json"
    )

    assert response.status_code == 201
    assert b"User registered successfully!" in response.data
    assert "test@example.com" in users


def test_register_missing_data(client):
    """Test registration with missing required fields"""
    data = {
        "name": "Test User",
        "email": "test@example.com",
        # Missing password
    }
    response = client.post(
        "/register", data=json.dumps(data), content_type="application/json"
    )

    assert response.status_code == 400
    assert b"Name, email, and password are required" in response.data


def test_register_existing_user(client):
    """Test registration with existing email"""
    # First registration
    data = {
        "name": "Test User",
        "email": "existing@example.com",
        "password": "password123",
        "role": "User",
    }
    client.post("/register", data=json.dumps(data), content_type="application/json")

    # Try to register again with same email
    response = client.post(
        "/register", data=json.dumps(data), content_type="application/json"
    )

    assert response.status_code == 400
    assert b"User already exists!" in response.data


def test_register_invalid_json(client):
    """Test registration with invalid JSON data"""
    response = client.post(
        "/register", data="invalid json", content_type="application/json"
    )

    assert response.status_code == 400
    assert b"Invalid request. JSON data is missing" in response.data


def test_login_success(client):
    """Test successful login"""
    # Register a user first
    register_data = {
        "name": "Login Test",
        "email": "login@example.com",
        "password": "password123",
        "role": "User",
    }
    client.post(
        "/register", data=json.dumps(register_data), content_type="application/json"
    )

    # Try to login
    login_data = {"email": "login@example.com", "password": "password123"}
    response = client.post(
        "/login", data=json.dumps(login_data), content_type="application/json"
    )

    assert response.status_code == 200
    response_data = json.loads(response.data)
    # Check all expected fields in the response
    assert "auth_token" in response_data
    assert "message" in response_data
    assert "role" in response_data
    assert response_data["message"] == "Login successful"
    assert isinstance(response_data["auth_token"], str)
    assert response_data["role"] == "User"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    login_data = {"email": "nonexistent@example.com", "password": "wrongpassword"}
    response = client.post(
        "/login", data=json.dumps(login_data), content_type="application/json"
    )

    assert response.status_code == 401


def test_login_missing_fields(client):
    """Test login with missing required fields"""
    login_data = {
        "email": "test@example.com"
        # Missing password
    }
    response = client.post(
        "/login", data=json.dumps(login_data), content_type="application/json"
    )

    assert response.status_code == 400
    assert b"Email and password are required" in response.data


def test_login_invalid_json(client):
    """Test login with invalid JSON data"""
    # Test case 1: Completely invalid JSON
    response = client.post(
        "/login", data="invalid json", content_type="application/json"
    )

    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data["message"] == "Bad Request, JSON data is missing"

    # Test case 2: Empty JSON object
    response = client.post(
        "/login", data=json.dumps({}), content_type="application/json"
    )

    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data["message"] == "Bad Request, JSON data is missing"


def test_logout(client):
    from services.user_services import active_sessions

    active_sessions.clear()  # Ensure no prior sessions interfere

    # Register and login the user
    user_data = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "securePassword",
        "role": "User",
    }
    client.post("/register", json=user_data)
    login_response = client.post(
        "/login", json={"email": user_data["email"], "password": user_data["password"]}
    )

    # Ensure token is retrieved correctly
    token = login_response.get_json()["auth_token"]
    print(f"Token before logout: {token}")  # Debug token

    # Perform logout
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/logout", headers=headers)

    # Debug active sessions
    print(f"Active Sessions before logout: {active_sessions}")

    # Check response
    assert (
        response.status_code == 200
    ), f"Expected 200, got {response.status_code}. Response: {response.get_json()}"

    # After logout, active sessions should be empty
    print(f"Active Sessions after logout: {active_sessions}")


def test_get_all_users(client):
    from services.user_services import users, active_sessions

    # Clear users and sessions to avoid conflicts
    users.clear()
    active_sessions.clear()

    # Register an admin user and login
    admin_data = {
        "name": "Admin",
        "email": "admin@example.com",
        "password": "adminpass",
        "role": "Admin",
    }
    register_response = client.post("/register", json=admin_data)
    assert register_response.status_code == 201, "Admin registration failed"

    # Login with the admin user
    login_response = client.post(
        "/login",
        json={"email": admin_data["email"], "password": admin_data["password"]},
    )
    assert login_response.status_code == 200, "Admin login failed"

    # Extract the token
    admin_token = login_response.get_json().get("auth_token")
    assert admin_token is not None, "Admin token was not generated"

    # Debug: Ensure token is stored in active_sessions
    print("Active Sessions:", active_sessions)

    # Make a GET request to /users
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.get("/users", headers=headers)

    # Debug: Print response details
    print(f"Response Status: {response.status_code}")
    print(f"Response JSON: {response.get_json()}")

    # Validate response
    assert response.status_code == 200, "Failed to fetch users list"
    users_data = response.get_json()
    assert "users" in users_data, "'users' key is missing in the response"
    assert isinstance(users_data["users"], list), "Users data is not a list"

    assert any(
        user["email"] == admin_data["email"] for user in users_data["users"]
    ), "Admin user not found"


def test_delete_user(client):
    # Register an admin user and login
    admin_data = {
        "name": "Admin1",
        "email": "admin1@example.com",
        "password": "adminpass1",
        "role": "Admin",
    }
    register_response = client.post("/register", json=admin_data)
    assert register_response.status_code == 201, "Admin registration failed"

    login_response = client.post(
        "/login",
        json={"email": admin_data["email"], "password": admin_data["password"]},
    )
    assert login_response.status_code == 200, "Admin login failed"

    # Extract auth_token from the login response
    login_data = login_response.get_json()
    assert "auth_token" in login_data, "Auth token not found"
    admin_token = login_data["auth_token"]

    # Register another user to delete
    user_data = {
        "name": "John Doe11",
        "email": "john11.doe@example.com",
        "password": "password1234",
        "role": "User",
    }
    register_response = client.post("/register", json=user_data)
    assert register_response.status_code == 201, "User registration failed"

    # Verify that the user is in the system
    response = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    print(f"Admin Token : {admin_token}")
    users = response.get_json()

    assert "users" in users, "'users' key not found in response"
    assert any(
        user["email"] == user_data["email"] for user in users["users"]
    ), "User to delete not found"

    # Delete the user
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = client.delete(f'/users/{user_data["email"]}', headers=headers)

    assert response.status_code == 200
    assert response.get_json()["message"] == "User deleted successfully"

    # Verify the user is deleted by fetching the users list again
    response = client.get("/users", headers=headers)
    users = response.get_json()
    assert not any(
        user["email"] == user_data["email"] for user in users
    ), "User not deleted"


@pytest.fixture(autouse=True)
def clear_data():
    """Clear users and active sessions before each test"""
    users.clear()
    active_sessions.clear()
    yield
