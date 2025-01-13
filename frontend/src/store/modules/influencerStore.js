import { defineStore } from 'pinia';
import { fetchInfluencers, fetchInitialInfluencers } from '../../services/influencerService';

export const useInfluencerStore = defineStore('influencer', {
  state: () => ({
    filters: {
      username: '',
      name: '',
      location: '',
      engagement: null,
      languages: [],
      niches: [],
      gender: '',
      platforms: [],
      followers: null,
    },
    filteredInfluencers: [],
    similarInfluencers: []
  }),

  actions: {

    async initialInfluencers(){
      try {
        const response = await fetchInitialInfluencers();
        console.log(response.data)
        this.similarInfluencers = Array.isArray(response.data) ? response.data : [];
      } catch (error) {
        console.error('Failed to search similar influencers:', error);
        this.similarInfluencers = [];
      }
    },
    async searchInfluencers() {
      try {
        const response = await fetchInfluencers(this.filters);
        console.log(response.data)
        this.filteredInfluencers = Array.isArray(response.data) ? response.data : [];
      } catch (error) {
        console.error('Failed to search influencers:', error);
        this.filteredInfluencers = [];
      }
    },

    setFilter(key, value) {
      this.filters[key] = value;
    },

    clearFilters() {
      this.filters = {
        username: '',
        name: '',
        location: '',
        engagement: null,
        languages: [],
        niches: [],
        gender: '',
        platforms: [],
        followers: null,
      };
      this.filteredInfluencers = [];
    },
  },

  getters: {
    getFilteredInfluencers: (state) => state.filteredInfluencers,
  },
});

export default useInfluencerStore;