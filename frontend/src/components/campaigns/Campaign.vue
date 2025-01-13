<template>
  <div v-if="authStore.userProfile" class="d-flex flex-column align-items-center justify-content-start hide-scrollbar">
    <!-- Tab Buttons to Switch Views -->
    <div class="tabs d-flex justify-content-around align-items-center p-3 text-white">
      <button @click="setCurrentView('search')" :class="{ active: currentView === 'search' }">Search Campaigns</button>
      <button v-if="authStore.userProfile.role === 'brand'" @click="setCurrentView('yourCampaigns')" :class="{ active: currentView === 'yourCampaigns' }">Create Campaigns</button>
    </div>

      <!-- Search Campaigns View -->
      <div v-if="currentView === 'search'" class="d-flex flex-column align-items-start justify-content-center w-100">
        <div class="d-flex align-items-center w-100 justify-content-center p-2">
          <EnhancedMultiselect
            id="select-filter"
            v-model="activeFilters"
            :options="filterOptions"
            label="Search by"
            class="w-100 mb-2"
          />

          <button @click="resetFilters" class="mb-3 ms-2"><i class="fa fa-close fs-4"></i></button>


        </div>
        


      <div class="search-bar d-flex flex-column justify-content-around flex-wrap gap-2 p-3 w-100">

        <input v-if="activeFilters.includes('brandName')" v-model="filters.brandName" type="text" placeholder="Brand/Business Name" class="form-control mb-2" />
        <input v-if="activeFilters.includes('campaignName')" v-model="filters.campaignName" type="text" placeholder="Campaign Name" class="form-control mb-2" />
        <input v-if="activeFilters.includes('budget')" v-model="filters.budget" type="number" placeholder="Budget" class="mb-2 form-control" />
        
        <select v-if="activeFilters.includes('status')" v-model="filters.status" class="form-control mb-2 text-black fw-bold">
          <!-- <option value="" disabled>Status</option> -->
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <!-- <option value="completed">Completed</option> -->
        </select>
        
        <EnhancedMultiselect
          :id="activeFilters[activeFilters.length-1]"
          v-if="activeFilters.includes('niches')"
          v-model="filters.niche"
          :options="niches"
          label="Select Niche"
          class="w-50 mb-2"
        />

        <input v-if="activeFilters.includes('dates')" v-model="filters.startDate" type="date" placeholder="Start Date" class="form-control mb-2" />
        <input v-if="activeFilters.includes('dates')" v-model="filters.endDate" type="date" placeholder="End Date" class="form-control mb-2" />

        <button @click="searchCampaigns" class="p-2">Search</button>

      </div>

      <div v-if="filteredCampaigns.length === 0 && searchedBefore" class="d-flex flex-column align-items-center justify-content-center w-100 fw-bold">
        <p>No Campaigns Match Your Search</p>
      </div>
      
      <div v-else class="d-flex gap-3 overflow-auto w-100 p-3" style="max-width: 100%; white-space: nowrap;">
        <CampaignCard
          v-for="campaign in filteredCampaigns"
          :key="campaign.id"
          :campaign="campaign"
          :userRole="authStore.userProfile.role"
          :currentUserId="authStore.userProfile.id"
          @view="viewCampaign(campaign)"
        />
      </div>

        <div class="d-flex flex-column w-100" v-if="authStore.userProfile.role==='influencer' & allCampaigns.length>0">
          <div class="d-flex align-items-center justify-content-center  fw-bold fs-6 text-secondary">
            <h4>Campaigns that might interest you!!!</h4>
          </div>
          <div class="d-flex gap-3 overflow-auto w-100 p-3" style="max-width: 100%; white-space: nowrap;" v-if="authStore.userProfile.role==='influencer'">
        <CampaignCard
          v-for="campaign in allCampaigns"
          :key="campaign.id"
          :campaign="campaign"
          :userRole="authStore.userProfile.role"
          :currentUserId="authStore.userProfile.id"
          @view="viewCampaign(campaign)"
        />
      </div>
        </div>

      
    </div>




    <!-- Your Campaigns View for Brands -->
    <div v-if="currentView === 'yourCampaigns'" class="d-flex flex-column align-items-start justify-content-start w-100 vh-100" style="">
    <div class="w-100 d-flex align-items-center justify-content-center">
      <button @click="openForm()" class="mb-3">Create</button>
    </div>

    <!-- Bootstrap Scrollable Container -->
    <div class="d-flex gap-3 overflow-auto w-100 p-3 hide-scrollbar" style="max-width: 100%; white-space: nowrap;">
      <CampaignCard
        v-for="campaign in brandCampaigns"
        :key="campaign.id"
        :campaign="campaign"
        :userRole="authStore.userProfile.role"
        :currentUserId="authStore.userProfile.id"
        @edit="openForm(campaign)"
        @delete="deleteCampaign(campaign.id)"
        @startCampaign="startCampaign(campaign.id)"
        @endCampaign="endCampaign(campaign.id)"
      />
    </div>
  </div>



  <!-- ##############################################    FORM SECTION    ################################################################################################################################################################################################################# -->
    <!-- Create/Update Campaign Form -->
    <div v-if="showForm" class="form-container d-flex flex-column mt-2 rounded-2" style=" width: 22rem; position: absolute; background-color: white;">
      <!-- <h3>{{ formData.id ? 'Update Campaign' : 'Create Campaign' }}</h3> -->


      <div class="">
        <div class="d-flex justify-content-end">
        <button @click="closeForm" class="close-btn">❌</button>
        </div>

        <form @submit.prevent="submitForm" class="campaignForm d-flex flex-column justify-content-between align-items-center gap-3 alert alert-warning p-2 fw-bold">
          
        <div v-if="currentStep===1" class="d-flex flex-column justify-content-start align-items-start gap-3 mt-2" key="step1">
          <label for="campaignname" class="form-label">Campaign Name</label>
          <input v-model="formData.name" placeholder="Campaign Name" required class="form-control alert alert-warning" />

        <label for="Description">Description</label>
        <textarea v-model="formData.description" placeholder="Short Description for Campaign" required class="form-control alert alert-warning"></textarea>

        <label for="budget">Budget</label>
        <input v-model="formData.budget" type="number" placeholder="Budget for each influencer" required class="form-control alert alert-warning" />

        <label for="startDate">Start Date</label>
        <input v-model="formData.start_date" type="date" placeholder="Start Date" required class="form-control alert alert-warning" />
        

        <label for="endDate">End Date</label>
        <div class="w-100 d-flex gap-2">
          <input v-model="formData.end_date" type="date" placeholder="End Date" required class="form-control alert alert-warning" />
            <div class="endDateinfo tooltipp">
              <i class="fa-solid fa-circle-question mt-2" style="color: #FFD43B;"></i>
              <div class="tooltiptext" style="width: 10rem; padding: 1rem;">
                Campaigns can't be editted after end date.
              </div>
            </div>
        </div>

        <label for="visibility">Visibility</label>
        <select v-model="formData.visibility" required class="form-control alert alert-warning">
          <option value="" disabled>Choose visibility</option>
          <option value="public">Public</option>
          <option value="private">Private</option>
        </select>
          

        </div>

        <div v-else-if="currentStep === 2" class="d-flex flex-column justify-content-center align-items-center gap-3 p-3" key="step2">
          <!-- Task Input -->
          <div class="mb-3 d-flex gap-2">
            <input
              v-model="newTask"
              placeholder="List Your Campaign Tasks"
              class="form-control mb-2"
            />
            <button type="button" @click="addTask" class="">➕</button>
          </div>
          <!-- List of Tasks with Complete/Incomplete Toggle -->
          <ul class="list-group mb-3">
            <li
              v-for="task in formData.tasks"
              :key="task.id"
              class="list-group-item d-flex justify-content-between align-items-center"
            >
              <div class="d-flex align-items-center gap-2">
                <input
                  type="checkbox"
                  v-model="task.status"
                  @change="toggleTaskStatus(task.id)"
                  class="bg-dark"
                />
                <span :class="{ 'text-decoration-line-through': task.status }">{{ task.description }} {{ task.id }}</span>
              </div>
              <button @click="removeTask(task.id)" class="ms-3">❌</button>
            </li>
          </ul>
          <div>
            <!-- {{ formData.value.tasks }} -->
          </div>
        </div>

        <div v-else-if="currentStep===3" class="w-100 h-100" key="step3">
          <label for="Guidelines">Detailed Guideline</label>
          <textarea v-model="formData.guidelines" placeholder="Detailed Campaign Guidelines" required class="form-control" style="width: 20rem; height: 20rem;"></textarea>
        </div>

        <div v-else-if="currentStep===4" class="d-flex flex-column justify-content-center align-items-center gap-3 form-control p-3" key="step4">

          <EnhancedMultiselect
          id="niche"
          label="Niche"
          :options="niches"
          v-model="formData.niches"
          class="w-100"
          required
        />

        <EnhancedMultiselect
            id="platforms"
            label="Preferred Platforms"
            :options="platforms"
            v-model="formData.platforms"
            class="w-100"
          />


          <EnhancedMultiselect
            id="goals"
            label="Campaign Goals"
            :options="goals"
            v-model="formData.goals"
            class="w-100"
          />


        </div>

        <div v-else-if="currentStep===5" class="d-flex flex-column justify-content-center align-items-center gap-3 form-control p-3" key="step5">
          
          <label class="btn checkbox">Choose Tracking Methods:</label>
          <p class="w-100 alert alert-warning p-2 fw-bold mt-2 mb-2">We recommed enabling all options for better tracking</p>
          <div class="trackingmethods" style="overflow: scroll;">
            <label class="p-3 border border-warning rounded">
              <input type="checkbox" :checked="isInfluencerSocial" class="checkbox" @change="handleTrackingChange('influencerSocials')" required/>
              Using Influencer Socials
              <button class="influencerSocials">
                <Tooltip text='Tracks Influencer Posts, engagement, comments, sentiments and more related to your campaign.' :triggerClass="'influencerSocials'" position="left" />
                <i class="fa-solid fa-circle-info"></i>
              </button>
            </label>
            <label class="p-3 border border-warning rounded">
              <input type="checkbox" :checked="isBrandSocial" class="checkbox" @change="handleTrackingChange('brandSocials')" required/>
              Using Brand Socials
              <button class="brandSocials">
                <Tooltip :text="'Use your brand social media growth/engagement as a metric to track influencer progress Supports only one account.'" :triggerClass="'brandSocials'"/>
                <i class="fa-solid fa-circle-info"></i>
              </button>
            </label>
            <label class="p-3 border border-warning rounded">
              <input type="checkbox" :checked="isUtmLinks" class="checkbox" @change="handleTrackingChange('utmLinks')" />
              Using UTM Links
              <button class="utmLinks">
                <Tooltip :text="'Use utm links and google analytics 4 api to track campaign progress. Recommended if your business has a web application whose users you want to track during the campaign.'" :triggerClass="'utmLinks'"/>
                <i class="fa-solid fa-circle-info"></i>
              </button>
            </label>
          </div>
          <!-- Conditional Rendering for Influencer Socials -->
          <div v-if="isInfluencerSocial" class="mb-3">
            <p class="checkbox p-3 border rounded">Choosing this option will enable you to track influencer's social media data related to your campaign.</p>

          </div>

          <!-- Conditional Rendering for Brand Socials -->
          <div v-if="isBrandSocial" class="mb-3">
            <div class="mb-3">
                        <!-- Select Interface for Platform Choice -->
                        <label for="brandplatform">Select Platform:</label>
                        <select v-model="formData.brandPlatform" id="brandplatform" class="form-control">
                          <option disabled value="">Choose a platform</option>
                          <option v-for="platform in platforms" :key="platform" :value="platform">
                            {{ platform }}
                          </option>
                        </select>
                      </div>

                      <!-- Conditionally Show URL Input Based on Selected Platform -->
                      <div v-if="formData.brandPlatform" class="mb-3">
                        <label :for="formData.brandPlatform">{{ formData.brandPlatform }} URL:</label>
                        <input v-model="formData.brandSocialLink" 
                              :placeholder="'Your brand/business ' + formData.brandPlatform + ' URL'" 
                              class="form-control" 
                              :required="formData.brandPlatform !== ''"/>
                      </div>
                      <div v-if="formData.brandSocialLink" class="mb-3">
                      <label for="follower-goal">Set Follower Goal:</label>
                      <input 
                        type="range" 
                        id="follower-goal" 
                        v-model="formData.brandTarget" 
                        min="0" 
                        max="1000000" 
                        step="1000" 
                        class="form-range"
                        required
                      />
                      <div>
                        <!-- Display the selected value dynamically -->
                        <span>Target Followers: {{ formData.brandTarget }}</span>
                      </div>
                    </div>
          </div>

          <!-- Conditional Rendering for UTM Links -->
          <div v-if="isUtmLinks" class="mb-3 d-flex flex-column align-iterms-center justify-content-center gap-2">
            <p class="checkbox p-3 border rounded">Check these videos to create necessary credentials on google cloud console:</p>
            <div class="d-flex align-items-center justify-content-center"><iframe width="300" height="" src="https://www.youtube.com/embed/HbxIXEfl-Hs?si=vnr8UuAPh1W3f0r3" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
            <p class="btn checkbox">After following the first half of first video you can go in google analytics platform and set up data stream using tag manager. Alternatively you can follow the video below.</p>
            <div><iframe width="300" height="" src="https://www.youtube.com/embed/F8_sbW63sH0?si=B-VbQo13AzCnjW70" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
            <div class="d-flex flex-column">
              <p class="btn checkbox">Google Analytics Data Stream</p>
              <p class="btn checkbox">After setting up Google Analytics project you can set up data stream of the project here.</p>
              <img width="300" src="\src\assets\gainstructions\instruction1.png" alt="">
              <p class="btn checkbox">Click on Add Stream and follow the instructions there.</p>
              <img width="300" src="\src\assets\gainstructions\instruction2.png" alt="">
            </div>

            <label class="btn checkbox">
              <input type="checkbox" v-model="formData.isAffiliate" @change="handleAffiliateChange" />
              Enable Affiliate Tracking
              <div class="tooltipp">
                <i class="fa-solid fa-circle-info"></i>
                <div class="tooltiptext">
                  <p>Affiliate tracking helps you to measure the performance of each influencer rather than all influencers as a whole. You can track each influencer seperately with more granular contraol over data. IF the url endpoint takes user to some payment dashboard, it is recommended to use this option as well.</p>
                  <p>When should you use this?</p>
                  <ul>
                    <li>Track performance of Influencers seperately</li>
                    <li>Site url takes to subscription/payment page</li>
                  </ul>
                </div>
              </div>
            </label>
            <input v-model="formData.ga4_base_url" placeholder="URL of your Site" class="form-control checkbox" :required="isUtmLinks"/>  <!-- New field for GA4 Base URL -->


            <textarea v-model="formData.jsonCredentials" placeholder="Paste JSON Credentials Here" class="form-control" rows="6" :required="isUtmLinks"></textarea>            
            <input v-model="formData.propertyId" placeholder="GA4 Property ID" class="form-control checkbox" :required="isUtmLinks"/>
          </div>

        </div>

        <div class="w-100 d-flex justify-content-between align-items-center">
          <button :disabled="currentStep===1" @click="previousStep">
            <i class="fa fa-arrow-left"></i>
          </button>
          <div v-show="currentStep===maxStep">
          <button type="submit">{{ formData.id ? 'Update Campaign' : 'Create Campaign' }} <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span></button>
          </div>
          <button :disabled="currentStep===maxStep" @click="nextStep">
            <i class="fa fa-arrow-right"></i>
          </button>
        </div>
        
        <button v-if="formData.id && currentStep===maxStep" @click="deleteCampaign(formData.id)" type="button" class="btn btn-danger mt-2">Delete Campaign</button>

      <div class="progress w-100">
        <div class="progress-bar bg-warning" role="progressbar" :style="{ width: (currentStep / maxStep) * 100 + '%' }" :aria-valuenow="(currentStep / maxStep) * 100" aria-valuemin="0" aria-valuemax="100">{{ (currentStep / maxStep) * 100 + '%' }}</div>
      </div>
      

      </form>

      </div>

    </div>
  </div>
