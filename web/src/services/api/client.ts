// api/client.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:11434';

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('cleudocode_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      localStorage.removeItem('cleudocode_token');
      localStorage.removeItem('cleudocode_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;