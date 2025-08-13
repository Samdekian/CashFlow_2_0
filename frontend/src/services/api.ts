import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TIMEOUT = 30000; // 30 seconds

// API Response Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: string;
}

export interface PaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Error Types
export interface ApiError {
  detail: string;
  status_code: number;
  timestamp?: string;
}

// Create axios instance with default configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError<ApiError>) => {
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        case 403:
          // Forbidden - show access denied message
          console.error('Access denied:', data?.detail);
          break;
        case 404:
          // Not found - show resource not found message
          console.error('Resource not found:', data?.detail);
          break;
        case 422:
          // Validation error - show validation message
          console.error('Validation error:', data?.detail);
          break;
        case 500:
          // Internal server error - show generic error
          console.error('Server error:', data?.detail);
          break;
        default:
          console.error(`HTTP ${status}:`, data?.detail);
      }
    } else if (error.request) {
      // Network error
      console.error('Network error: No response received');
    } else {
      // Other error
      console.error('Request error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// Generic API methods
export const api = {
  // GET request
  get: async <T>(url: string, params?: any): Promise<T> => {
    const response = await apiClient.get(url, { params });
    return response.data;
  },

  // POST request
  post: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.post(url, data);
    return response.data;
  },

  // PUT request
  put: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.put(url, data);
    return response.data;
  },

  // DELETE request
  delete: async <T>(url: string): Promise<T> => {
    const response = await apiClient.delete(url);
    return response.data;
  },

  // PATCH request
  patch: async <T>(url: string, data?: any): Promise<T> => {
    const response = await apiClient.patch(url, data);
    return response.data;
  },
};

// Health check
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    await api.get('/health');
    return true;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};

// Export the client for direct use if needed
export default apiClient;
