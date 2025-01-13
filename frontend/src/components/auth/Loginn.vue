<template>
  <section class="login-section mt-3 p-3">
    <header class="d-flex justify-content-center">
      <h2 style="text-decoration: underline;">Sign In</h2>
    </header>
    <div class="d-flex">
      <ErrorPopup/>
    </div>
    <form @submit.prevent="handleLogin" class="border border-3 d-flex flex-column gap-2 dark p-3 mt-3 fw-bold rounded">
      <label for="email">Email:</label>
      <input type="email" class="rounded form-control" id="email" v-model="email" placeholder="Email" required />
  
      <label for="password">Password:</label>
      <div class="password-container">
        <input
          :type="showpassword ? 'text' : 'password'"
          class="rounded form-control"
          id="password"
          v-model="password"
          placeholder="Password"
          required
        />
        <i
          class="fa"
          :class="showpassword ? 'fa-eye-slash' : 'fa-eye'"
          @click="toggleShowPassword"
        ></i>
      </div>
      
      <div>
        <button type="submit" class="rounded mt-2">
          Login
          <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        </button>
      </div>
      <div class="d-flex justify-content-between mt-3 w-100 flex-wrap gap-2">
        <button type="button" class="rounded border" @click="loginWithGoogle">Sign In <i class="fa-brands fa-google" style="color: white;"></i></button>
        <button type="button" class="rounded border" @click="forgotpassword">Forgot Passw?</button>
      </div>
    </form>
  </section>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { useAuthStore } from '../../store/index'; // Import the useAuthStore
import router from '../../router/index';
import ErrorPopup from '../utilities/ErrorPopup.vue';

export default {
  components: { ErrorPopup },
  setup() {
    const email = ref('');
    const password = ref('');
    const authStore = useAuthStore(); // Get the auth store instance
    const isLoading = ref(false)
    const showpassword = ref(false);

    const handleLogin = async () => {
      try {
        // Use the auth store action for login
        isLoading.value = true;
        await authStore.login(email.value, password.value);
        
        if (authStore.isAuthenticated) {
          router.push('/dashboard'); // Navigate to dashboard on success
        }
      } catch (error) {
        isLoading.value=false;
        console.error('Login failed err:', error.response?.data || error.message);
        const errorEvent = new CustomEvent('show-error-popup', {
          detail: { message: error.response?.data?.message || 'Login failed, please try again' }
        });
        window.dispatchEvent(errorEvent); 
      }
    };

    // watch(email, (newValue, oldValue) => {
    //   email.value = newValue.toUpperCase();
    // });

    const loginWithGoogle = () => {
      window.location.href = `https://accounts.google.com/o/oauth2/auth?client_id=${import.meta.env.VITE_APP_CLIENT_ID}&redirect_uri=${import.meta.env.VITE_APP_FRONTEND_URL}/auth/google/callback&response_type=code&scope=email%20profile`;
    };

    const forgotpassword = () => {
      router.push('/auth/forgot-password');
    };

    const toggleShowPassword = () => {
      showpassword.value = !showpassword.value;
    }

    return {
      email,
      password,
      handleLogin,
      loginWithGoogle,
      forgotpassword,
      isLoading,
      showpassword,
      toggleShowPassword,
    };
  }
};
</script>

<style scoped>
.password-container {
  position: relative;
}
.login-section{
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
form{
  width: 20rem;
}

.password-container input {
  padding-right: 35px; /* Space for the eye icon */
}

.password-container .fa {
  position: absolute;
  top: 50%;
  right: 10px;
  transform: translateY(-50%);
  cursor: pointer;
  font-size: 1.2em;
  color: #6c757d;
}

.password-container .fa:hover {
  color: #000;
}
</style>
