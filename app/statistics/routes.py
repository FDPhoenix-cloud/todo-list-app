"""
Маршруты для статистики и аналитики
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
    """Дашборд со статистикой"""
    
    # Сегодняшняя статистика (используй datetime.now() вместо datetime.utcnow())
    today = datetime.now().date()  # ✅ ИСПРАВЛЕНО: datetime.now() вместо datetime.utcnow()
    
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
    
    # Статистика по приоритетам
    priority_stats = db.session.query(
        Task.priority,
        func.count(Task.id)
    ).filter_by(user_id=current_user.id).group_by(Task.priority).all()
    
    # Последние 7 дней ✅ ИСПРАВЛЕНО: теперь используется правильное локальное время
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
        total_completed=total_completed,
        total_active=total_active,
        priority_stats=priority_stats,
        week_stats=week_stats,
        calculated_at=datetime.now().strftime('%d.%m.%Y %H:%M:%S')  # ✅ ДОБАВЛЕНО: время расчёта
    )



@statistics_bp.route('/api/daily-stats')
@login_required
def api_daily_stats():
    """API для получения статистики за день (JSON для графиков)"""
    
    today = datetime.now().date()  # ✅ ИСПРАВЛЕНО: datetime.now() вместо datetime.utcnow()
    
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
        'calculated_at': datetime.now().strftime('%d.%m.%Y %H:%M:%S')  # ✅ ДОБАВЛЕНО: время расчёта
    }
    
    return jsonify(stats)



@statistics_bp.route('/api/weekly-stats')
@login_required
def api_weekly_stats():
    """API для недельной статистики - ИСПРАВЛЕНО: используется локальное время"""
    
    today = datetime.now().date()  # ✅ ИСПРАВЛЕНО: datetime.now() вместо datetime.utcnow()
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
            'day': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][date.weekday()],  # ✅ ДОБАВЛЕНО: день недели
            'created': created,
            'completed': completed
        })
    
    return jsonify(stats)



@statistics_bp.route('/')
@login_required
def statistics():
    """Основная страница статистики с детальной информацией"""
    
    # Получи дату 7 дней назад
    today = datetime.now().date()  # ✅ Локальное время!
    last_week = datetime.now() - timedelta(days=7)
    
    # Все задачи за всё время
    all_tasks = Task.query.filter_by(user_id=current_user.id).all()
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t.completed)
    active_tasks = total_tasks - completed_tasks
    
    # СТАТИСТИКА ЗА ПОСЛЕДНИЕ 7 ДНЕЙ
    last_7_days_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.created_at >= last_week  # ✅ Правильное сравнение!
    ).all()
    
    last_7_days_total = len(last_7_days_tasks)
    last_7_days_completed = sum(1 for t in last_7_days_tasks if t.completed)
    last_7_days_active = last_7_days_total - last_7_days_completed
    
    # Статистика по приоритетам
    high_priority = sum(1 for t in all_tasks if t.priority == 'high')
    medium_priority = sum(1 for t in all_tasks if t.priority == 'medium')
    low_priority = sum(1 for t in all_tasks if t.priority == 'low')
    
    # За последние 7 дней по приоритетам
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
            'date': day_date.strftime('%d.%m'),  # Формат: 23.01
            'day_name': ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'][day.weekday()],
            'total': len(day_tasks),
            'completed': sum(1 for t in day_tasks if t.completed),
            'active': len(day_tasks) - sum(1 for t in day_tasks if t.completed),
        })
    
    return render_template('statistics/statistics.html',
        # Всего задач
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        active_tasks=active_tasks,
        
        # Последние 7 дней
        last_7_days_total=last_7_days_total,
        last_7_days_completed=last_7_days_completed,
        last_7_days_active=last_7_days_active,
        
        # По приоритетам (всё время)
        high_priority=high_priority,
        medium_priority=medium_priority,
        low_priority=low_priority,
        
        # По приоритетам (последние 7 дней)
        last_7_high=last_7_high,
        last_7_medium=last_7_medium,
        last_7_low=last_7_low,
        
        # По дням
        daily_stats=daily_stats,
        
        # Дата последнего расчёта
        calculated_at=datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    )