/**
 * Municipal Complaint Management System (MCMS)
 * Main JavaScript File - Vanilla JS
 * Government-grade client-side functionality
 */

// ===== Document Ready =====
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeForms();
    initializeCaptcha();
    initializeDepartmentCategories();
    initializeConfirmDialogs();
    initializeFileUpload();
});

// ===== Form Validation =====
function initializeForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showAlert('Please fill all required fields correctly.', 'error');
            }
        });
    });
}

function validateForm(form) {
    let isValid = true;
    const requiredInputs = form.querySelectorAll('[required]');
    
    requiredInputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = '#dc3545';
        } else {
            input.style.borderColor = '#dee2e6';
        }
    });
    
    return isValid;
}

// ===== CAPTCHA Functions =====
function initializeCaptcha() {
    const refreshBtn = document.getElementById('refresh-captcha');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshCaptcha);
    }
    
    // Also allow clicking on captcha image to refresh
    const captchaImg = document.getElementById('captcha-image');
    if (captchaImg) {
        captchaImg.addEventListener('click', refreshCaptcha);
        captchaImg.style.cursor = 'pointer';
    }
}

function refreshCaptcha() {
    fetch('/accounts/refresh-captcha/')
        .then(response => response.json())
        .then(data => {
            const captchaImg = document.getElementById('captcha-image');
            if (captchaImg && data.captcha_image) {
                captchaImg.src = data.captcha_image + '?t=' + new Date().getTime();
            }
        })
        .catch(error => {
            console.error('Error refreshing CAPTCHA:', error);
        });
}

// ===== Department & Category Dynamic Loading =====
function initializeDepartmentCategories() {
    const deptSelect = document.getElementById('id_department');
    const catSelect = document.getElementById('id_category');
    
    if (deptSelect && catSelect) {
        deptSelect.addEventListener('change', function() {
            const departmentId = this.value;
            
            if (departmentId) {
                loadCategories(departmentId, catSelect);
            } else {
                catSelect.innerHTML = '<option value="">-- Select Category (Optional) --</option>';
                catSelect.disabled = true;
            }
        });
    }
}

function loadCategories(departmentId, categorySelect) {
    // Show loading state
    categorySelect.disabled = true;
    categorySelect.innerHTML = '<option value="">Loading...</option>';
    
    fetch(`/complaints/ajax/load-categories/?department_id=${departmentId}`)
        .then(response => response.json())
        .then(data => {
            categorySelect.innerHTML = '<option value="">-- Select Category (Optional) --</option>';
            
            if (data.categories && data.categories.length > 0) {
                data.categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category.id;
                    option.textContent = category.name;
                    categorySelect.appendChild(option);
                });
                categorySelect.disabled = false;
            } else {
                categorySelect.innerHTML = '<option value="">No categories available</option>';
            }
        })
        .catch(error => {
            console.error('Error loading categories:', error);
            categorySelect.innerHTML = '<option value="">Error loading categories</option>';
        });
}

// ===== File Upload Validation =====
function initializeFileUpload() {
    const fileInput = document.getElementById('id_proof_file');
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            validateFileUpload(this);
        });
    }
}

function validateFileUpload(input) {
    const file = input.files[0];
    
    if (!file) return;
    
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf'];
    
    // Check file size
    if (file.size > maxSize) {
        showAlert('File size cannot exceed 5MB.', 'error');
        input.value = '';
        return false;
    }
    
    // Check file type
    if (!allowedTypes.includes(file.type)) {
        showAlert('Only JPG, PNG, and PDF files are allowed.', 'error');
        input.value = '';
        return false;
    }
    
    // Show file name
    const fileName = file.name;
    const fileInfo = document.getElementById('file-info');
    if (fileInfo) {
        fileInfo.textContent = `Selected: ${fileName}`;
        fileInfo.style.color = '#28a745';
    }
    
    return true;
}

// ===== Confirm Dialogs =====
function initializeConfirmDialogs() {
    const confirmBtns = document.querySelectorAll('[data-confirm]');
    
    confirmBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
}

// ===== Alert Messages =====
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.main-content .container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.style.opacity = '0';
            setTimeout(() => alertDiv.remove(), 300);
        }, 5000);
    }
}

// ===== Search/Filter Functions =====
function filterTable() {
    const searchInput = document.getElementById('search-input');
    const statusFilter = document.getElementById('status-filter');
    const table = document.getElementById('data-table');
    
    if (!table) return;
    
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    const statusValue = statusFilter ? statusFilter.value : '';
    
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const status = row.getAttribute('data-status') || '';
        
        const matchesSearch = text.includes(searchTerm);
        const matchesStatus = !statusValue || status === statusValue;
        
        if (matchesSearch && matchesStatus) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// ===== Print Function =====
function printPage() {
    window.print();
}

// ===== OTP Timer =====
function startOTPTimer(duration) {
    const timerElement = document.getElementById('otp-timer');
    if (!timerElement) return;
    
    let timeLeft = duration;
    
    const timer = setInterval(function() {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        
        timerElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        if (timeLeft <= 0) {
            clearInterval(timer);
            timerElement.textContent = 'OTP Expired';
            timerElement.style.color = '#dc3545';
        }
        
        timeLeft--;
    }, 1000);
}

// ===== Status Color Coding =====
function updateStatusColors() {
    const statusBadges = document.querySelectorAll('.status-badge');
    
    statusBadges.forEach(badge => {
        const status = badge.textContent.trim().toLowerCase();
        
        switch(status) {
            case 'submitted':
                badge.style.backgroundColor = '#e3f2fd';
                badge.style.color = '#1976d2';
                break;
            case 'under review':
                badge.style.backgroundColor = '#fff3e0';
                badge.style.color = '#f57c00';
                break;
            case 'in progress':
                badge.style.backgroundColor = '#e1f5fe';
                badge.style.color = '#0288d1';
                break;
            case 'resolved':
                badge.style.backgroundColor = '#e8f5e9';
                badge.style.color = '#388e3c';
                break;
            case 'closed':
                badge.style.backgroundColor = '#f3e5f5';
                badge.style.color = '#7b1fa2';
                break;
        }
    });
}

// Auto-dismiss Django messages
setTimeout(function() {
    const messages = document.querySelectorAll('.alert');
    messages.forEach(msg => {
        msg.style.transition = 'opacity 0.5s';
        msg.style.opacity = '0';
        setTimeout(() => msg.remove(), 500);
    });
}, 5000);
