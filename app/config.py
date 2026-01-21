"""
Конфигурация Flask приложения
"""
import os
from dotenv import load_dotenv

# Загрузи переменные из .env
load_dotenv()

class Config:
    """Базовая конфигурация"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = False
    TESTING = False
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.environ.get('SQLALCHEMY_ECHO', False)
    
    # Приложение
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 10))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB максимум загрузки


class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Конфигурация для тестов"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # БД в памяти для тестов


class ProductionConfig(Config):
    """Конфигурация для production"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY не установлен в production!")


# Выбирай конфигурацию в зависимости от окружения
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
