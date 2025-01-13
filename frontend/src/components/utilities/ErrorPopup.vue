<template>
  <div class="w-100 d-flex flex-column align-items-center justify-content-center">
    <div v-if="visible" class="error-popup">

<div class="alert alert-danger d-flex align-items-center justify-content-center p-2">
  <p class="mt-3 fw-bold w-100 d-flex align-items-center justify-content-center text-danger">{{ message }}</p>
  <span class="close-btn btn-danger" @click="closePopup">&times;</span>
</div>
</div>

  </div>
   
  </template>
  
  <script>
  import { ref } from 'vue';
  
  export default {
    name: 'ErrorPopup',
    setup() {
      const visible = ref(false);
      const message = ref('');
  
      const showPopup = (msg) => {
        message.value = msg;
        visible.value = true;
        setTimeout(() => {
          visible.value = false;  // Auto-hide the popup after 5 seconds
        }, 5000);
      };
  
      const closePopup = () => {
        visible.value = false;
      };
  
      // Example of how to trigger the popup from anywhere in the app
      window.addEventListener('show-error-popup', (event) => {
        showPopup(event.detail.message);
      });
  
      return {
        visible,
        message,
        closePopup
      };
    }
  };
  </script>
  
<style scoped>
  .error-popup {
    position: absolute;
    width: 60%;
    border-radius: 5px;
    z-index: 2;
  }
  
  .error-popup-content {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .close-btn {
    cursor: pointer;
    font-size: 1.5rem;
    font-weight: bold;
    padding: 2px 0.5rem;
    border-radius: 0.21rem;
  }
  </style>
  