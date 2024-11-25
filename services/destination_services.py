from models.destination import destinations, Destination

def add_destination_service(data, admin_email):
    """Service to add a new destination (Admin only)."""
    name = data.get('name')
    description = data.get('description')
    location = data.get('location')

    if not name or not description or not location:
        return {"message": "All fields are required"}, 400

    # Create a new Destination instance
    new_destination = Destination(name, description, location, admin_email)

    # Store the destination in the dictionary
    destinations[new_destination.id] = new_destination

    return {"message": "Destination added successfully", "destination_id": new_destination.id}, 201



destinations = {
    "1": {"id": "1", "name": "Paris", "description": "The city of lights.", "location": "France"},
    "2": {"id": "2", "name": "Maldives", "description": "Tropical paradise.", "location": "Indian Ocean"},
}

def get_all_destinations():
    """
    Fetch all destinations.
    """
    if not destinations:
        return {"message": "No destinations available."}, 200
    return list(destinations.values()), 200



def get_destination_by_id_service(destination_id):
    """
    Fetch a destination by its ID.
    """
    destination = destinations.get(destination_id)
    if not destination:
        return {"message": "Destination not found."}, 404
    return destination, 200


# services/destination_services.py

def update_destination_service(destination_id, updated_data):
    """
    Update a destination's details.
    """
    destination = destinations.get(destination_id)
    if not destination:
        return {"message": "Destination not found."}, 404

    # Update fields if they exist in the request
    for key, value in updated_data.items():
        if key in destination:
            destination[key] = value

    return {"message": "Destination updated successfully.", "destination": destination}, 200



def delete_destination_service(destination_id):
    """
    Delete a destination by its ID.
    """
    destination = destinations.pop(destination_id, None)  # Remove destination if it exists
    if not destination:
        return {"message": "Destination not found."}, 404

    return {"message": "Destination deleted successfully."}, 200