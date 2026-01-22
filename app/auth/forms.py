"""
Формы для аутентификации
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User


class LoginForm(FlaskForm):
    """Форма входа"""
    email = StringField('Email', validators=[
        DataRequired('Email обязателен'),
        Email('Введите корректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired('Пароль обязателен')
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    """Форма регистрации"""
    username = StringField('Имя пользователя', validators=[
        DataRequired('Имя пользователя обязательно'),
        Length(min=3, max=20, message='Имя должно быть от 3 до 20 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired('Email обязателен'),
        Email('Введите корректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired('Пароль обязателен'),
        Length(min=6, message='Пароль должен быть минимум 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired('Подтверждение обязательно'),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        """Проверка что email не зарегистрирован"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Этот email уже зарегистрирован')

    def validate_username(self, username):
        """Проверка что username не занят"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Это имя пользователя уже занято')
