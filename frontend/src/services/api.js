/**
 * API Service for backend communication
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, try to refresh
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken,
          });
          
          const { access_token, refresh_token } = response.data;
          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);
          
          // Retry original request
          error.config.headers.Authorization = `Bearer ${access_token}`;
          return axios(error.config);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  register: (userData) => api.post('/api/auth/register', userData),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// Agents API
export const agentsAPI = {
  list: (params) => api.get('/api/agents/', { params }),
  get: (id) => api.get(`/api/agents/${id}`),
  create: (data) => api.post('/api/agents/', data),
  update: (id, data) => api.put(`/api/agents/${id}`, data),
  delete: (id) => api.delete(`/api/agents/${id}`),
  activate: (id) => api.post(`/api/agents/${id}/activate`),
  deactivate: (id) => api.post(`/api/agents/${id}/deactivate`),
  listAvailable: () => api.get('/api/agents/registry/list'),
};

export default api;
