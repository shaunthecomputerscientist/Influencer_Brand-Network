# app/services/Celery/schedules.py
from celery.schedules import crontab
from flask import current_app
from main import celery, app

# Remove notifications at intervals
# Clear chats of non operating campaigns whose date is passed
# send reports through email
# send notification through email
# Update social links for influencers

celery.conf.beat_schedule = {
    'send_notifications_every_day': {
        'task': 'services.Celery.tasks.send_notifications_for_unread',  # Corrected path
        'schedule': crontab(minute='*/1'),  # Runs once a day at 5:10 PM
    },
    'remove_old_chat_data': {
        'task': 'services.Celery.tasks.remove_old_chat_data',  # Corrected path
        'schedule': crontab(minute='*/1'),  # Runs once a day at 12:30 AM
    },
    'test_notification_message': {
        'task': 'tasks.test_notification_message',  # Corrected path
        'schedule': crontab(hour='22',minute='*'),  # Runs once a day at 12:30 AM
    },
}

# Optionally, to log all tasks
# print(f"Registered Celery tasks: {celery.conf.beat_schedule}")