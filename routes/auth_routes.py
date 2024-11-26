from flask import Blueprint, request, jsonify
from services.user_services import register_user, login_user, logout_user, get_all_users_service, delete_user_service
from flasgger import Swagger, swag_from
import uuid
from services.user_services import users, active_sessions, validate_token
from models.user import User


auth_bp = Blueprint('auth', __name__)



@auth_bp.errorhandler(400)
def bad_request_error(error):
    return jsonify({"message": str(error.description)}), 400


@auth_bp.route('/register', methods=['POST'])
@swag_from({
    "tags": ["Authentication"],
    "summary": "Register a new user",
    "description": "Allows new users to register by providing their name, email, password, and an optional role.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "password": {"type": "string"},
                    "role": {"type": "string", "default": "User"},
                },
                "required": ["name", "email", "password"],
            },
        }
    ],
    "responses": {
        "201": {
            "description": "User registered successfully!",
        },
        "400": {
            "description": "Invalid request or user already exists.",
        },
    },
})

def register():
    try:
        data = request.get_json()
    except Exception:
        return jsonify({"message": "Invalid request. JSON data is missing"}), 400

    if not data:
        return jsonify({"message": "Invalid request. JSON data is missing"}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'User')

    if not name or not email or not password:
        return jsonify({"message": "Name, email, and password are required"}), 400

    if email in users:
        return jsonify({"message": "User already exists!"}), 400

    user = User(name, email, password, role)
    user.token = str(uuid.uuid4())  # Generate a unique token
    users[email] = user 

    return jsonify({"message": "User registered successfully!"}), 201


@auth_bp.route('/login', methods=['POST'])

@swag_from({
    "tags": ["Authentication"],
    "summary": "User Login",
    "description": "Allows a registered user to log in by providing their email and password. Returns an authentication token upon successful login.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "password": {"type": "string"},
                },
                "required": ["email", "password"],
            },
        }
    ],
    "responses": {
        "200": {
            "description": "Login successful, returns an authentication token.",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "auth_token": {"type": "string"},
                    "role": {"type": "string"},
                },
            },
        },
        "400": {
            "description": "Invalid request. Email and password are required.",
        },
        "401": {
            "description": "Invalid email or password.",
        },
        "403": {
            "description": "User already logged in.",
        },
    },
})

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
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Bad Request, JSON data is missing"}), 400
    except Exception:
        return jsonify({"message": "Bad Request, JSON data is missing"}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Call the service layer function to handle login
    response, status_code = login_user(email, password)

    return jsonify(response), status_code


@auth_bp.route('/logout', methods=['POST'])

@swag_from({
    "tags": ["Authentication"],
    "summary": "User Logout",
    "description": "Logs out a user by invalidating their authentication token.",
    "parameters": [
        {
            "name": "Authorization",
            "in": "header",
            "required": True,
            "type": "string",
            "description": "Bearer <auth_token>",
        }
    ],
    "responses": {
        "200": {
            "description": "Logout successful.",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                },
            },
        },
        "401": {
            "description": "Unauthorized. Invalid or missing token.",
        },
    },
})

def logout():
    """Logs the user out by removing their session."""
    token = request.headers.get('Authorization').split(" ")[1]  # Extract token from 'Bearer <token>'
    
    # Check if the token is valid
    user = validate_token(token)
    if not user:
        return jsonify({"message": "Invalid or expired token."}), 401
    
    # Remove the token from active_sessions to log the user out
    active_sessions.pop(user.email, None)
    
    return jsonify({"message": "Logout successful"}), 200

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
    # Check if the Authorization header exists
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"message": "Unauthorized. Please log in."}), 401
    
    print(f"Received Authorization Header: {auth_header}")
    
    try:
        # Call the service function to get the list of users
        result, status_code = get_all_users_service(auth_header)
        
        # Return the result from the service function
        return jsonify(result), status_code
    except Exception as e:
        # Add error logging
        print(f"Error in get_all_users route: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500
    

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