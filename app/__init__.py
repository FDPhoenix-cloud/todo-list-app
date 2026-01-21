"""
Инициализация Flask приложения (Application Factory Pattern)
"""
import os
from flask import Flask
from app.extensions import db, login_manager
from app.config import config


def create_app(config_name=None):
    """
    Создает и конфигурирует Flask приложение
    
    Args:
        config_name: Тип конфигурации ('development', 'testing', 'production')
    
    Returns:
        Сконфигурированное Flask приложение
    """
    
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    
    # Загрузи конфигурацию
    app.config.from_object(config[config_name])
    
    # Инициализируй расширения с приложением
    db.init_app(app)
    login_manager.init_app(app)
    
    # Импортируй модели (ДО создания таблиц!)
    from app.models import User, Task, SharedTask
    
    # Регистрируй пользователей для login_manager
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Создай контекст приложения
    with app.app_context():
        # Создай таблицы если их нет
        db.create_all()
        
        # Регистрируй blueprints (модули)
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
            from flask import redirect, url_for
            from flask_login import current_user
            if current_user.is_authenticated:
                return redirect(url_for('tasks.task_list'))
            return redirect(url_for('auth.login'))
    
    return app
