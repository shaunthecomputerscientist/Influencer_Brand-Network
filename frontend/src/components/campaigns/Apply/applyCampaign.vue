<template>

<section>
    <!--common fields-->
    <div class="d-flex gap-2 btn-primary align-items-center justify-content-center flex-wrap text-wrap fw-bold">
      <div class="d-flex hide-scrollbar gap-1"  style="overflow: auto;">
        <p class="btn btn-info alert alert-secondary text-nowrap">Total Applicants : <span class="text-success">{{ campaign.appliedInfluencers }}</span></p>
        <p class="btn btn-info alert alert-secondary text-nowrap">Current Participants: <span class="text-success">{{ campaign.acceptedInfluencers }}</span></p>
        <p class="btn btn-info alert alert-secondary text-nowrap">Rejected Requests: <span class="text-success">{{ rejectedInfluencers.length }}</span></p>
      </div>
       
    </div>
    <!--Influencer fields-->
    <div v-if="authStore && authStore.userProfile.role==='influencer'" class="d-flex flex-column gap-2 justify-content-center">
        <!-- <p>{{ filteredInfluencer }}</p> -->
         <!-- <div v-if="!filteredInfluencer">
            <button @click="applyToCampaign" :disabled="applyButtonState === 'inactive'">{{ applyButtonLabel }}</button>
         </div> -->
         <div class="d-flex w-100 justify-content-end">
          <button @click="togglePolicies" class="btn-warning">{{showPolicy?'Hide policies...':'See polices...'}}</button>
         </div>
         <div v-if="showPolicy">
          <campaignPolicies/>
         </div>

        <div v-if="(!filteredInfluencer || filteredInfluencer.status==='pending' || filteredInfluencer.status==='null' ||  filteredInfluencer.status===null)">
          <!-- <p>{{ campaign.acceptedInfluencers }}{{ campaign }}</p> -->
            <button @click="applyToCampaign" :disabled="filteredInfluencer.status === 'pending' || applyButtonState === 'inactive' || applied || campaign.acceptedInfluencers>=campaign.influencersPerCampaign">{{ applyButtonLabel }}</button>
        </div>
        
        <div v-else-if="filteredInfluencer.status==='accepted'">
            <div class="alert alert-success">
                Congratulations your request is now accepted.
            </div>
        </div>
        <div v-else-if="filteredInfluencer.status==='rejected'" class="fw-bold">
            <div class="alert alert-danger">
                Sorry your request was rejected! Don't lose hope, apply to other campaigns.
            </div>
            <div v-if="filteredInfluencer.influencer_feedback" class="alert alert-info">
                <p>Here is a little feedback from our sponsor : {{ filteredInfluencer.influencer_feedback }}</p>
            </div>
        </div>
    </div>
    <!---->
    <div v-else class="d-flex flex-column w-100 mb-2">
        <div class="w-100 d-flex justify-content-between">
      <button @click="currentTab = 'pending'" :class="[currentTab==='pending'?'active':'']">Pending</button>
      <button @click="currentTab = 'accepted'" :class="[currentTab==='accepted'?'active':'']">Accepted</button>
      <button @click="currentTab = 'rejected'" :class="[currentTab==='rejected'?'active':'']">Rejected</button>
    </div>

    <!-- <p>{{ pendingInfluencers }}{{ acceptedInfluencers }}</p> -->
    <!-- Display influencers based on selected tab -->
    <div v-if="currentTab === 'pending'" class="d-flex fw-bold align-items-center flex-column w-100 justify-content-center mt-2">
        <p class="mt-5" v-if="pendingInfluencers.length===0">No pending requests.</p>
        <div v-for="influencer in pendingInfluencers" :key="influencer.influencer_id" class="influencer-card">
            <button><router-link class="nav-link" :to="`/user/user-profile/${influencer.influencer_id}`">{{ influencer.influencer_name }}</router-link></button>
        <div class="inner-card">
        <button disabled class="pending">{{ influencer.status || 'Pending' }}</button>
        <button @click="handleAccept(influencer)" :disabled="influencer.status === 'accepted' || campaign.acceptedInfluencers>=campaign.influencersPerCampaign || disableButton" class="accepted">Accept</button>
        <button @click="handleReject(influencer)" :disabled="influencer.status === 'rejected' || disableButton" class="rejected">Reject</button>
        <button @click="toggleFeedbackForm(influencer.influencer_id)">
            {{ feedbackVisibility[influencer.influencer_id] ? 'Close' : 'Feedback?' }}
          </button>
          <textarea
            v-if="feedbackVisibility[influencer.influencer_id]"
            v-model="feedback[influencer.influencer_id]"
            placeholder="Add feedback..."
          ></textarea>
        </div>
        <p v-if="feedback[influencer.influencer_id]" class="feedback">{{ feedback[influencer.influencer_id] }}</p>
        </div>
    </div>

    <div v-else-if="currentTab === 'accepted'" class="d-flex fw-bold align-items-center w-100 justify-content-center mt-2 flex-column">
      <!-- <h3>Accepted Requests</h3> -->
       <p class="mt-5" v-if="acceptedInfluencers.length===0">No influencers currently accepted</p>
      <div v-for="influencer in acceptedInfluencers" :key="influencer.influencer_id" class="influencer-card">
        <button><router-link class="nav-link" :to="`/user/user-profile/${influencer.influencer_id}`">{{ influencer.influencer_name }}</router-link></button>
        <div class="inner-card">

        <button disabled class="accepted">Accepted</button>
        <button @click="handleReject(influencer)" :disabled="influencer.status === 'rejected' || disableButton" class="rejected">Reject</button>
        <button @click="toggleFeedbackForm(influencer.influencer_id)">
            {{ feedbackVisibility[influencer.influencer_id] ? 'Close' : 'Feedback?' }}
          </button>
          <textarea
            v-if="feedbackVisibility[influencer.influencer_id]"
            v-model="feedback[influencer.influencer_id]"
            placeholder="Add feedback..."
          ></textarea>

        </div>
        <p v-if="feedback[influencer.influencer_id]" class="feedback">{{ feedback[influencer.influencer_id] }}</p>
       
      </div>
    </div>

    <div v-else-if="currentTab === 'rejected'" class="d-flex flex-column fw-bold align-items-center w-100 justify-content-center mt-2">
        <p class="mt-5" v-if="rejectedInfluencers.length===0">No influencers currently rejected</p>
      <div v-for="influencer in rejectedInfluencers" :key="influencer.influencer_id" class="influencer-card">
        <button><router-link class="nav-link" :to="`/user/user-profile/${influencer.influencer_id}`">{{ influencer.influencer_name }}</router-link></button>
        <div class="inner-card">
            <button disabled class="rejected">Rejected</button>
            <button @click="handleAccept(influencer)" :disabled="influencer.status === 'accepted' || disableButton" class="accepted">Accept</button>
            <button @click="toggleFeedbackForm(influencer.influencer_id)">
            {{ feedbackVisibility[influencer.influencer_id] ? 'Close' : 'Feedback?' }}
          </button>
          <textarea
            v-if="feedbackVisibility[influencer.influencer_id]"
            v-model="feedback[influencer.influencer_id]"
            placeholder="Add feedback..."
          ></textarea>
        </div>
        <p v-if="feedback[influencer.influencer_id]" class="feedback">{{ feedback[influencer.influencer_id] }}</p>

      </div>
    </div>
    </div>
 
    <!-- <div><p>{{ filteredInfluencer }}</p></div>
    <div><p>{{ campaign }}</p></div> -->
