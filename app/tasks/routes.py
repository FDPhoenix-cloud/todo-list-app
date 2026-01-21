"""
Маршруты для работы с задачами (CRUD операции)
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Task, SharedTask
from app.tasks.forms import TaskForm
import secrets

# Создай blueprint
tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_bp.route('/')
@login_required
def task_list():
    """Список всех задач пользователя"""
    
    # Получи параметры фильтрации
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('filter', 'all')  # all, completed, active
    
    # Базовый запрос
    query = Task.query.filter_by(user_id=current_user.id)
    
    # Применяй фильтр
    if filter_type == 'completed':
        query = query.filter_by(completed=True)
    elif filter_type == 'active':
        query = query.filter_by(completed=False)
    
    # Сортировка по приоритету и дате
    query = query.order_by(
        Task.completed.asc(),  # Активные сверху
        Task.priority.desc(),  # Высокий приоритет выше
        Task.created_at.desc()  # Новые сверху
    )
    
    # Пагинация (10 задач на странице)
    tasks = query.paginate(page=page, per_page=10)
    
    # Статистика
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, completed=True).count()
    active_tasks = total_tasks - completed_tasks
    
    return render_template(
        'tasks/task_list.html',
        tasks=tasks,
        filter_type=filter_type,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        active_tasks=active_tasks
    )


@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    """Создание новой задачи"""
    
    form = TaskForm()
    
    if form.validate_on_submit():
        # Создай новую задачу
        task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            user_id=current_user.id
        )
        
        # Добавь в БД
        db.session.add(task)
        db.session.commit()
        
        flash('✅ Задача создана!', 'success')
        return redirect(url_for('tasks.task_list'))
    
    return render_template('tasks/create_task.html', form=form)


@tasks_bp.route('/<int:task_id>')
@login_required
def view_task(task_id):
    """Просмотр одной задачи"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверь что задача принадлежит пользователю
    if task.user_id != current_user.id:
        flash('❌ Доступ запрещен', 'danger')
        return redirect(url_for('tasks.task_list'))
    
    return render_template('tasks/view_task.html', task=task)


@tasks_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Редактирование задачи"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверь что задача принадлежит пользователю
    if task.user_id != current_user.id:
        flash('❌ Доступ запрещен', 'danger')
        return redirect(url_for('tasks.task_list'))
    
    form = TaskForm()
    
    if form.validate_on_submit():
        # Обнови данные
        task.title = form.title.data
        task.description = form.description.data
        task.priority = form.priority.data
        
        db.session.commit()
        
        flash('✏️ Задача обновлена!', 'success')
        return redirect(url_for('tasks.view_task', task_id=task.id))
    
    # Заполни форму текущими данными
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.priority.data = task.priority
    
    return render_template('tasks/edit_task.html', form=form, task=task)


@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Удаление задачи"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверь что задача принадлежит пользователю
    if task.user_id != current_user.id:
        flash('❌ Доступ запрещен', 'danger')
        return redirect(url_for('tasks.task_list'))
    
    # Удали из БД
    db.session.delete(task)
    db.session.commit()
    
    flash('🗑️ Задача удалена!', 'success')
    return redirect(url_for('tasks.task_list'))


@tasks_bp.route('/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    """Переключение статуса задачи (завершена/активна) - AJAX запрос"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверь что задача принадлежит пользователю
    if task.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    # Переключи статус
    task.toggle_complete()
    
    # Верни JSON ответ для AJAX
    return jsonify({
        'success': True,
        'completed': task.completed,
        'message': '✅ Задача завершена!' if task.completed else '⏳ Задача активирована!'
    })


@tasks_bp.route('/<int:task_id>/share', methods=['GET', 'POST'])
@login_required
def share_task(task_id):
    """Создание общей ссылки для задачи"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверь что задача принадлежит пользователю
    if task.user_id != current_user.id:
        flash('❌ Доступ запрещен', 'danger')
        return redirect(url_for('tasks.task_list'))
    
    if request.method == 'POST':
        # Проверь есть ли уже общая ссылка
        if task.shared_task:
            # Удали старую ссылку
            db.session.delete(task.shared_task)
        
        # Создай новую общую ссылку
        token = secrets.token_urlsafe(24)  # Генерируй уникальный токен
        shared_task = SharedTask(
            token=token,
            task_id=task.id,
            user_id=current_user.id
        )
        
        db.session.add(shared_task)
        db.session.commit()
        
        # Создай полную ссылку для копирования
        share_link = url_for('shared.view_shared_task', token=token, _external=True)
        
        flash(f'🔗 Ссылка создана! Скопируй: {share_link}', 'success')
        return redirect(url_for('tasks.view_task', task_id=task.id))
    
    return render_template('tasks/share_task.html', task=task)


@tasks_bp.route('/<int:task_id>/unshare', methods=['POST'])
@login_required
def unshare_task(task_id):
    """Удаление общей ссылки для задачи"""
    
    task = Task.query.get_or_404(task_id)
    
    # Проверь что задача принадлежит пользователю
    if task.user_id != current_user.id:
        flash('❌ Доступ запрещен', 'danger')
        return redirect(url_for('tasks.task_list'))
    
    # Удали общую ссылку
    if task.shared_task:
        db.session.delete(task.shared_task)
        db.session.commit()
        flash('🔒 Общая ссылка удалена!', 'success')
    
    return redirect(url_for('tasks.view_task', task_id=task.id))


@tasks_bp.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибки"""
    flash('❌ Задача не найдена', 'danger')
    return redirect(url_for('tasks.task_list'))
