// import axios from 'axios';
import {axiosInstance, getHeaders} from './axiosInstance';


export const fetchdashboardData = async (userId) => {
    return axiosInstance.get(`/user/dashboard${userId}`, { headers: getHeaders() });
};

export function updateData(formData){
    return axiosInstance.put('/user/profile/update', formData, {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'multipart/form-data' // Set the content type for FormData
        }
    });
}

export const fetchUserProfile = async () => {
    try {
        const token = localStorage.getItem('access_token');
        const response = await axiosInstance.get('/user/profile', {
            headers: {
                Authorization: `Bearer ${token}`, // Include the JWT in the Authorization header
            },
        });
        console.log(response);
        return response.data;
    } catch (error) {
        console.error('Error fetching user profile:', error);
        throw error; // Rethrow the error for handling in the calling component
    }
};

export const fetchUserProfileById = async (userId) => {
    try {
        // Retrieve the JWT token from localStorage
        const token = localStorage.getItem('access_token');
        
        // Make the GET request to fetch the user profile using axiosInstance
        const response = await axiosInstance.get(`/user/userProfile/${userId}`, {
            headers: {
                'Authorization': `Bearer ${token}`, // Include the token in the Authorization header
            },
        });
        
        // Log the response (optional, for debugging purposes)
        console.log(response);

        // Return the response data for further handling
        return response.data;

    } catch (error) {
        // Log any errors encountered during the request
        console.error('Error fetching user profile:', error);
        throw error; // Rethrow the error for handling in the calling component
    }
};

// Fetch notifications from the last 30 days for the logged-in user
export const fetchRecentNotifications = async (userId) => {
    return axiosInstance.get(`/user/notification/${userId}`, { headers: getHeaders() });
};

// Mark all unread notifications as read for the logged-in user
export const markNotificationsAsRead = async (notificationIds) => {
    return axiosInstance.put(`/user/notification/read`, { notification_ids: notificationIds }, { headers: getHeaders() });
};