</section>
</template>
  
  <script>
  import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
  import { useCampaignsStore } from '../../../store';
  import { useAuthStore } from '../../../store';
  import { fetchUserProfileById } from '../../../services/userservice';
  import campaignPolicies from '../Terms&Conditions/campaignPolicies.vue';  
  export default {
    name: 'CampaignApply',
    components : {
      campaignPolicies
    },
    props: {
      campaign: {
        type: Object,
        required: true,
      },
   
    },
    setup(props, {emit}) {
      const campaignsStore = useCampaignsStore();
      const authStore = useAuthStore();
      const selectedInfluencerId = ref(null);
      const currentTab = ref('pending'); // Track the current tab
      const feedback = ref({});
      const feedbackVisibility = ref({});
      const applied = ref(false)
      const showPolicy = ref(false);
      const disableButton = ref(false);


      //influencer states
      const applyButtonState = ref('active');

      const filteredInfluencer = computed(() => {
        // Find the influencer by matching influencer_id
        const influencer = props.campaign.influencers.find(
            (influencer) => influencer.influencer_id === authStore.userProfile.id
        );
        
        // If no influencer is found, return a default object with { status: null }
        return influencer || { status: null };
        });

      const togglePolicies = ()=> {
        showPolicy.value = !showPolicy.value;
      }

      const applyButtonLabel = computed(() => {
      if (filteredInfluencer.value.status === 'pending') {
        return 'Pending Approval';
      } else if (filteredInfluencer.value.status === 'accepted' || filteredInfluencer.value.status === 'rejected' || applied.value) 
      {
        applyButtonState.value='inactive';
        return 'Applied';
      }
      else if (props.campaign.acceptedInfluencers>=props.campaign.influencersPerCampaign){
        applyButtonState.value='inactive';
        return 'No more accepting applications'
      }
      return 'Apply to Work';
    });

      const applyToCampaign = ( async ()=>{
        try{
            if (applyButtonState.value==='active')
      {
        const response = await campaignsStore.submitCampaignRequest(props.campaign.id);
        if (response || response.status === 200) {
        applyButtonState.value = 'inactive';
        applied.value = true;
      }
    }
        }
        catch(error){
            console.log(error);
        }
       
      })

      const pendingInfluencers = computed(() =>
      props.campaign.influencers.filter(influencer => (influencer.status === 'pending' || influencer.status===null))
    );
    const acceptedInfluencers = computed(() =>
      props.campaign.influencers.filter(influencer => influencer.status === 'accepted')
    );
    const rejectedInfluencers = computed(() =>
      props.campaign.influencers.filter(influencer => influencer.status === 'rejected')
    );

    const handleAccept = async (influencer) => {
      disableButton.value=false;
      await campaignsStore.respondToJoinRequest(influencer.influencer_id, { status: 'accepted', influencer_feedback: feedback.value[influencer.influencer_id] }, props.campaign.id);
      const updateCampaignsData = await campaignsStore.getCampaignDetails(props.campaign.id);
      emit('updateCampaignData',updateCampaignsData)
    };

    const handleReject = async (influencer) => {
      disableButton.value=false;
      await campaignsStore.respondToJoinRequest(influencer.influencer_id, { status: 'rejected', influencer_feedback: feedback.value[influencer.influencer_id] }, props.campaign.id);
      const updateCampaignsData = await campaignsStore.getCampaignDetails(props.campaign.id);
      emit('updateCampaignData',updateCampaignsData)
    };
    const toggleFeedbackForm = (influencerId) => {
      feedbackVisibility.value[influencerId] = !feedbackVisibility.value[influencerId];
      feedback.value[influencerId] = feedback.value[influencerId] || '';
    };


  
      // Send a new message


      return {
        filteredInfluencer,
        applyButtonState,
        applyToCampaign,
        authStore,
        campaignsStore,
        pendingInfluencers,
        acceptedInfluencers,
        rejectedInfluencers,
        handleAccept,
        handleReject,
        currentTab,
        feedback,
        feedbackVisibility,
        applyButtonLabel,
        toggleFeedbackForm,
        applied,
        togglePolicies,
        showPolicy,
        disableButton
        
      };
    },
  };
  </script>
  
  
  <style scoped>
