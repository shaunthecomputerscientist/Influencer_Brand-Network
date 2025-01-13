<template>
  <div class="d-flex align-items-center justify-content-center w-100 h-100">
    <p class="spinner-grow text-theme"></p>
  </div>

</template>

<script>
import { useAuthStore } from '../../store/modules/auth'; // Import the auth store from Pinia
import router from '../../router/index';
import {axiosInstance} from '../../services/axiosInstance';

export default {
  async created() {
    const authStore = useAuthStore(); // Initialize the auth store

    try {
      // Get the authorization code from the URL
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');

      if (code) {
        // Send the code to the backend to get the tokens
        const response = await axiosInstance.get(`/auth/login/google/callback?code=${code}`);

        // Extract tokens from the backend response
        const { access_token } = response.data;

        if (access_token) {
          // Store tokens in localStorage
          localStorage.setItem('access_token', access_token);
          // localStorage.setItem('refresh_token', refresh_token);

          // Optionally, fetch user profile
          await authStore.checkUserStatus(); // Call the action from Pinia store

          // Redirect to dashboard
          router.push('/dashboard');
        } else {
          console.error('Failed to receive tokens');
          router.push('/auth/login');
        }
      } else {
        console.error('No authorization code found');
        router.push('/auth/login');
      }
    } catch (error) {
      console.error('Error during OAuth process:', error);
      router.push('/auth/login');
    }
  }
};
</script>