</template>


<script>
import { ref, computed, onMounted } from 'vue';
import CampaignCard from './CampaignCard.vue';
import { useCampaignsStore } from '../../store';
import { useAuthStore } from '../../store';
import EnhancedMultiselect from '../utilities/EnhancedMultiselect.vue';
import { fetchSignupOptions } from '../../services/authService';
import Tooltip from '../utilities/Tooltip.vue';

export default {
  name: 'Campaigns',
  components: { CampaignCard, EnhancedMultiselect, Tooltip },
  setup() {
    //variables

    // campaign and auth stores
    const campaignsStore = useCampaignsStore();
    const authStore = useAuthStore();

    // general data collection
    const niches = ref([]);
    const platforms = ref([])
    const goals = ref([])

    // formdata and currentview data storage
    const formData = ref({ tasks: [],});  // Holds campaign data for form
    const currentView = ref('');

    // utilities storage
    const showForm = ref(false);  // Whether to show the form
    const newTask = ref('');
    const isLoading = ref(false);
    const searchvalue = ref('brandName');

    const isupdatingorcreating = ref(false);

    // form transition variables

    const currentStep = ref(1);
    const maxStep = 5;
    const filteredCampaigns = ref([])
    const searchedBefore = ref(false);



    // filter reactivity

    const filterOptions = [
      'brandName',
      'campaignName',
      'budget',
      'status',
      'niches',
      'dates'
    ];
    const activeFilters = ref([]);

    const filters = ref({
      brandName: null,
      campaignName: null,
      budget: 0,
      status: null,
      niche: [],
      startDate: null,
      endDate: null
    });


    // Fetch campaigns for brand
    const brandCampaigns = computed(() => campaignsStore.brandCampaigns(authStore.userProfile.id) || []);
    const allCampaigns = computed(() => campaignsStore.campaigns || []);
    const isBrandSocial = computed(() => formData.value.trackingMethods.includes('brandSocials'));
    const isInfluencerSocial = computed(() => formData.value.trackingMethods.includes('influencerSocials'));
    const isUtmLinks = computed(() => formData.value.trackingMethods.includes('utmLinks'));
    console.log(isBrandSocial,isInfluencerSocial,isUtmLinks)




    //functions


    const formatDate = (date) => {
      if (!date) return null;  // Check if the date is defined
      const parsedDate = new Date(date);
      if (isNaN(parsedDate)) return null;  // Check if the date is valid
      return parsedDate.toISOString().split("T")[0];
    };

    const searchCampaigns = async () => {
      try {
        const campaigns = await campaignsStore.searchCampaigns(filters.value);
        filteredCampaigns.value = Array.isArray(campaigns) ? campaigns : [];
        searchedBefore.value=true;
      } catch (error) {
        console.error("Failed to search campaigns:", error);
        filteredCampaigns.value = [];  // Ensure fallback to empty array on error
      }
    };

    const resetFilters = () => {
      filters.value = {
        brandName: '',
        campaignName: '',
        budget: '',
        status: '',
        niche: [],
        startDate: '',
        endDate: ''
      };
      activeFilters.value = [];
    };


    // Load campaigns and niches when the component mounts
    onMounted(async () => {
      // await authStore.checkUserStatus();
      await campaignsStore.loadCampaigns(authStore.userProfile.id);  // Load all campaigns
      console.log(campaignsStore.campaigns)

      if (authStore.userProfile){
      currentView.value=authStore.userProfile.role==='brand'?'yourCampaigns':'search'
    }

      try {
        const options = await fetchSignupOptions();
        niches.value = options.niches;  // Populate niches for the form
        platforms.value = options.platforms;
        goals.value = options.goals;
      } catch (error) {
        console.error('Failed to load niches:', error);
      }
    });
    

    //utilities


    const setCurrentView = (view) => {
      currentView.value = view;
      closeForm();  // Reset the form when switching views
    };

    // Open the form for create or edit
    
    const handleTrackingChange = (method) => {
      const index = formData.value.trackingMethods.indexOf(method);
      if (index > -1) {
        // If method is already in the array, remove it (uncheck)
        formData.value.trackingMethods.splice(index, 1);
      } else {
        // If method is not in the array, add it (check)
        formData.value.trackingMethods.push(method);
      }
    };

    const handleAffiliateChange = () => {
      if (!isUtmLinks.value) {
        formData.value.isAffiliate = false; // Disable affiliate tracking if UTM links are not checked
      }
    };
    const openForm = (campaign = null) => {
      formData.value = campaign
        ? { ...campaign }  // Edit mode
        : { name: '', description: '', budget: '', start_date: '', end_date: '', visibility: 'public', goals: [],tasks: [],guidelines: '', niches: [], platforms: [], trackingMethods: [], brandSocialLink: '',jsonCredentials: '',propertyId: '', isAffiliate: false, brandPlatform: '', ga4_base_url : ''};  // Create mode
      showForm.value = true;
    };


    // Close the form
    const closeForm = () => {
      showForm.value = false;
      formData.value = {};  // Reset form data
    };

    // Submit the form (Create or Update)
    const submitForm = async () => {
      if (currentStep.value===maxStep){
      isLoading.value = true;
      if (formData.value.id) {
        await campaignsStore.updateCampaign(formData.value.id, formData.value);  // Update campaign
        const updateCampaignsData = await campaignsStore.getCampaignDetails(formData.value.id);

        campaignsStore.updateCampaignInStore(updateCampaignsData);
      } else {
        const response = await campaignsStore.createCampaign(formData.value);  // Create new campaign
        // campaignsStore.addNewCampaign(response.newCampaign);
      }
      setCurrentView('yourCampaigns');  // Return to campaigns list
    }
    };
    // Delete a campaign
    const deleteCampaign = async (id) => {
      await campaignsStore.deleteCampaign(id);
      setCurrentView('yourCampaigns');
    };

    const addTask = () => {
        if (newTask.value.trim()) {
          formData.value.tasks.push({
            id: formData.value.tasks.length + 1,  // Assign the current counter value and then increment
            description: newTask.value.trim(),
            status: false,  // Default to incomplete
          });
          newTask.value = '';  // Clear input
        }
      };
    // Method to remove a task by id
    const removeTask = (taskId) => {
      formData.value.tasks = formData.value.tasks.filter(task => task.id !== taskId);
    };

    const toggleTaskStatus = (taskId) => {
      const task = formData.value.tasks.find(task => task.id === taskId);
      if (task) task.status = !task.status;
    };



    //form transition

    const nextStep = () => {
      if (currentStep.value < maxStep){
        currentStep.value += 1
      }
    }
    const previousStep = () => {
      if (currentStep.value > 1) {
        currentStep.value -= 1;
      }
    }


    const startCampaign = (campaignId) => {
      campaignsStore.startCampaign(campaignId);
    }
    const endCampaign = (campaignId) => {
      campaignsStore.endCampaign(campaignId);
    }


    return {
      currentView,
      setCurrentView,
      brandCampaigns,
      allCampaigns,
      formData,
      showForm,
      openForm,
      closeForm,
      submitForm,
      deleteCampaign,
      authStore,
      niches,
      addTask,
      removeTask,
      newTask,
      platforms,
      goals,
      isBrandSocial,
      isInfluencerSocial,
      isUtmLinks,
      handleTrackingChange,
      handleAffiliateChange,
      isLoading,
      filteredCampaigns,
      resetFilters,
      filters,
      searchvalue,
      activeFilters,
      filterOptions,
      nextStep,
      previousStep,
      currentStep,
      maxStep,
      startCampaign,
      endCampaign,
      searchCampaigns,
      toggleTaskStatus,
      searchedBefore

    };
  },
};
</script>


