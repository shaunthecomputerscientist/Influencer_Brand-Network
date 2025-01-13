<template>
    <div v-if="currentView === 'search'" class="d-flex flex-column align-items-start justify-content-center w-100">
      <header class="fw-bold alert alert-warning w-100">Search Influencers</header>
      <!-- Filter Selection -->
      <div class="d-flex align-items-center w-100 justify-content-center gap-2 p-2">
        <EnhancedMultiselect
          id="select-filter"
          v-model="activeFilters"
          :options="filterOptions"
          label="Search by"
          class="w-100 mb-2"
        />
        <button @click="resetFilters" class="mb-3">
          <i class="fa fa-close fs-4"></i>
        </button>
      </div>
  
      <!-- Search Bar -->
      <div class="search-bar d-flex justify-content-around flex-wrap gap-2 p-3 w-100">
        <input v-if="activeFilters.includes('username')" v-model="filters.username" type="text" placeholder="Username" class="form-control mb-2" />
        <input v-if="activeFilters.includes('name')" v-model="filters.name" type="text" placeholder="Name" class="form-control mb-2" />
        <input v-if="activeFilters.includes('followers')" v-model="filters.followers" type="number" placeholder="Followers" class="form-control mb-2" />
        <input v-if="activeFilters.includes('engagement')" v-model="filters.engagement" type="number" placeholder="Engagement" class="form-control mb-2" />
        
        <EnhancedMultiselect
          v-if="activeFilters.includes('niches')"
          id="niches"
          v-model="filters.niches"
          :options="niches"
          label="Select Niche"
          class="w-100 mb-2"
        />
  
        <EnhancedMultiselect
          v-if="activeFilters.includes('languages')"
          id="languages"
          v-model="filters.languages"
          :options="languages"
          label="Select languages"
          class="w-100 mb-2"
        />
        
        <select v-if="activeFilters.includes('gender')" v-model="filters.gender" class="form-control mb-2">
            <option value="" disabled>Select Gender</option>
            <option v-for="gender in genders" :key="gender" :value="gender">{{ gender.charAt(0).toUpperCase() + gender.slice(1) }}</option>
        </select>

        <!-- <div class="mb-3">
      <label for="location" class="form-label">Location:</label>
      <select class="form-control" id="location" v-model="filters.location" required>
        <option class="w-50" value="" disabled>Select Location</option>
        <option class="" v-for="location in locations" :key="location" :value="location">
          {{ location }}
        </option>
      </select>
    </div> -->


  
        <EnhancedMultiselect
          v-if="activeFilters.includes('platforms')"
          id="platforms"
          v-model="filters.platforms"
          :options="platforms"
          label="Select Platform"
          class="w-100 mb-2"
        />
  
        <button @click="searchInfluencers" class="p-2">Search</button>
      </div>
  
      <!-- Search Results -->
      <div v-if="filteredInfluencers.length === 0 && initialSearch" class="d-flex flex-column align-items-center justify-content-center w-100 fw-bold alert alert-secondary mt-2">
        <p>No Influencers Match Your Search</p>
      </div>
      
      <div v-else class="d-flex gap-3 overflow-auto w-100 p-3 hide-scrollbar" style="max-width: 100%; white-space: nowrap;">
        <influencerCard
          v-for="influencer in filteredInfluencers"
          :key="influencer.id"
          :influencerData="influencer"
          :currentUserId="authStore.userProfile.id"
        />
      </div>
    </div>

    <div class="d-flex gap-3 overflow-auto w-100 p-3 hide-scrollbar" style="max-width: 100%; white-space: nowrap;">
        <influencerCard
          v-for="influencer in similarInfluencers"
          :key="influencer.id"
          :influencerData="influencer"
          :currentUserId="authStore.userProfile.id"
        />
      </div>
  </template>
  
  <script>
  import { ref, computed, onMounted } from 'vue';
  import{ useInfluencerStore } from '../../store';
  import { useAuthStore } from '../../store';
  import EnhancedMultiselect from '../utilities/EnhancedMultiselect.vue';
  import { fetchSignupOptions } from '../../services/authService';
  import influencerCard from './influencerCard.vue';
  
  export default {
    name: 'Influencers',
    components: { influencerCard, EnhancedMultiselect },
    setup() {
      // Store and reactive variables
      const influencerStore = useInfluencerStore();
      const authStore = useAuthStore();
  
      const niches = ref([]);
      const initialSearch = ref(false);
      const platforms = ref([]);
      const languages = ref([]);
      const currentView = ref('search');
      const genders = ref([]);
      const locations = ref([])
      const similarInfluencers = ref([]);
  
      // Filter data
      const filterOptions = [
        'username',
        'name',
        // 'location',
        'engagement',
        'niches',
        'gender',
        'platforms',
        'followers',
        'languages'
      ];
      const activeFilters = ref([]);
  
      const filters = computed(() => influencerStore.filters);
      const filteredInfluencers = computed(() => influencerStore.getFilteredInfluencers);
  
      // Fetch options and initialize data
      onMounted(async () => {
        try {
          const options = await fetchSignupOptions();
          if (authStore.userProfile.role==='influencer'){
            await influencerStore.initialInfluencers();
            similarInfluencers.value = influencerStore.similarInfluencers
            console.log(similarInfluencers)
          }
          niches.value = options.niches;
          platforms.value = options.platforms;
          languages.value = options.languages;
          genders.value = options.gender
          locations.value = options.locations
        } catch (error) {
          console.error('Failed to load niches:', error);
        }
      });
  
      // Search influencers function
      const searchInfluencers = async () => {
        initialSearch.value = true;
        await influencerStore.searchInfluencers();
      };
  
      // Reset filters function
      const resetFilters = () => {
        influencerStore.clearFilters();
        activeFilters.value = [];
      };
  
      return {
        currentView,
        filterOptions,
        activeFilters,
        filters,
        filteredInfluencers,
        niches,
        platforms,
        authStore,
        searchInfluencers,
        resetFilters,
        languages,
        genders,
        initialSearch,
        similarInfluencers,
        locations
      };
    },
  };
  </script>  