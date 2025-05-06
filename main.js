// Handle flash message dismissal
document.addEventListener('DOMContentLoaded', function() {
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    
    flashMessages.forEach(message => {
        // Auto-dismiss flash messages after 5 seconds
        setTimeout(() => {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
    
    // Password strength indicator for registration
    const passwordField = document.querySelector('#password');
    if (passwordField) {
        passwordField.addEventListener('input', function() {
            checkPasswordStrength(this.value);
        });
    }
    
    function checkPasswordStrength(password) {
        // Get the password field element
        const passwordField = document.querySelector('#password');
        if (!passwordField) return;
        
        // Create strength indicator if it doesn't exist
        let strengthIndicator = document.querySelector('#password-strength');
        if (!strengthIndicator) {
            strengthIndicator = document.createElement('div');
            strengthIndicator.id = 'password-strength';
            strengthIndicator.classList.add('progress', 'mt-2');
            strengthIndicator.innerHTML = '<div class="progress-bar" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>';
            passwordField.parentNode.appendChild(strengthIndicator);
        }
        
        // Get the progress bar
        const progressBar = strengthIndicator.querySelector('.progress-bar');
        
        // Criteria
        const hasLength = password.length >= 6;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSpecialChars = /[!@#$%^&*(),.?":{}|<>]/.test(password);
        
        // Calculate strength
        let strength = 0;
        if (hasLength) strength += 20;
        if (hasUpperCase) strength += 20;
        if (hasLowerCase) strength += 20;
        if (hasNumbers) strength += 20;
        if (hasSpecialChars) strength += 20;
        
        // Update progress bar
        progressBar.style.width = `${strength}%`;
        progressBar.setAttribute('aria-valuenow', strength);
        
        // Update color based on strength
        progressBar.classList.remove('bg-danger', 'bg-warning', 'bg-info', 'bg-success');
        
        if (strength < 40) {
            progressBar.classList.add('bg-danger');
            progressBar.textContent = 'Weak';
        } else if (strength < 60) {
            progressBar.classList.add('bg-warning');
            progressBar.textContent = 'Fair';
        } else if (strength < 80) {
            progressBar.classList.add('bg-info');
            progressBar.textContent = 'Good';
        } else {
            progressBar.classList.add('bg-success');
            progressBar.textContent = 'Strong';
        }
    }
    
    // Confirm password deletion when clicking delete button
    const deleteButtons = document.querySelectorAll('[data-bs-target="#deleteModal"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            document.querySelector('#deleteModal').classList.add('show');
        });
    });
});
