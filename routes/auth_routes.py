from flask import Blueprint, request, jsonify
from services.user_services import register_user, login_user, logout_user, get_all_users_service, delete_user_service
from services.session_manager import validate_session
from flasgger import Swagger, swag_from


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    parameters:
      - name: name
        in: body
        type: string
        required: true
        description: Full name of the user
      - name: email
        in: body
        type: string
        required: true
        description: Email address of the user
      - name: password
        in: body
        type: string
        required: true
        description: Password for the user account
      - name: role
        in: body
        type: string
        required: false
        description: Role of the user ('User' or 'Admin'). Default is 'User'.
    responses:
      201:
        description: User successfully registered
      400:
        description: User already exists
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "Invalid request. JSON data is missing"}), 400
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'User')

    if not name or not email or not password:
        return jsonify({"message": "Name, email, and password are required"}), 400

    # Use the register_user service to handle registration logic
    data = {
    "name": name,
    "email": email,
    "password": password,
    "role": role
    }
    response, status_code = register_user(data)

    
    return jsonify(response), status_code

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login to authenticate and get an auth token.
    ---
    parameters:
      - name: email
        in: body
        type: string
        required: true
        description: Email address of the user
      - name: password
        in: body
        type: string
        required: true
        description: Password of the user
    responses:
      200:
        description: User successfully authenticated, returns an auth token
      401:
        description: Invalid email or password
      403:
        description: User already logged in
    """
    data = request.get_json()

    if not data:
        return jsonify({"message": "Bad Request, JSON data is missing"}), 400
    
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Call the service layer function to handle login
    response, status_code = login_user(email, password)

    return jsonify(response), status_code

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    User logout to invalidate the auth token.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
    responses:
      200:
        description: User successfully logged out
      401:
        description: Unauthorized access (Invalid or missing token)
    """
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Authorization token is required"}), 401

    # Call the logout service function
    response, status_code = logout_user(token)

    return jsonify(response), status_code

@auth_bp.route('/users', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Get all registered users (Admin only)',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        }
    ],
    'responses': {
        '200': {
            'description': 'A list of all users (Admin only)',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'name': {'type': 'string'},
                                'email': {'type': 'string'},
                                'role': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        },
        '401': {'description': 'User not authenticated'},
        '403': {'description': 'Access denied (Only Admins allowed)'}
    }
})


def get_all_users():
    """
    Get all registered users (Admin only).
    """
    # Get the token from the request header
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Unauthorized. Please log in."}), 401
    
    # Call the service function to get the list of users
    result, status_code = get_all_users_service(token)
    
    return jsonify(result), status_code

@auth_bp.route('/users/<string:email>', methods=['DELETE'])

@swag_from({
    'tags': ['Users'],  # Add this tag to group it under Users section
    'summary': 'Delete a user',
    'parameters': [
        {
            'name': 'email',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Email of the user to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'User deleted successfully'
        },
        404: {
            'description': 'User not found'
        }
    }
})

def delete_user(email):
    """
    Admin can delete a user.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
    responses:
      200:
        description: User deleted successfully
      401:
        description: Unauthorized access (Invalid or missing token)
      403:
        description: Forbidden access (Admin only)
      404:
        description: User not found
      400:
        description: Admin cannot delete themselves or other admins
    """
    # Get the token from the request header
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Authorization token is required"}), 401
    
    # Call the service function to delete the user
    result, status_code = delete_user_service(email, token)

    return jsonify(result), status_code