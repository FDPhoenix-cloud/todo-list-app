"""
Инициализация расширений Flask
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# SQLAlchemy - для работы с БД
db = SQLAlchemy()

# LoginManager - для управления сессиями пользователей
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Редирект на страницу входа если не авторизован
login_manager.login_message = 'Пожалуйста, войдите в аккаунт'
login_manager.login_message_category = 'info'
