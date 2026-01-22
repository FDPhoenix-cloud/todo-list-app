#!/bin/bash
echo "🚀 Установка MyTasks..."

# Создай виртуальное окружение
python3 -m venv venv
source venv/bin/activate || venv\\Scripts\\activate

# Установи зависимости
pip install -r requirements.txt

# Создай папки
mkdir -p instance static/css static/js templates/auth templates/tasks templates/shared templates/statistics

# Создай .env
cp .env.example .env

echo "✅ Установка завершена!"
echo "📝 Создай аккаунт на http://127.0.0.1:5000/auth/register"
echo "🚀 Запуск: python run.py"
