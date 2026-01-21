"""
Маршруты для просмотра общих задач
"""
from flask import Blueprint, render_template, flash, redirect, url_for
from app.models import SharedTask, Task

# Создай blueprint
shared_bp = Blueprint('shared', __name__, url_prefix='/shared')


@shared_bp.route('/task/<token>')
def view_shared_task(token):
    """Просмотр общей задачи по токену (без авторизации)"""
    
    # Найди общую задачу по токену
    shared_task = SharedTask.query.filter_by(token=token).first_or_404()
    
    # Проверь что ссылка не истекла
    if shared_task.is_expired():
        flash('❌ Ссылка истекла', 'danger')
        return redirect(url_for('auth.login'))
    
    # Получи основную задачу
    task = shared_task.task
    
    return render_template('shared/view_shared_task.html', task=task, shared_task=shared_task)
