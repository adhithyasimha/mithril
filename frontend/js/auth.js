// Authentication Manager
const AuthManager = {
  getToken() {
    return localStorage.getItem(CONFIG.TOKEN_KEY);
  },

  setToken(token) {
    localStorage.setItem(CONFIG.TOKEN_KEY, token);
  },

  removeToken() {
    localStorage.removeItem(CONFIG.TOKEN_KEY);
  },

  getRefreshToken() {
    return localStorage.getItem(CONFIG.REFRESH_TOKEN_KEY);
  },

  setRefreshToken(token) {
    localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, token);
  },

  removeRefreshToken() {
    localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
  },

  getManager() {
    const manager = localStorage.getItem(CONFIG.MANAGER_KEY);
    return manager ? JSON.parse(manager) : null;
  },

  setManager(manager) {
    localStorage.setItem(CONFIG.MANAGER_KEY, JSON.stringify(manager));
  },

  removeManager() {
    localStorage.removeItem(CONFIG.MANAGER_KEY);
  },

  isLoggedIn() {
    // Check for token OR manager data (local auth doesn't use tokens)
    return !!this.getToken() || !!this.getManager();
  },

  logout() {
    this.removeToken();
    this.removeRefreshToken();
    this.removeManager();
    window.location.href = 'signin.html';
  },

  redirectIfLoggedIn() {
    if (this.isLoggedIn()) {
      // Get the current page name (works with both file:// and http:// protocols)
      const href = window.location.href;
      const isAuthPage = href.includes('signin.html') || href.includes('signup.html');
      
      if (isAuthPage) {
        window.location.href = 'dashboard.html';
      }
    }
  },

  redirectIfNotLoggedIn() {
    if (!this.isLoggedIn()) {
      window.location.href = 'signin.html';
    }
  }
};
