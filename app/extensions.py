"""
Расширения Flask приложения
SQLAlchemy для работы с БД, LoginManager для авторизации
"""
from flask_sqlalchemy import SQLAlchemy

# Инициализируем SQLAlchemy
db = SQLAlchemy()

# LoginManager будет инициализирован позже в __init__.py
login_manager = None
