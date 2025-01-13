<template>
  <div class="dashboard-container d-flex h-100">
    <aside class="h-100 d-flex align-items-center justify-content-center navigation">
      <div  v-if="togglenavigation" class="sidebar d-flex flex-column align-items-center  justify-content-start w-100 border h-50 gap-3 mb-5 rounded-5">


        <button :class="[currentView==='dashboard'?'active-tab':'']" @click="changeCurrentView('dashboard')"><i class="fa-solid fa-table-columns"></i></button>
        
        <button :class="{'active-tab' : currentView==='campaigns'}" @click="changeCurrentView('campaigns')">
          <div class="d-flex align-items-center justify-content-center">
            <i class="fw-bold fs-6 d-inline">Camp-</i><i class="fa-solid fa-rectangle-ad mt-1"></i>
          </div>
          </button>
        <button :class="{'active-tab' : currentView==='influencers'}" @click="changeCurrentView('influencers')"><i class="fa-solid fa-people-arrows"></i></button>
        <button :class="{'active-tab' : currentView==='profile'}" @click="changeCurrentView('profile')"><i class="fa fa-user"></i></button>
        <button @click="logout"><i class="fa-solid fa-right-from-bracket"></i></button>
      </div>
      <div class="togglenavigation">
        <div @click="togglenavbutton" v-if="!togglenavigation" class="openClose">
          <i class="fa-solid fa-angles-right"></i> 
        </div>

        <div @click="togglenavbutton" v-if="togglenavigation" class="openClose">
          <i class="fa-solid fa-angles-left"></i> 
        </div>

      </div>
    </aside>

    <main class="main-content">
      

      <!-- Conditionally render components based on the currentView value -->
      <div v-if="currentView ==='dashboard'">
        <div class="dashboard p-2 d-flex gap-2 justify-content-around alert alert-warning">
          <p :class="currentComponent==='notification'?'active-tab2':'btn-warning'" @click="changeCurrentComponent('notification')"><i class="fa fa-bell"></i></p>
          <p :class="currentComponent==='info'?'active-tab2':'btn-warning'" @click="changeCurrentComponent('info')"><i class="fa fa-circle-info"></i></p>
        </div>
        
        <div class="notification" v-if="currentComponent=='notification'">
          <Notification/>
        </div>
        <div v-if="currentComponent=='info'">
          <h1>{{ dashboardMessage }}</h1>
          <!-- <p>{{ authStore.userProfile }}</p> -->
          <div v-if="authStore.userProfile.role==='brand'">
          </div>
        </div>
      </div>
      <Profile v-if="currentView === 'profile'" />
      <Campaign v-if="currentView === 'campaigns'" />
      <Influencers  v-if="currentView === 'influencers'" />

    </main>
  </div>
</template>


<script>
import { ref, onMounted, computed } from 'vue';
import {axiosInstance} from '../services/axiosInstance';
import { useAuthStore } from '../store';
import { useRouter } from 'vue-router';
import Campaign from '../components/campaigns/Campaign.vue';
import Profile from '../components/user/Profile.vue';
import { isTokenExpired } from '../main';
import Influencers from '../components/Influencers/influencers.vue';
import Notification from '../components/Notification/Notification.vue';
// import ga4asyncExport from '../components/campaigns/campaignJobs/ga4asyncExport.vue';
import Ga4asyncExport from '../components/campaigns/campaignJobs/ga4asyncExport.vue';

