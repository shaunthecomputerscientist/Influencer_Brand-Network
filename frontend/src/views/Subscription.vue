<template>
    <div class="payment-plans">
      <!-- Extra Details Section -->
      <div class="details-section">
        <h1>Choose the Perfect Plan for Your Campaigns</h1>
        <p>
          Whether you're just getting started or managing large campaigns, we have the perfect
          plan for your needs. Compare our Silver, and Gold tiers below.
        </p>
      </div>
  
      <!-- Plans Section -->
      <div class="plans-container">
        <!-- Bronze Plan -->
        <div class="plan-card bronze">
          <h2>Bronze Plan</h2>
          <p class="price">$20:00 / month</p>
          <ul>
            <li>Limited platform support (Youtube, Instagram).</li>
            <li>5 influencers per campaign.</li>
          </ul>
          <button class="subscribe-button">Subscribe</button>
        </div>
  
        <!-- Silver Plan -->
        <div class="plan-card silver">
          <h2>Silver Plan</h2>
          <p class="price">$49.99 / month</p>
          <ul>
            <li>10+ platform support.</li>
            <li>Add upto 10 influencers per campaign.</li>
            <li>Detailed personalized analytics report for campaigns.</li>
            <li>AI influencer discovery (up to 100 per month).</li>
          </ul>
          <button class="subscribe-button">Subscribe</button>
        </div>
  
        <!-- Gold Plan -->
        <div class="plan-card gold">
          <h2>Gold Plan</h2>
          <p class="price">$99.99 / month</p>
          <ul>
            <li>20+ platform support.</li>
            <li>Up to 20 influencers per campaign.</li>
            <li>Enhanced analytics reports with additional campaign insights.</li>
            <li>AI influencer discovery (up to 500 per month).</li>
            <li>AI assisted campaign management and suggestions</li>
          </ul>
          <button class="subscribe-button">Subscribe</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "PlanDetails",
  };
  </script>
  
  <style scoped>
  /* General Styling */
  .payment-plans {
    text-align: center;
    padding: 2rem;
    font-family: Arial, sans-serif;
    background-color: #f9f9f9;
  }
  
  /* Extra Details Section */
  .details-section {
    margin-bottom: 2rem;
  }
  
  .details-section h1 {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    color: #333;
  }
  
  .details-section p {
    font-size: 1.2rem;
    color: #666;
  }
  
  /* Plans Section */
  .plans-container {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    flex-wrap: wrap;
  }
  
  /* Plan Card */
  .plan-card {
    background: #fff3e1;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    padding: 1.5rem;
    width: 300px;
    text-align: left;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
  }
  .plan-card:hover{
    background: #ffefd8;

  }
  
  .plan-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
  }
  
  .plan-card h2 {
    font-size: 1.8rem;
    color: #444;
  }
  
  .plan-card .price {
    font-size: 1.5rem;
    color: #ffb35d;
    margin: 0.5rem 0 1rem;
  }
  
  .plan-card ul {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
  }
  
  .plan-card ul li {
    font-size: 1rem;
    color: #555;
    margin-bottom: 0.5rem;
    list-style:disc;
  }
  
  .subscribe-button {
    background-color: #ffdd98;
    color: white;
    padding: 0.5rem 1rem;
    font-size: 1rem;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.3s ease;
  }
  
  .subscribe-button:hover {
    background-color: #ffae7c;
  }
  
  /* Bronze, Silver, and Gold Plan Styling */
  .bronze {
    border-top: 4px solid #cd7f32;
  }
  
  .silver {
    border-top: 4px solid #c0c0c0;
  }
  
  .gold {
    border-top: 4px solid #ffd700;
  }
  </style>
  