<template>
    <div class="resetpassword d-flex w-100 align-items-center justify-content-center">
        <div class="d-flex align-items-center justify-content-center flex-column border p-5 rounded-5 theme-background">
        <span class="w-100"><i @click="goBack" class="fa fa-arrow-left ms-0 mb-2 btn-theme"></i></span>
        <h2>Reset Password</h2>
        <form @submit.prevent="handleResetPassword">
            <div class="mb-3">
                <label for="password" class="form-label">New Password:</label>
                <input type="password" v-model="password" class="form-control" id="password" required />
            </div>
            <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirm Password:</label>
                <input type="password" v-model="confirmPassword" class="form-control" id="confirmPassword" required />
            </div>
            <button type="submit">Reset Password</button>
        </form>
    </div>
    </div>
</template>

<script>
import { ref } from 'vue';
import {axiosInstance} from '../services/axiosInstance';
import router from '../router/index'
import { goBack } from '../main';

export default {
    name:'ResetPassword',
    setup() {
        const password = ref('');
        const confirmPassword = ref('');

        const handleResetPassword = async () => {
            if (password.value !== confirmPassword.value) {
                alert('Passwords do not match.');
                return;
            }

            const token = router.query.token; // Get the token from the URL
            try {
                await axiosInstance.post('/auth/reset-password', { token, password: password.value });
                alert('Your password has been reset successfully. Redirecting to login...');
                router.push('/login')
            } catch (error) {
                alert('Error: ' + error.response.data.message);
            }
        };

        return {
            password,
            confirmPassword,
            handleResetPassword,
            goBack
        };
    }
};
</script>
<style scoped>
.resetpassword{
    margin-top: 20%;
}
</style>