<template>
    <div>
      <EnhancedMultiselect 
        id="language" 
        label="Targeted demographics (languages)" 
        :options="availableOptions.languages" 
        v-model="form.language"
      />
      <!-- Company Name -->
      <div class="mb-3">
        <label for="company_name" class="form-label">Company Name:</label>
        <input
          type="text"
          class="form-control"
          id="company_name"
          v-model="form.company_name"
          placeholder="Company Name"
          required
        />
      </div>


        <!-- Industry Selection -->
        <EnhancedMultiselect
        id="industry"
        label="Industry"
        :options="availableOptions.industries"
        v-model="form.industry"
      />


      <div class="mb-3">
        <label for="dob" class="form-label">When was your Brand/business started?</label>
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
        label="Brand/Business Niche"
        :options="availableOptions.niches"
        v-model="form.niche"
      />
    </div>

  </template>
  
  <script>
  import EnhancedMultiselect from '../utilities/EnhancedMultiselect.vue';
  export default {
    props: {
      form: {
        type: Object,
        required: true
      },
      availableOptions: {
        type: Object,
        required: true
      }
    },
    components: { EnhancedMultiselect },
  };
  </script>
  
  <style scoped>
  .mb-3 {
    margin-bottom: 1rem;
  }
  </style>
  