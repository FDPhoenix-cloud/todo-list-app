"""
Формы для управления задачами
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional


class TaskForm(FlaskForm):
    """Форма для создания/редактирования задачи"""
    title = StringField('Название задачи', validators=[
        DataRequired('Название обязательно'),
        Length(min=3, max=100, message='Название: от 3 до 100 символов')
    ])
    description = TextAreaField('Описание', validators=[
        Optional(),
        Length(max=500, message='Максимум 500 символов')
    ])
    priority = SelectField('Приоритет', choices=[
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий')
    ], default='medium')
    completed = BooleanField('Завершено')
    submit = SubmitField('Сохранить')
