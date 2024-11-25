from flask import Flask
from flasgger import Swagger
from models.user import User
from services.user_services import users  # Import the users dictionary
from routes.auth_routes import auth_bp  # Import the auth_routes Blueprint
from routes.profile_routes import profile_bp
from routes.destination_routes import destination_bp

def create_app():
    app = Flask(__name__)

    # Initialize Swagger
    swagger = Swagger(app)

    # Preload users
    User.preload_users(users)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(profile_bp, url_prefix='/')
    app.register_blueprint(destination_bp, url_prefix='/')

    # Root route
    @app.route('/', methods=['GET'])
    def hello_flask():
        return {"message": "Hello, Welcome to travel-API!"}

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)