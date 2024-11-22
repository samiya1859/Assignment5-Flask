import uuid
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, name, email, password, role='User'):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)  # Hash the password before storing
        self.role = role
        self.token = None  # Initially no token

    # This method checks if the provided password matches the stored hashed password
    def verify_password(self, password):
        return check_password_hash(self.password, password)  # Compare the hashes

    # This method generates a new token for the user
    def generate_token(self):
        self.token = str(uuid.uuid4())  # Generate a unique token for the user
        return self.token
    
    @staticmethod
    def preload_users(users):
        """Add some predefined users for testing purposes."""
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password="adminpass",
            role="Admin"
        )
        admin.token = "admin-token"
    
        user1 = User(
            name="John Doe",
            email="john.doe@example.com",
            password="password123",
            role="User"
        )
        user1.token = "user1-token"
    
        users[admin.email] = admin
        users[user1.email] = user1
    
        print("Predefined users loaded successfully.")  # Use print for debugging, not jsonify.
    
        