<style scoped>
.tabs {
  margin-bottom: 20px;
}

button {
  border: 1px solid white;

}

.form-container {
  margin-top: 20px;
}


.tooltipp {
  position:relative; /* Positioning context for the tooltip */
  /* display: inline-block; Keeps the tooltip next to the status indicator */

}

.tooltiptext {
  visibility: hidden; /* Hidden by default */
  width: 15rem;
  background-color: rgba(255, 202, 122, 0.975);
  color: #fff;
  text-align: center;
  border-radius: 5px;
  padding: 0.5rem 1rem;
  position: absolute;
  /* text-wrap: wrap; */
  z-index: 1;
  bottom: 100%; /* Position above the indicator */
  /* left: 30%; */
  margin-left: -10rem; /* Center the tooltip */
  opacity: 0; /* Start as invisible */
  transition: opacity 0.3s; /* Smooth transition */
}

.tooltipp:hover .tooltiptext {
  visibility: visible; /* Show the tooltip on hover */
  opacity: 1; /* Make it visible */
  z-index: 10;
}
.checkbox{
  background-color: rgba(255, 202, 122, 0.975) !important;

}

.campaignForm input, textarea, select{
  box-shadow: 3px 2px 0.5rem rgba(222, 222, 222, 0.49);
}

.campaignForm{
  box-shadow: 5px 10px 1rem rgb(108, 108, 108);
  border: 1px solid beige;
  border-radius: 1rem 1rem;
  background-color: transparent;
}

.campaignForm label{
  font-weight: bold;
  /* background-color: rgba(255, 240, 175, 0.577); */
  /* padding: 0.5rem; */
  /* border: #fff; */
  border-radius: 0.5rem;
}
.campaignForm textarea{
  background-color: rgba(255, 253, 246, 0.837);
  margin-top: 0.5rem;
}

.campaignForm input:hover, select:hover{
  box-shadow: 2px 1px 0.2rem rgba(141, 141, 141, 0.49);
  background-color: rgb(255, 255, 255);
  /* padding: 0.5rem; */
}

.trackingmethods{
  display: flex;
  align-items: end;
  justify-content: space-between;
  width: 20rem;
  gap: 2rem;
  padding: 1rem;
}

.trackingmethods label{
 text-wrap: nowrap;
}
</style>