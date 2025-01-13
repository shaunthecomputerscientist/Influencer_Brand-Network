# from .celery_utils import get_current_celery_instance
from main import app, celery
from flask import render_template
from datetime import datetime, timedelta
from models.models import db, Chat, Campaign, Notification  # Import your models
from services.email_service.email_service import send_notification_email, send_confirmation_email
from sqlalchemy.orm import joinedload
import os

@celery.task
def remove_old_chat_data():
    """Remove chat data for campaigns that have ended."""
    # from flask import current_app
    # app = current_app
    with app.app_context():
        campaigns = Campaign.query.all()
        for campaign in campaigns:
            if campaign.end_date < datetime.utcnow():
                Chat.query.filter_by(campaign_id=campaign.id).delete()
        db.session.commit()
        print("Old chat data removed for expired campaigns.")

@celery.task
def send_notifications_for_unread():
    """Celery task to send campaign notifications for unread notifications from the last 10 days."""
    print('Executing task notification')
    # from flask import current_app
    # app = current_app
    with app.app_context():
        try:
            print('executing celery')
            ten_days_ago = datetime.utcnow() - timedelta(days=10)
            notifications = db.session.query(Notification).filter(
                Notification.is_read == False,
                Notification.created_at >= ten_days_ago
            ).options(joinedload(Notification.receiver)).all()
            print(notifications)

            users_to_notify = set()
            FRONTEND_BASE_URL = os.getenv('FRONTEND_URL')

            for notification in notifications:
                user = notification.receiver
                if user not in users_to_notify and not notification.email_sent:
                    users_to_notify.add(user)
                    # print(user)
                    
                    subject = f"New Notification from {os.getenv('APP_NAME')}"
                    dashboard_url = f"{FRONTEND_BASE_URL}/auth/login"

                    body_html = render_template(
                        ('templates','emailnotificationtemplate.html'),
                        user_name=user.name,
                        sender=notification.sender.name,
                        message=notification.message,
                        dashboard_url=dashboard_url,
                        platformName = os.environ.get('APP_NAME')
                    )
                    # print(body_html)

                    # body = f"""{notification.message}"""

                    send_notification_email(user.email, subject, body=body_html)

                    notification.is_read = True
                    notification.email_sent = True
            
            db.session.commit()

        except Exception as e:
            print(f"Failed to send campaign notifications: {e}")

@celery.task
def delete_old_read_notifications():
    """Deletes notifications that are marked as read and are older than a month."""
    print("Executing task to delete old read notifications")
    # from flask import current_app
    # app=current_app
    with app.app_context():  # Ensure we are in application context
        try:
            one_month_ago = datetime.utcnow() - timedelta(days=30)
            # Query for notifications that are read and older than a month
            old_notifications = db.session.query(Notification).filter(
                Notification.is_read == True,
                Notification.created_at < one_month_ago
            ).all()

            count = len(old_notifications)
            if count > 0:
                # Delete the fetched notifications
                for notification in old_notifications:
                    db.session.delete(notification)

                # Commit the changes to the database
                db.session.commit()

            print(f"Deleted {count} old read notifications")
        except Exception as e:
            print(f"Error occurred while deleting old read notifications: {e}")


@celery.task
def test_notification_message():
    with app.app_context():
        try:
            send_confirmation_email()
        except Exception as e:
            return e
            
    







