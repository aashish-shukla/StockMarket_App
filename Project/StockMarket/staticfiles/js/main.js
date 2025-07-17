// Main JavaScript file for StockMarket Pro

// CSRF Token setup for AJAX requests
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Update stock price function
function updateStockPrice(symbol) {
    return fetch(`/api/update-stock/${symbol}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return data;
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    });
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format number with commas
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

// Auto-refresh stock prices (if enabled)
let autoRefreshInterval;

function startAutoRefresh(intervalMinutes = 5) {
    stopAutoRefresh(); // Clear any existing interval
    
    autoRefreshInterval = setInterval(() => {
        const stockElements = document.querySelectorAll('[data-symbol]');
        stockElements.forEach(element => {
            const symbol = element.dataset.symbol;
            updateStockPrice(symbol)
                .then(data => {
                    updateStockDisplay(symbol, data);
                })
                .catch(error => {
                    console.error(`Error updating ${symbol}:`, error);
                });
        });
    }, intervalMinutes * 60 * 1000);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Update stock display elements
function updateStockDisplay(symbol, data) {
    const elements = document.querySelectorAll(`[data-symbol="${symbol}"]`);
    
    elements.forEach(element => {
        // Update price
        const priceElement = element.querySelector('.price-display, .stock-price');
        if (priceElement) {
            priceElement.textContent = formatCurrency(data.current_price);
        }
        
        // Update change
        const changeElement = element.querySelector('.price-change');
        if (changeElement) {
            const changeClass = data.price_change >= 0 ? 'text-success' : 'text-danger';
            const changeIcon = data.price_change >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
            const changeSign = data.price_change >= 0 ? '+' : '';
            
            changeElement.innerHTML = `
                <span class="${changeClass}">
                    <i class="fas ${changeIcon}"></i> ${changeSign}${formatCurrency(data.price_change)}
                </span>
            `;
        }
        
        // Update percentage change
        const percentElement = element.querySelector('.price-change-percent');
        if (percentElement) {
            const changeClass = data.price_change_percent >= 0 ? 'text-success' : 'text-danger';
            const changeSign = data.price_change_percent >= 0 ? '+' : '';
            
            percentElement.innerHTML = `
                <span class="${changeClass}">${changeSign}${data.price_change_percent.toFixed(2)}%</span>
            `;
        }
    });
}

// Toast notifications
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                    data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1055';
    document.body.appendChild(container);
    return container;
}

// Confirm dialogs for important actions
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Local storage utilities
const Storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error saving to localStorage:', e);
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Error removing from localStorage:', e);
        }
    }
};

// User preferences
const UserPrefs = {
    getAutoRefresh: () => Storage.get('autoRefresh', false),
    setAutoRefresh: (enabled) => Storage.set('autoRefresh', enabled),
    
    getRefreshInterval: () => Storage.get('refreshInterval', 5),
    setRefreshInterval: (minutes) => Storage.set('refreshInterval', minutes),
    
    getTheme: () => Storage.get('theme', 'light'),
    setTheme: (theme) => Storage.set('theme', theme)
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize auto-refresh if enabled
    if (UserPrefs.getAutoRefresh()) {
        startAutoRefresh(UserPrefs.getRefreshInterval());
    }
    
    // Add loading states to buttons
    const actionButtons = document.querySelectorAll('.btn[onclick], .btn[data-action]');
    actionButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (!this.disabled) {
                this.disabled = true;
                const originalText = this.innerHTML;
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
                
                // Re-enable after 3 seconds as fallback
                setTimeout(() => {
                    this.disabled = false;
                    this.innerHTML = originalText;
                }, 3000);
            }
        });
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal.show');
        if (activeModal) {
            const modal = bootstrap.Modal.getInstance(activeModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Export functions for global use
window.StockMarket = {
    updateStockPrice,
    formatCurrency,
    formatNumber,
    showToast,
    confirmAction,
    startAutoRefresh,
    stopAutoRefresh,
    Storage,
    UserPrefs
};