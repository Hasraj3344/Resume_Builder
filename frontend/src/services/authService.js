import api from './api';

const authService = {
  /**
   * Register a new user
   * @param {Object} userData - { email, password, full_name, phone, address, profile_pic (File), resume (File), parsed_data (Object) }
   * @returns {Promise} Response with user, token, and subscription data
   */
  register: async (userData) => {
    const formData = new FormData();
    formData.append('email', userData.email);
    formData.append('password', userData.password);
    formData.append('full_name', userData.full_name);

    // Optional fields
    if (userData.phone) {
      formData.append('phone', userData.phone);
    }
    if (userData.address) {
      formData.append('address', userData.address);
    }

    // File uploads
    if (userData.profile_pic) {
      formData.append('profile_pic', userData.profile_pic);
    }
    if (userData.resume) {
      formData.append('resume', userData.resume);
    }

    // Parsed resume data as JSON string
    if (userData.parsed_data) {
      formData.append('parsed_data', JSON.stringify(userData.parsed_data));
    }

    const response = await api.post('/api/auth/register', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    // Store token and user in localStorage
    // Backend returns 'access_token', not 'token'
    const token = response.data.access_token || response.data.token;
    if (token) {
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      console.log('[AUTH] Token saved to localStorage after registration');
    }

    return response.data;
  },

  /**
   * Login user
   * @param {Object} credentials - { email, password }
   * @returns {Promise} Response with user and token
   */
  login: async (credentials) => {
    const response = await api.post('/api/auth/login', credentials);

    // Store token and user in localStorage
    // Backend returns 'access_token', not 'token'
    const token = response.data.access_token || response.data.token;
    if (token) {
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      console.log('[AUTH] Token saved to localStorage:', token.substring(0, 20) + '...');
    } else {
      console.error('[AUTH] No token in response:', response.data);
    }

    return response.data;
  },

  /**
   * Logout user (revoke all sessions)
   * @returns {Promise}
   */
  logout: async () => {
    try {
      await api.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear local storage regardless of API response
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
    }
  },

  /**
   * Get current user info
   * @returns {Promise} User data
   */
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated: () => {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('user');
    return !!(token && user);
  },

  /**
   * Get stored user data
   * @returns {Object|null}
   */
  getStoredUser: () => {
    const userString = localStorage.getItem('user');
    if (userString) {
      try {
        return JSON.parse(userString);
      } catch (error) {
        console.error('Error parsing stored user:', error);
        return null;
      }
    }
    return null;
  },
};

export default authService;
