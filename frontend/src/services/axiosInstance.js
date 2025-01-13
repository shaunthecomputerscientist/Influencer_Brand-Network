// src/services/axiosInstance.js

import axios from 'axios';
import { BACKEND_BASE_URL } from './config';
import { useAuthStore } from '../store';


const axiosInstance = axios.create({
  baseURL: BACKEND_BASE_URL || null, // Default to localhost if not set
  timeout: 50000,  // Optional: Set a timeout for requests
  withCredentials: true, // Include credentials in the request
  headers: {
    'Content-Type': 'application/json', // Default content type
  },
});

// Function to get the token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('access_token');
};

// Function to set up headers for each request
const getHeaders = (customContentType = 'application/json') => {
  const headers = {
    'Content-Type': customContentType, // Default to JSON, can be overridden
  };

  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};


// axiosInstance.interceptors.request.use(
//   (config) => {
//     const token = getAuthToken();
//     console.log('axiosinstance')
//     if (token) {
//       config.headers['Authorization'] = `Bearer ${token}`;
//     }
//     return config;
//   },
//   (error) => Promise.reject(error)
// );

axiosInstance.interceptors.response.use(
  (response) => response, // Pass through successful responses
  async (error) => {
    const authStore = useAuthStore();
    const originalRequest = error.config;

    // Initialize retry count if not already set
    if (!originalRequest._retryCount) {
      originalRequest._retryCount = 0;
    }
    console.log('Interceptor', authStore);

    if (
      error.response &&
      error.response.status === 401 &&
      authStore.isAuthenticated // Ensure user is logged in
    ) {
      // Retry if the count is below the limit
      if (originalRequest._retryCount < 10) {
        originalRequest._retryCount++;

        try {
          // Attempt to refresh the access token
          await authStore.refreshAccessToken();

          // Retry the original request with the new token
          originalRequest.headers['Authorization'] = `Bearer ${authStore.accessToken}`;
          return axiosInstance(originalRequest); // Retry request
        } catch (refreshError) {
          console.error("Token refresh failed during retry.");
        }
      }

      // Logout if retries exceeded
      if (originalRequest._retryCount >= 10) {
        console.error("Max retry attempts reached. Redirecting to login.");
        authStore.logout(); // Clear session and redirect
        window.location.href = '/auth/login';
      }
    }

    return Promise.reject(error); // Reject with the original error
  }
);

// Export the Axios instance and the getHeaders function
export { axiosInstance, getHeaders };
