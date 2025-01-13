from celery import Celery
import os

def make_celery(app):
    """Create and configure a Celery instance."""
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    # # Windows compatibility for Celery workers
    # if os.name == 'nt':
    #     celery.conf.update(app.config)

    # Autodiscover tasks from specific modules
    celery.autodiscover_tasks(['services.Celery'])

    # ContextTask to enable Flask app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def get_current_celery_instance():
    """Retrieve the Celery instance from the current Flask app."""
    from flask import current_app
    if current_app:

        return current_app.config['CELERY']

# Optional: Remove standalone Celery instance unless needed
# celery = Celery()  # Uncomment only if this is required in certain contexts