.influencer-card {
  margin: 10px;
  padding: 10px;
  border: 1px solid #ccc;
  display: flex;
  align-items: start;
  justify-content: center;
  gap: 0.5rem;
  flex-direction: column;
  width: 100%;
}
.pending{
    background-color: #ccc;
}

/* This allows scrolling but hides scrollbar */
.hide-scrollbar::-webkit-scrollbar {
    display: none; /* Safari and Chrome */
}
.hide-scrollbar{
  padding: 2rem;
  background-color: 1px solid black;
}

.hide-scrollbar p:hover{
background-color: #12dbe6;
box-shadow: 2px 1px 0.2rem rgb(55, 55, 55);
position: relative;
}
.accepted{
    background-color: rgb(105, 175, 93);
}
.rejected{
    background-color: rgb(255, 91, 91);
}

.influencer-card .inner-card{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
    width: 100%;
}
textarea{
    border: 1px solid lavenderblush;
    border-radius: 0.2rem;
    position: absolute;
    margin-top: -5rem;
    width: 20rem;
    font-weight: bolder;
    margin-left: -1rem;
    background-color: rgba(205, 205, 205, 0.876);
}
.feedback{
    box-shadow: 1px 1px 0.5rem rgb(156, 156, 156);
    padding: 1rem 0.5rem;
    border: 1px solid transparent;
    border-radius: 0.5rem;
    background-color: antiquewhite;
}
  </style>
  