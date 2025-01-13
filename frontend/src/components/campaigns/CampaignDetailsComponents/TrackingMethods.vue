<template>

  <div>

    <div>
    <div class="d-flex flex-column gap-2 justify-content-center" v-if="trackingData">
      <!-- <div class="tracking-item" v-for="(value, key) in trackingData" :key="key">
        <strong>{{ key }}:</strong> {{ value }}
      </div> -->
      <div class="d-flex gap-2 justify-content-around flex-wrap">
      <!-- <p>This campaign has {{ trackingData.trackingMethods.length }} active tracking methods</p> -->
      <div v-for="trackingMethod in trackingData.trackingMethods" :key="trackingMethod">
        <button @click="showTrackingDetails(trackingMethod)" :class="{'selected': trackingMethod === selectedTrackingMethod}">{{ trackingMethod }}</button>
      </div>
      </div>

      <div class="tracking-item fw-bold flex-wrap">
        <p>
          {{ trackingDetails }}
        </p>
      </div>
    </div>
    <div v-else>
      <p>No tracking data available.</p>
    </div>





    <div v-if="(selectedTrackingMethod==='influencerSocials') && (trackingData.status==='active') && (currentInfluencer || trackingData.influencers)">
      <div class="subnavigation d-flex justify-content-between">
        <button v-if="authStore.userProfile.role==='influencer'" @click="showSelectedSubView('Post Content')" :class="selectedSubview==='Post Content'?'active':''">Submit Links</button>
        <button @click="showSelectedSubView('Media Progress')" :class="selectedSubview==='Media Progress'?'active':''">Media Progress</button>
      </div>

      <div v-if="selectedSubview==='Post Content'" class="d-flex flex-column justify-content fw-bold mt-2" :style="{ opacity: isLoading ? 0.5 : 1 }">
        <p class="alert alert-warning fw-bold">Add links of your content here. These will be used to track your content.</p>
        <div v-if="(currentInfluencer.status==='accepted')">
      <div class="mb">
        <label for="platform-select" class="form-label">Select Platform</label>
        <select v-model="newLink.platform" class="form-select" id="platform-select">
          <option v-for="platform in platforms" :key="platform" :value="platform">
            {{ platform }}
          </option>
        </select>
      </div>
      
      <div class="mb-3">
        <label for="link-input" class="form-label">Enter Link</label>
        <input
          v-model="newLink.url"
          type="text"
          class="form-control"
          id="link-input"
          placeholder="Enter post link"
        />
      </div>
      
      <button
        class="btn-subtheme"
        :disabled="links.length >= 5 || !newLink.platform || !newLink.url"
        @click="addLink"
      >
        + Add Link
      </button>
    </div>

    <div v-if="links.length > 0" class="mt-4 w-100">
      <p class="fw-bold">Added Links</p>
      <ul class="list-group">
        <li
          v-for="(link, index) in links"
          :key="index"
          class="list-group-item d-flex justify-content-between align-items-center gap-2"
        >
          <span class="overflow-scroll mb-3" style="font-size: small;">{{ link.platform }}: {{ link.url }}</span>
          <p class="btn-danger p-2 rounded-3 fw-bold fa fa-close text-light border" @click="removeLink(index)"></p>
        </li>
      </ul>
    </div>

    <div class="mt-4 mb-2">
      <button
        class="btn btn-primary"
        :disabled="links.length === 0"
        @click="submitLinks"
      >
        Submit Links <i :class="isLoading?'spinner-border spinner-border-sm':''"></i>
      </button>
    </div>

      </div>







      <div v-if="selectedSubview === 'Media Progress'" class="fw-bold alert alert-transparent mt-2">
    <!-- Handle case when there's no data or it's empty -->
    <p v-if="(!currentInfluencer || currentInfluencer.postrackingMetric.length === 0) & authStore.userProfile.role==='influencer'">
    </p>

    <div v-else :style="{ opacity: isLoading ? 0.5 : 1 }">
      <!-- {{ currentInfluencer.postrackingMetric }} -->
       <div class="w-100 d-flex mb-2 justify-content-end">
        <button class="bg-transparent" @click="updatepostMetrics"><i  :class="[isLoading?'spinner-border text-black spinner-sm':'fa fa-repeat', 'bg-transparent text-dark']"></i></button>
       </div>
      <!-- Loop over all influencers' data when the user is a brand/owner -->
      <div v-for="(influencer, index) in influencersToShow" :key="index" class="alert alert-warning">
      <h5>{{ influencer.influencer_name }}</h5>
      <p class="text-danger fw-bold" v-if="(!parsedMetrics || Object.keys(parsedMetrics).length === 0)">No Content Posted yet</p>

      <div v-for="(platformData, platformName) in parsedMetrics[influencer.influencer_id]" :key="platformName">
        <!-- <h6>{{ platformName.charAt(0).toUpperCase() + platformName.slice(1) }} Posts</h6> -->
        
        <div v-for="(linkData, linkIndex) in platformData" :key="linkIndex">

          <p>
            <a :href="linkData.url" target="_blank" rel="noopener noreferrer">
              Open {{ platformName }} Post {{ linkIndex + 1 }}
            </a>
          </p>

          <div :class="[linkData.metrics.obtained < linkData.metrics.target ? 'alert alert-danger' : 'alert alert-success', 'd-flex justify-content-center align-items-center border flex-wrap']">
            <p class="border fw-bold">Metric : {{ linkData.metrics.type }}</p>
            <div class="d-flex justify-content-center align-items-center gap-2 w-100">
              <p :class="[linkData.metrics.obtained < linkData.metrics.target ? 'bg-danger' : 'bg-success', 'text-center text-white rounded-2']" style="font-size: small; padding: 0.2rem 0.5rem;">
              {{ formatLargeNumber(linkData.metrics.obtained)  }}
            </p>
            <p>/</p>
            <p :class="[linkData.metrics.obtained < linkData.metrics.target ? 'bg-info' : 'bg-success', 'text-center text-white rounded-2']" style="font-size: small; padding: 0.2rem 0.5rem;">
              {{formatLargeNumber(linkData.metrics.target) }}
            </p>
            </div>
            <button @click="deletePostMetric(influencer.influencer_id,linkData.url, platformName)" class="btn btn-danger alert alert-danger"><i class="fa fa-trash"></i></button>

          </div>
          <!-- {{trackingData}} -->

          <div class="progress mb-5">
            <div class="progress-bar bg-info" role="progressbar" :style="{ width: (linkData.metrics.progressPercentage + '%') }" :aria-valuenow="linkData.metrics.progressPercentage" aria-valuemin="0" aria-valuemax="100">
              {{ linkData.metrics.progressPercentage<100?linkData.metrics.progressPercentage:100 }}%
             
            </div>
          </div>

        </div>
      </div>
