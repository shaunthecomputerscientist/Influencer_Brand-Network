import os
from flask_mail import Message
from flask import current_app, render_template

def send_verification_email(user_email, token):
    """Send a verification email to the user."""
    with current_app.app_context():
        mail = current_app.extensions['mail']  # Get mail instance from current_app
        subject = "Please verify your email"
        verification_link = f"{os.getenv('FRONTEND_URL')}/verify?token={token}"

        msg = Message(subject, sender=os.getenv('EMAIL_USER'), recipients=[user_email])
        msg.body = f"Please click the link to verify your email: {verification_link}"
        
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send verification email: {e}")

def send_confirmation_email(user_email='22f2001208@ds.study.iitm.ac.in', name='Shaunak'):
    """Send a confirmation email after successful signup."""
    with current_app.app_context():
        mail = current_app.extensions['mail']  # Get mail instance from current_app
        subject = "Signup Successful"
        # print(os.getcwd())
        # Render the HTML from the file
        html_content = render_template(('templates','signup.html'), name=name, platformName=os.environ.get('APP_NAME'))

        # Create the email message
        msg = Message(subject, sender=os.getenv('EMAIL_USER'), recipients=[user_email])
        msg.html = html_content

        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send confirmation email: {e}")

def send_password_reset_email(user_email, reset_link, name):
    """Send a password reset email to the user."""
    with current_app.app_context():
        mail = current_app.extensions['mail']  # Get mail instance from current_app
        subject = "Password Reset Request"

        # Render the HTML template with dynamic reset link
        html_content = render_template(('templates','resetpassword.html'), reset_link=reset_link, platformName=os.environ.get('APP_NAME'), user=name)

        # Create the email
        msg = Message(subject, sender=os.getenv('EMAIL_USER'), recipients=[user_email])
        msg.html = html_content

        try:
            mail.send(msg)
            print(f"Password reset email sent to {user_email}")
        except Exception as e:
            print(f"Failed to send password reset email: {e}")

def send_notification_email(user_email, subject, body):
    """Send a campaign-related notification email to the user."""
    with current_app.app_context():
        mail = current_app.extensions['mail']  # Get the mail instance from current_app
        
        # Create the message
        msg = Message(subject, sender=os.getenv('EMAIL_USER'), recipients=[user_email])
        msg.html = body
        # print(msg.body)
        
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Failed to send campaign notification email: {e}")
