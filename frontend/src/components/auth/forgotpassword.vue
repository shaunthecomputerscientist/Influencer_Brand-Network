<template>
    <div class="d-flex justify-content-center align-items-center p-5">
      <div class="border p-3 rounded-2 shadow-lg">
        <h2 class="text-center mb-4 text-decoration-underline">Forgot Password</h2>
        <div v-if=" !!errormsg & toggleshow">
              <p class="d-flex gap-2 justify-content-between text-danger alert alert-warning">{{ errormsg }} <p @click="toggleshow=!toggleshow"><i class="fa fa-x text-danger fw-bold btn btn-light"></i></p></p>
        </div>
        <form @submit.prevent="handleForgotPassword">
          <div class="bg-white p-5 rounded">
            <div class="mb-3">
              <label for="email" class="form-label">Email:</label>
              <input
                type="email"
                v-model="email"
                class="form-control"
                id="email"
                required
              />
            </div>
            <button type="submit" class="w-100">Send Reset Link <i v-if="isLoading" class="spinner-border spinner-border-sm"></i></button>
          </div>
        </form>
      </div>
    </div>
  </template>

<script>
import { ref } from 'vue';
import {axiosInstance} from '../../services/axiosInstance';

export default {
    setup() {
        const email = ref('');
        const errormsg = ref(null);
        const isLoading = ref(false);
        const toggleshow = ref(false);


        const handleForgotPassword = async () => {
            try {
                isLoading.value=true;
                await axiosInstance.post('/auth/forgot-password', { email: email.value });
                alert('Check your email for a password reset link.');
                isLoading.value=false;
            } catch (error) {
                isLoading.value=false;
                toggleshow.value=true;
                errormsg.value = error
                console.log(error)
                // alert('Error: ' + error.response.data.message);
            }
        };

        return {
            email,
            handleForgotPassword,
            errormsg,
            isLoading,
            toggleshow
        };
    }
};
</script>
