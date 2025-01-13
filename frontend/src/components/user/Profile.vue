<template class="section d-flex flex-column align-items-center justify-content-center">
  <section v-if="profile" class="d-flex flex-column w-100 mt-3">

    <div class="d-flex flex-column align-items-center justify-content-center rounded gap-2" v-if="profile">
      <div class="d-flex flex-column align-items-center justify-content-center gap-2">
        <div class="bg-transparent d-flex align-items-center justify-content-center">
          <img class="w-50 p-3" :src="imageurl" alt="">
        </div>

        <h6 v-if="profile" class="fw-bold text-underline">{{ profile.first_name }} {{ profile.last_name }}</h6>

        <div v-if="personalprofile" class="d-flex align-items-center justify-content-center">
          <button @click="editProfile">
            Edit Profile
          </button>
          
        </div>
      </div>
      <div v-if="authStore.userProfile.role==='admin'" class="d-flex justify-content-end gap-2">
            <button @click="increaseFlag" class="btn btn-danger">+</button>
            <p> {{ flagCount }}</p>
            <button @click="decreaseFlag" class="btn btn-success">-</button>
      </div>
     

      <!-- Common fields -->
      <div class="section d-flex p-3 flex-column gap-2 align-items-center justify-content-center text-white flex-wrap text-wrap">
      <button><strong>Username:</strong> {{ profile.username }}</button>
      <button><a :href="'mailto:' + profile.email" class="text-black">
          <strong>Email:</strong> {{ profile.email }}
        </a>
      </button>

        <button><strong>Location:</strong> {{ profile.location }}</button>
        <button class="text-wrap"><strong>{{`${ profile.role==='influencer'?'Bio:':'Description:' }`}}</strong> {{ profile.description }}</button>
        <button v-if="profile.role === 'brand'"><strong>Company Name:</strong> {{ profile.company_name }}</button>
        <button v-if="profile.role === 'brand'" class="text-wrap"><strong>Industry:</strong> {{ profile.industry.join(', ') }}</button>

        <button v-if="profile.role === 'influencer'"><strong>Gender:</strong> {{ profile.gender }}</button>
        <button class="text-wrap" v-if="profile.role === 'influencer'"><strong>Date of Birth:</strong> {{ profile.dob }}</button>
        <button class="text-wrap" v-if="profile.role === 'influencer'"><strong>Languages:</strong> {{ profile.language.join(', ') }}</button>
      <button class="text-wrap"><strong class="text-wrap">{{ profile.role==='influencer'?'Niches:':'Brand Niche:' }}</strong> {{ profile.niche.join(', ') }}</button>


      <!-- {{ profile.socialData }} -->
      <div class="w-100 d-flex gap-3"v-if="profile.role === 'influencer'">
          <div v-for="(url, platform) in profile.platforms" :key="platform">
            <div class="d-flex w-100 gap-2 fs-6 border tooltipp">
              <button>
                <a :class="'fa-brands fa-' + platform.toLowerCase() +' fw-bold text-dark fs-3'" :href="url" @click.prevent="openUrl(url)" target="_blank" rel="noopener noreferrer"></a>
              </button>
              <div v-if="profile.socialData && profile.socialData[platform.toLowerCase()]" class="tooltiptext">
            <!-- <p><strong>Bio:</strong> {{ profile.socialData[platform.toLowerCase()].socialData.bio }}</p> -->
            <p><strong>Followers:</strong> {{ profile.socialData[platform.toLowerCase()].socialData.followers || profile.socialData[platform.toLowerCase()].socialData.statistics.followers }}</p>
            <p v-if="!videoPlatforms.some(plat => plat.includes(platform.toLowerCase()))"><strong>Following:</strong> {{ profile.socialData[platform.toLowerCase()].socialData.following}}</p>
            <p  v-else><strong>View Count:</strong> {{ profile.socialData[platform.toLowerCase()].socialData.statistics.view_count}}</p>
            <p><strong>Engagement:</strong> {{ Math.round(profile.socialData[platform.toLowerCase()].socialData.engagement *100)/100 || Math.round(profile.socialData[platform.toLowerCase()].socialData.statistics.engagement *100)/100 }}%</p>
            <p><strong>Media Count:</strong> {{ profile.socialData[platform.toLowerCase()].socialData?.media_count || profile.socialData[platform.toLowerCase()].socialData.statistics?.media_count }}</p>
            <!-- <img :src="profile.socialData[platform.toLowerCase()].socialData.image_link" alt="Profile Image" class="profile-image"/> -->
        </div>

            </div>
          </div>
          
      </div>

      </div>

    </div>

    <!-- Show "Edit Profile" button only for personal profile -->
    
  </section>
  <div v-else class="d-flex align-items-center justify-content-center h-100">
    <div class="spinner-grow text-theme fs-1">
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref, watch } from 'vue';
import { useAuthStore } from '../../store/modules/auth'; // Import the auth store from Pinia
import router from '../../router/index';
import { useRoute } from 'vue-router';
import { fetchUserProfileById, fetchUserProfile } from '../../services/userservice';
import { increaseInfluencerFlag, decreaseInfluencerFlag } from '../../services/adminService';

