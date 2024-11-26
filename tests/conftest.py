import pytest
from app import create_app
from models.user import User
from services.user_services import users, active_sessions

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    
    # Clear users and active sessions before each test
    users.clear()
    active_sessions.clear()
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

