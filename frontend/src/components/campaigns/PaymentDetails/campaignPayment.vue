<template>
  <section class="payment-page">
    <h3 class="text-secondary fw-bold mb-4">Payment Summary</h3>
    <p v-if="campaign.influencers.length>0" class="alert alert-info fw-bold">You can click on amount details to directly edit</p>
    <p v-else class="alert alert-info fw-bold">Ask influencers to join your campaign. No payment summary yet.</p>
    <div class="influencer-payment-list">
      <div
        v-for="influencer in campaign.influencers"
        :key="influencer.influencer_id"
        class="influencer-payment-card d-flex justify-content-between align-items-center alert alert-warning p-3 my-2"
      >
        <div
          v-if="influencer.status === 'accepted'"
          class="d-flex flex-column align-items-center justify-content-around w-100 gap-3"
        >
          <div class="d-flex align-items-start  w-100 justify-content-between gap-3">
            <router-link class="nav-link" :to="`/user/user-profile/${influencer.influencer_id}`">
              <img
                :src="imageurl(influencer)"
                alt="Profile Image"
                class="rounded-circle border-3 border-secondary"
                style="width: 50px; height: 50px; object-fit: cover;"
              />
            </router-link>

            <button class="btn btn-theme">
              <router-link class="nav-link" :to="`/user/user-profile/${influencer.influencer_id}`">
                {{ influencer.influencer_name }}
              </router-link>
            </button>
          </div>

          <div class="d-flex align-items-center gap-3">
            <!-- Display span or input based on editing state -->
            <span
              v-if="!influencer.isEditing"
              class="badge bg-info fs-5"
              @click="influencer.isEditing = true"
              @mouseenter="hoveredInfluencer = influencer.influencer_id"
              @mouseleave="hoveredInfluencer = null"
            >
              ${{ influencer.payment_amount ? formatLargeNumber(influencer.payment_amount).toLocaleString() : 0 }}
            </span>
            

            <input
              v-else
              type="number"
              class="form-control w-100"
              :value="influencer.payment_amount"
              @input="updatePaymentHandler(influencer, $event.target.value)"
              @blur="influencer.isEditing = false"
            />
<!-- 
            <div v-if="influencer?.payment_amount>0">
              <checkoutComponent/>

            </div> -->
            
          </div>
        </div>
      </div>
    </div>
  </section>
</template>


<script>
import { defineComponent, ref } from "vue";
import { updatepaymentAmount } from "../../../services/campaignService";
import { formatLargeNumber } from "../../../main";
import checkoutComponent from "../../PaymentGateway/checkoutComponent.vue";

export default defineComponent({
  name: "CampaignPayments",
  props: {
    campaign: {
      type: Object,
      required: true,
    },
  },
  components:{
    checkoutComponent

  },
  setup(props, { emit }) {
    const hoveredInfluencer = ref(null); // Tracks the hovered influencer

    const imageurl = (profile) => {
      return profile && profile.profile_image
        ? `${import.meta.env.VITE_APP_BACKEND_URL}/${profile.profile_image}`
        : "";
    };

    const updatePaymentHandler = async (influencer, newValue) => {
      const value = parseFloat(newValue);
      if (!isNaN(value) && value >= 0) {
        try {
          influencer.payment_amount = value; // Update the local state
          const response = await updatepaymentAmount(
            props.campaign.id,
            influencer.influencer_id,
            value
          );
          console.log(response.message); // Log success message
          emit("updateCampaignData", props.campaign); // Emit the updated campaign object
        } catch (error) {
          console.error("Failed to update payment:", error);
        }
      }
    };


    return {
      hoveredInfluencer,
      imageurl,
      updatePaymentHandler,
      formatLargeNumber
    };
  },
});
</script>

  <style scoped>
  .payment-page {
    padding: 20px;
    background: #f8f9fa;
  }
  .influencer-payment-list {
    max-width: 800px;
    margin: 0 auto;
  }
  .influencer-payment-card {
    border-radius: 8px;
  }
  input{
    background-color: rgb(162, 227, 255);
  }
  </style>
  