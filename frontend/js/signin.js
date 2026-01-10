// Signin page functionality

document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('signinForm');
  const submitBtn = document.getElementById('submitBtn');
  const emailField = document.getElementById('email');
  const passwordField = document.getElementById('password');
  const passwordToggle = document.getElementById('passwordToggle');

  // Setup form submission
  if (form) {
    form.addEventListener('submit', handleSignin);
  }

  // Setup password toggle
  if (passwordToggle) {
    setupPasswordToggle('passwordToggle', 'password');
  }

  // Email validation on blur
  if (emailField) {
    emailField.addEventListener('blur', function () {
      clearError('email');
      if (this.value && !validateEmail(this.value)) {
        showError('email', 'Please enter a valid email');
      }
    });
  }

  // Clear errors on input
  const inputs = document.querySelectorAll('input');
  inputs.forEach(input => {
    input.addEventListener('input', function () {
      clearError(this.name);
    });
  });

  // Enter key submits form
  if (passwordField) {
    passwordField.addEventListener('keypress', function (e) {
      if (e.key === 'Enter') {
        form.dispatchEvent(new Event('submit'));
      }
    });
  }
});

function showError(fieldName, message) {
  const errorEl = document.getElementById(`${fieldName}Error`);
  const fieldEl = document.getElementById(fieldName);

  if (errorEl) {
    errorEl.textContent = message;
    errorEl.classList.add('show');
  }

  if (fieldEl) {
    fieldEl.style.borderColor = '#EB0000';
  }
}

function clearError(fieldName) {
  const errorEl = document.getElementById(`${fieldName}Error`);
  const fieldEl = document.getElementById(fieldName);

  if (errorEl) {
    errorEl.classList.remove('show');
    errorEl.textContent = '';
  }

  if (fieldEl) {
    fieldEl.style.borderColor = '';
  }
}

function showAlert(message, type = 'error') {
  const alertEl = document.getElementById('errorAlert');
  const messageEl = document.getElementById('errorMessage');

  if (!alertEl || !messageEl) return;

  messageEl.textContent = message;
  
  if (type === 'error') {
    alertEl.classList.add('alert-error');
    alertEl.classList.remove('alert-success');
  } else {
    alertEl.classList.add('alert-success');
    alertEl.classList.remove('alert-error');
  }

  alertEl.style.display = 'block';

  // Auto-hide success message
  if (type === 'success') {
    setTimeout(() => {
      alertEl.style.display = 'none';
    }, 3000);
  }
}

function hideAlert() {
  const alertEl = document.getElementById('errorAlert');
  if (alertEl) {
    alertEl.style.display = 'none';
  }
}

async function handleSignin(e) {
  e.preventDefault();

  hideAlert();
  clearError('email');
  clearError('password');

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const submitBtn = document.getElementById('submitBtn');

  // Validation
  if (!email) {
    showError('email', 'Email is required');
    return;
  }

  if (!password) {
    showError('password', 'Password is required');
    return;
  }

  if (!validateEmail(email)) {
    showError('email', 'Invalid email address');
    return;
  }

  if (password.length < 6) {
    showError('password', 'Password must be at least 6 characters');
    return;
  }

  setLoading(submitBtn, true);

  try {
    const response = await API.login(email, password);

    // Store tokens (local auth doesn't use tokens, but we store them anyway)
    if (response.access_token) {
      AuthManager.setToken(response.access_token);
    }
    if (response.refresh_token) {
      AuthManager.setRefreshToken(response.refresh_token);
    }

    // Store manager info
    const managerInfo = {
      id: response.manager_id,
      email: response.email,
      name: response.manager_name,
      agency_id: response.agency_id,
      tier: response.tier,
    };
    AuthManager.setManager(managerInfo);

    showAlert('Login successful! Redirecting...', 'success');

    // Redirect after a short delay
    setTimeout(() => {
      window.location.href = 'dashboard.html';
    }, 1500);
  } catch (error) {
    console.error('Login error:', error);
    const errorMessage = error.message || 'Invalid email or password';
    showAlert(errorMessage, 'error');
  } finally {
    setLoading(submitBtn, false);
  }
}
