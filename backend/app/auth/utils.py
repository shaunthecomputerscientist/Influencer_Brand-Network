import re
from zerobouncesdk import ZeroBounce, ZBException
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
import os

zero_bounce = ZeroBounce("zerobouncesdk")

def is_valid_email(email):
    """Check if email is in a valid format."""
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email)

def validate_email(email, ip_address=None):
    """
    Validates an email using the ZeroBounce API.

    Args:
        email (str): The email address to validate.
        ip_address (str): Optional. The IP address the email signed up from.

    Returns:
        bool: True if the email status is 'valid', False otherwise.
    """
    try:
        api_key = os.environ.get("ZEROBOUNCE")
        if not api_key:
            raise ValueError("ZEROBOUNCESDK environment variable is not set.")

        # Initialize ZeroBounce with the API key
        zero_bounce = ZeroBounce(api_key)

        # Call the ZeroBounce API to validate the email
        response = zero_bounce.validate(email, ip_address)
        print(response.status.value)
        # Check the status key in the response
        if response.status.value == "valid":
            return True
        else:
            return False
    except ZBException as e:
        print("ZeroBounce validate error:", str(e))
        return False

def hash_password(password):
    """Hash the password."""
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """Check if password matches hashed password."""
    return check_password_hash(hashed_password, password)

def create_jwt_token(identity):
    """Create a JWT token."""
    return create_access_token(identity=identity)
