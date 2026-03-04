/**
 * Gym Analytics - Main JavaScript
 * Interactive functionality for the gym management system
 */

document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initModals();
    initFormValidation();
    initCharts();
    initAnimations();
    initTooltips();
});

/**
 * Navigation functionality
 */
function initNavigation() {
    const mobileToggle = document.querySelector('.mobile-toggle');
    const navbarLinks = document.querySelector('.navbar-links');
    
    if (mobileToggle) {
        mobileToggle.addEventListener('click', function() {
            navbarLinks.classList.toggle('active');
        });
    }
    
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-links a');
    
    navLinks.forEach(function(link) {
        const linkPath = new URL(link.href).pathname;
        if (currentPath === linkPath || currentPath.startsWith(linkPath)) {
            link.classList.add('active');
        }
    });
    
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.style.background = 'rgba(15, 15, 15, 0.98)';
            } else {
                navbar.style.background = 'rgba(15, 15, 15, 0.95)';
            }
        });
    }
}

/**
 * Modal functionality
 */
function initModals() {
    const modalTriggers = document.querySelectorAll('[data-modal]');
    const modalCloses = document.querySelectorAll('.modal-close');
    
    modalTriggers.forEach(function(trigger) {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const modalId = trigger.dataset.modal;
            const modal = document.getElementById(modalId);
            if (modal) {
                modal.classList.add('active');
                document.body.style.overflow = 'hidden';
            }
        });
    });
    
    modalCloses.forEach(function(close) {
        close.addEventListener('click', function() {
            const modal = close.closest('.modal');
            if (modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
    
    document.querySelectorAll('.modal').forEach(function(modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.active').forEach(function(modal) {
                modal.classList.remove('active');
                document.body.style.overflow = '';
            });
        }
    });
}

/**
 * Form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
            }
        });
        
        const inputs = form.querySelectorAll('.form-control');
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(input);
            });
            
            input.addEventListener('input', function() {
                if (input.classList.contains('error')) {
                    validateField(input);
                }
            });
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('.form-control[required]');
    
    inputs.forEach(function(input) {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

function validateField(input) {
    const value = input.value.trim();
    let isValid = true;
    let errorMessage = '';
    
    if (input.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    }
    
    if (input.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address';
        }
    }
    
    if (input.dataset.minLength && value) {
        const minLength = parseInt(input.dataset.minLength);
        if (value.length < minLength) {
            isValid = false;
            errorMessage = 'Must be at least ' + minLength + ' characters';
        }
    }
    
    if (input.type === 'number' && value) {
        const min = input.getAttribute('min');
        const max = input.getAttribute('max');
        
        if (min && parseFloat(value) < parseFloat(min)) {
            isValid = false;
            errorMessage = 'Minimum value is ' + min;
        }
        
        if (max && parseFloat(value) > parseFloat(max)) {
            isValid = false;
            errorMessage = 'Maximum value is ' + max;
        }
    }
    
    if (isValid) {
        clearFieldError(input);
    } else {
        setFieldError(input, errorMessage);
    }
    
    return isValid;
}

function setFieldError(input, message) {
    input.classList.add('error');
    input.classList.remove('valid');
    
    let errorEl = input.parentElement.querySelector('.error-message');
    if (!errorEl) {
        errorEl = document.createElement('div');
        errorEl.className = 'error-message';
        errorEl.style.color = '#e94560';
        errorEl.style.fontSize = '0.75rem';
        errorEl.style.marginTop = '0.25rem';
        input.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
}

function clearFieldError(input) {
    input.classList.remove('error');
    input.classList.add('valid');
    
    const errorEl = input.parentElement.querySelector('.error-message');
    if (errorEl) {
        errorEl.remove();
    }
}

/**
 * Charts initialization
 */
function initCharts() {
    const workoutChartEl = document.getElementById('workoutChart');
    if (workoutChartEl && typeof Chart !== 'undefined') {
        const ctx = workoutChartEl.getContext('2d');
        const labels = JSON.parse(workoutChartEl.dataset.labels || '[]');
        const data = JSON.parse(workoutChartEl.dataset.data || '[]');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Workouts',
                    data: data,
                    borderColor: '#e94560',
                    backgroundColor: 'rgba(233, 69, 96, 0.1)',
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#e94560',
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: '#e94560'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#a0a0a0'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: '#a0a0a0'
                        }
                    }
                }
            }
        });
    }
    
    const analyticsCharts = document.querySelectorAll('.analytics-chart');
    analyticsCharts.forEach(function(chartEl) {
        if (typeof Chart !== 'undefined') {
            const ctx = chartEl.getContext('2d');
            const chartType = chartEl.dataset.chartType || 'bar';
            const labels = JSON.parse(chartEl.dataset.labels || '[]');
            const data = JSON.parse(chartEl.dataset.data || '[]');
            const label = chartEl.dataset.label || 'Data';
            
            new Chart(ctx, {
                type: chartType,
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: data,
                        backgroundColor: [
                            'rgba(233, 69, 96, 0.7)',
                            'rgba(22, 199, 154, 0.7)',
                            'rgba(255, 193, 7, 0.7)',
                            'rgba(0, 123, 255, 0.7)',
                            'rgba(138, 43, 226, 0.7)'
                        ],
                        borderColor: [
                            '#e94560',
                            '#16c79a',
                            '#ffc107',
                            '#007bff',
                            '#8a2be2'
                        ],
                        borderWidth: 2,
                        fill: chartType === 'line'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#a0a0a0'
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)'
                            },
                            ticks: {
                                color: '#a0a0a0'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.05)'
                            },
                            ticks: {
                                color: '#a0a0a0'
                            }
                        }
                    }
                }
            });
        }
    });
}

