<template>
    <div class="d-flex flex-column gap-3 fw-bold text-secondary">
      <div class="detail-row d-flex gap-2">
        <span class="detail-label">Campaign Name:</span> <p>{{ campaign.name }}</p>
      </div>
      <div class="detail-row d-flex gap-2">
        <span class="detail-label">Description:</span> <p class="w-100">{{ campaign.description }}</p>
      </div>
      <div class="detail-row d-flex gap-2">
        <span class="detail-label">Budget:</span> <p>$ {{ campaign.budget }}</p>
      </div>
      <div class="detail-row d-flex align-items-center justify-content-start gap-2">
        <span class="detail-label">Duration:</span>
        <div class="date-buttons d-flex overflow-scroll align-items-center justify-content-start gap-2">
          <button class="text-nowrap">{{ formatDateTime(campaign.start_date).month }} {{ formatDateTime(campaign.start_date).day }}</button>
          <span class="date-divider">to</span>
          <button class="text-nowrap">{{ formatDateTime(campaign.end_date).month }} {{ formatDateTime(campaign.end_date).day }}</button>
        </div>
      </div>
      <div class="detail-row d-flex gap-2">
        <span class="detail-label mt-2">Niche:</span>
        <div class="d-flex overflow-scroll detail-row gap-3">
          <div class="d-flex" v-for="niche in campaign.niches">
            <button class="alert alert-warning">{{ niche }}</button>
        </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      campaign: Object,
    },
    methods: {
      formatDateTime(dateString) {
        const date = new Date(dateString);
        const month = date.toLocaleString('en-US', { month: 'long' });
        const day = date.getDate();
        return { month, day };
      },
    },
  };
  </script>

<style scoped>
.detail-row p{
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid #ffc85bc2;
    background-color: #ffc85b3c;
    width: 50%;
    padding: 0.2rem;
    flex-wrap: wrap;

}
.date-buttons button{
  text-wrap: wrap;
  text-align: center;
}
</style>
  