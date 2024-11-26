from models.destination import Destination

destination_counter = 2
destinations = {
    "1": Destination("Paris", "The city of lights.", "France", "admin@paris.com"),
    "2": Destination("Maldives", "Tropical paradise.", "Indian Ocean", "admin@maldives.com"),
}

def add_destination_service(data, admin_user):
    """Service to add a new destination (Admin only)."""

    global destination_counter

    name = data.get('name')
    description = data.get('description')
    location = data.get('location')

    if not name or not description or not location:
        return {"message": "All fields are required"}, 400
    
    
    destination_counter += 1
    new_id = str(destination_counter)

    # Create a new Destination instance
    new_destination = Destination(
        name=name,
        description=description,
        location=location,
        admin_email=admin_user.email  
    )

    # Store the destination in the dictionary
    destinations[new_id] = new_destination 

    return {"message": "Destination added successfully", "destination_id": new_id}, 201



def get_all_destinations_service():
    """
    Fetch all destinations.
    """
    if not destinations:
        return {"message": "No destinations available."}, 200
    
    # Convert Destination objects to dictionaries using the to_dict() method
    destination_list = [dest.to_dict() for dest in destinations.values()]
    
    return destination_list, 200


def get_destination_by_id_service(destination_id):
    """
    Fetch a destination by its ID.
    """
    destination_id = str(destination_id)
    destination = destinations.get(destination_id)
    if not destination:
        return {"message": f"Destination with ID {destination_id} not found."}, 404
    
    return destination.to_dict(), 200


# services/destination_services.py

def update_destination_service(destination_id, updated_data):
    """
    Update a destination's details.
    """
    destination_id = str(destination_id)  # Ensure string conversion
    destination = destinations.get(destination_id)
    if not destination:
        return {"message": "Destination not found."}, 404

    # Update fields if they exist in the request
    if 'name' in updated_data:
        destination.name = updated_data['name']
    if 'description' in updated_data:
        destination.description = updated_data['description']
    if 'location' in updated_data:
        destination.location = updated_data['location']

    # Return the updated destination as a dictionary
    return {
        "message": "Destination updated successfully.", 
        "destination": destination.to_dict()
    }, 200


def delete_destination_service(destination_id):
    """
    Delete a destination by its ID.
    """
    destination_id = str(destination_id)
    
    destination = destinations.pop(destination_id, None)  # Remove destination if it exists
    if not destination:
        return {"message": "Destination not found."}, 404

    return {"message": "Destination deleted successfully."}, 200

