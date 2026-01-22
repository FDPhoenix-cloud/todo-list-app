// ========================
// MyTasks - Main JavaScript
// ========================

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Инициализация приложения
function initializeApp() {
    // Закрытие алертов через 5 секунд
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Вы уверены? Это действие нельзя отменить.')) {
                e.preventDefault();
            }
        });
    });

    // Toggle completed задач
    const toggleButtons = document.querySelectorAll('[data-toggle-task]');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const taskId = this.getAttribute('data-toggle-task');
            toggleTask(taskId);
        });
    });

    // Инициализация Tooltips
    initializeTooltips();

    // Инициализация Popovers
    initializePopovers();
}

// Переключение статуса задачи
function toggleTask(taskId) {
    const url = `/tasks/${taskId}/toggle`;
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем страницу или элемент
            location.reload();
        } else {
            alert('Ошибка при обновлении задачи');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Произошла ошибка');
    });
}

// Инициализация подсказок (Tooltips)
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Инициализация Popovers
function initializePopovers() {
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Форматирование даты
function formatDate(dateString) {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('ru-RU', options);
}

// Форматирование времени
function formatTime(dateString) {
    const date = new Date(dateString);
    const options = { hour: '2-digit', minute: '2-digit' };
    return date.toLocaleTimeString('ru-RU', options);
}

// Валидация формы
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return true;

    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });

    return isValid;
}

// Отправка формы с AJAX
function submitFormAjax(formId, url) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        if (!validateForm(formId)) {
            alert('Пожалуйста, заполните все требуемые поля');
            return;
        }

        const formData = new FormData(form);

        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Успешно!');
                location.reload();
            } else {
                alert('Ошибка: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Произошла ошибка');
        });
    });
}

// Утилита: копирование текста в буфер обмена
function copyToClipboard(text, buttonElement) {
    navigator.clipboard.writeText(text).then(() => {
        const originalText = buttonElement.textContent;
        buttonElement.textContent = '✅ Скопировано!';
        setTimeout(() => {
            buttonElement.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Ошибка копирования:', err);
        alert('Ошибка при копировании');
    });
}

// Показать/скрыть пароль
function togglePasswordVisibility(inputId, buttonElement) {
    const input = document.getElementById(inputId);
    if (!input) return;

    if (input.type === 'password') {
        input.type = 'text';
        buttonElement.textContent = '🙈 Скрыть';
    } else {
        input.type = 'password';
        buttonElement.textContent = '👁️ Показать';
    }
}

// Подсчёт символов в текстовом поле
function countCharacters(inputId, counterId) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);

    if (!input || !counter) return;

    input.addEventListener('input', function() {
        counter.textContent = this.value.length;
    });
}

// Поиск в таблице
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);

    if (!input || !table) return;

    input.addEventListener('keyup', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    });
}

// Сортировка таблицы
function makeTableSortable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => sortTable(tableId, index));
    });
}

function sortTable(tableId, columnIndex) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        return aValue.localeCompare(bValue);
    });

    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

// Логирование в консоль (для отладки)
function log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
}

// Экспорт функций для использования на страницах
window.MyTasks = {
    formatDate,
    formatTime,
    validateForm,
    submitFormAjax,
    copyToClipboard,
    togglePasswordVisibility,
    countCharacters,
    searchTable,
    makeTableSortable,
    log,
    toggleTask
};