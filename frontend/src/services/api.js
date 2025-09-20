import axios from 'axios';

const API_BASE_URL = "/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    
    if (error.response?.status === 404) {
      console.warn('Resource not found');
    } else if (error.response?.status >= 500) {
      console.error('Server error occurred');
    }
    
    return Promise.reject(error);
  }
);

export const carService = {
  getCars: async (filters = {}) => {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value);
      }
    });
    
    try {
      const response = await api.get(`/cars?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch cars:', error);
      throw new Error('Failed to load car listings');
    }
  },

  getCar: async (id) => {
    try {
      const response = await api.get(`/cars/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch car ${id}:`, error);
      if (error.response?.status === 404) {
        throw new Error('Car not found');
      }
      throw new Error('Failed to load car details');
    }
  },

  getFilterOptions: async () => {
    try {
      const response = await api.get('/cars/filters/options');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch filter options:', error);
      throw new Error('Failed to load filter options');
    }
  }
};

export default api;
