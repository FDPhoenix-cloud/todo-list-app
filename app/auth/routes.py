"""
Маршруты аутентификации
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import traceback

from app.extensions import db
from app.models import User
from app.auth.forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if current_user.is_authenticated:
        return redirect(url_for('tasks.task_list'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Используем email вместо username
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                flash('✅ Вы успешно вошли!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('tasks.task_list'))
            else:
                flash('❌ Неправильный email или пароль', 'danger')
        except Exception as e:
            print(f"Ошибка при входе: {str(e)}")
            print(traceback.format_exc())
            flash('❌ Ошибка при входе. Попробуйте ещё раз', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if current_user.is_authenticated:
        return redirect(url_for('tasks.task_list'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            # Проверяем что email не существует
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('❌ Этот email уже зарегистрирован', 'danger')
                return redirect(url_for('auth.register'))
            
            # Проверяем что username не существует
            existing_username = User.query.filter_by(username=form.username.data).first()
            if existing_username:
                flash('❌ Это имя пользователя уже занято', 'danger')
                return redirect(url_for('auth.register'))
            
            # Создаём нового пользователя
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            
            # Используем метод set_password из модели
            user.set_password(form.password.data)
            
            print(f"Создаём пользователя: {form.username.data} ({form.email.data})")
            
            db.session.add(user)
            db.session.commit()
            
            print(f"Пользователь успешно создан!")
            
            flash('✅ Регистрация успешна! Теперь войдите в аккаунт', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"ОШИБКА ПРИ РЕГИСТРАЦИИ: {str(e)}")
            print(traceback.format_exc())
            flash(f'❌ Ошибка при регистрации: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из аккаунта"""
    logout_user()
    flash('✅ Вы вышли из аккаунта', 'info')
    return redirect(url_for('auth.login'))