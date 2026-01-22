#!/usr/bin/env python3
"""
Запуск To-Do List приложения
"""
import os
import sys
from dotenv import load_dotenv
from app import create_app
from app.extensions import db

def create_app_instance():
    """Создает и конфигурирует приложение"""
    app = create_app()
    
    # Зарегистрируй маршруты
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    # Загрузи переменные окружения
    load_dotenv()
    
    app = create_app_instance()
    
    # Получи параметры запуска
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"🚀 Запуск MyTasks на http://{host}:{port}")
    print(f"📱 Админка: http://{host}:{port}/admin")
    print(f"📊 Статистика: http://{host}:{port}/statistics/dashboard")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
