// static/js/main.js
// Location: C:\private_chat_app\private_chat_app\static\js\main.js

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});

// Form validation
(function() {
    'use strict';
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();

// Password confirmation validation
const passwordInputs = document.querySelectorAll('input[name="password"]');
const confirmInputs = document.querySelectorAll('input[name="password_confirm"]');

if (passwordInputs.length && confirmInputs.length) {
    confirmInputs[0].addEventListener('input', function() {
        if (this.value !== passwordInputs[0].value) {
            this.setCustomValidity('Passwords do not match');
        } else {
            this.setCustomValidity('');
        }
    });
}