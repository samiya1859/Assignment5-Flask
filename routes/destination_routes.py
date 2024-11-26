from flask import Blueprint, request, jsonify
from services.destination_services import add_destination_service,get_all_destinations_service,get_destination_by_id_service, update_destination_service, delete_destination_service
from services.user_services import get_user_by_email, validate_token
from flasgger import swag_from

destination_bp = Blueprint('destinations', __name__)

@destination_bp.route('/destinations', methods=['POST'])
@swag_from({
    'tags': ['Destinations'],  # Group under 'Destinations' in Swagger
    'summary': 'Add a new destination (Admin only)',
    'description': 'Admins can add new destinations by providing details such as name, description, location, and price.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'required': ['name', 'description', 'location', 'price'],
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'Name of the destination'
                    },
                    'description': {
                        'type': 'string',
                        'description': 'Description of the destination'
                    },
                    'location': {
                        'type': 'string',
                        'description': 'Location of the destination'
                    },
                    
                }
            },
            'description': 'Destination details to add'
        }
    ],
    'responses': {
        201: {
            'description': 'Destination added successfully',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'},
                            'destination_id': {'type': 'string'}
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Missing required fields'
        },
        401: {
            'description': 'Unauthorized access (Invalid or missing token)'
        },
        403: {
            'description': 'Forbidden access (Not an Admin)'
        }
    }
})
def add_destination():
    """
    Add a new destination (Admin only).
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Authorization token is required"}), 401
    
    print("Token : ", token)
    user = validate_token(token)
    if not user:
        return jsonify({"message": "Invalid or expired token"}), 401
    
    print(f"User validated: {user.name}, Role: {user.role}")
    print(f"User email from token: ", user.email)

    

    if user.role != 'Admin':
        return jsonify({"message": "Forbidden. Only admins can add destinations."}), 403

    # Call the service function
    data = request.get_json()
    result, status_code = add_destination_service(data, user)
    return jsonify(result), status_code

@destination_bp.route('/destinations', methods=['GET'])
def get_all_destinations():
    """
    Get all destinations (Logged-in users only).
    ---
    tags:
      - Destinations
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
    responses:
      200:
        description: A list of destinations
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    description: ID of the destination
                  name:
                    type: string
                    description: Name of the destination
                  description:
                    type: string
                    description: Description of the destination
                  location:
                    type: string
                    description: Location of the destination
                  price:
                    type: number
                    description: Price of the destination
      401:
        description: Unauthorized access (Invalid or missing token)
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Authorization token is required"}), 401

    # Validate session and token
    user_email = validate_token(token)
    if not user_email:
        return jsonify({"message": "Invalid or expired token"}), 401

    # Call the service to get all destinations
    result, status_code = get_all_destinations_service()
    return jsonify(result), status_code

@destination_bp.route('/destinations/<string:destination_id>', methods=['GET'])
def get_destination_by_id(destination_id):
    """
    Get a destination by ID (Logged-in users only).
    ---
    tags:
      - Destinations
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - name: destination_id
        in: path
        type: string
        required: true
        description: ID of the destination to retrieve
    responses:
      200:
        description: Details of the destination
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: string
                  description: ID of the destination
                name:
                  type: string
                  description: Name of the destination
                description:
                  type: string
                  description: Description of the destination
                location:
                  type: string
                  description: Location of the destination
                price:
                  type: number
                  description: Price of the destination
      401:
        description: Unauthorized access (Invalid or missing token)
      404:
        description: Destination not found
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Authorization token is required"}), 401

    # Validate session and token
    user_email = validate_token(token)
    if not user_email:
        return jsonify({"message": "Invalid or expired token"}), 401

    # Extract destination ID from the URL path
    result, status_code = get_destination_by_id_service(destination_id)
    return jsonify(result), status_code

@destination_bp.route('/destinations/<string:destination_id>', methods=['PUT'])
def update_destination_by_id(destination_id):
    """
    Update a destination by ID (Admin only).
    ---
    tags:
      - Destinations
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - name: destination_id
        in: path
        type: string
        required: true
        description: ID of the destination to update
      - in: body
        name: destination
        schema:
          type: object
          properties:
            name:
              type: string
              description: Updated name of the destination
            description:
              type: string
              description: Updated description of the destination
            location:
              type: string
              description: Updated location of the destination
            
    responses:
      200:
        description: Destination updated successfully
      400:
        description: Invalid data or missing fields
      401:
        description: Unauthorized access (Invalid or missing token)
      403:
        description: Forbidden access (Not an Admin)
      404:
        description: Destination not found
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Authorization token is required"}), 401

    # Validate session and token
    user_email = validate_token(token)
    if not user_email:
        return jsonify({"message": "Invalid or expired token"}), 401

    
    if user_email.role != 'Admin':
        return jsonify({"message": "Forbidden. Only admins can update destinations."}), 403

    # Get the updated data from the request body
    data = request.get_json()
    result, status_code = update_destination_service(destination_id, data)
    return jsonify(result), status_code

@destination_bp.route('/destinations/<string:destination_id>', methods=['DELETE'])
def delete_destination_by_id(destination_id):
    """
    Delete a destination by ID (Admin only).
    ---
    tags:
      - Destinations
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - name: destination_id
        in: path
        type: string
        required: true
        description: ID of the destination to delete
    responses:
      200:
        description: Destination deleted successfully
      401:
        description: Unauthorized access (Invalid or missing token)
      403:
        description: Forbidden access (Not an Admin)
      404:
        description: Destination not found
    """
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Authorization token is required"}), 401

    # Validate session and token
    user_email = validate_token(token)
    if not user_email:
        return jsonify({"message": "Invalid or expired token"}), 401

    
    if user_email.role != 'Admin':
        return jsonify({"message": "Forbidden. Only admins can delete destinations."}), 403

    # Extract destination ID from the URL path
    destination_id = request.view_args['destination_id']

    # Call the service function
    result, status_code = delete_destination_service(destination_id)
    return jsonify(result), status_code
