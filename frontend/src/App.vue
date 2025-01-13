<script>
import Navbar from './components/LandingPage/Navbar.vue';
import ErrorPopup from './components/utilities/ErrorPopup.vue';
export default {
  name: 'App',
  components: {Navbar, ErrorPopup},
};
</script>

<template>
  
  <Navbar/>

  <router-view/>
 
</template>


<style scoped>
</style>