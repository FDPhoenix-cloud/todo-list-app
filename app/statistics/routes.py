"""
Маршруты для статистики и аналитики
Окончательная версия с правильной структурой файлов
"""
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
from app.models import Task
from app.extensions import db


# Создай blueprint
statistics_bp = Blueprint('statistics', __name__, url_prefix='/statistics')



@statistics_bp.route('/dashboard')
@login_required
def dashboard():
    """Краткий дашборд со статистикой сегодня и неделей"""
    
    # Сегодняшняя статистика (используй datetime.now() вместо datetime.utcnow())
    today = datetime.now().date()  # ✅ Локальное время
    
    today_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        func.date(Task.created_at) == today
    ).count()
    
    today_completed = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed == True,
        func.date(Task.completed_at) == today
    ).count()
    
    # Общая статистика
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    total_completed = Task.query.filter_by(user_id=current_user.id, completed=True).count()
    total_active = total_tasks - total_completed
    
    # Последние 7 дней
    week_ago = today - timedelta(days=7)
    week_stats = {}
    
    for i in range(7):
        date = week_ago + timedelta(days=i)
        count = Task.query.filter(
            Task.user_id == current_user.id,
            func.date(Task.created_at) == date
        ).count()
        week_stats[date.strftime('%d.%m')] = count
    
    return render_template(
        'statistics/dashboard.html',
        today_tasks=today_tasks,
        today_completed=today_completed,
        total_tasks=total_tasks,
        total_active=total_active,
        week_stats=week_stats,
        calculated_at=datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    )



@statistics_bp.route('/api/daily-stats')
@login_required
def api_daily_stats():
    """API для получения статистики за день (JSON для графиков)"""
    
    today = datetime.now().date()
    
    stats = {
        'total': Task.query.filter_by(user_id=current_user.id).count(),
        'completed': Task.query.filter_by(user_id=current_user.id, completed=True).count(),
        'active': Task.query.filter(
            Task.user_id == current_user.id,
            Task.completed == False
        ).count(),
        'today_created': Task.query.filter(
            Task.user_id == current_user.id,
            func.date(Task.created_at) == today
        ).count(),
        'today_completed': Task.query.filter(
            Task.user_id == current_user.id,
            Task.completed == True,
            func.date(Task.completed_at) == today
        ).count(),
        'calculated_at': datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    }
    
    return jsonify(stats)



@statistics_bp.route('/api/weekly-stats')
@login_required
def api_weekly_stats():
    """API для недельной статистики"""
    
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    stats = []
    
    for i in range(7):
        date = week_ago + timedelta(days=i)
        created = Task.query.filter(
            Task.user_id == current_user.id,
            func.date(Task.created_at) == date
        ).count()
        completed = Task.query.filter(
            Task.user_id == current_user.id,
            Task.completed == True,
            func.date(Task.completed_at) == date
        ).count()
        
        stats.append({
            'date': date.strftime('%d.%m'),
            'day': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][date.weekday()],
            'created': created,
            'completed': completed
        })
    
    return jsonify(stats)



@statistics_bp.route('/')
@login_required
def statistics():
    """Полная страница статистики с детальной информацией"""
    
    # Получи дату 7 дней назад
    today = datetime.now().date()
    last_week = datetime.now() - timedelta(days=7)
    
    # Все задачи за всё время
    all_tasks = Task.query.filter_by(user_id=current_user.id).all()
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t.completed)
    active_tasks = total_tasks - completed_tasks
    
    # СТАТИСТИКА ЗА ПОСЛЕДНИЕ 7 ДНЕЙ
    last_7_days_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.created_at >= last_week
    ).all()
    
    last_7_days_total = len(last_7_days_tasks)
    last_7_days_completed = sum(1 for t in last_7_days_tasks if t.completed)
    last_7_days_active = last_7_days_total - last_7_days_completed
    
    # Статистика по приоритетам (последние 7 дней)
    last_7_high = sum(1 for t in last_7_days_tasks if t.priority == 'high')
    last_7_medium = sum(1 for t in last_7_days_tasks if t.priority == 'medium')
    last_7_low = sum(1 for t in last_7_days_tasks if t.priority == 'low')
    
    # Статистика по дням (последние 7 дней)
    daily_stats = []
    for i in range(6, -1, -1):  # От 6 дней назад до сегодня
        day = datetime.now() - timedelta(days=i)
        day_date = day.date()
        
        day_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            func.date(Task.created_at) == day_date
        ).all()
        
        daily_stats.append({
            'date': day_date.strftime('%d.%m'),
            'day_name': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][day.weekday()],
            'total': len(day_tasks),
            'completed': sum(1 for t in day_tasks if t.completed),
            'active': len(day_tasks) - sum(1 for t in day_tasks if t.completed),
        })
    
    # ✅ ПРАВИЛЬНЫЙ ШАБЛОН: statistics.html
    return render_template('statistics/statistics.html',
        # Всего задач
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        active_tasks=active_tasks,
        
        # Последние 7 дней
        last_7_days_total=last_7_days_total,
        last_7_days_completed=last_7_days_completed,
        last_7_days_active=last_7_days_active,
        
        # По приоритетам (последние 7 дней)
        last_7_high=last_7_high,
        last_7_medium=last_7_medium,
        last_7_low=last_7_low,
        
        # По дням
        daily_stats=daily_stats,
        
        # Дата последнего расчёта
        calculated_at=datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    )