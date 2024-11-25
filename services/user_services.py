import uuid
from models.user import User
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask,jsonify

users = {}
active_sessions = {}

def validate_token(token):
    """Validate the provided token and return the user associated with it, if valid."""
    
    # Check if the token exists in active_sessions
    if token in active_sessions:
        user_info = active_sessions[token]  # Get the user info (email, role)
        email = user_info["email"]  # Get the email from the stored data
        
        # Return the user object based on the email
        return users.get(email)  # Assuming users is a dictionary where email is the key
    
    return None  # Return None if no valid user is found



def register_user(data):
    """Register a new user."""
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'User')

    if not name or not email or not password:
        return {"message": "Name, email, and password are required"}, 400

    if email in users:
        return {"message": "User already exists!"}, 400

    user = User(name, email, password, role)
    user.token = str(uuid.uuid4())  # Generate unique token
    users[email] = user

    return {"message": "User registered successfully!"}, 201

active_sessions = {}

def login_user(email, password):
    """Service to handle user login."""
    
    # Check if the email exists in users dictionary
    if email not in users:
        return {"message": "Invalid email or password"}, 401
    
    user = users[email]

    # Verify password
    if not user.verify_password(password):
        return {"message": "Invalid email or password"}, 401

    # Check if the user is already logged in
    if email in active_sessions:
        return {"message": "User already logged in. Please log out first to login into another account"}, 403

    # Generate a new token and store it in active sessions
    token = str(uuid.uuid4())
    # Store only the token in active_sessions (the key is token, value is user data or ID)
    active_sessions[token] = {"email": user.email, "role": user.role}  # Store user details if needed

    return {"message": "Login successful", "auth_token": f"Bearer {token}", "role": user.role}, 200


# logout service
def logout_user(token):
    for email, stored_token in active_sessions.items():
        if stored_token == token:
            del active_sessions[email]  # Invalidate the token
            return {"message": "Logout successful"}, 200
    return {"message": "Unauthorized"}, 401


# get all user service. Only applicable for admin
def get_all_users_service(token):
    """Service to get all users if the authenticated user is an Admin."""
    
    # Validate the token to authenticate the user
    authenticated_user = validate_token(token)
    
    if not authenticated_user:
        return {"message": "Invalid or expired token."}, 401

    # Check if the authenticated user is an Admin
    if authenticated_user.role != "Admin":
        return {"message": "Forbidden. Admin access only."}, 403
    
    # Return the list of all users if the user is an Admin
    user_list = [
        {"name": user.name, "email": user.email, "role": user.role}
        for user in users.values()
    ]
    return {"users": user_list}, 200

# services/user_services.py

def get_user_by_email(email):
    # Assuming users are stored in some dictionary or database
    user = users.get(email)
    if user:
        return user
    return None


# for deleting any user (only Applicable for admin)
def delete_user_service(email, token):
    """Service to delete a user (only accessible by logged-in Admin)."""
    
    # Validate token and get user details
    authenticated_user = validate_token(token)

    if not authenticated_user:
        return {"message": "Invalid or expired token."}, 401

    # Check if the authenticated user is an admin
    if authenticated_user.role != 'Admin':
        return {"message": "Forbidden. Admin access only."}, 403

    # Check if the user exists
    if email not in users:
        return {"message": "User not found."}, 404

    # Ensure an admin cannot delete themselves
    if authenticated_user.email == email:
        return {"message": "Admins cannot delete themselves."}, 400

    # Ensure an admin cannot delete another admin
    if users[email].role == 'Admin':
        return {"message": "Admins cannot delete other admins."}, 400

    # Remove the user from the users dictionary
    del users[email]

    # Remove the user from active_sessions if they are logged in
    if email in active_sessions:
        del active_sessions[email]

    return {"message": f"User {email} deleted successfully."}, 200


# viewing own profile
def get_user_profile(email):
    """Retrieve user profile data."""
    user = users.get(email)
    if user:
        return {
            "name": user.name,
            "email": user.email,
            "role": user.role
        }, 200
    return {"message": "User not found"}, 404

# updating profile
def update_user_profile(email, name, password, new_password=None):
    """Update user profile details."""
    user = users.get(email)
    if not user:
        return {"message": "User not found"}, 404
    
    if password and not check_password_hash(user.password, password):
        return {"message": "Invalid current password"}, 401
    
    # Update profile information
    user.name = name if name else user.name
    if new_password:
        user.password = generate_password_hash(new_password)

    return {"message": "Profile updated successfully"}, 200

# deleting user data
def delete_user_profile(email):
    """Delete user profile."""
    user = users.pop(email, None)
    if not user:
        return {"message": "User not found"}, 404
    # Remove from active sessions
    active_sessions.pop(email, None)
    return {"message": "User deleted successfully"}, 200
