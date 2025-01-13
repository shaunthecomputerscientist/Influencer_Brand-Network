import { defineStore } from 'pinia';
import { login as authLogin, logout as authLogout, refreshToken as refreshAuthToken } from '../../services/authService';
import { fetchUserProfile as getUserProfile, fetchRecentNotifications, markNotificationsAsRead, fetchdashboardData } from '../../services/userservice';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: JSON.parse(localStorage.getItem('isAuthenticated')) || false,
    userProfile: JSON.parse(localStorage.getItem('userProfile')) || null,
    accessToken: localStorage.getItem('access_token') || null,
    // refreshToken: localStorage.getItem('refresh_token') || null,
    notifications: [],
  }),

  actions: {
    async login(email, password) {
      try {
        const response = await authLogin(email, password);
        const { access_token} = response;

        this.isAuthenticated = true;
        this.accessToken = access_token;
        // this.refreshToken = refresh_token;

        localStorage.setItem('access_token', access_token);
        // localStorage.setItem('refresh_token', refresh_token);
        localStorage.setItem('isAuthenticated', JSON.stringify(true));

        const profile = await getUserProfile();
        console.log(profile)
        this.userProfile = profile.profile;

        // Store profile in localStorage
        localStorage.setItem('userProfile', JSON.stringify(this.userProfile));

        console.log('User Profile', profile.profile);
      } catch (error) {
        console.error('Login failed:', error);
        throw error;
      }
    },

    async logout() {
      try {
        await authLogout();
        this.isAuthenticated = false;
        this.userProfile = null;

        // Clear localStorage
        localStorage.removeItem('access_token');
        // localStorage.removeItem('refresh_token');
        localStorage.removeItem('userProfile');
        localStorage.setItem('isAuthenticated', JSON.stringify(false));
      } catch (error) {
        console.error('Logout failed:', error);
      }
    },

    async refreshAccessToken() {
      try {
        const response = await refreshAuthToken(this.refreshToken);
        this.accessToken = response.access_token;
        localStorage.setItem('access_token', response.access_token);
      } catch (error) {
        console.error('Failed to refresh access token:', error);
        this.logout();
      }
    },

    async checkUserStatus() {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          // Check if the profile is already loaded in the state or localStorage
          if (!this.userProfile) {
            const profile = await getUserProfile();
            this.userProfile = profile.profile;

            // Update profile in localStorage
            localStorage.setItem('userProfile', JSON.stringify(this.userProfile));
          }

          this.isAuthenticated = true;
          this.accessToken = token;
          // this.refreshToken = localStorage.getItem('refresh_token');
        } catch (error) {
          console.error('Failed to fetch user profile:', error);
          this.userProfile = null;
          this.isAuthenticated = false;

          // Clear localStorage if token is invalid
          this.logout();
        }
      } else {
        // If no token is found, log out the user
        this.logout();
      }
    },

    async fetchNotifications(userId) {
      try {
        // Pass the userId to the API request, assuming fetchRecentNotifications accepts userId
        const response = await fetchRecentNotifications(userId);
        
        console.log(response.data);
        this.notifications = response.data;
      } catch (error) {
        console.error('Failed to fetch notifications:', error);
      }
    },
    

    // New Action: Mark all notifications as read
    async markAllNotificationsAsRead() {
      try {
        // Extract unread notification IDs
        const unreadNotificationIds = this.notifications
          .filter(notification => !notification.is_read)
          .map(notification => notification.id);

        if (unreadNotificationIds.length) {
          await markNotificationsAsRead(unreadNotificationIds);

          // Update the local notifications array to mark them as read
          this.notifications = this.notifications.map(notification => ({
            ...notification,
            is_read: unreadNotificationIds.includes(notification.id) ? true : notification.is_read,
          }));
        }
      } catch (error) {
        console.error('Failed to mark notifications as read:', error);
      }
    },
  },

  getters: {
    isUserProfileComplete: (state) => {
      return state.userProfile && state.userProfile.name && state.userProfile.email; // Example condition
    },

    userProfileData: (state) => {
      return state.userProfile;
    },

    isAuthenticatedData: (state) => {
      return state.isAuthenticated;
    },
    unreadNotifications: (state) => {
      return state.notifications.filter(notification => !notification.is_read);
    }
  }
});

export default useAuthStore;