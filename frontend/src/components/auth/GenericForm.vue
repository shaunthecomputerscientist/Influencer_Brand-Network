<template>
  <section class="form-section">
    <header>
      <button class="rounded-1 alert alert-warning" style="padding: 0.5rem 2rem;">{{ isUpdateMode ? 'Update Profile' : 'Signup' }}</button>
    </header>

    <form @submit.prevent="handleSubmit" :class="{'form-disabled': isLoading}" novalidate>
      <label for="profile_image" class="form-label">{{form.role==='brand'?'Brand/Business Logo':'Profile Image'}}</label>
      <input type="file" class="form-control" @change="handleFileUpload" />
        <!-- Conditionally show the image preview if it exists -->
        <img v-if="imagePreview" :src="imagePreview" class="rounded w-100 p-2 border" alt="Image Preview" />

        <!-- Conditionally show the profile image from the server in update mode -->
        <img v-else-if="isUpdateMode && profileImageUrl && !form.profile_image" :src="profileImageUrl" class="rounded-5 w-100 p-2 border" alt="Profile Image" />


      <!-- Common fields -->
      <CommonFields :form="form" :errors="errors" :isUpdateMode="isUpdateMode" :availableOptions="availableOptions"/>
 
      <!-- Influencer fields -->
      <InfluencerFields v-if="form.role === 'influencer'" :form="form" :availableOptions="availableOptions" />

      <!-- Brand fields -->
      <BrandFields v-if="form.role === 'brand'" :form="form" :availableOptions="availableOptions" />

      <button type="submit" :disabled="isSubmitDisabled || isLoading">
        <span v-if="isLoading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ isUpdateMode ? 'Update' : 'Signup' }}
      </button>
    </form>
  </section>
</template>

<script>
import { ref, computed, onBeforeUnmount, watch } from 'vue';
import CommonFields from './CommonFields.vue';
import InfluencerFields from './InfluencerFields.vue'
import router from '../../router';
import BrandFields from './BrandFields.vue';
import { signup, generatePhylloSDK } from '../../services/authService';
import { updateData } from '../../services/userservice';
import { useAuthStore } from '../../store/modules/auth';

