"""
Маршруты авторизации
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.extensions import db
from app.models import User
from app.auth.forms import LoginForm, RegisterForm

# Создай blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    
    # Если пользователь уже вошел, перенаправь на главную
    if current_user.is_authenticated:
        return redirect(url_for('tasks.task_list'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Найди пользователя по имени
        user = User.query.filter_by(username=form.username.data).first()
        
        # Проверь пароль
        if user is None or not user.check_password(form.password.data):
            flash('Неправильное имя пользователя или пароль', 'danger')
            return redirect(url_for('auth.login'))
        
        # Залогинь пользователя
        login_user(user, remember=form.remember_me.data)
        
        # Редирект на страницу которую пытался открыть или на главную
        next_page = request.args.get('next')
        if not next_page or url_has_allowed_host_and_scheme(next_page):
            next_page = url_for('tasks.task_list')
        
        flash(f'Добро пожаловать, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    
    # Если уже вошел, перенаправь на главную
    if current_user.is_authenticated:
        return redirect(url_for('tasks.task_list'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Создай нового пользователя
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        # Добавь в БД
        db.session.add(user)
        db.session.commit()
        
        flash('Аккаунт создан! Теперь ты можешь войти', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
def logout():
    """Выход из аккаунта"""
    logout_user()
    flash('Ты вышел из аккаунта', 'info')
    return redirect(url_for('auth.login'))


def url_has_allowed_host_and_scheme(url, allowed_hosts=None):
    """Проверяет что URL безопасен (защита от CSRF)"""
    from urllib.parse import urlparse
    if allowed_hosts is None:
        allowed_hosts = None
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and parsed.netloc in allowed_hosts if allowed_hosts else True
