// Utility functions for validation and formatting

function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function validatePassword(password) {
  const minLength = 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);

  return {
    valid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumber && hasSpecialChar,
    length: password.length >= minLength,
    uppercase: hasUpperCase,
    number: hasNumber,
    special: hasSpecialChar,
    password: password
  };
}

function formatManagerName(email) {
  return email.split('@')[0].charAt(0).toUpperCase() + email.split('@')[0].slice(1);
}

function setLoading(button, isLoading) {
  if (!button) return;

  const loader = button.querySelector('.btn-loader');
  const text = button.querySelector('.btn-text');

  if (isLoading) {
    button.disabled = true;
    if (loader) loader.style.display = 'inline-block';
    if (text) text.style.display = 'none';
  } else {
    button.disabled = false;
    if (loader) loader.style.display = 'none';
    if (text) text.style.display = 'inline';
  }
}

// Show/hide password toggle
function setupPasswordToggle(toggleButtonId, inputFieldId) {
  const toggleBtn = document.getElementById(toggleButtonId);
  const inputField = document.getElementById(inputFieldId);

  if (!toggleBtn || !inputField) return;

  toggleBtn.addEventListener('click', (e) => {
    e.preventDefault();
    const isPassword = inputField.type === 'password';
    inputField.type = isPassword ? 'text' : 'password';
  });
}
