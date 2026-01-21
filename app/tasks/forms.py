"""
Формы для работы с задачами
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class TaskForm(FlaskForm):
    """Форма для создания и редактирования задачи"""
    
    title = StringField(
        'Название задачи',
        validators=[
            DataRequired('Название обязательно'),
            Length(min=3, max=255, message='Название должно быть от 3 до 255 символов')
        ],
        render_kw={"placeholder": "Введи название задачи", "class": "form-control"}
    )
    
    description = TextAreaField(
        'Описание (опционально)',
        validators=[Optional(), Length(max=1000, message='Описание не должно быть длиннее 1000 символов')],
        render_kw={"placeholder": "Добавь описание...", "class": "form-control", "rows": "4"}
    )
    
    priority = SelectField(
        'Приоритет',
        choices=[
            ('low', '🟢 Низкий'),
            ('medium', '🟡 Средний'),
            ('high', '🔴 Высокий')
        ],
        default='medium',
        render_kw={"class": "form-select"}
    )
    
    submit = SubmitField('Сохранить задачу', render_kw={"class": "btn btn-success"})
