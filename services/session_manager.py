from models.user import User
from .user_services import users, active_sessions

def validate_session(email, token):
    """
    Validate if a user's session is active and their token is correct.

    Args:
        email (str): The user's email.
        token (str): The token to validate.

    Returns:
        tuple: (is_valid, message)
    """
    if email not in active_sessions:
        return False, "No active session for this user"

    expected_token = active_sessions[email]

    if token != expected_token:
        return False, "Invalid token"

    user = users.get(email)
    if not user or user.token != token:
        return False, "Invalid session or user data"

    return True, "Session is valid"
