def test_add_destination(client):
    # Admin token for authentication
    admin_token = "Bearer admin_token"
    destination_data = {
        "name": "Paris",
        "description": "City of Lights",
        "location": "France",
        "price": 1200
    }
    response = client.post('/destinations', json=destination_data, headers={"Authorization": admin_token})
    assert response.status_code == 201
    assert response.get_json()["message"] == "Destination added successfully"

def test_get_all_destinations(client):
    # Assuming you have a valid token that can be used for testing
    user_token = "Bearer valid_token_example"  # Replace with a valid token for the test
    response = client.get('/destinations', headers={"Authorization": user_token})
    assert response.status_code == 200
    destinations = response.get_json()
    assert isinstance(destinations, list)
