"""
Формы для авторизации
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    """Форма входа"""
    
    username = StringField(
        'Имя пользователя',
        validators=[
            DataRequired('Имя пользователя обязательно'),
            Length(min=3, max=80, message='Имя должно быть от 3 до 80 символов')
        ],
        render_kw={"placeholder": "Введи имя пользователя", "class": "form-control"}
    )
    
    password = PasswordField(
        'Пароль',
        validators=[DataRequired('Пароль обязателен')],
        render_kw={"placeholder": "Введи пароль", "class": "form-control"}
    )
    
    remember_me = BooleanField('Запомнить меня')
    
    submit = SubmitField('Войти', render_kw={"class": "btn btn-primary w-100"})


class RegisterForm(FlaskForm):
    """Форма регистрации"""
    
    username = StringField(
        'Имя пользователя',
        validators=[
            DataRequired('Имя пользователя обязательно'),
            Length(min=3, max=80, message='Имя должно быть от 3 до 80 символов')
        ],
        render_kw={"placeholder": "Выбери имя пользователя", "class": "form-control"}
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired('Email обязателен'),
            Email('Некорректный email')
        ],
        render_kw={"placeholder": "Введи email", "class": "form-control"}
    )
    
    password = PasswordField(
        'Пароль',
        validators=[
            DataRequired('Пароль обязателен'),
            Length(min=6, message='Пароль должен быть минимум 6 символов')
        ],
        render_kw={"placeholder": "Придумай пароль", "class": "form-control"}
    )
    
    password_confirm = PasswordField(
        'Подтверди пароль',
        validators=[
            DataRequired('Подтверждение пароля обязательно'),
            EqualTo('password', message='Пароли должны совпадать')
        ],
        render_kw={"placeholder": "Повтори пароль", "class": "form-control"}
    )
    
    submit = SubmitField('Зарегистрироваться', render_kw={"class": "btn btn-success w-100"})
    
    def validate_username(self, field):
        """Проверяет что имя пользователя не занято"""
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято')
    
    def validate_email(self, field):
        """Проверяет что email не зарегистрирован"""
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован')
