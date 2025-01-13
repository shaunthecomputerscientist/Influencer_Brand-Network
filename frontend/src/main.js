import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index'; // Import the router instance
import {pinia} from './store/index'; // Import the Vuex store instance
import 'bootstrap/dist/css/bootstrap.min.css';
import Multiselect from 'vue-multiselect';
import 'vue-multiselect/dist/vue-multiselect.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.js';
import { jwtDecode } from 'jwt-decode';
const app = createApp(App);
const appName = import.meta.env.VITE_APP_NAME;

const isTokenExpired = (token) => {
    try {
      const decoded = jwtDecode(token);
      const currentTime = Date.now() / 1000;
      return decoded.exp < currentTime;
    } catch (error) {
      console.error('Error decoding token:', error);
      return true;
    }
  };
const goBack = () => {
  window.history.back();
};

export const vViewport = {
    beforeMount(el, binding) {
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            binding.value(); // Call the provided function
            observer.unobserve(el); // Stop observing after the first view
          }
        },
        { threshold: 0.4 } // 50% of element should be visible
      );
      observer.observe(el);
    }
  };

const formatLargeNumber = (num) => {
  if (num >= 1e12) {
    return (num / 1e12).toFixed(2) + 'T'; //
  }
  else if (num >= 1e9) {
      return (num / 1e9).toFixed(2) + 'B'; // Billion
  } else if (num >= 1e6) {
      return (num / 1e6).toFixed(2) + 'M'; // Million
  } else if (num >= 1e3) {
      return (num / 1e3).toFixed(2) + 'K'; // Thousand
  } else {
      return num.toString(); // Small numbers, no formatting
  }
}

app.directive('viewport', vViewport);
app.use(pinia); // Use the Vuex store instance
app.use(router); // Use the router instance
app.component('Multiselect', Multiselect);
app.mount('#app');

export {appName, isTokenExpired, goBack, formatLargeNumber};