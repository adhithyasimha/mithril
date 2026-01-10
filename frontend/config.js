// Configuration
const CONFIG = {
  API_BASE_URL: 'https://x7c3ncdr0l.execute-api.us-east-1.amazonaws.com/prod/api', // Replace YOUR_API_ID with your actual API ID
  TOKEN_KEY: 'manager_token',
  REFRESH_TOKEN_KEY: 'manager_refresh_token',
  MANAGER_KEY: 'manager_info',
};

// Detect environment and set API base URL
if (typeof process !== 'undefined' && process.env.NODE_ENV === 'production') {
  CONFIG.API_BASE_URL = 'https://x7c3ncdr0l.execute-api.us-east-1.amazonaws.com/prod/api'; 
}
