<template>
    <div>
      <EnhancedMultiselect 
        id="language" 
        label="Language" 
        :options="availableOptions.languages" 
        v-model="form.language" 
      />
      <div class="mb-3">
    <label for="gender" class="form-label">Gender:</label>
    <select 
      class="form-select" 
      id="gender" 
      v-model="form.gender" 
      placeholder="You Identify As?"
    >
        <option value="" disabled>You Identify As?</option>
        <option value="male">Male</option>
        <option value="female">Female</option>
        <option value="non-binary">Non-Binary</option>
        <option value="other">Other</option>
    </select>
</div>
  
      <div class="mb-3">
        <label for="dob" class="form-label">Date of Birth:</label>
        <input 
          type="date" 
          class="form-control" 
          id="dob" 
          v-model="form.dob" 
          placeholder="dob" 
        />
      </div>
  
      <EnhancedMultiselect 
        id="niche" 
        label="Niche" 
        :options="availableOptions.niches" 
        v-model="form.niche" 
      />
      
      <EnhancedMultiselect 
        id="platforms" 
        label="Platforms" 
        :options="availableOptions.platforms" 
        v-model="form.selectedPlatforms" 
      />
      
      <div v-for="(platform, index) in form.selectedPlatforms" :key="platform">
        <div class="mb-3">
          <label :for="`url_${platform}`" class="form-label">{{ platform }} URL:</label>
          <input
            type="url"
            :id="`url_${platform}`"
            v-model="form.platforms[platform]"
            class="form-control"
            :placeholder="`${platform} URL`"
            required
          />
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import EnhancedMultiselect from '../utilities/EnhancedMultiselect.vue';
  import ErrorPopup from '../utilities/ErrorPopup.vue';
  
  export default {
    components: {
      EnhancedMultiselect,
      ErrorPopup,
    },
  
    props: {
      form: Object,
      availableOptions: Object,
    },
  
    mounted() {
      console.log('Available Options:', this.availableOptions);
      console.log('Form:', this.form);
    },
  };
  </script>
  