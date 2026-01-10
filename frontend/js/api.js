// API Manager
const API = {
  async request(endpoint, options = {}) {
    const url = `${CONFIG.API_BASE_URL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add auth token if available
    const token = AuthManager.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `API Error: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API Error at ${endpoint}:`, error);
      throw error;
    }
  },

  async register(email, password, firstName = '', lastName = '', agencyName = null) {
    // Use local auth if enabled
    if (typeof LOCAL_AUTH !== 'undefined' && LOCAL_AUTH.USE_LOCAL_AUTH) {
      return LOCAL_AUTH.register(email, password, firstName, lastName, agencyName);
    }

    return this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
        agency_name: agencyName || 'New Agency',
      }),
    });
  },

  async login(email, password) {
    // Use local auth if enabled
    if (typeof LOCAL_AUTH !== 'undefined' && LOCAL_AUTH.USE_LOCAL_AUTH) {
      return LOCAL_AUTH.login(email, password);
    }

    return this.request('/auth/signin', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  async refreshToken() {
    const refreshToken = AuthManager.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await this.request('/auth/refresh_token', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    });

    AuthManager.setToken(response.access_token);
    return response;
  },

  async getDashboard() {
    return this.request('/manager/dashboard', {
      method: 'GET',
    });
  },

  async getCases(filters = {}) {
    const queryString = new URLSearchParams(filters).toString();
    const endpoint = `/manager/cases${queryString ? '?' + queryString : ''}`;
    return this.request(endpoint, {
      method: 'GET',
    });
  },

  async getCase(caseId) {
    return this.request(`/manager/cases/${caseId}`, {
      method: 'GET',
    });
  },

  async logActivity(caseId, activityData) {
    return this.request(`/manager/cases/${caseId}/activity`, {
      method: 'POST',
      body: JSON.stringify(activityData),
    });
  },
};