export default {
  setup() {
    const authStore = useAuthStore();
    const route = useRoute();
   
    
    const profile = ref(null); // Separate ref for fetched profile data
    const personalprofile = ref(false); // Flag for personal profile

    // Computed property for the logged-in user's profile from the store
    const user = computed(() => authStore.userProfile);
    // const flagCount = computed(() =>profile.value.flagCount )
    const flagCount = ref(0)
    const videoPlatforms = ['youtube']

    // Function to fetch profile based on the route or current user
    const fetchProfile = async () => {
      const userId = route.params.id; // Get the ID from the URL
      try {
        if (userId) {
          // Fetch the profile by ID (for viewing other profiles)
          const profileData = await fetchUserProfileById(userId);
          profile.value = profileData;
          flagCount.value = profile.value?profile.value.flagCount:0
          personalprofile.value = profile.value.id === user.value?.id;
        } else if (localStorage.getItem('ProfileUpdatedRecently')){

          const profileData = await fetchUserProfile()

          profile.value = profileData.profile;
          personalprofile.value = profile.value.id === user.value?.id;

        }

        else {
           // Fetch the logged-in user's profile
          profile.value = authStore.userProfileData; // Assign personal profile data
          console.log(profile)
          personalprofile.value = true; // This is the personal profile
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
      }
    };

    // Watch for route changes to refetch the profile when navigating
    watch(route, () => {
      fetchProfile();
    });

    // Fetch the profile when the component mounts
    onMounted(() => {
      // authStore.checkUserStatus();
      fetchProfile();
    });

    // Edit profile logic
    const editProfile = () => {
      router.push('/user/profile/edit'); // Navigate to the profile edit page
    };

    // Computed property for the profile image URL
    const imageurl = computed(() => {
      return profile.value && profile.value.profile_image
        ? `${import.meta.env.VITE_APP_BACKEND_URL}/${profile.value.profile_image}`
        : '';
    });

    //Admin features

    const increaseFlag = async () => {
      try {
        await increaseInfluencerFlag(profile.value.id, "Flagging for review"); // Example feedback message
        flagCount.value+=1;
        // window.dispatchEvent(new CustomEvent('show-error-popup', { detail: { message: "Flag increased successfully!" } }));
      } catch (error) {
        const errorMessage = error.response?.data?.message || "Error occurred while flagging.";
        // window.dispatchEvent(new CustomEvent('show-error-popup', { detail: { message: errorMessage } }));

      }
    };

    const decreaseFlag = async () => {
      try {
        await decreaseInfluencerFlag(profile.value.id);
        // window.dispatchEvent(new CustomEvent('show-error-popup', { detail: { message: "Flag decreased successfully!" } }));
        if (flagCount.value>0){
          flagCount.value-=1;
        }
      } catch (error) {
        const errorMessage = error.response?.data?.message || "Error occurred while removing flag.";
        // window.dispatchEvent(new CustomEvent('show-error-popup', { detail: { message: errorMessage } }));
      }
    };

    return {
      profile,
      personalprofile,
      editProfile,
      imageurl,
      openUrl: (url) => window.open(url, '_blank'),
      increaseFlag,
      decreaseFlag,
      authStore,
      flagCount,
      videoPlatforms
    };
  },
};
</script>

<style scoped>
button{
  box-shadow: 2px 0.1rem 0.2rem rgba(77, 77, 77, 0.433);
  border: 1px solid rgba(197, 188, 145, 0.617);
  background-color: rgba(250, 235, 215, 0.493);
  color: black;
}
.text-theme{
  color: rgba(250, 235, 215, 0.493);
}
.tooltipp {
  position: relative; /* Positioning context for the tooltip */
  display: inline-block; /* Keeps the tooltip next to the status indicator */

}
.section{
  background-color: rgba(255, 225, 144, 0.121);
}

.tooltiptext {
  visibility: hidden; /* Hidden by default */
  width: 10rem;
  background-color: rgb(255, 188, 144);
  color: #ffffff;
  text-align: center;
  border-radius: 1rem;
  padding: 5px 0;
  position: absolute;
  z-index: 1;
  box-shadow: 0.2rem 0.2rem 0.5rem rgb(255, 210, 173);
  bottom: 100%; /* Position above the indicator */
  /* left: 30%; */
  margin: 2rem 2rem;
  opacity: 0; /* Start as invisible */
  transition: opacity 0.3s; /* Smooth transition */
}

.tooltipp:hover .tooltiptext {
  visibility: visible; /* Show the tooltip on hover */
  opacity: 1; /* Make it visible */
}
img{
  border: 2px solid rgba(131, 104, 104, 0);
  border-radius: 5rem;
  background-color: antiquewhite;
  box-shadow: 0.2rem 0.2rem 0.5rem rgb(144, 114, 50);
  max-width: 20rem;
  max-height: 20rem;

}
button:hover{
  box-shadow: none;
  transition: 0.25s;
}

</style>
