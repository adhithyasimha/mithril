// Signup page functionality with real-time password validation

document.addEventListener('DOMContentLoaded', function () {
  // Redirect if already logged in
  AuthManager.redirectIfLoggedIn();

  const form = document.getElementById('signupForm');
  const submitBtn = document.getElementById('submitBtn');
  const passwordField = document.getElementById('password');
  const confirmPasswordField = document.getElementById('confirmPassword');
  const passwordToggle = document.getElementById('passwordToggle');
  const confirmPasswordToggle = document.getElementById('confirmPasswordToggle');

  // Setup form submission
  if (form) {
    form.addEventListener('submit', handleSignup);
  }

  // Setup password toggles
  if (passwordToggle) {
    setupPasswordToggle('passwordToggle', 'password');
  }
  if (confirmPasswordToggle) {
    setupPasswordToggle('confirmPasswordToggle', 'confirmPassword');
  }

  // Real-time password validation
  if (passwordField) {
    passwordField.addEventListener('input', function () {
      validatePasswordStrength(this.value);
      clearError('password');
    });
  }

  // Confirm password validation
  if (confirmPasswordField) {
    confirmPasswordField.addEventListener('input', function () {
      clearError('confirmPassword');
      if (this.value && passwordField.value && this.value !== passwordField.value) {
        showError('confirmPassword', 'Passwords do not match');
      }
    });
  }

  // Email validation on blur
  const emailField = document.getElementById('email');
  if (emailField) {
    emailField.addEventListener('blur', function () {
      clearError('email');
      if (this.value && !validateEmail(this.value)) {
        showError('email', 'Please enter a valid email address');
      }
    });
  }

  // Clear errors on input
  const inputs = document.querySelectorAll('input');
  inputs.forEach(input => {
    input.addEventListener('input', function () {
      if (this.id !== 'password' && this.id !== 'confirmPassword') {
        clearError(this.name);
      }
    });
  });
});

function validatePasswordStrength(password) {
  const checks = {
    checkLength: document.getElementById('checkLength'),
    checkUpperCase: document.getElementById('checkUpperCase'),
    checkNumber: document.getElementById('checkNumber'),
    checkSpecial: document.getElementById('checkSpecial'),
  };

  const strength = validatePassword(password);

  // Update checks
  updateCheck(checks.checkLength, strength.length);
  updateCheck(checks.checkUpperCase, strength.uppercase);
  updateCheck(checks.checkNumber, strength.number);
  updateCheck(checks.checkSpecial, strength.special);
}

function updateCheck(checkElement, isValid) {
  if (!checkElement) return;

  if (isValid) {
    checkElement.classList.add('done');
    checkElement.textContent = '✓';
  } else {
    checkElement.classList.remove('done');
    checkElement.textContent = '';
  }
}

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

async function handleSignup(e) {
  e.preventDefault();

  hideAlert();
  clearAllErrors();

  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  const firstName = document.getElementById('firstName').value.trim();
  const lastName = document.getElementById('lastName').value.trim();
  const submitBtn = document.getElementById('submitBtn');

  // Validate first name
  if (!firstName) {
    showError('firstName', 'First name is required');
    return;
  }

  // Validate last name
  if (!lastName) {
    showError('lastName', 'Last name is required');
    return;
  }

  // Basic validation
  if (!email) {
    showError('email', 'Email is required');
    return;
  }

  if (!validateEmail(email)) {
    showError('email', 'Please enter a valid email address');
    return;
  }

  if (!password) {
    showError('password', 'Password is required');
    return;
  }

  const passwordValidation = validatePassword(password);
  if (!passwordValidation.valid) {
    showError('password', 'Password must have 8+ chars, uppercase, number, and special character');
    return;
  }

  if (!confirmPassword) {
    showError('confirmPassword', 'Please confirm your password');
    return;
  }

  if (password !== confirmPassword) {
    showError('confirmPassword', 'Passwords do not match');
    return;
  }

  setLoading(submitBtn, true);

  try {
    const response = await API.register(email, password, firstName, lastName, 'New Agency');

    // Store tokens
    AuthManager.setToken(response.access_token);
    AuthManager.setRefreshToken(response.refresh_token);

    // Store manager info
    const managerInfo = {
      id: response.manager_id,
      email: email,
      name: response.manager_name || `${firstName} ${lastName}`,
      agency_id: response.agency_id,
      tier: response.tier || 'small',
    };
    AuthManager.setManager(managerInfo);

    showAlert('Account created successfully! Redirecting to dashboard...', 'success');

    // Redirect after a short delay
    setTimeout(() => {
      window.location.href = 'dashboard.html';
    }, 1500);
  } catch (error) {
    console.error('Signup error:', error);
    const errorMessage = error.message || 'Registration failed. Please try again.';
    showAlert(errorMessage, 'error');
  } finally {
    setLoading(submitBtn, false);
  }
}

function clearAllErrors() {
  const errorElements = document.querySelectorAll('.input-error.show');
  errorElements.forEach(el => {
    el.classList.remove('show');
    el.textContent = '';
  });

  const fields = document.querySelectorAll('input');
  fields.forEach(el => {
    el.style.borderColor = '';
  });
}
