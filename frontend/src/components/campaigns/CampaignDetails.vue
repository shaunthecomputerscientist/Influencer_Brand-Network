<template>
  <div v-if="campaign" class="campaign-detail-container mt-2">
    <!-- Header Section -->
    <div class="header-section d-flex flex-column gap-2 align-items-center justify-content-center">
      <div class="profile-section d-flex flex-column align-items-center">
        <img :src="imageurl" alt="Company Logo" class="profile-pic" style="width: 5rem;" />
      </div>
      <button class="company-name fs-4 fw-bold"><router-link class="nav-link" :to="`/user/user-profile/${campaign.sponsor_id}`">{{ campaign.company_name }}</router-link></button>
      <div v-if="authStore.userProfile.role==='admin'" class="d-flex justify-content-end gap-2">
            <button @click="increaseFlag" class="btn-danger btn flag">+</button>
            <p> {{ flagCount }}</p>
            <button @click="decreaseFlag" class="btn-success btn flag">-</button>
      </div>

    </div>

    <!-- Tabs for switching views -->
    <div class="tab-section d-flex justify-content-around mt-2 p-2 rounded gap-2">
          <button @click="setCurrentView('generalInfo')" :class="{'active-tab': currentView === 'generalInfo'}">
            <i class="fa-solid fa-circle-info"></i>
            <i class="icon-label">General</i>
          </button>
          <button @click="setCurrentView('goals')" :class="{'active-tab': currentView === 'goals'}">
            <i class="fa-duotone fa-solid fa-bullseye"></i>
            <i class="icon-label">Goals</i>
          </button>
          <button @click="setCurrentView('tasks & guidelines')" :class="{'active-tab': currentView === 'tasks & guidelines'}">
            <i class="fa-solid fa-list-check"></i>
            <i class="icon-label">Tasks&Guidelines</i>
          </button>
          <button @click="setCurrentView('tracking')" :class="{'active-tab': currentView === 'tracking'}">
            <i class="fa-solid fa-binoculars"></i>
            <i class="icon-label">Tracking</i>
          </button>
          <button @click="setCurrentView('apply')" 
                  v-if="(authStore.userProfile.role==='influencer' || authStore.userProfile.id===campaign.sponsor_id) && new Date() < new Date(campaign.end_date)" 
                  :class="{'active-tab': currentView === 'apply'}">
            <i class="fa-regular fa-hand"></i>
            <i class="icon-label">{{authStore.userProfile.id===campaign.sponsor_id?'Applicants':'Apply'}}</i>
          </button>
          <button @click="setCurrentView('chat')" 
                  v-if="authStore.userProfile.role==='influencer' || authStore.userProfile.id===campaign.sponsor_id" 
                  :class="{'active-tab': currentView === 'chat'}">
            <i class="fa-solid fa-comment"></i>
            <i class="icon-label">Chat</i>
          </button>
          <button @click="setCurrentView('taskProgress')" 
                  v-if="campaign.status==='active' && (isUserAcceptedInfluencer || authStore.userProfile.id===campaign.sponsor_id)" 
                  :class="{'active-tab': currentView === 'taskProgress'}">
            <i class="fa-solid fa-bars-progress"></i>
            <i class="icon-label">{{authStore.userProfile.id===campaign.sponsor_id?'ApproveTasks':'CompleteTasks'}}</i>
          </button>
          <button @click="setCurrentView('campaignPayment')" 
                  v-if="authStore.userProfile.id===campaign.sponsor_id" 
                  :class="{'active-tab': currentView === 'campaignPayment'}">
            <i class="fa-solid fa-money-bill-transfer"></i>
            <i class="icon-label">Payments</i>
          </button>
          <button @click="setCurrentView('analytics')" 
                  v-if="authStore.userProfile.id===campaign.sponsor_id" 
                  :class="{'active-tab': currentView === 'analytics'}">
            <i class="fa-solid fa-chart-pie"></i>
            <i class="icon-label">Analytics</i>
          </button>
     </div>



    <!-- Conditional rendering based on currentView -->
    <div class="view-section mt-4">
      <GeneralInfo v-if="currentView === 'generalInfo'" :campaign="campaign" />
      <Goals v-if="currentView === 'goals'" :goals="campaign.goals" />
      <TrackingVue @updateCampaignData="handleCampaignData" v-if="currentView === 'tracking'" :trackingData="campaign" />
      <taskaGuidelines v-if="currentView === 'tasks & guidelines'" :tasks="campaign" />
      <campaignChat v-if="currentView==='chat'" :campaign="campaign"/>
      <applyCampaign @updateCampaignData="handleCampaignData" v-if="currentView==='apply'" :campaign="campaign"/>
      <campaignProgress @updateCampaignData="handleCampaignData" v-if="currentView==='taskProgress'" :campaign="campaign"/>
      <campaignPayment  v-if="currentView==='campaignPayment'" @updateCampaignData="handleCampaignData" :campaign="campaign"/>
      <consolidatedData v-if="currentView==='analytics'" :campaign="campaign"/>

    </div>

    <!-- Back Button -->
    <button class="btn-back mt-4" @click="goBack"><i class="fa-solid fa-arrow-left"></i></button>
  </div>

  <div v-else class="d-flex align-items-center justify-content-center w-100 h-100">
    <p class="spinner-grow text-theme"></p>
  </div>
</template>