export default {
  props: {
    isUpdateMode: {
      type: Boolean,
      default: false,
    },
    initialData: {
      type: Object,
      default: () => ({}),
    },
    availableOptions: {
      type: Object,
      required: true,
    },
  },
  components: {
    CommonFields,
    InfluencerFields,
    BrandFields,
  },
  setup(props) {

    const isLoading = ref(false)
    const form = ref({
      username: props.initialData.username || '',
      email: props.initialData.email || '',
      password: '',
      first_name: props.initialData.first_name || '',
      last_name: props.initialData.last_name || '',
      role: props.initialData.role || '',
      language: props.initialData.language || [],
      gender: props.initialData.gender || '',
      dob: props.initialData.dob || null,
      niche: props.initialData.niche || [],
      company_name: props.initialData.company_name || '',
      industry: props.initialData.industry || [],
      location: props.initialData.location || '',
      platforms: props.initialData.platforms || {},
      selectedPlatforms: props.initialData.selectedPlatforms || [],
      description: props.initialData.description || '',
      profile_image: null,
      phyllo_user_id: null, // Initialize phyllo_user_id
    });

    const errors = ref({
      username: false,
      email: false,
    });

    const authStore = useAuthStore();

    const profileImageUrl = computed(() => {
      // Assuming `authStore.userProfile` contains the profile image path
      const profileImage = authStore.userProfile?.profile_image; // Optional chaining to avoid errors if `userProfile` is null or undefined
      console.log(profileImage);
      
      return `${import.meta.env.VITE_APP_BACKEND_URL}/${profileImage}`;
    });
    const imagePreview = ref(null);

    const handleFileUpload = (event) => {
      const file = event.target.files[0];
      if (file) {
        imagePreview.value = URL.createObjectURL(file);
        form.value.profile_image = file; // Save the file object to the form
      } else {
        console.error("No file selected.");
      }
    };
    // watch(
//   () => form.value.platforms, // Watch the form.platforms object
//   (newValue) => {
//     const formData = new FormData();
  
//   // Append platforms as a JSON string to FormData
//   formData.append('platforms', JSON.stringify(newValue));

//   // Log the content of FormData to inspect the platforms value
//   for (let pair of formData.entries()) {
//     console.log(`${pair[0]}: ${pair[1]}`);
//   }
//   },
//   { deep: true } // Important to ensure changes inside the object are detected
// );

    onBeforeUnmount(() => {
      if (imagePreview.value) {
        URL.revokeObjectURL(imagePreview.value);
      }
    });

    const connectedAccounts = ref([]);
    const allAccountsConnected = ref(false);
    
    const checkAccountsConnected = () => {
      const expectedPlatformCount = form.value.selectedPlatforms.length;
      if (connectedAccounts.value.length >= expectedPlatformCount) {
        allAccountsConnected.value = true;
        handleSignup();
      }
    };

    const isSubmitDisabled = computed(() => {
      return (
        !form.value.username ||
        !form.value.email ||
        !form.value.first_name ||
        !form.value.last_name ||
        !form.value.role
      );
    });

    const connectAccounts = async () => {
      try {
        const { user_id, sdk_token, platform_id } = await generatePhylloSDK(form.value.first_name, form.value.last_name,form.value.platforms);
        form.value.phyllo_user_id = user_id; // Attach Phyllo user ID to the form

        const config = {
          clientDisplayName: `${import.meta.env.VITE_APP_NAME}`,
          environment: `${import.meta.env.VITE_APP_PHYLLO_ENVIRONMENT}`,
          userId: user_id,
          token: sdk_token,
          redirect: false,
          // workplatformId: platform_id
        };

        const phylloConnect = PhylloConnect.initialize(config);

        phylloConnect.on("accountConnected", (accountId, workplatformId, userId) => {
          connectedAccounts.value.push({ accountId, workplatformId });
          checkAccountsConnected();
        });
        phylloConnect.on("accountDisconnected", (accountId, workplatformId, userId) => {  // gives the successfully disconnected account ID and work platform ID for the given user ID
          console.log(`onAccountDisconnected: ${accountId}, ${workplatformId}, ${userId}`);
        })
        phylloConnect.on("tokenExpired", (userId) => {  // gives the user ID for which the token has expired
          console.log(`onTokenExpired: ${userId}`);  // the SDK closes automatically in case the token has expired, and you need to handle this by showing an appropriate UI and messaging to the users
        })
        phylloConnect.on("exit", (reason, userId) => {  // indicates that the user with given user ID has closed the SDK and gives an appropriate reason for it
          console.log(`onExit: ${reason}, ${userId}`);
        })
        phylloConnect.on("connectionFailure", (reason, workplatformId, userId) => {  // optional, indicates that the user with given user ID has attempted connecting to the work platform but resulted in a failure and gives an appropriate reason for it
          console.log(`onConnectionFailure: ${reason}, ${workplatformId}, ${userId}`);
        })

        phylloConnect.open();
      } catch (error) {
        console.error("Error during connecting accounts:", error);
      }
    };

    const handleSignup = async () => {
      try {
        const formData = new FormData(); // Use FormData to handle file uploads

        isLoading.value = true

        // Append all other fields
        Object.keys(form.value).forEach(key => {
          if (key !== 'platforms') {
            formData.append(key, form.value[key]);
          }
        });

        // Append platforms as a JSON string
        formData.append('platforms', JSON.stringify(form.value.platforms));
        console.log(JSON.stringify(form.value.platforms))


        const response = await signup(formData); // Pass FormData to signup
        console.log(response)

        if (response && response.status === 201) {
          router.push("/auth/login");
        }
      } catch (error) {
        console.error("Error during signup:", error);
      }
      finally {
        isLoading.value = false;
      }
    };

    const handleUpdate = async () => {
      try {
        const formData = new FormData(); // Use FormData to handle file uploads
        isLoading.value = true;
        Object.keys(form.value).forEach(key => {
        if (key === 'platforms') {
          // Serialize platforms as JSON string
          console.log(form.value.platforms)
          formData.append(key, JSON.stringify(form.value[key]));
        } else {
          formData.append(key, form.value[key]);
        }
      });

        const response = await updateData(formData); // Pass FormData to update

        if (response && response.status === 200) {
          localStorage.setItem('ProfileUpdatedRecently', true)
          router.push("/user/profile");
        }
      } catch (error) {
        console.error("Error during update:", error);
      }
      finally {
        isLoading.value=false;
      }
    };

    const handleSubmit = async () => {
      try {
        if (props.isUpdateMode) {
          await handleUpdate();
        } else {
          if (form.value.role === 'influencer') {
            await connectAccounts();
          } else {
            await handleSignup();
          }
        }
      } catch (error) {
        console.error("Error during submission:", error);
      }
    };

    return {
      form,
      errors,
      handleFileUpload,
      isSubmitDisabled,
      handleSubmit,
      imagePreview,
      profileImageUrl,
      isLoading
    };
  },
};
</script>

<style scoped>
.form-section {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}
.form-disabled {
  pointer-events: none;
  opacity: 0.6;
}

</style>