export default {
  name: 'Dashboard',
  components: {
    Profile,
    Campaign,
    Influencers,
    Notification,
    Ga4asyncExport
  },
  setup() {
    const dashboardMessage = ref('');
    const authStore = useAuthStore();
    const router = useRouter();
    const currentView = ref(localStorage.getItem('currentView') || 'dashboard');  // Default view is 'profile'
    const currentComponent = ref('info')
    const isMobile = ref(false);
    const togglenavigation = ref(false) // true indicates open


    const checkScreenSize = () => {
      isMobile.value = window.innerWidth <= 768; // Adjust the breakpoint as needed
    };

    // Computed property to determine if the user is a brand
    const isBrand = computed(() => {
      return authStore.userProfile && authStore.userProfile.role === 'brand';
    });

    const changeCurrentView = (view) => {
      localStorage.setItem('currentView',view)
      currentView.value = view;
    }

    const changeCurrentComponent = (view) => {
      currentComponent.value = view;
    }

    const logout = async () => {
      await authStore.logout(); // Call Pinia action to logout
      router.push('/auth/login');
    };
    
    const togglenavbutton = () => {
      togglenavigation.value = !togglenavigation.value
    }


    onMounted(() => {
      checkScreenSize();
      window.addEventListener('resize', checkScreenSize);
      // Cleanup event listener on component unmount
      return () => {
        window.removeEventListener('resize', checkScreenSize);
      };
    });

    onMounted(async () => {
      try {
        const accessToken = authStore.accessToken;
        if (accessToken && isTokenExpired(accessToken)) {
          await authStore.refreshAccessToken(); // Call Pinia action to refresh token
        }

        if (!accessToken) {
          throw new Error('No access token available');
        }

        const response = await axiosInstance.get(`/user/dashboard/${authStore.userProfile.id}`, {
          headers: {
            Authorization: `Bearer ${authStore.accessToken}`,
          },
        });

        dashboardMessage.value = response.data.dashboard;
      } catch (error) {
        console.error('Error fetching dashboard:', error.response?.data || error.message);
        router.push('/auth/login');
      }
    });

    return {
      dashboardMessage,
      isBrand,
      currentView,
      isMobile,
      changeCurrentView,
      logout,
      togglenavigation,
      togglenavbutton,
      currentComponent,
      changeCurrentComponent,
      authStore   
    };
  },
};
</script>

<style scoped>
.dashboard-container {
  display: flex;
}


.dashboard-container button{
  border: 2px solid #fff4e1;
  border-radius: 0px;
  padding: 1rem;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  width: 5rem;
}
.dashboard-container button:hover{
  width: 5.3rem !important;
  height: 3.5rem !important;
  margin-left: 1rem !important;

}

.sidebar {
  width:  8rem !important; /* Adjust the width as needed */
  overflow: scroll;
  background-color: #fff4c1; /* Sidebar background color */
  padding: 1rem;
  box-shadow: 1px 1px 1rem rgb(129, 129, 129);
  z-index: 3;

}
.sidebar:hover{
  z-index: 3;
}

.active-tab{
  margin-left: 2rem !important;
  
}

.main-content {
  flex-grow: 1; /* Allow main content to take remaining space */
  padding: 2rem;
  width: 100%;
}
.navigation{
  position: absolute;
}
.togglenavigation{
  background-color: rgba(247, 246, 246, 0);
  font-size: large;
  border: 1px solid rgba(0, 0, 0, 0);
  text-align: center;
  display: flex;
  justify-content: center;
  align-items: center;
}
.togglenavigation .openClose{
  height: 3rem;
  text-align: start;
  padding: 1rem !important;
  display: flex;
  border-right: 1px solid rgb(190, 190, 190);
  border-radius: 2rem;
  margin-left: -12px;
  margin-top: -2rem;
  background-color: #fff4c1;
  color: white;
  text-shadow: 0.1px 0.1px 0.1rem rgb(139, 139, 139);
  z-index: 3;
}
.togglenavigation .openClose:hover{
  text-shadow: 0.1px 0.1px 0.1rem rgb(61, 61, 61);
  box-shadow: 2px 0.1px 0.1rem rgb(129, 129, 129);
  color: rgb(255, 192, 137);

}
.notification{
 background-color: #fff3bd57;
 border: 1px solid rgba(240, 230, 140, 0.173);
 border-radius: 1rem;
 padding: 1rem;
}

.btn-warning{
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: 0px 0px 0.2rem rgb(136, 136, 136);
  font-size: large;
  width: 3rem;
  background-color: #ffd99c;
}

.btn-warning i{
  color: rgb(255, 164, 103);
}

.btn-warning:hover{
  padding: 1rem;
  background-color: #ffe8af;
  border-radius: 0.5rem;
  box-shadow: none;
}

.active-tab2{
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: large;
  width: 3rem;
  font-size: larger !important;
  background-color: rgb(255, 179, 86);
  color: rgb(255, 218, 125);
}

.dashboard p{
  margin-top: 1rem;
}
</style>