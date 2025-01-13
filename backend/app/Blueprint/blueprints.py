from flask import Blueprint

def register_blueprints(app):
    from auth.routes import auth_bp
    from user.routes import user_bp
    from campaigns.routes import campaigns_bp
    from user.Admin.routes import admin_bp
    from campaigns.GoalProgressTracking.trackingInfluencerSocials import campaigns_tracking_bp
    from AsyncJobs.asyncJob import trigger_bp
    # from sse.routes import sse_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
    app.register_blueprint(campaigns_tracking_bp, url_prefix='/campaign/tracking')
    app.register_blueprint(trigger_bp, url_prefix='/triggerjobs')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    # app.register_blueprint(sse_bp, url_prefix='/stream')
    for blueprint_name, blueprint in app.blueprints.items():
        app.logger.info(f"Registered blueprint: {blueprint_name}, URL prefix: {blueprint}")
