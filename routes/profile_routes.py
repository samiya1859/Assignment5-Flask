from flask import Blueprint, jsonify, request
from services.user_services import get_user_profile,update_user_profile, delete_user_profile
from .auth_routes import validate_session
from flasgger import swag_from  # Make sure to import swag_from for Swagger doc

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile', methods=['GET'])
@swag_from({
    'tags': ['Profile'],
    'summary': 'View logged-in user profile',
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
        200: {
            'description': 'User profile data',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'email': {'type': 'string'},
                            'role': {'type': 'string'}
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized access (Invalid or missing token)'
        },
        404: {
            'description': 'User not found'
        }
    }
})
def view_profile():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"message": "Authorization token is required"}), 401

    user_email = validate_session(token)
    if not user_email:
        return jsonify({"message": "Invalid or expired token"}), 401

    # Fetch the user profile from database or in-memory data
    return jsonify({"user_email": user_email}), 200

@profile_bp.route('/profile',methods=['PUT'])

@swag_from({
    'tags': ['Profile'],  # Group under Profile section in Swagger
    'summary': 'Update logged-in user profile',
    'description': 'Allows a logged-in user to update their profile information such as name or password.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'type': 'string',
            'required': True,
            'description': 'Bearer token for authentication'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'description': 'JSON object containing profile update data',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'New name for the user (optional)'
                    },
                    'password': {
                        'type': 'string',
                        'description': 'Current password to authenticate the user'
                    },
                    'new_password': {
                        'type': 'string',
                        'description': 'New password for the user (optional)'
                    }
                },
                'required': ['password']  # Only current password is required
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Profile updated successfully',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized access (Invalid or missing token)',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        404: {
            'description': 'User not found',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
})

def update_profile():
    """
    Update the logged-in user's profile.
    ---
    parameters:
      - name: Authorization
        in: header
        type: string
        required: true
        description: Bearer token for authentication
      - name: name
        in: body
        type: string
        required: false
        description: New name for the user
      - name: password
        in: body
        type: string
        required: true
        description: Current password to authenticate the user
      - name: new_password
        in: body
        type: string
        required: false
        description: New password for the user (optional)
    responses:
      200:
        description: Profile updated successfully
      401:
        description: Unauthorized (Incorrect password or token)
      404:
        description: User not found
    """
    data = request.get_json()
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Authorization token is required"}), 401
    
    # Validate the token and get the user's email
    user_email = validate_session(token)  # Assuming validate_token checks token and returns email
    if not user_email:
        return jsonify({"message": "Invalid or expired token"}), 401

    name = data.get('name')
    password = data.get('password')
    new_password = data.get('new_password')

    result, status_code = update_user_profile(user_email, name, password, new_password)
    return jsonify(result), status_code

@profile_bp.route('/profile',methods=['DELETE'])

@swag_from({
    'tags': ['Profile'],  # Add this tag to group it under the Profile section
    'summary': 'Delete logged-in user profile',
    'description': 'Allows a logged-in user to delete their own profile using a valid authorization token.',
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
        200: {
            'description': 'Profile deleted successfully',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized access (Invalid or missing token)',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        },
        404: {
            'description': 'User not found',
            'content': {
                'application/json': {
                    'schema': {
                        'type': 'object',
                        'properties': {
                            'message': {'type': 'string'}
                        }
                    }
                }
            }
        }
    }
})
def delete_profile():
    """
    Delete the logged-in user's profile.
    ---
    responses:
      200:
        description: Profile deleted successfully
      401:
        description: Unauthorized access (Invalid token)
    """
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Authorization token is required"}), 401
    
    # Validate the token and get the user's email
    user_email = validate_session(token)  # Assuming validate_token checks token and returns email
    if not user_email:
        return jsonify({"message": "Invalid or expired token"}), 401

    result, status_code = delete_user_profile(user_email)
    return jsonify(result), status_code