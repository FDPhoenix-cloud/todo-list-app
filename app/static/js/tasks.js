/**
 * Tasks Module - Специфичный функционал для работы с задачами
 */

// ========== ФИЛЬТРАЦИЯ И ПОИСК ==========

/**
 * Поиск задач в реальном времени
 */
function initializeTaskSearch() {
    const searchInput = document.querySelector('#task-search');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        const rows = document.querySelectorAll('table tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            const taskTitle = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
            const taskDescription = row.getAttribute('data-description')?.toLowerCase() || '';
            
            if (taskTitle.includes(query) || taskDescription.includes(query)) {
                row.style.display = '';
                visibleCount++;
            } else {
                row.style.display = 'none';
            }
        });
        
        // Показать сообщение если нет результатов
        const tbody = document.querySelector('table tbody');
        if (visibleCount === 0 && tbody.children.length > 0) {
            const emptyRow = tbody.querySelector('.no-results');
            if (!emptyRow) {
                const row = document.createElement('tr');
                row.className = 'no-results';
                row.innerHTML = `
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="fas fa-search fa-2x mb-2"></i>
                        <p>Задач не найдено по запросу "${query}"</p>
                    </td>
                `;
                tbody.appendChild(row);
            }
        } else {
            const emptyRow = tbody.querySelector('.no-results');
            if (emptyRow) emptyRow.remove();
        }
    });
}

/**
 * Фильтрация по статусу
 */
function initializeStatusFilter() {
    const filterButtons = document.querySelectorAll('[data-filter]');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filter = this.getAttribute('data-filter');
            const rows = document.querySelectorAll('table tbody tr');
            
            rows.forEach(row => {
                const isCompleted = row.classList.contains('completed-task');
                
                if (filter === 'all') {
                    row.style.display = '';
                } else if (filter === 'completed' && isCompleted) {
                    row.style.display = '';
                } else if (filter === 'active' && !isCompleted) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

/**
 * Сортировка таблицы по клику на заголовок
 */
function initializeTableSort() {
    const headers = document.querySelectorAll('table th[data-sortable]');
    
    headers.forEach((header, index) => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            sortTable(index);
        });
    });
}

function sortTable(columnIndex) {
    const table = document.querySelector('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAsc = table.getAttribute('data-sort-dir') === 'asc';
    
    rows.sort((a, b) => {
        const cellA = a.children[columnIndex].textContent.trim();
        const cellB = b.children[columnIndex].textContent.trim();
        
        // Попытайся распарсить как числа
        const numA = parseFloat(cellA);
        const numB = parseFloat(cellB);
        
        if (!isNaN(numA) && !isNaN(numB)) {
            return isAsc ? numB - numA : numA - numB;
        }
        
        return isAsc ? cellB.localeCompare(cellA) : cellA.localeCompare(cellB);
    });
    
    rows.forEach(row => tbody.appendChild(row));
    table.setAttribute('data-sort-dir', isAsc ? 'desc' : 'asc');
}

// ========== ФОРМА СОЗДАНИЯ ЗАДАЧИ ==========

/**
 * Валидация формы в реальном времени
 */
function initializeFormValidation() {
    const form = document.querySelector('form[data-task-form]');
    if (!form) return;
    
    const titleInput = form.querySelector('[name="title"]');
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (titleInput) {
        titleInput.addEventListener('input', function() {
            submitButton.disabled = this.value.trim().length < 3;
        });
    }
}

/**
 * Автосохранение черновика формы
 */
function initializeFormAutosave() {
    const form = document.querySelector('form[data-task-form]');
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('change', function() {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            localStorage.setItem('task_draft', JSON.stringify(data));
        });
    });
    
    // Восстанови черновик при загрузке
    window.addEventListener('DOMContentLoaded', function() {
        const draft = localStorage.getItem('task_draft');
        if (draft && form.querySelector('[name="title"]').value === '') {
            const data = JSON.parse(draft);
            Object.entries(data).forEach(([key, value]) => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) input.value = value;
            });
            showNotification('📝 Черновик восстановлен', 'info');
        }
    });
    
    // Очисти черновик при отправке
    form.addEventListener('submit', function() {
        localStorage.removeItem('task_draft');
    });
}

// ========== МОДАЛЬНЫЕ ОКНА ==========

/**
 * Инициализация модальных окон
 */
function initializeModals() {
    // Закрытие модального окна по нажатию на фон
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                bootstrap.Modal.getInstance(this)?.hide();
            }
        });
    });
}

// ========== БЫСТРЫЕ ДЕЙСТВИЯ ==========

/**
 * Быстрое добавление задачи из навигации
 */
function initializeQuickAddTask() {
    const quickAddBtn = document.querySelector('[data-quick-add-task]');
    if (!quickAddBtn) return;
    
    quickAddBtn.addEventListener('click', function() {
        const title = prompt('Введи название новой задачи:');
        if (title && title.trim().length > 0) {
            // Отправь AJAX запрос
            fetch('/tasks/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'title': title.trim(),
                    'csrf_token': document.querySelector('[name="csrf_token"]')?.value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('✅ Задача создана!', 'success');
                    location.reload();
                }
            });
        }
    });
}

/**
 * Пакетные операции с задачами
 */
function initializeBatchOperations() {
    const selectAllCheckbox = document.querySelector('[data-select-all]');
    if (!selectAllCheckbox) return;
    
    selectAllCheckbox.addEventListener('change', function() {
        document.querySelectorAll('input[data-task-checkbox]').forEach(checkbox => {
            checkbox.checked = this.checked;
        });
    });
}

// ========== ИНИЦИАЛИЗАЦИЯ ==========

document.addEventListener('DOMContentLoaded', function() {
    initializeTaskSearch();
    initializeStatusFilter();
    initializeTableSort();
    initializeFormValidation();
    initializeFormAutosave();
    initializeModals();
    initializeQuickAddTask();
    initializeBatchOperations();
    
    console.log('✅ Tasks module initialized');
});
