<template>
  <div class="influencer-card p-3 mb-3 d-flex flex-column align-items-start justify-content-around">
    <div class="d-flex align-items-center justify-content-around p-2 w-100">
      <div class="d-flex align-items-center justify-content-start gap-2 p-2 w-100">
        <img style="width: 3rem; height: 3rem; border: 1px solid black; border-radius: 5rem;" :src="imageUrl" :alt="influencerData.name">
        <router-link :to="`/user/user-profile/${influencerData.id}`" class="fw-bold" style="font-size: medium;">
          <button>{{ influencerData.name }}</button>
        </router-link>
      </div>
      <div v-if="authStore.userProfile.role==='brand'" class="mb-2">
        <button @click="toggleRequestForm"><i class="fa fa-envelope text-white fs-4"></i></button>
      </div>
      <!-- Admin flagging buttons -->
    </div>

    <div class="d-flex flex-column gap-3">
      <div class="d-flex flex-column gap-2">
        <button class="fw-bold w-100" style="font-size: medium;">{{ influencerData.location }}</button>

        <!-- Loop through each platform in socialData -->
        <div v-for="(data, platform) in influencerData.socialData" :key="platform" class="d-flex flex-wrap justify-content-start gap-2 fw-bold" style="font-size: medium;">
          <div class="w-100 d-flex justify-content-around gap-2">
            <button class="platform"><i :class="['fa-brands','border', 'fa-'+ platform]"></i></button>
            <button class="followers">{{ data.socialData.statistics?.followers || data.socialData.followers }}</button>
            <Tooltip text='followers' :triggerClass="'followers'" />
            <button class="engagement-rate">{{data.socialData.statistics?.engagement ||  Math.round(data.socialData.engagement * 100) / 100}}%</button>
            <Tooltip text='Engagement Rate' :triggerClass="'engagement-rate'"/>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="send-request hide-scrollbar" v-if="showRequestForm">
    <div class="w-100 d-flex justify-content-end fs-4">
      <i @click="toggleRequestForm" class="fa fa-times btn btn-danger" aria-hidden="true"></i>
    </div>
    <p class="alert alert-warning fw-bold" v-if="brandcampaigns.length==0">Create campaigns and ask influencers to join. Only inactive campaigns can be joined by influencers.</p>
    <div v-else>
      <div v-for="campaign in brandcampaigns" class="d-flex justify-content-around w-100">
        <p class="alert alert-warning mt-2 fw-bold">{{ campaign.name }}<i v-if="!sentRequests.includes(campaign.id)" @click="sendRequestToInfluencer(campaign.id, influencerData.id)" class="fa fa-paper-plane text-white p-2 fs-4 ms-2 btn btn-warning"></i></p>
      </div>
    </div>
  </div>
</template>

  
<script>
import { ref, computed, onMounted } from 'vue';
import router from '../../router';
import { useAuthStore } from '../../store';
import { useCampaignsStore } from '../../store';
import { increaseInfluencerFlag, decreaseInfluencerFlag } from '../../services/adminService';
import Tooltip from '../utilities/Tooltip.vue';

export default {
  name: 'InfluencerCard',
  props: {
    influencerData: Object,
    userRole: String,
    currentUserId: Number
  },
  components: {
    Tooltip
  },
  setup(props) {
    const isExpanded = ref(false);
    const authStore = useAuthStore();
    const campaignsStore = useCampaignsStore();
    const showRequestForm = ref(false);
    const sentRequests = ref([]);

    console.log(props.influencerData)

    const brandcampaigns = computed(() => {
      return campaignsStore.inactiveBCampaigns(authStore.userProfile.id);
    });

    const toggleView = () => {
      isExpanded.value = !isExpanded.value;
    };

    const toggleRequestForm = () => {
      showRequestForm.value = !showRequestForm.value;
    };

    const sendRequestToInfluencer = async (campaignID, influencerID) => {
      try {
        // Attempt to send the campaign request
        await campaignsStore.sendCampaignRequestToInfluencer(campaignID, influencerID);
        sentRequests.value.push(campaignID); // Add to sent requests if successful
      } catch (error) {
        // If an error occurs (e.g., request already sent within 2 days), show the popup
        const errorMessage = error.response?.data?.message || "An error occurred.";
        window.dispatchEvent(new CustomEvent('show-error-popup', { detail: { message: errorMessage } }));
      }
    };

    const imageUrl = computed(() => {
      return `${import.meta.env.VITE_APP_BACKEND_URL}/${props.influencerData.profile_image}`;
    });

    onMounted(async () => {
      await campaignsStore.loadCampaigns(authStore.userProfile.id);
    });

    return {
      isExpanded,
      toggleView,
      imageUrl,
      authStore,
      campaignsStore,
      toggleRequestForm,
      showRequestForm,
      brandcampaigns,
      sendRequestToInfluencer,
      sentRequests,
    };
  }
};
</script>
  
  <style scoped>
  .influencer-card {
    background-color: #ffecd4dd;
    box-shadow: 4px 1px 0.5rem rgb(158, 158, 158);
    font-size: small;
    border: 1px solid rgba(255, 255, 255, 0);
    border-radius: 6rem 1rem 2rem 2rem;
  }
  
  .btn-info {
    background-color: rgb(14, 189, 209);
    padding: 0.5rem 1rem;
  }
  
  .btn-info:hover {
    background-color: rgb(14, 212, 234) !important;
    padding: 0.5rem 1rem !important;
  }
  
  .tooltipp {
    position: relative;
    display: inline-block;
  }
  
  .tooltiptext {
    visibility: hidden;
    color: #050505;
    width: 10rem;
    text-align: center;
    display: flex;
    border-radius: 5px;
    padding: 5px 5px;
    position: absolute;
    z-index: 4;
    bottom: 10%;
    left: 50%;
    margin-left: -100px;
    opacity: 0;
    transition: opacity 0.3s;
  }
  
  .tooltipp:hover .tooltiptext {
    visibility: visible;
    opacity: 1;
  }

  button{
    box-shadow: 5px 2px 0.5rem rgba(45, 45, 45, 0.65);
  }
  button:hover{
    box-shadow: none;
    transition: 0.1s;
  }
  .send-request{
    position: absolute;
    border: 2px solid rgba(159, 159, 159, 0.667);
    border-radius: 1rem;
    margin: 6% 0%;
    height: 10rem;
    overflow: scroll;
    background-color: antiquewhite;
    box-shadow: 1px 1px 1rem rgb(98, 98, 98);
    text-wrap: wrap;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: center;
    padding: 1rem;

  }

  </style>
  