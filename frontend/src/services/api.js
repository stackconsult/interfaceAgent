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

// Pipelines API
export const pipelinesAPI = {
  list: (params) => api.get('/api/pipelines/', { params }),
  get: (id) => api.get(`/api/pipelines/${id}`),
  create: (data) => api.post('/api/pipelines/', data),
  update: (id, data) => api.put(`/api/pipelines/${id}`, data),
  delete: (id) => api.delete(`/api/pipelines/${id}`),
  addStep: (id, stepData) => api.post(`/api/pipelines/${id}/steps`, stepData),
  execute: (id, inputData) => api.post(`/api/pipelines/${id}/execute`, inputData),
  listExecutions: (id, params) => api.get(`/api/pipelines/${id}/executions`, { params }),
};

// Audit Logs API
export const auditLogsAPI = {
  list: (params) => api.get('/api/audit-logs/', { params }),
  get: (id) => api.get(`/api/audit-logs/${id}`),
  listActions: () => api.get('/api/audit-logs/actions/list'),
  listResourceTypes: () => api.get('/api/audit-logs/resource-types/list'),
};

// Admin API
export const adminAPI = {
  // Users
  listUsers: (params) => api.get('/api/admin/users/', { params }),
  createUser: (userData) => api.post('/api/admin/users/', userData),
  updateUser: (id, userData) => api.put(`/api/admin/users/${id}`, userData),
  assignRole: (userId, roleData) => api.post(`/api/admin/users/${userId}/roles`, roleData),
  
  // Roles
  listRoles: (params) => api.get('/api/admin/roles/', { params }),
  createRole: (roleData) => api.post('/api/admin/roles/', roleData),
  listRolePermissions: (roleId) => api.get(`/api/admin/roles/${roleId}/permissions`),
  addPermission: (roleId, permissionData) => api.post(`/api/admin/roles/${roleId}/permissions`, permissionData),
};

export default api;
