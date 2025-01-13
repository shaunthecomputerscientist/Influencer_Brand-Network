<template>
    <section class="signup-section">
      <div class="d-flex">
        <img width="400" class="rounded-5" src="\src\assets\signup\signupImg.png" alt="">
      </div>
      <div class="overflow-scroll">
        <header class="d-flex align-items-center justify-content-center text-secondary">
        <h3 v-if="!role" style="text-decoration: underline;">What best describes You?</h3>
        <h3 v-else style="text-decoration: underline;">Fill all the fields:</h3>
      </header>
  
      <!-- Step 1: Role selection -->
      <div class="d-flex justify-content-around sticky-top bg-transparent p-2 w-100">
        <!-- The buttons stay on top of the screen (sticky-top) -->
        <button 
          @click="setRole('influencer')" 
          :class="[role === 'influencer' ? 'active' : '']">
          Influencer
        </button>
        <button 
          @click="setRole('brand')" 
          :class="[role === 'brand' ? 'active' : '']">
          Brand
        </button>
      </div>
  
      <!-- Step 2: Display relevant form based on role -->
      <div v-if="role" class="mt-4 fw-bold overflow-scroll" ref="formSection" :key="role">
        <GenericForm 
          :initialData="form" 
          :availableOptions="availableOptions" 
          :isUpdateMode="false" 
        />
      </div>

      </div>
    
    </section>
  </template>
<script>
import { ref, onMounted, nextTick } from 'vue';
import GenericForm from '../components/auth/GenericForm.vue';
import { fetchSignupOptions } from '../services/authService';

export default {
  components: {
    GenericForm,
  },
  setup() {
    const role = ref('');
    const form = ref({
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      role: '',  // Add the role property here
    });

    const availableOptions = ref({
      languages: [],
      niches: [],
      platforms: [],
      industries: [],
    });

    const setRole = async (selectedRole) => {
      role.value = selectedRole;
      form.value.role = selectedRole; // Update form object with selected role

      // Wait for the DOM to render, then scroll to form section
      await nextTick();
      scrollToForm();
    };

    const scrollToForm = () => {
      const formElement = document.querySelector(".signup-section .mt-4");
      if (formElement) {
        formElement.scrollIntoView({ behavior: 'smooth' });
      }
    };

    onMounted(async () => {
      try {
        const options = await fetchSignupOptions();
        availableOptions.value = options;
      } catch (error) {
        console.error('Failed to fetch signup options:', error);
      }
    });

    return {
      role,
      form,
      availableOptions,
      setRole,
    };
  },
};
</script>

<style scoped>
.signup-section {
  width: 100%;
  max-height: 90vh;
  margin: 0 auto;
  padding: 20px;
  display: flex;
  gap: 2rem;
}

.sticky-top {
  position: -webkit-sticky;
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #343a40; /* Dark background for contrast */
}

.text-danger {
  color: red;
}
</style>