from flask import Flask
from flasgger import Swagger
from models.user import User
from services.user_services import users  # Import the users dictionary
from routes.auth_routes import auth_bp  # Import the auth_routes Blueprint
from routes.profile_routes import profile_bp

# Initialize Flask application
app = Flask(__name__)

# Initialize Swagger using Flasgger
swagger = Swagger(app)

# Preload users at startup
User.preload_users(users)

# Register Blueprints for routing
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(profile_bp, url_prefix='/')  


# Define a route for the root endpoint
@app.route('/', methods=['GET'])
def hello_flask():
    return {"message": "Hello, Welcome to travel-API!"}

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