</div>

    </div>
  </div>
      
    </div>



    <div v-if="selectedTrackingMethod=='brandSocials' && (trackingData.status==='active')">
      <button @click="retrieveBrandSocialsData" class="bg-transparent">
        <i :class="[isLoading?'spinner-border':'fa fa-repeat','text-dark']"></i>
      </button>
      <div :class="[(trackingData.brandCurrent || 0)< (trackingData.brandTarget || 10000)?'alert alert-danger':'alert alert-success','d-flex align-items-center gap-2 justify-content-around fw-bold']">
      <p class="d-flex flex-nowrap gap-2"><p class="">Current:</p> {{ formatLargeNumber( trackingData.brandCurrent?trackingData.brandCurrent:0) }}</p>
      <p class="d-flex flex-nowrap gap-2"><p class="">Target: </p> {{ formatLargeNumber(trackingData.brandTarget?trackingData.brandTarget:10000) }}</p>
      </div>
      <div class="progress">
        <div
          class="progress-bar bg-info progress-bar-striped"
          role="progressbar"
          :style="{ width:((trackingData.brandCurrent || 0)/(trackingData.brandTarget || 10000))*100 + '%' }"
          :aria-valuenow="((trackingData.brandCurrent || 0)/(trackingData.brandTarget || 10000))*100"
          aria-valuemin="0"
          aria-valuemax="100"
        >
          {{ (((trackingData.brandCurrent || 0)/(trackingData.brandTarget || 10000))*100).toFixed(2) }}%
        </div>
      </div>
    </div>


    <div v-if="selectedTrackingMethod == 'utmLinks' && trackingData.status === 'active'" class="d-flex flex-column gap-2">
    <button v-if="currentInfluencer" @click="generateUtmLinks(currentInfluencer.influencer_id)">
      <i :class="[isLoading ? 'spinner-border spinner-border-sm' : 'fa-solid fa-link']"></i>
      Generate Links
    </button>

    <div v-for="(utmLink, index) in utmLinks" :key="index" class="mt-3">
      <div class="d-flex align-items-center justify-content-around gap-2 alert alert-secondary">
        <i :class="'mt-1 fa-brands fs-1 fa-' + utmLink.platform"></i>
        <input
          type="text"
          :value="utmLink.utm_link"
          :ref="(el) => (utmInputRefs[index] = el)"
          readonly
          class="form-control w-75"
        />
        <button @click="copyToClipboard(index)" class="btn rounded border" :key="utmLink.utm_link">
          <i :class="[copyStatus==='Copied!'?'text-success':'text-secondary','fa fa-clipboard']"></i>
          
        </button>
      </div>
    </div>

    <div class="GA4Analytics d-flex flex-column">
      <button :class="[showGA4Analytics?'alert alert-info':'']" @click="toggleGa4view">
        {{ !showGA4Analytics?'Track UTM Analytics':'close' }}
      </button>

      <div v-if="showGA4Analytics">
        <ga4analytics :campaign="trackingData"/>
      </div>

    </div>
  </div>

  </div>







  <div class="progressbar w-100 d-flex flex-column gap-2 mt-5">
        <p class="alert alert-warning rounded-2 fw-bold text-center">Campaign Progress</p>
        <div class="progress">
          <div :class="['progress-bar', 'progress-bar-striped', 'bg-warning', progressvalue < 100 ? 'progress-bar-animated' : '']" role="progressbar" :style="{ width: progressvalue + '%' }" :aria-valuenow="progressvalue" aria-valuemin="0" aria-valuemax="100"><p class="mt-3 text-success fw-bold">{{ progressvalue.toFixed(2) }} %</p></div>
        </div>
  </div>
  </div>
