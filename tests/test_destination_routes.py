import pytest
import json

def test_add_destination_unauthorized(client, logged_in_user):
    """Test adding a destination without admin privileges"""
    destination_data = {
        "name": "Test Destination",
        "description": "A test destination",
        "location": "Test Location",
        "price": 1000
    }

    response = client.post('/destinations', 
                           data=json.dumps(destination_data), 
                           content_type='application/json',
                           headers={'Authorization': logged_in_user['auth_token']})
    
    assert response.status_code == 403
    assert "Only admins can add destinations" in response.get_json()['message']

def test_add_destination_as_admin(client):
    """Test adding a destination with admin privileges"""
    # First, create an admin user
    admin_register_data = {
        'name': 'Admin User',
        'email': 'admin@example.com',
        'password': 'adminpassword123',
        'role': 'Admin'
    }

    # Register admin
    register_response = client.post('/register', 
                                    json=admin_register_data, 
                                    content_type='application/json')
    assert register_response.status_code == 201

    # Get admin's token
    admin_token = register_response.get_json()['auth_token']

    # Prepare destination data
    destination_data = {
        "name": "Test Destination",
        "description": "A test destination",
        "location": "Test Location",
        "price": 1000
    }

    # Add destination
    response = client.post('/destinations', 
                           data=json.dumps(destination_data), 
                           content_type='application/json',
                           headers={'Authorization': admin_token})
    
    assert response.status_code == 201
    assert "Destination added successfully" in response.get_json()['message']
    assert "destination_id" in response.get_json()

def test_get_all_destinations(client, logged_in_user):
    """Test retrieving all destinations"""
    response = client.get('/destinations', 
                          headers={'Authorization': logged_in_user['auth_token']})
    
    assert response.status_code == 200
    destinations = response.get_json()
    assert isinstance(destinations, list)
    assert len(destinations) > 0

def test_get_destination_by_id(client, logged_in_user):
    """Test retrieving a specific destination by ID"""
    # First, get all destinations
    destinations_response = client.get('/destinations', 
                                       headers={'Authorization': logged_in_user['auth_token']})
    destinations = destinations_response.get_json()
    
    # Pick the first destination
    first_destination_id = destinations[0]['id']

    # Retrieve the specific destination
    response = client.get(f'/destinations/{first_destination_id}', 
                          headers={'Authorization': logged_in_user['auth_token']})
    
    assert response.status_code == 200
    destination = response.get_json()
    assert destination['id'] == first_destination_id

def test_update_destination_unauthorized(client, logged_in_user):
    """Test updating a destination without admin privileges"""
    # First, get a destination ID
    destinations_response = client.get('/destinations', 
                                       headers={'Authorization': logged_in_user['auth_token']})
    destinations = destinations_response.get_json()
    first_destination_id = destinations[0]['id']

    update_data = {
        "name": "Updated Destination Name",
        "description": "Updated description"
    }

    response = client.put(f'/destinations/{first_destination_id}', 
                          data=json.dumps(update_data), 
                          content_type='application/json',
                          headers={'Authorization': logged_in_user['auth_token']})
    
    assert response.status_code == 403
    assert "Only admins can update destinations" in response.get_json()['message']

def test_update_destination_as_admin(client):
    """Test updating a destination with admin privileges"""
    # Create admin user
    admin_register_data = {
        'name': 'Admin User',
        'email': 'admin2@example.com',
        'password': 'adminpassword123',
        'role': 'Admin'
    }

    # Register admin
    register_response = client.post('/register', 
                                    json=admin_register_data, 
                                    content_type='application/json')
    assert register_response.status_code == 201

    # Get admin's token
    admin_token = register_response.get_json()['auth_token']

    # First, get a destination ID
    destinations_response = client.get('/destinations', 
                                       headers={'Authorization': admin_token})
    destinations = destinations_response.get_json()
    first_destination_id = destinations[0]['id']

    update_data = {
        "name": "Updated Destination Name",
        "description": "Updated description"
    }

    response = client.put(f'/destinations/{first_destination_id}', 
                          data=json.dumps(update_data), 
                          content_type='application/json',
                          headers={'Authorization': admin_token})
    
    assert response.status_code == 200
    assert "Destination updated successfully" in response.get_json()['message']

def test_delete_destination_unauthorized(client, logged_in_user):
    """Test deleting a destination without admin privileges"""
    # First, get a destination ID
    destinations_response = client.get('/destinations', 
                                       headers={'Authorization': logged_in_user['auth_token']})
    destinations = destinations_response.get_json()
    first_destination_id = destinations[0]['id']

    response = client.delete(f'/destinations/{first_destination_id}', 
                             headers={'Authorization': logged_in_user['auth_token']})
    
    assert response.status_code == 403
    assert "Only admins can delete destinations" in response.get_json()['message']

def test_delete_destination_as_admin(client):
    """Test deleting a destination with admin privileges"""
    # Create admin user
    admin_register_data = {
        'name': 'Admin User',
        'email': 'admin3@example.com',
        'password': 'adminpassword123',
        'role': 'Admin'
    }

    # Register admin
    register_response = client.post('/register', 
                                    json=admin_register_data, 
                                    content_type='application/json')
    assert register_response.status_code == 201

    # Get admin's token
    admin_token = register_response.get_json()['auth_token']

    # First, get a destination ID
    destinations_response = client.get('/destinations', 
                                       headers={'Authorization': admin_token})
    destinations = destinations_response.get_json()
    first_destination_id = destinations[0]['id']

    response = client.delete(f'/destinations/{first_destination_id}', 
                             headers={'Authorization': admin_token})
    
    assert response.status_code == 200
    assert "Destination deleted successfully" in response.get_json()['message']

def test_get_nonexistent_destination(client, logged_in_user):
    """Test retrieving a non-existent destination"""
    response = client.get('/destinations/nonexistent_id', 
                          headers={'Authorization': logged_in_user['auth_token']})
    
    assert response.status_code == 404
    assert "Destination not found" in response.get_json()['message']