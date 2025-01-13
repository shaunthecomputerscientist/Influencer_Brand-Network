<template>
    <section class="edit-profile-section">
      <header>
        <!-- <h3>Edit {{ user.first_name }} {{ user.last_name }}'s Profile</h3> -->
      </header>
  
      <!-- Step 1: Hardcoded Role -->
      <!-- <div v-if="!user.role" class="d-flex bg-dark justify-content-around sticky-top p-2">
        <button 
          :class="['btn', user.role === 'influencer' ? 'btn-success' : 'btn-primary']" 
          disabled>
          Edit as Influencer
        </button>
        <button 
          :class="['btn', user.role === 'brand' ? 'btn-success' : 'btn-primary']" 
          disabled>
          Edit as Brand
        </button>
      </div> -->
  
      <!-- Step 2: Display relevant form based on role -->
      <div class="mt-4" ref="formSection">
        <GenericForm 
          :initialData="form" 
          :availableOptions="availableOptions" 
          :isUpdateMode="true"
        />
      </div>
    </section>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  import { useAuthStore } from '../store';
  import GenericForm from '../components/auth/GenericForm.vue';
  import { fetchSignupOptions } from '../services/authService';  
  export default {
  components: {
    GenericForm,
  },
  setup() {
    const authstore = useAuthStore()
    const user = authstore.userProfile; // Get user info from Vuex store
    const form = ref({ ...user }); // Initialize form with user data
    const availableOptions = ref({
      languages: [],
      niches: [],
      platforms: [],
      industries: [],
    });

    onMounted(async () => {
      // Fetch available options for the form
      try {
        const options = await fetchSignupOptions();
        availableOptions.value = options;
      } catch (error) {
        console.error('Failed to fetch signup options:', error);
      }
    });

    return {
      user,
      form,
      availableOptions,
    };
  },
};
</script>
  
  <style scoped>
  .edit-profile-section {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .sticky-top {
    position: sticky;
    top: 0;
    z-index: 100;
    background-color: #343a40; /* Dark background for contrast */
  }
  
  .text-danger {
    color: red;
  }
  </style>
  