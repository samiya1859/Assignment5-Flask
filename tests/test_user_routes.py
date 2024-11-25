def test_register_user(client):
    # Sample registration data
    user_data = {
        "name": "Alice",
        "email": "alice@example.com",
        "password": "securePassword",
        "role": "User"
    }
    response = client.post('/register', json=user_data)
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"

def test_login_user(client):
    # Assuming user has already been registered
    login_data = {
        "email": "alice@example.com",
        "password": "securePassword"
    }
    response = client.post('/login', json=login_data)
    assert response.status_code == 200
    assert "token" in response.get_json()

def test_get_profile(client):
    # Mock token for authentication
    token = "Bearer valid_token"
    response = client.get('/profile', headers={"Authorization": token})
    assert response.status_code == 200
    profile = response.get_json()
    assert "name" in profile
    assert "email" in profile