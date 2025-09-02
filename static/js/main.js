/**
 * Accounting System - Main JavaScript File
 * Handles interactive functionality and UI enhancements
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeSidebar();
    initializeAlerts();
    initializeTooltips();
    initializeFormValidation();
    initializeTableEnhancements();
    initializeLoadingStates();
});

/**
 * Sidebar Toggle Functionality
 */
function initializeSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            
            // Save sidebar state to localStorage
            const isCollapsed = sidebar.classList.contains('collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });

        // Restore sidebar state from localStorage
        const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
        if (isCollapsed) {
            sidebar.classList.add('collapsed');
        }

        // Mobile sidebar toggle
        if (window.innerWidth <= 768) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('show');
            });

            // Close sidebar when clicking outside on mobile
            document.addEventListener('click', function(e) {
                if (window.innerWidth <= 768 && 
                    !sidebar.contains(e.target) && 
                    !sidebarToggle.contains(e.target)) {
                    sidebar.classList.remove('show');
                }
            });
        }
    }
}

/**
 * Auto-dismiss alerts after 5 seconds
 */
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach(function(alert) {
        // Add fade-in animation
        alert.classList.add('fade-in');
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            if (alert && alert.parentNode) {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(function() {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 500);
            }
        }, 5000);
    });
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Form Validation and Enhancement
 */
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(function(form) {
        // Add loading state on form submission
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner"></span> Processing...';
                submitBtn.disabled = true;
            }
        });

        // Real-time validation for email fields
        const emailFields = form.querySelectorAll('input[type="email"]');
        emailFields.forEach(function(field) {
            field.addEventListener('blur', function() {
                validateEmail(field);
            });
        });

        // Real-time validation for required fields
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(function(field) {
            field.addEventListener('blur', function() {
                validateRequired(field);
            });
        });

        // Number field validation
        const numberFields = form.querySelectorAll('input[type="number"]');
        numberFields.forEach(function(field) {
            field.addEventListener('input', function() {
                validateNumber(field);
            });
        });
    });
}

/**
 * Validate email format
 */
function validateEmail(field) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const isValid = !field.value || emailRegex.test(field.value);
    
    toggleFieldValidation(field, isValid, 'Please enter a valid email address');
}

/**
 * Validate required fields
 */
function validateRequired(field) {
    const isValid = field.value.trim() !== '';
    toggleFieldValidation(field, isValid, 'This field is required');
}

/**
 * Validate number fields
 */
function validateNumber(field) {
    const value = parseFloat(field.value);
    const min = parseFloat(field.getAttribute('min'));
    const max = parseFloat(field.getAttribute('max'));
    
    let isValid = true;
    let message = '';
    
    if (isNaN(value) && field.value !== '') {
        isValid = false;
        message = 'Please enter a valid number';
    } else if (!isNaN(min) && value < min) {
        isValid = false;
        message = `Value must be at least ${min}`;
    } else if (!isNaN(max) && value > max) {
        isValid = false;
        message = `Value must be no more than ${max}`;
    }
    
    toggleFieldValidation(field, isValid, message);
}

/**
 * Toggle field validation state
 */
function toggleFieldValidation(field, isValid, message) {
    const formGroup = field.closest('.mb-3') || field.parentElement;
    let feedback = formGroup.querySelector('.invalid-feedback');
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        if (feedback) {
            feedback.style.display = 'none';
        }
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            formGroup.appendChild(feedback);
        }
        
        feedback.textContent = message;
        feedback.style.display = 'block';
    }
}

/**
 * Table Enhancements
 */
function initializeTableEnhancements() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(function(table) {
        // Add hover effects
        table.classList.add('table-hover');
        
        // Add search functionality for large tables
        if (table.rows.length > 10) {
            addTableSearch(table);
        }
        
        // Add sorting functionality
        addTableSorting(table);
    });
}

/**
 * Add search functionality to table
 */
function addTableSearch(table) {
    const wrapper = table.closest('.table-responsive') || table.parentElement;
    const searchContainer = document.createElement('div');
    searchContainer.className = 'table-search mb-3';
    
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.className = 'form-control';
    searchInput.placeholder = 'Search table...';
    
    const searchIcon = document.createElement('i');
    searchIcon.className = 'fas fa-search';
    
    searchContainer.appendChild(searchIcon);
    searchContainer.appendChild(searchInput);
    wrapper.insertBefore(searchContainer, table);
    
    searchInput.addEventListener('input', function() {
        filterTable(table, this.value);
    });
}

/**
 * Filter table rows based on search term
 */