<script>
import GeneralInfo from './CampaignDetailsComponents/GeneralInfo.vue';
import Goals from './CampaignDetailsComponents/Goals.vue';
import TrackingVue from './CampaignDetailsComponents/TrackingMethods.vue';
import taskaGuidelines from './CampaignDetailsComponents/taska&Guidelines.vue';
import { increaseCampaignFlag, decreaseCampaignFlag } from '../../services/adminService';
import { computed, onMounted, ref } from 'vue';
import { useCampaignsStore } from '../../store';
import { useRoute } from 'vue-router';
import { useAuthStore } from '../../store';
import campaignChat from './CampaignChat/campaignChat.vue';
import applyCampaign from './Apply/applyCampaign.vue';
import campaignProgress from './CampaignAnalytics/campaignProgress.vue';
import campaignPayment from './PaymentDetails/campaignPayment.vue'
import consolidatedData from './CampaignAnalytics/consolidatedData.vue';
import ga4asyncExport from './campaignJobs/ga4asyncExport.vue';

export default {
  name: 'CampaignDetail',
  components: {
    GeneralInfo,
    Goals,
    TrackingVue,
    taskaGuidelines,
    campaignChat,
    applyCampaign,
    campaignProgress,
    campaignPayment,
    consolidatedData,
    ga4asyncExport
  },
  setup() {
    const currentView = ref('generalInfo'); // Default tab
    const authStore = useAuthStore();
    const flagCount = ref(0);

    const setCurrentView = (view) => {
      currentView.value = view;
    };
    


    const formatDateTime = (dateString) => {
      const date = new Date(dateString);
      const month = date.toLocaleString('en-US', { month: 'long' });
      const day = date.getDate();
      return { month, day };
    };

    const route = useRoute();
    const campaign = ref(null);
    const campaignId = route.params.id;
    const campaignStore = useCampaignsStore();

    const isUserAcceptedInfluencer = computed(() => {
    // Check if campaign.influencers is defined and is an array
    if (campaign.value.influencers && Array.isArray(campaign.value.influencers)) {
      return campaign.value.influencers.some(
        influencer => influencer.influencer_id === authStore.userProfile.id && influencer.status === "accepted"
      );
    }
    console.log(campaign.influencers)
    // Return false if influencers is not defined or not an array
    return false;
  });

    const imageurl = computed(() => `${import.meta.env.VITE_APP_BACKEND_URL}/${campaign.value.company_logo}`);

    const goBack = () => {
      window.history.back();
    };

    onMounted(async () => {
      campaign.value = await campaignStore.retrieveCampaignById(campaignId);
      flagCount.value = campaign.value.flagCount

      console.log(campaign)
    });

    const handleCampaignData = (updateCampaignData) => {
      campaign.value=updateCampaignData;
    }

    // Admin features

    const increaseFlag = async () => {
      await increaseCampaignFlag(campaign.value.id, 'Admin finds your activity sus')
      flagCount.value+=1;
    }
    
    const decreaseFlag = async () => {
      await decreaseCampaignFlag(campaign.value.id)
      flagCount.value-=1;
    }




    return {
      currentView,
      setCurrentView,
      imageurl,
      goBack,
      campaign,
      formatDateTime,
      authStore,
      handleCampaignData,
      isUserAcceptedInfluencer,
      increaseFlag,
      decreaseFlag,
      flagCount
    };
  },
};
</script>

<style scoped>
/* Tabs styling */

.btn,.flag{
  box-shadow: 2px 0.1rem 0.2rem rgba(77, 77, 77, 0.433);
  border: 1px solid rgba(197, 188, 145, 0.617);
  background-color: rgba(250, 235, 215, 0.493);
  color: black;
}
.profile-pic{
  border: 1px solid rgba(0, 0, 0, 0);
  border-radius: 12rem;
  /* box-shadow: 1px 1px 1rem rgb(170, 170, 170); */
}
.profile-section{
  padding: 1rem 1rem;
  background-color: #ffeecc;
  border: 1px solid rgba(96, 96, 96, 0.367);
  border-radius: 20rem;
  box-shadow: 2px 1px 0.5rem rgb(76, 76, 76);

}
.company-name{
  color: #ffcb8b;
  background-color: rgba(255, 214, 159, 0.153);
  border: none;
}

.company-name:hover{
  background-color: rgba(224, 176, 103, 0.196);
  padding: 0.45rem;
}

.tab-section{
  background-color: #ff953f1f;
  overflow-wrap: scroll;
  flex-wrap: nowrap;
  overflow: scroll;
}
.tab-section button i{
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0.1rem;
}
.tab-section button .icon-label{
  font-size: 0;
}
.tab-section button{
  font-size: 0;
  max-width: 100%;
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: start;
  text-align: start;
  text-wrap: nowrap;
  max-width: 100%;
  padding: 0.7rem;
}
.tab-section button:hover .icon-label{
  font-size: 0.8rem;
  transition: 700ms cubic-bezier(0.075, 0.82, 0.165, 1);
  text-wrap: wrap;
  /* text-align: center; */
  /* position: relative; */
}
.tab-section button:hover{
  font-size: 0.8rem;
  transition: 700ms cubic-bezier(0.075, 0.82, 0.165, 1);
  text-wrap: wrap;
  /* text-align: center; */
  padding: 0.5rem;
  /* position: relative; */
}

.tab-section .active-tab {
  background-color: #ff895e;
  color: white;
  font-weight: bold;
}

.view-section {
  padding: 1.5rem;
  border-top: 2px solid #eaeaea;
}

/* Back Button */
.btn-back {
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
}
</style>