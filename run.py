"""
Точка входа приложения
"""
from app import create_app

# Создай приложение
app = create_app()

if __name__ == '__main__':
    # Запусти Flask приложение
    # debug=True автоматически перезагружает при изменении кода
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True
    )
