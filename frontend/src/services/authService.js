import axios from 'axios';
import { axiosInstance } from './axiosInstance';

// Signup service
// export function signup(additionalData) {
//     // Merge the base data with role-specific additional data
//     const data = {
//       ...additionalData // Spread additional data (influencer/business specific)
//     };
//     console.log(data)
//     return axiosInstance.post('/auth/signup', data);
// }

export function signup(formData) {
  // Directly return the axios POST request with FormData
  console.log(formData); // This will log the FormData object
  return axiosInstance.post('/auth/signup', formData, {
      headers: {
          'Content-Type': 'multipart/form-data' // Set the content type for FormData
      }
  });
}



export const login = async (email, password) => {
  console.log(email, password);
  const response = await axiosInstance.post('/auth/login', {
    email,
    password,
  })
  console.log(response.data)
  return response.data;
};



export const checkUsernameAvailability = async (username) => {
    try {
      const response = await axiosInstance.get(`/auth/check-username/${username}`);
      console.log(`data is ${response.data.available}`)
      return response.data;
    } catch (error) {
      console.error('Error checking username:', error);
      return false;
    }
  };
  
export const checkEmailAvailability = async (email) => {
    try {
      const response = await axiosInstance.get(`/auth/check-email/${email}`);
      console.log(`data is ${response.data.available}`)
      return response.data;
    } catch (error) {
      console.error('Error checking email:', error);
      return false;
    }
  };
  
  export const logout = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('No access token found');
  
      // Add token to the Authorization header
      const response = await axiosInstance.post('/auth/logout',null, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      console.log('Logout successful');
      return response.data;
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  };

export const fetchSignupOptions = async () => {
    try {
      const response = await axiosInstance.get('/auth/signup/options');
      console.log('Signup options:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching signup options:', error);
      throw error;
    }
  };


export  async function generatePhylloSDK(firstname, lastname, platformName) {
    try {
      // Call backend to get SDK token and user ID
      const response = await axiosInstance.post('/auth/getsdktoken', { firstname, lastname, platformName });
      return response.data; // Expecting { user_id, sdk_token } from backend
    } catch (error) {
      throw new Error("Error generating Phyllo SDK token: " + error.message);
    }
  }

  export const refreshToken = async () => {
    try {
      const response = await axiosInstance.post('/auth/refresh'
      //   , {}, {
      //   headers: {
      //     'Authorization': `Bearer ${localStorage.getItem('refresh_token')}`
      //   }
      // }
    
    );
      return response.data;
    } catch (error) {
      console.error('Error refreshing token:', error);
      throw error;
    }
  };