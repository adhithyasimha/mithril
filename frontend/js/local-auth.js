// Local Dummy Authentication System
// This is a temporary local auth system for testing without AWS Lambda

const LOCAL_AUTH = {
  USE_LOCAL_AUTH: true, // Set to false to use real API
  
  // Initialize with dummy users
  init() {
    if (!localStorage.getItem('local_users')) {
      const dummyUsers = [
        {
          manager_id: 1,
          email: 'john@example.com',
          password: 'TestPass123!',
          first_name: 'John',
          last_name: 'Doe',
          manager_name: 'John Doe',
          agency_id: 1,
          tier: 'small',
          status: 'active'
        },
        {
          manager_id: 2,
          email: 'jane@example.com',
          password: 'TestPass123!',
          first_name: 'Jane',
          last_name: 'Smith',
          manager_name: 'Jane Smith',
          agency_id: 1,
          tier: 'mid',
          status: 'active'
        },
        {
          manager_id: 3,
          email: 'bob@example.com',
          password: 'TestPass123!',
          first_name: 'Bob',
          last_name: 'Johnson',
          manager_name: 'Bob Johnson',
          agency_id: 2,
          tier: 'large',
          status: 'active'
        }
      ];
      localStorage.setItem('local_users', JSON.stringify(dummyUsers));
    }
  },

  // Register new user locally
  async register(email, password, first_name, last_name, agency_name) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    const users = JSON.parse(localStorage.getItem('local_users') || '[]');
    
    // Check if email exists
    if (users.find(u => u.email === email)) {
      throw new Error('Email already registered');
    }

    // Create new user
    const newUser = {
      manager_id: Math.max(...users.map(u => u.manager_id), 0) + 1,
      email: email,
      password: password, // In real app, this would be hashed
      first_name: first_name,
      last_name: last_name,
      manager_name: `${first_name} ${last_name}`,
      agency_id: Math.max(...users.map(u => u.agency_id), 0) + 1,
      tier: 'small', // Default tier
      status: 'active'
    };

    users.push(newUser);
    localStorage.setItem('local_users', JSON.stringify(users));

    return {
      success: true,
      manager_id: newUser.manager_id,
      manager_name: newUser.manager_name,
      email: newUser.email,
      agency_id: newUser.agency_id,
      tier: newUser.tier
    };
  },

  // Login user locally
  async login(email, password) {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    const users = JSON.parse(localStorage.getItem('local_users') || '[]');
    const user = users.find(u => u.email === email);

    if (!user) {
      throw new Error('Invalid email or password');
    }

    if (user.password !== password) {
      throw new Error('Invalid email or password');
    }

    return {
      success: true,
      manager_id: user.manager_id,
      manager_name: user.manager_name,
      email: user.email,
      agency_id: user.agency_id,
      tier: user.tier
    };
  },

  // Get all dummy users
  getAllUsers() {
    return JSON.parse(localStorage.getItem('local_users') || '[]');
  },

  // Clear and reset to dummy users
  reset() {
    const dummyUsers = [
      {
        manager_id: 1,
        email: 'john@example.com',
        password: 'TestPass123!',
        first_name: 'John',
        last_name: 'Doe',
        manager_name: 'John Doe',
        agency_id: 1,
        tier: 'small',
        status: 'active'
      },
      {
        manager_id: 2,
        email: 'jane@example.com',
        password: 'TestPass123!',
        first_name: 'Jane',
        last_name: 'Smith',
        manager_name: 'Jane Smith',
        agency_id: 1,
        tier: 'mid',
        status: 'active'
      },
      {
        manager_id: 3,
        email: 'bob@example.com',
        password: 'TestPass123!',
        first_name: 'Bob',
        last_name: 'Johnson',
        manager_name: 'Bob Johnson',
        agency_id: 2,
        tier: 'large',
        status: 'active'
      }
    ];
    localStorage.setItem('local_users', JSON.stringify(dummyUsers));
    console.log('Local auth reset to dummy users');
  }
};

// Initialize on page load
LOCAL_AUTH.init();
