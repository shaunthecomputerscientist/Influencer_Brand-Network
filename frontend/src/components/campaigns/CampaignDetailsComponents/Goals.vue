<template>
    <div>
      <h3>Goals</h3>
      <ul class="goals-list">
        <li v-for="(goal, index) in goals" :key="index" class="goal-item">
          <strong>{{ index + 1 }}.</strong> {{ goal }}
        </li>
      </ul>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      goals: {
        type: Array,
        required: true,
      },
    },
  };
  </script>
  
  <style scoped>
  /* Styling for Goals */
  .goals-list {
    list-style: none;
    padding: 0;
  }
  
  .goal-item {
    padding: 0.75rem;
    background-color: #f9f9f9;
    border-radius: 0.5rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid #ffc85b;
  }
  </style>
  