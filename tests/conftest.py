import pytest
import json
from app import create_app
from models.user import User
from services.user_services import users, active_sessions


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True

    # Clear users and active sessions before each test
    users.clear()
    active_sessions.clear()

    return app


@pytest.fixture
def client(app):
    return app.test_client()


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
