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
    
    # Сегодняшняя статистика
    today = datetime.utcnow().date()
    
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
        total_completed=total_completed,
        total_active=total_active,
        priority_stats=priority_stats,
        week_stats=week_stats
    )


@statistics_bp.route('/api/daily-stats')
@login_required
def api_daily_stats():
    """API для получения статистики за день (JSON для графиков)"""
    
    today = datetime.utcnow().date()
    
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
        ).count()
    }
    
    return jsonify(stats)


@statistics_bp.route('/api/weekly-stats')
@login_required
def api_weekly_stats():
    """API для недельной статистики"""
    
    today = datetime.utcnow().date()
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
            'created': created,
            'completed': completed
        })
    
    return jsonify(stats)
