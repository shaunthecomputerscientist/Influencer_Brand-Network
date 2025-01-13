<template>
    <div :class="[campaign.isBlocked?'alert alert-secondary rounded-5':'campaign-card btn-theme p-3 mb-3 d-flex flex-column align-items-start justify-content-around']">
      <div class="d-flex align-items-center justify-content-around p-2 w-100">
        <div class="d-flex align-items-center justify-content-start gap-2 p-2 w-100">
        <img style="width: 2rem; border: 2px solid black; border-radius: 1rem;" :src="imageurl" :alt="imageurl">
        <h4 class="">{{ campaign.company_name }}</h4>
        </div>
        <div class="tooltipp">
            <p class="mt-3">
            {{ campaign.status === "active" ? "🟢" : "🔴" }}
            </p>
            <span :class="['tooltiptext d-flex align-items-center justify-content-center alert', campaign.status==='inactive' ? 'alert-danger' : 'alert-success']" style="margin-left: -5rem; width: 5rem;">
            {{ campaign.status === "active" ? "active" : "inactive" }}
            </span>
        </div>

      </div>
      
      <div class="d-flex flex-column gap-3 text-light">
            <div class="d-flex flex-column">
            <p class="btn btn-theme2 fw-bold text-center" style="font-size: large;">{{ truncatedNames }}</p>
            <p class="btn btn-theme2 fw-bold text-start d-flex justify-content-start gap-5" style="font-size: medium;"> <i class="fa-solid fa-money-check-dollar fs-2"></i> {{ campaign.budget }}</p>
            <p class="btn btn-theme2 fw-bold text-start" style="font-size: medium;"><i class="fa-sharp-duotone fa-solid fa-pen fs-3"></i> {{ truncateddescription }}</p>
            <div v-if="isExpanded" class="d-flex btn btn-theme2 justify-content-around">
            <p class="fw-bold" style="font-size: medium;"><i class="fa-solid fa-hourglass-start fs-6"></i> {{ formattedStartDate }}</p>
            <p class="fw-bold ms-2 me-2">-</p>
            <p class="fw-bold" style="font-size: medium;">{{ formattedEndDate }} <i class="fa-solid fa-hourglass-end fs-6"></i> </p>
            </div>
            
            </div>

            <div class="campaign-actions d-flex flex-row justify-content-between">
            <button @click="goToDetails" class="btn btn-theme"><i class="fa-solid fa-angle-right"></i></button>

            <button v-if="userRole === 'brand' && campaign.sponsor_id === currentUserId" :disabled="campaign.status==='active'" @click="deleteCampaign" class="btn-danger fs-6 text-nowrap"><i class="fa-solid fa-trash"></i></button>
            <button v-if="userRole === 'brand' && campaign.sponsor_id === currentUserId" @click="editCampaign" :disabled="new Date() > new Date(campaign.end_date) || campaign.status==='active'" class="btn-warning mx-2 fs-6 text-nowrap"><i class="fa-solid fa-pen-to-square"></i></button>
            </div>
            <div  v-if="userRole === 'brand'"  class="d-flex justify-content-center align-items-center tooltipp">
              <button v-if="userRole === 'brand' && campaign.sponsor_id === currentUserId && campaign.status==='inactive'" @click="startCampaign" class="mx-2 text-nowrap" :disabled="campaign.acceptedInfluencers === 0 || new Date() > new Date(campaign.end_date) || campaign.isBlocked">Start Campaign <i class="fa fa-hourglass-start"></i> <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span></button>
              <div v-if=" !(campaign.status==='active') && (campaign.acceptedInfluencers===0 || campaign.isBlocked)" class="tooltiptext fw-bold alert alert-warning d-flex flex-column gap-2">
                <div>
                  <span v-if="campaign.acceptedInfluencers===0">Can not start campaign with no influencers participation or if end date is crossed.</span>
                  <span class="text-danger" v-if="campaign.isBlocked">Your campaign is blocked by admin. Contact customer support.</span>
                </div>
              </div>               
              <button v-if="userRole === 'brand' && campaign.sponsor_id === currentUserId && campaign.status==='active'" @click="endCampaign" class="mx-2 text-nowrap">End/Pause Campaign <i class="fa fa-hourglass-end"></i> <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span></button>
            </div>
            <!-- <p class="text-dark">
              {{ campaign.isBlocked }} {{ campaign.flagCount }}
            </p> -->

      </div>
  
      
    </div>
  </template>
  
  <script>
  import { ref, computed } from 'vue';
  import router from '../../router';
  
