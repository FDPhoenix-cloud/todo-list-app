/**
 * To-Do List Application - Main JavaScript
 * Динамический функционал, AJAX и утилиты
 */

// ========== ИНИЦИАЛИЗАЦИЯ ==========
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 To-Do List Application Loaded');
    
    // Инициализируй все компоненты
    initializeTooltips();
    initializeTaskToggle();
    initializeDeleteConfirmation();
    loadStatistics();
});

// ========== УТИЛИТЫ ==========

/**
 * Показать уведомление (toast/alert)
 */
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show fade-in`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Автоматически скрыть через 5 секунд
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

/**
 * Форматирование даты
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('ru-RU', options);
}

/**
 * Копирование текста в буфер обмена
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('✅ Скопировано в буфер обмена!', 'success');
    }).catch(() => {
        showNotification('❌ Ошибка копирования', 'danger');
    });
}

// ========== КОМПОНЕНТЫ ==========

/**
 * Инициализация всплывающих подсказок (Tooltips)
 */
function initializeTooltips() {
    // Bootstrap tooltips
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        new bootstrap.Tooltip(element);
    });
}

/**
 * AJAX переключение статуса задачи
 */
function initializeTaskToggle() {
    const toggleButtons = document.querySelectorAll('.toggle-task-btn');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const taskId = this.getAttribute('data-task-id');
            const isCompleted = this.getAttribute('data-completed') === 'true';
            
            // AJAX запрос
            fetch(`/tasks/${taskId}/toggle`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Обнови иконку
                    if (data.completed) {
                        this.innerHTML = '<i class="fas fa-check-circle text-success fa-lg"></i>';
                    } else {
                        this.innerHTML = '<i class="far fa-circle text-muted fa-lg"></i>';
                    }
                    
                    // Показать уведомление
                    showNotification(data.message, 'success');
                    
                    // Обновить визуальный статус задачи
                    const row = this.closest('tr');
                    if (row) {
                        if (data.completed) {
                            row.classList.add('table-success', 'completed-task');
                        } else {
                            row.classList.remove('table-success', 'completed-task');
                        }
                    }
                } else {
                    showNotification('❌ Ошибка при обновлении задачи', 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('❌ Ошибка сервера', 'danger');
            });
        });
    });
}

/**
 * Подтверждение при удалении
 */
function initializeDeleteConfirmation() {
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-delete') || 
                           'Ты уверен, что хочешь это удалить?';
            
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

/**
 * Загрузка и отображение статистики
 */
function loadStatistics() {
    // Если это страница статистики
    const dashboardElement = document.querySelector('[data-dashboard="true"]');
    if (!dashboardElement) return;
    
    // AJAX запрос к API
    fetch('/statistics/api/daily-stats')
        .then(response => response.json())
        .then(data => {
            console.log('📊 Статистика загружена:', data);
            updateStatisticsDisplay(data);
        })
        .catch(error => console.error('Ошибка загрузки статистики:', error));
}

/**
 * Обновление отображения статистики
 */
function updateStatisticsDisplay(stats) {
    // Обнови значения если элементы существуют
    const elements = {
        'total-tasks': stats.total,
        'completed-tasks': stats.completed,
        'active-tasks': stats.active,
        'today-created': stats.today_created,
        'today-completed': stats.today_completed
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            // Анимация
            element.classList.add('fade-in');
        }
    });
}

/**
 * Поиск задач (фильтрация на клиенте)
 */
function searchTasks(query) {
    const rows = document.querySelectorAll('table tbody tr');
    const lowerQuery = query.toLowerCase();
    
    rows.forEach(row => {
        const taskTitle = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        
        if (taskTitle.includes(lowerQuery)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Сортировка задач по приоритету
 */
function sortTasksByPriority() {
    const table = document.querySelector('table tbody');
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tr'));
    
    const priorityOrder = { 'Высокий': 1, 'Средний': 2, 'Низкий': 3 };
    
    rows.sort((a, b) => {
        const priorityA = a.querySelector('.badge')?.textContent || '';
        const priorityB = b.querySelector('.badge')?.textContent || '';
        
        const orderA = priorityOrder[priorityA.split(' ')[1]] || 999;
        const orderB = priorityOrder[priorityB.split(' ')[1]] || 999;
        
        return orderA - orderB;
    });
    
    rows.forEach(row => table.appendChild(row));
    showNotification('✅ Задачи отсортированы по приоритету', 'success');
}

/**
 * Экспорт задач в JSON
 */
function exportTasksToJSON() {
    const tasks = [];
    
    document.querySelectorAll('table tbody tr').forEach(row => {
        const cells = row.querySelectorAll('td');
        tasks.push({
            title: cells[1]?.textContent.trim(),
            priority: cells[2]?.textContent.trim(),
            date: cells[3]?.textContent.trim(),
            completed: row.classList.contains('completed-task')
        });
    });
    
    const dataStr = JSON.stringify(tasks, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `tasks_${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    
    showNotification('✅ Задачи экспортированы', 'success');
}

/**
 * Очистка завершенных задач
 */
function clearCompletedTasks() {
    if (!confirm('Удалить все завершенные задачи? Это действие необратимо!')) {
        return;
    }
    
    const completedRows = document.querySelectorAll('table tbody tr.completed-task');
    const taskIds = Array.from(completedRows).map(row => {
        return row.querySelector('.toggle-task-btn')?.getAttribute('data-task-id');
    });
    
    if (taskIds.length === 0) {
        showNotification('Нет завершенных задач', 'info');
        return;
    }
    
    // Отправь запросы на удаление
    Promise.all(taskIds.map(id => 
        fetch(`/tasks/${id}/delete`, { method: 'POST' })
    )).then(() => {
        location.reload();
    });
}

// ========== EVENT LISTENERS ==========

// Поиск при печати
document.addEventListener('keydown', function(e) {
    // Ctrl+F для фокуса на поиск (если есть поле поиска)
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        const searchInput = document.querySelector('[data-search]');
        if (searchInput) {
            e.preventDefault();
            searchInput.focus();
        }
    }
});

// Обработка Escape клавиши
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        // Закрой модальные окна если нужно
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(modal => {
            const bootstrapModal = bootstrap.Modal.getInstance(modal);
            if (bootstrapModal) bootstrapModal.hide();
        });
    }
});

console.log('✅ All JavaScript modules loaded successfully');