function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(function(row) {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

/**
 * Add sorting functionality to table headers
 */
function addTableSorting(table) {
    const headers = table.querySelectorAll('thead th');
    
    headers.forEach(function(header, index) {
        // Skip action columns
        if (header.textContent.toLowerCase().includes('action')) {
            return;
        }
        
        header.style.cursor = 'pointer';
        header.title = 'Click to sort';
        
        header.addEventListener('click', function() {
            sortTable(table, index);
        });
    });
}

/**
 * Sort table by column index
 */
function sortTable(table, columnIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAscending = !table.dataset.sortDirection || table.dataset.sortDirection === 'desc';
    
    rows.sort(function(a, b) {
        const aText = a.cells[columnIndex].textContent.trim();
        const bText = b.cells[columnIndex].textContent.trim();
        
        // Try to sort as numbers first
        const aNum = parseFloat(aText.replace(/[$,]/g, ''));
        const bNum = parseFloat(bText.replace(/[$,]/g, ''));
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return isAscending ? aNum - bNum : bNum - aNum;
        }
        
        // Sort as text
        return isAscending ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    
    // Clear and re-append sorted rows
    tbody.innerHTML = '';
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
    
    // Update sort direction
    table.dataset.sortDirection = isAscending ? 'asc' : 'desc';
    
    // Update header indicators
    const headers = table.querySelectorAll('thead th');
    headers.forEach(function(header) {
        header.classList.remove('sort-asc', 'sort-desc');
    });
    
    headers[columnIndex].classList.add(isAscending ? 'sort-asc' : 'sort-desc');
}

/**
 * Loading States for Buttons and Forms
 */
function initializeLoadingStates() {
    // Add loading state to buttons with data-loading attribute
    const loadingButtons = document.querySelectorAll('[data-loading]');
    
    loadingButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            showButtonLoading(button);
        });
    });
}

/**
 * Show loading state for button
 */
function showButtonLoading(button) {
    const originalText = button.innerHTML;
    button.dataset.originalText = originalText;
    button.innerHTML = '<span class="spinner"></span> Loading...';
    button.disabled = true;
    
    // Auto-restore after 5 seconds if not manually restored
    setTimeout(function() {
        if (button.dataset.originalText) {
            hideButtonLoading(button);
        }
    }, 5000);
}

/**
 * Hide loading state for button
 */
function hideButtonLoading(button) {
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
        button.disabled = false;
        delete button.dataset.originalText;
    }
}

/**
 * Confirm Delete Actions
 */
function confirmDelete(element, message) {
    message = message || 'Are you sure you want to delete this item?';
    return confirm(message);
}

/**
 * Format Currency Display
 */
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

/**
 * Debounce Function for Search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = function() {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Show Toast Notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} toast-notification`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 300px;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(function() {
        toast.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(function() {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

/**
 * Copy to Clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copied to clipboard!', 'success');
    }
}

/**
 * Handle Window Resize
 */
window.addEventListener('resize', function() {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth > 768 && sidebar) {
        sidebar.classList.remove('show');
    }
});

/**
 * Keyboard Shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.table-search input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close mobile sidebar
    if (e.key === 'Escape') {
        const sidebar = document.getElementById('sidebar');
        if (sidebar && window.innerWidth <= 768) {
            sidebar.classList.remove('show');
        }
    }
});

/**
 * Smooth Scrolling for Anchor Links
 */
document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

/**
 * Form Auto-save (for draft functionality)
 */
function initializeAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    
    forms.forEach(function(form) {
        const formId = form.dataset.autosave;
        const inputs = form.querySelectorAll('input, textarea, select');
        
        // Load saved data
        loadFormData(form, formId);
        
        // Save data on input
        inputs.forEach(function(input) {
            input.addEventListener('input', debounce(function() {
                saveFormData(form, formId);
            }, 1000));
        });
        
        // Clear saved data on successful submit
        form.addEventListener('submit', function() {
            clearFormData(formId);
        });
    });
}

function saveFormData(form, formId) {
    const formData = new FormData(form);
    const data = {};
    
    for (let [key, value] of formData.entries()) {
        data[key] = value;
    }
    
    localStorage.setItem(`form_${formId}`, JSON.stringify(data));
    showToast('Draft saved', 'info');
}

function loadFormData(form, formId) {
    const savedData = localStorage.getItem(`form_${formId}`);
    if (savedData) {
        const data = JSON.parse(savedData);
        
        Object.entries(data).forEach(function([key, value]) {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = value;
            }
        });
    }
}

function clearFormData(formId) {
    localStorage.removeItem(`form_${formId}`);
}

// Export functions for global access
window.AccountingSystem = {
    showToast,
    copyToClipboard,
    showButtonLoading,
    hideButtonLoading,
    confirmDelete,
    formatCurrency
};
