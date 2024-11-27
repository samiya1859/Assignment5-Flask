import pytest
import json
from werkzeug.security import generate_password_hash


def test_view_profile_unauthorized(client):
    """Test viewing profile without authentication"""
    response = client.get("/profile")
    assert response.status_code == 401
    assert "Invalid or expired token" in response.json["message"]


def test_view_profile_successful(client, logged_in_user):
    """Test successful profile view"""

    # Retrieve the token or user information from the logged_in_user fixture
    token = logged_in_user["auth_token"].replace("Bearer ", "")

    response = client.get("/profile", headers={"Authorization": f"Bearer {token}"})

    # Add more debugging
    print(f"Token used: {token}")
    print(f"Response status: {response.status_code}")
    print(f"Response data: {response.data}")

    assert response.status_code == 200


def test_update_profile_unauthorized(client):
    """Test updating profile without authentication"""
    response = client.put(
        "/profile", json={"name": "New Name", "password": "current_password"}
    )

    assert response.status_code == 401
    assert "Authorization token is required" in response.json["message"]


def test_update_profile_invalid_password(client, logged_in_user):
    """Test profile update with incorrect current password"""
    token = logged_in_user["auth_token"]

    response = client.put(
        "/profile",
        json={"name": "Updated Name", "password": "wrong_password"},
        headers={"Authorization": token},
    )

    assert response.status_code == 401
    assert "Invalid current password" in response.json["message"]


def test_update_profile_change_password(client, logged_in_user):
    """Test changing password"""
    token = logged_in_user["auth_token"]

    response = client.put(
        "/profile",
        json={
            "password": logged_in_user["password"],
            "new_password": "new_secure_password123",
        },
        headers={"Authorization": token},
    )

    assert response.status_code == 200
    assert "Profile updated successfully" in response.json["message"]


def test_delete_profile_unauthorized(client):
    """Test deleting profile without authentication"""
    response = client.delete("/profile")

    assert response.status_code == 401
    assert "Authorization token is required" in response.json["message"]


def test_delete_profile_successful(client, logged_in_user):
    """Test successful profile deletion"""
    token = logged_in_user["auth_token"]

    response = client.delete("/profile", headers={"Authorization": token})

    assert response.status_code == 200
    assert "User deleted successfully" in response.json["message"]


# Additional fixture for logged-in user
@pytest.fixture
def logged_in_user(client):
    """
    Fixture to create and log in a test user
    This assumes you have a route for user registration and login
    """
    # Prepare user registration data
    register_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword123",
        "role": "User",
    }

    # Register the user
    register_response = client.post("/register", json=register_data)
    assert register_response.status_code == 201, "User registration failed"

    # Login the user
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"],
    }
    login_response = client.post("/login", json=login_data)
    assert login_response.status_code == 200, "User login failed"

    # Return login details for use in tests
    return {
        "name": register_data["name"],
        "email": register_data["email"],
        "password": register_data["password"],
        "auth_token": login_response.json["auth_token"],
        "role": login_response.json["role"],
    }
