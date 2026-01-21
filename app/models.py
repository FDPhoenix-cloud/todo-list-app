"""
Модели базы данных
"""
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    """
    Модель пользователя для авторизации
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    
    # Связь с задачами (один пользователь - много задач)
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    shared_tasks = db.relationship('SharedTask', backref='user', lazy=True, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Хеширует и сохраняет пароль"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Проверяет правильность пароля"""
        return check_password_hash(self.password_hash, password)
    
    def get_tasks_today(self):
        """Возвращает задачи созданные сегодня"""
        today = datetime.utcnow().date()
        return Task.query.filter(
            Task.user_id == self.id,
            db.func.date(Task.created_at) == today
        ).all()
    
    def get_completed_today(self):
        """Возвращает количество завершенных задач сегодня"""
        today = datetime.utcnow().date()
        return Task.query.filter(
            Task.user_id == self.id,
            Task.completed == True,
            db.func.date(Task.completed_at) == today
        ).count()
    
    def __repr__(self):
        return f'<User {self.username}>'


class Task(db.Model):
    """
    Модель задачи пользователя
    """
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False, index=True)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    
    # Связь с пользователем
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Связь с общей задачей
    shared_task = db.relationship('SharedTask', backref='task', uselist=False, cascade='all, delete-orphan')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def toggle_complete(self):
        """Переключает статус завершения задачи"""
        self.completed = not self.completed
        if self.completed:
            self.completed_at = datetime.utcnow()
        else:
            self.completed_at = None
        db.session.commit()
    
    def get_shared_token(self):
        """Возвращает токен для общей ссылки если существует"""
        if self.shared_task:
            return self.shared_task.token
        return None
    
    def __repr__(self):
        return f'<Task {self.title}>'


class SharedTask(db.Model):
    """
    Модель для общих задач (доступны по уникальной ссылке без авторизации)
    """
    __tablename__ = 'shared_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(32), unique=True, nullable=False, index=True)  # Уникальный токен
    
    # Связь с задачей
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False, index=True)
    
    # Связь с пользователем которому принадлежит задача
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Кто может видеть (пусто = все)
    allowed_email = db.Column(db.String(120), nullable=True)  # Опционально ограничение по email
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)  # Опционально ограничение по времени
    
    def is_expired(self):
        """Проверяет истекла ли ссылка"""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True
        return False
    
    def __repr__(self):
        return f'<SharedTask {self.token}>'


# Индексы для оптимизации поиска
db.Index('idx_tasks_user_completed', Task.user_id, Task.completed)
db.Index('idx_tasks_user_created', Task.user_id, Task.created_at)