</template>
<script>
import { onMounted, ref, computed } from 'vue';
import { useAuthStore, useCampaignsStore } from '../../../store';
import { postmediaforinfluencerSocials, updatepostmetrics, retrievebrandSocials, retrieveutmLinks, deletepostmetrics} from '../../../services/campaignService';
import { fetchSignupOptions } from '../../../services/authService';
import ga4analytics from '../CampaignAnalytics/ga4analytics.vue';
import { formatLargeNumber } from '../../../main';

export default {
  props: {
    trackingData: {
      type: Object,
      required: true,
    },

  },
  components : {
    ga4analytics
  },
  setup(props, {emit}) {
    // Define local state using ref
    const selectedTrackingMethod = ref('');
    const trackingDetails = ref('');
    const progressvalue=ref(0);
    const authStore = useAuthStore();
    const platforms = ref([]);
    const links = ref([]);
    const newLink = ref({ platform: '', url: '' });
    const selectedSubview = ref('');
    const isLoading = ref(false)
    const campaignStore = useCampaignsStore();
    // const parsedMetrics = ref({});
    const noTrackingMessage = 'Add Links to track your media progress';
    const utmLinks = ref([]);
    const copyStatus = ref('Copy');
    const utmInputRefs = ref([]);
    const showGA4Analytics = ref(false);

    // Method to show tracking details based on the selected tracking method
    const showTrackingDetails = (trackingMethod) => {
      selectedTrackingMethod.value = trackingMethod;

      // Determine the tracking details text
      switch (trackingMethod) {
        case 'influencerSocials':
          trackingDetails.value = 'As influencer, your social media will be tracked for relevant data. This data will help the brand/business take better decisions about the campaign and track its progress';
          break;
        case 'brandSocials':
          trackingDetails.value = 'This method makes brand/sponsor social mediia a metric. Brands can track their social media growth and changes in user behaviour caused directly/indirectly by the creators and influencers. All influencers associated with the campaign will be equally responsible for this metric to progress which will ultimately determine overall campaign progress.';
          break;
        case 'utmLinks':
          trackingDetails.value = 'This method tracks user activity on your website to see how effective the campaign is. Paste these links on appropriate platforms when posting content as directed by campaign owner.';
          break;
        default:
          trackingDetails.value = 'This method uses utm links that creators and/or influencers share with their audience. These links are tracked to measure progress of campaign goals. Each influencer associated with the campaign is tracked seperately. Sometimes compensation depend on each influencers indivdual performance. On getting selected for this ccampaign you will be given relevant utm links to use accross social media.';
      }
    };
    


    const showSelectedSubView = (subView) => {
      selectedSubview.value=subView;

    }

    const currentInfluencer = computed(() => {
      // Find the influencer by matching influencer_id
      console.log(props.trackingData.influencers)
      return props.trackingData.influencers.find(
          (influencer) => influencer.influencer_id === authStore.userProfile.id);
    });



    onMounted(async ()=>{
      trackingDetails.value=`Uses methods to track campaign progress. When an influencer/creator is approved for the campaign they are assigned their unique set of utm links based on the platform the platform they choose to post the ads on. This campaign has currently ${props.trackingData.trackingMethods.length} tracking methods active.`
      progressvalue.value=parseFloat(props.trackingData.progress)*100;
      // if (currentInfluencer.value && currentInfluencer.value.postrackingMetric) {
      //   parsedMetrics.value = parseTrackingMetrics(currentInfluencer.value.postrackingMetric);
      // }
      try {
        const options = await fetchSignupOptions();
        platforms.value = options.platforms;
      } catch (error) {
        console.error('Failed to fetch platforms:', error);
      }
    });

    const addLink = () => {
      if (links.value.length < 5 && newLink.value.platform && newLink.value.url) {
        links.value.push({ ...newLink.value });
        newLink.value = { platform: '', url: '' }; // Reset input fields
      }
    };

    // Remove a link
    const removeLink = (index) => {
      links.value.splice(index, 1);
    };

    // Submit links
    const submitLinks = async () => {
      try {
        const payload = links.value.map((link) => ({
          platform: link.platform,
          url: link.url,
        }));
        isLoading.value=true;
        await postmediaforinfluencerSocials(props.trackingData.id, payload);
        const updateCampaignsData = await campaignStore.getCampaignDetails(props.trackingData.id);
        emit('updateCampaignData',updateCampaignsData)
        links.value = []; // Reset links after submission
        isLoading.value=false;
        // parsedMetrics.value = parseTrackingMetrics(currentInfluencer.value.postrackingMetric);
        // console.log(parsedMetrics)
        selectedSubview.value='Media Progress'
      } catch (error) {
        isLoading.value=false;
        console.error('Failed to submit links:', error);
        alert('Failed to submit links. Please try again.');
      }
    };

    const influencersToShow = computed(() => {
      if (authStore.userProfile.role === 'influencer') {
        return [currentInfluencer.value];  // Display only the current influencer data
      }
      return props.trackingData.influencers;  // Display data for all influencers if the user is a brand
    });


    const deletePostMetric = async (influencer_id, link, platform) => {
  try {
    isLoading.value = true;

    // Call the delete function to make the API request (e.g., `deletepostmetrics`)
    const response = await deletepostmetrics(props.trackingData.id, link, platform); // Replace with actual campaignId
    console.log('Delete Success:', response.data);

    // Filter the influencer object based on influencer_id
    const influencerIndex = influencersToShow.value.findIndex(i => i.influencer_id === influencer_id);
    
    // If influencer is not found, exit the function
    if (influencerIndex === -1) {
      isLoading.value = false;
      return;
    }

    // Get the influencer object
    const influencer = influencersToShow.value[influencerIndex];

    // Ensure the influencer has parsedMetrics
    if (!influencer.parsedMetrics) {
      isLoading.value = false;
      return;
    }

    // Get the platform's data for the influencer's post metrics
    const platformData = influencer.parsedMetrics[influencer_id]?.[platform];

    // If no platform data, exit the function
    if (!platformData) {
      isLoading.value = false;
      return;
    }

    // Filter out the post link to be deleted
    influencer.parsedMetrics[influencer_id][platform] = platformData.filter(post => post.url !== link);

    // Update the influencersToShow.value with the new influencer data
    influencersToShow.value = [...influencersToShow.value.slice(0, influencerIndex), influencer, ...influencersToShow.value.slice(influencerIndex + 1)];

    isLoading.value = false;
  } catch (error) {
    console.error('Delete Error:', error);
    isLoading.value = false;
    // Optionally, handle error and show a message to the user
  }
};





 // Parse tracking metrics into a usable format
 const parsedMetrics = computed(() => {
  const result = {};

  influencersToShow.value.forEach((influencer) => {
    const influencerMetrics = influencer.postrackingMetric;

    Object.entries(influencerMetrics).forEach(([platform, posts]) => {
      if (!result[influencer.influencer_id]) {
        result[influencer.influencer_id] = {};
      }

      result[influencer.influencer_id][platform] = posts.map((postData) => {
        const [url, data] = Object.entries(postData)[0];

        // Determine the type of metric based on the keys in the data
        const type = data.metrics.likes_target && data.metrics.likes_obtained
          ? 'likes'
          : 'views';

        // Parse obtained and target values as integers
        const obtained = parseInt(
          type === 'likes'
            ? data.metrics.likes_obtained
            : data.metrics.views_obtained,
          10
        );
        const target = parseInt(
          type === 'likes'
            ? data.metrics.likes_target
            : data.metrics.views_target,
          10
        );

        // Calculate progressPercentage after parsing
        const progressPercentage = parseFloat((obtained / target) * 100).toFixed(2);

        return {
          url,
          metrics: {
            obtained,
            target,
            progressPercentage,
            type,
          },
        };
      });
    });
  });

  return result;
});

  const updatepostMetrics =  async () => {
      try {
        isLoading.value=true;
        await updatepostmetrics(props.trackingData.id)
        isLoading.value=false;
        const updateCampaignsData = await campaignStore.getCampaignDetails(props.trackingData.id);
        emit('updateCampaignData',updateCampaignsData)
      }
      catch(error){
        isLoading.value=false;
      }
        
    }


    const retrieveBrandSocialsData = async () => {
  try {
    isLoading.value = true;
    console.log('inside');

    // Fetch data
    const response = await retrievebrandSocials(props.trackingData.id);

    // Log the entire response object to understand its structure
    console.log('Response:', response);

    // Ensure the response is an object and contains the 'followers' field
    if (response && typeof response === 'object' && response.hasOwnProperty('followers')) {
      console.log('Followers:', response['followers']);
      props.trackingData.brandCurrent = response['followers'];  // Update the variable
      emit('updateCampaignData', props.trackingData);  // Emit updated data to parent
    } else {
      console.error('Followers field not found or invalid response structure');
    }

    isLoading.value = false;
  } catch (error) {
    console.error('Error fetching brand socials:', error);
    isLoading.value = false;
  }
};




    // UTM Links section

    const generateUtmLinks = async (influencerId) => {
      try {
        isLoading.value = true
        const data = await retrieveutmLinks(props.trackingData.id,influencerId);
        utmLinks.value = data.data.utmLinks
        isLoading.value = false;
      // console.log(utmLinks)

      }
      catch(error){
        isLoading.value=false;
        console.log(error)
      }
      


    }

    const copyToClipboard = async (index) => {
      try {
        const inputElement = utmInputRefs.value[index];
        if (inputElement) {
          inputElement.select();
          document.execCommand("copy"); // Copy the text
          // Alternatively, use modern Clipboard API:
          // await navigator.clipboard.writeText(inputElement.value);

          copyStatus.value = "Copied!";
          setTimeout(() => {
            copyStatus.value = "Copy";
          }, 1500);
        } else {
          throw new Error("Input element not found");
        }
      } catch (error) {
        console.error("Failed to copy text:", error);
        copyStatus.value = "Failed!";
      }
    };

    // Return variables and methods to the template

    //GA4 Analysis

    const toggleGa4view = () => {
      showGA4Analytics.value = !showGA4Analytics.value;
    }
    return {
      selectedTrackingMethod,
      trackingDetails,
      showTrackingDetails,
      progressvalue,
      currentInfluencer,
      addLink,
      removeLink,
      submitLinks,
      platforms,
      newLink,
      links,
      selectedSubview,
      showSelectedSubView,
      isLoading,
      parsedMetrics,
      influencersToShow,
      noTrackingMessage,
      authStore,
      updatepostMetrics,
      retrieveBrandSocialsData,
      generateUtmLinks,
      utmLinks,
      copyToClipboard,
      utmInputRefs,
      copyStatus,
      showGA4Analytics,
      toggleGa4view,
      formatLargeNumber,
      deletePostMetric
    };
  },
};
</script>


<style scoped>
/* Styling for Tracking */
.tracking-item {
  padding: 0.75rem;
  background-color: #ffbf702e;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  border-left: 4px solid #ffc85b;
  color: #ff5b76;
}
button.selected{
  background-color: #ff8398 !important;
}
a{
  color: #ff2c65;
}
</style>
