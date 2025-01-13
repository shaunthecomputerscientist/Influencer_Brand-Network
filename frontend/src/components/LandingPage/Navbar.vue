<template>
  <nav class="navbar theme-background">
    <div class="container-fluid ">
      <router-link v-if="applicationName" class="navbar-brand" to="/">{{applicationName}}</router-link>
      <button class="navbar-toggler" type="button" @click="toggleCollapse">
        <span class="navbar-toggler-icon fs-6"></span>
      </button>
      <div class="collapse navbar-collapse" :class="{ show: isCollapsed }" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link" to="/auth/signup" @click="closeCollapse"><button class="w-100">Signup</button></router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link w-100" to="/" @click="closeCollapse"><button class="w-100"><i class="fas fa-home"></i> Home</button></router-link>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <router-link class="nav-link" to="/auth/login" @click="closeCollapse"><button class="w-100">Login</button></router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <router-link class="nav-link" to="/user/profile" @click="closeCollapse"><button class="w-100"><i class="fas fa-user"></i> Profile</button></router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <router-link class="nav-link" to="/dashboard" @click="closeCollapse"><button class="w-100"><i class="fas fa-table"></i> Dashboard</button></router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/subscription/plans" @click="closeCollapse"><button class="w-100"><i class="fas fa-solid fa-coins me-2"></i>Services & Subscription</button></router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/" @click="closeCollapse"><button class="w-100"><i class="fa fa-phone" aria-hidden="true"></i>
              Contact Us</button></router-link>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <a class="nav-link" @click="logout"><button class="w-100"> <i class="fa-solid fa-right-from-bracket p-1"></i></button></a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed, onMounted, ref } from 'vue';
import { useAuthStore } from '../../store';
import { useRouter } from 'vue-router';
import { appName } from '../../main';
import { isTokenExpired } from '../../main';

export default {
  name: 'Navbar',
  setup() {
    const authStore = useAuthStore(); // Access Pinia store
    const router = useRouter();
    const isCollapsed = ref(false);
    const isAuthenticated = computed(() => authStore.isAuthenticated);
    const applicationName = ref('appname')

    onMounted(async () => {
      const token = authStore.accessToken;
      // await authStore.checkUserStatus();
      if (token && isTokenExpired(token)) {
        await authStore.refreshAccessToken(); // Call Pinia action to refresh token
      }
      if (isAuthenticated.value){
          authStore.checkUserStatus();
      }
    });

    onMounted(()=>{
      applicationName.value=appName;
    })

    const logout = async () => {
      await authStore.logout(); // Call Pinia action to logout
      router.push('/auth/login');
    };

    const toggleCollapse = () => {
      isCollapsed.value = !isCollapsed.value;
    };

    const closeCollapse = () => {
      isCollapsed.value = false;
    };

    return {
      isAuthenticated,
      logout,
      isCollapsed,
      toggleCollapse,
      closeCollapse,
      applicationName
    };
  },
};
</script>

<style scoped>
button {
  background-color: rgba(175, 151, 110, 0.256); /* Make sure the navbar's background is solid */
  border: 2px solid rgba(255, 210, 170, 0);
}

button:hover {
  background-color: rgba(255, 173, 73, 0.414);
  border: 2px solid rgb(255, 219, 227);
}
</style>
