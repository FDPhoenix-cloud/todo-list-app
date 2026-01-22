"""
Инициализация Flask приложения (Application Factory Pattern)
"""
import os
from flask import Flask, redirect, url_for

from app.config import config
from app.extensions import db, login_manager


def create_app(config_name=None):
    """Создает и конфигурирует Flask приложение"""
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
        # Инициализируй расширения
    db.init_app(app)
    
    # Инициализируй LoginManager
    from flask_login import LoginManager
    global login_manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '⚠️ Пожалуйста, залогинься'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    
    # Импортируй модели
    from app.models import User, Task, SharedTask
    
    # Регистрируй user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    with app.app_context():
        # Создай таблицы
        db.create_all()
        
        # Регистрируй blueprints
        from app.auth.routes import auth_bp
        from app.tasks.routes import tasks_bp
        from app.shared.routes import shared_bp
        from app.statistics.routes import statistics_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(tasks_bp)
        app.register_blueprint(shared_bp)
        app.register_blueprint(statistics_bp)
        
        # Главная страница
        @app.route('/')
        def index():
            from flask_login import current_user
            if current_user.is_authenticated:
                return redirect(url_for('tasks.task_list'))
            return redirect(url_for('auth.login'))

        
        # Обработка ошибок
        @app.errorhandler(404)
        def not_found_error(error):
            from flask import render_template
            return render_template('404.html'), 404
        
        @app.errorhandler(500)
        def internal_error(error):
            db.session.rollback()
            from flask import render_template
            return render_template('500.html'), 500
        
        @app.errorhandler(403)
        def forbidden_error(error):
            from flask import render_template
            return render_template('403.html'), 403
    
    return app
