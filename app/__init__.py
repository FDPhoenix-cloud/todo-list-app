from flask import Flask
from app.extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    login_manager.init_app(app)
    
    from app.auth import auth_bp
    from app.tasks import tasks_bp
    from app.shared import shared_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(shared_bp)
    
    with app.app_context():
        db.create_all()
    
    return app