/**
 * Animations
 */
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.animate-on-scroll').forEach(function(el) {
        observer.observe(el);
    });
    
    const statNumbers = document.querySelectorAll('.stat-number');
    statNumbers.forEach(function(stat) {
        const target = parseInt(stat.dataset.target);
        if (target) {
            animateCounter(stat, target);
        }
    });
}

function animateCounter(element, target) {
    let current = 0;
    const increment = target / 50;
    const duration = 1000;
    const stepTime = duration / 50;
    
    const timer = setInterval(function() {
        current += increment;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.floor(current);
        }
    }, stepTime);
}

/**
 * Tooltips
 */
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    
    tooltipTriggers.forEach(function(trigger) {
        trigger.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = trigger.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            const rect = trigger.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
            
            trigger._tooltip = tooltip;
        });
        
        trigger.addEventListener('mouseleave', function() {
            if (trigger._tooltip) {
                trigger._tooltip.remove();
                delete trigger._tooltip;
            }
        });
    });
}

/**
 * Utility functions
 */
function showAlert(message, type) {
    if (!type) type = 'info';
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-' + type;
    alertDiv.innerHTML = '<i class="fas fa-' + getAlertIcon(type) + '"></i><span>' + message + '</span>';
    
    const container = document.querySelector('.alert-container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(function() {
        alertDiv.remove();
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        success: 'check-circle',
        danger: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction() {
        const args = arguments;
        const later = function() {
            clearTimeout(timeout);
            func.apply(null, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Search functionality with debounce
const searchInput = document.querySelector('[data-search]');
if (searchInput) {
    searchInput.addEventListener('input', debounce(function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const items = document.querySelectorAll('[data-search-item]');
        
        items.forEach(function(item) {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }, 300));
}

// Toggle password visibility
document.querySelectorAll('.password-toggle').forEach(function(toggle) {
    toggle.addEventListener('click', function() {
        const input = toggle.previousElementSibling;
        if (input.type === 'password') {
            input.type = 'text';
            toggle.classList.remove('fa-eye');
            toggle.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            toggle.classList.remove('fa-eye-slash');
            toggle.classList.add('fa-eye');
        }
    });
});

// Delete confirmation
document.querySelectorAll('[data-delete]').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });
});

// Auto-dismiss alerts
document.querySelectorAll('.alert').forEach(function(alertEl) {
    setTimeout(function() {
        alertEl.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(function() {
            alertEl.remove();
        }, 300);
    }, 5000);
});

// Add slideOut animation
const style = document.createElement('style');
style.textContent = '@keyframes slideOut { to { opacity: 0; transform: translateX(100%); } }';
document.head.appendChild(style);

// Export functions for global use
window.GymAnalytics = {
    showAlert: showAlert,
    formatDate: formatDate,
    formatTime: formatTime,
    formatNumber: formatNumber,
    debounce: debounce
};