export default {
    name: 'CampaignCard',
    props: {
      campaign: Object,
      userRole: String,
      currentUserId: Number
    },
    setup(props, { emit }) {
      const isExpanded = ref(false);
      const isLoading = ref(false);
  
      const toggleView = () => {
        isExpanded.value = !isExpanded.value;
      };
  
      const editCampaign = () => {
        emit('edit', props.campaign);
      };
  
      const deleteCampaign = () => {
        emit('delete', props.campaign);
      };

      const startCampaign = () =>{
        isLoading.value=true
        emit('startCampaign', props.campaign);
        isLoading.value=false
      }
      const endCampaign = () =>{
        isLoading.value=true
        emit('endCampaign', props.campaign);
        isLoading.value=false
      }
  
      const truncatedNames = computed(() => {
        return props.campaign.name.length > 20
          ? props.campaign.name.slice(0, 20) + '...'
          : props.campaign.name;
      });

      const truncateddescription = computed(() => {
        return props.campaign.description.length > 20
          ? props.campaign.description.slice(0, 20) + '...'
          : props.campaign.description;
      });
  
      // Computed class based on visibility
      const visibilityClass = computed(() => {
        return props.campaign.visibility === 'public' ? 'btn btn-success ' : 'btn btn-danger';
      });



      const formatDateTime = (dateString) => {
      const date = new Date(dateString);
      // Example of formatting: 'October 10, 2024'
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    };

    const formattedStartDate = computed(() => formatDateTime(props.campaign.start_date));
    const formattedEndDate = computed(() => formatDateTime(props.campaign.end_date));
    const imageurl= computed(()=>{
      return `${import.meta.env.VITE_APP_BACKEND_URL}/${props.campaign.company_logo}`
    })
    const goToDetails = () => {
        router.push({ name: 'CampaignDetails', params: { id: props.campaign.id }})
    }


  
      return {
        isExpanded,
        toggleView,
        editCampaign,
        deleteCampaign,
        truncatedNames,
        visibilityClass,
        formattedStartDate,
        formattedEndDate,
        imageurl,
        truncateddescription,
        goToDetails,
        startCampaign,
        endCampaign,
        isLoading
      };
    }
  };
  </script>
  
  <style scoped>
.tooltipp {
  position: relative; /* Positioning context for the tooltip */
  display: inline-block; /* Keeps the tooltip next to the status indicator */

}

.campaign-card{
  background-color: #ffd5a465;
  box-shadow: 10px 5px 1rem rgb(141, 141, 141);
  font-size: small;
  border: 1px solid rgba(255, 255, 255, 0);
  border-radius: 5rem 1rem 2rem 2rem;
}
.btn-info{
  background-color: rgb(14, 189, 209);
  padding: 0.5rem 1rem;

}
.btn-info:hover{
  background-color: rgb(14, 212, 234) !important;
  padding: 0.5rem 1rem !important;

}
.tooltiptext {
  visibility: hidden; /* Hidden by default */
  color: #050505;
  width: 12rem;
  text-align: center;
  display: flex;
  text-wrap: wrap;
  border-radius: 5px;
  padding: 5px 5px;
  position: absolute;
  z-index: 4;
  bottom: 10%; /* Position above the indicator */
  left: 50%;
  margin-left: -100px; /* Center the tooltip */
  opacity: 0; /* Start as invisible */
  transition: opacity 0.3s; /* Smooth transition */
}

.tooltipp:hover .tooltiptext {
  visibility: visible; /* Show the tooltip on hover */
  opacity: 1; /* Make it visible */
}
.btn{
  color: rgb(57, 6, 23);
  background-color: #ffffff86;
}
.btn:hover{
  color: rgb(255, 142, 49);
  background-color: #ffd06b00;
}
</style>