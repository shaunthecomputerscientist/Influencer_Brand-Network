<template>
    <div class="mt-2">
      <Hero />
      
      
      <MidSection>
      </MidSection>
      
      <Footer>

      </Footer>
    </div>
  </template>
  
  <script>
  import { defineComponent } from 'vue';
  import Hero from './Hero.vue';
  import MidSection from './MidSection.vue';
  import Footer from './Footer.vue';
  import Navbar from './Navbar.vue';
  
  export default defineComponent({
    name: 'LandingPage',
    components: {
      Hero,
      MidSection,
      Footer,
      Navbar
    },
    setup() {
      // This is where you can define reactive properties, methods, and lifecycle hooks.
      
      // Example of logging to console when the component is set up
      console.log('LandingPage component is set up');
  
      // Returning nothing in setup means we don't need to expose any data or methods to the template.
      return {};
    }
  });
  </script>
  
  <style scoped>
  /* Scoped styles for the LandingPage component */
  </style>
  