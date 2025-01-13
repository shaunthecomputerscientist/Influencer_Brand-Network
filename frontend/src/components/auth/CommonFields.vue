<template>
    <div>
      <div class="mb-3">
        <label for="username" class="form-label">Username:</label>
        <input type="text" class="form-control" id="username" v-model="form.username" placeholder="Username" required />
        <div v-if="usernameError" class="text-danger">Username is already taken</div>
      </div>
  
      <div class="d-flex justify-content-between">
        <div class="mb-3">
          <label for="first_name" class="form-label">First Name</label>
          <input type="text" class="form-control" id="first_name" v-model="form.first_name" placeholder="John" required />
        </div>
        <div class="mb-3">
          <label for="last_name" class="form-label">Last Name:</label>
          <input type="text" class="form-control" id="last_name" v-model="form.last_name" placeholder="Doe" required />
        </div>
      </div>
  
      <div class="mb-3">
        <label for="email" class="form-label">{{form.role==='brand'?'Business Email:':'Work Email'}}</label>
        <input type="email" class="form-control" id="email" v-model="form.email" placeholder="Email" required />
        <div v-if="emailError" class="text-danger">{{ emailError }}</div>
      </div>
  
      <div v-if="!isUpdateMode" class="mb-3">
        <label for="password" class="form-label">Password:</label>
        <input type="password" class="form-control" id="password" v-model="form.password" :placeholder="form.password" required :disabled="isUpdateMode"/>
        <h3 v-if="passwordError" class="text-danger fs-6">{{ passwordError }}</h3>
      </div>

      <div class="mb-3">
          <label for="description" class="form-label">{{form.role==='brand'?'Describe Your Brand/Business':'Bio'}}</label>
          <input type="textarea" class="form-control" id="description" v-model="form.description" placeholder="" required />
      </div>


      <div class="mb-3">
      <label for="location" class="form-label">Location:</label>
      <select class="form-control" id="location" v-model="form.location" required>
        <option class="w-50" value="" disabled>Select Location</option>
        <option class="" v-for="location in combinedLocations" :key="location" :value="location">
          {{ location }}
        </option>
      </select>
    </div>

    </div>
  </template>
  
  <script>
import { ref, watch, onMounted } from "vue";
import { checkUsernameAvailability, checkEmailAvailability } from "../../services/authService";

export default {
  props: {
    form: Object,
    isUpdateMode: {
      type: Boolean,
      default: false,
    },
    availableOptions: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    // Define refs for username and email errors
    const usernameError = ref("");
    const emailError = ref("");
    const passwordError = ref("");
    const combinedLocations = ref([]);



    // Populate combined locations when availableOptions is received
    const populateCombinedLocations = () => {
      combinedLocations.value = [];
      if (props.availableOptions.locations && props.availableOptions.locations.countries) {
        props.availableOptions.locations.countries.forEach(country => {
          country.states.forEach(state => {
            combinedLocations.value.push(`${country.name}, ${state}`);
          });
        });
      }
    };

    // Call populateCombinedLocations when availableOptions changes
    watch(() => props.availableOptions, populateCombinedLocations, { immediate: true });

    onMounted(()=>{
      populateCombinedLocations();
    })

    // Function to check availability with a delay
    const checkAvailabilityWithDelay = (checkFunction, value, errorRef) => {
      setTimeout(async () => {
        if (value) {
          const response = await checkFunction(value);
          errorRef.value = response.available ? "" : `${checkFunction === checkUsernameAvailability ? 'Username' : 'Email'} ${response.message}`;
        } else {
          errorRef.value = "";  // Clear the error if input is empty
        }
      }, 2000);  // 2 seconds delay
    };

    // Watch for changes in the username and validate it
    watch(
      () => props.form.username,
      (newUsername) => {
        checkAvailabilityWithDelay(checkUsernameAvailability, newUsername, usernameError);
      }
    );


    // Watch for changes in the email and validate it
    watch(
      () => props.form.email,
      (newEmail) => {
        checkAvailabilityWithDelay(checkEmailAvailability, newEmail, emailError);
      }
    );
    

    const validatePassword = (password) => {
      const hasNumber = /\d/;  // Regular expression to check for a number

      if (password.length < 8) {
        return "Password must be at least 8 characters long.";
      }
      
      if (!hasNumber.test(password)) {
        return "Password must contain at least one number.";
      }

      return "";  // Return an empty string if the password is valid
    };

    watch(
      () => props.form.password,
      (newPassword) => {
        const errorMessage = validatePassword(newPassword);
        passwordError.value = errorMessage;  // Set the custom error message or clear it
      }
    );

    return {
      usernameError,
      emailError,
      passwordError,
      combinedLocations
    };
  },
};
</script>
