<template>
    <div class="stripe-checkout-page">
      <h1>Stripe Checkout Payment</h1>
      <StripeCheckout
        :pk="publishableKey"
        :line-items="lineItems"
        :mode="mode"
        :success-url="successUrl"
        :cancel-url="cancelUrl"
        @loading="handleLoading"
        @error="handleError"
      />
    </div>
  </template>
  
  <script>
  import { StripeCheckout } from "@vue-stripe/vue-stripe";
  
  export default {
    components: {
      StripeCheckout,
    },
    data() {
      return {
        // Your Stripe publishable key
        publishableKey: "pk_test_12345",
  
        // Items to purchase
        lineItems: [
          {
            price_data: {
              currency: "usd",
              product_data: {
                name: "Test Product",
                description: "A sample product for testing Stripe Checkout",
              },
              unit_amount: 2000, // $20.00
            },
            quantity: 1,
          },
        ],
  
        // Checkout mode
        mode: "payment", // Payment mode
  
        // URLs for success and cancellation
        successUrl: "http://localhost:8080/success",
        cancelUrl: "http://localhost:8080/cancel",
      };
    },
    methods: {
      handleLoading(loading) {
        console.log("Loading state:", loading);
      },
      handleError(error) {
        console.error("Stripe Checkout Error:", error);
      },
    },
  };
  </script>
  
  <style scoped>
  .stripe-checkout-page {
    text-align: center;
    padding: 2rem;
  }
  
  h1 {
    font-size: 24px;
    margin-bottom: 1.5rem;
  }
  
  button {
    background-color: #6772e5;
    color: white;
    padding: 12px 20px;
    font-size: 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  button:hover {
    background-color: #5469d4;
  }
  </style>
  