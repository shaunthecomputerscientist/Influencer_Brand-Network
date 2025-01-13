<template>
  <div>
    <h3>Tasks</h3>
    <ul class="tasks-list">
      <li v-for="(task, index) in tasks.tasks" :key="index" class="task-item">
        <strong>{{ index + 1 }}.</strong> {{ task.description }}
      </li>
    </ul>
  </div>
  <div>
    <h3>Guidelines</h3>
    <!-- Use v-html to render processed HTML with line breaks -->
    <p class="task-item" v-html="formattedGuidelines"></p>
  </div>
</template>

<script>
import { computed } from 'vue';

export default {
  props: {
    tasks: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    // Function to format the guidelines
    const formatGuidelines = (text) => {
      // Add line breaks before numbered points and bullet points
      let formattedText = text.replace(/(\d+\.\s|\•\s)/g, '<br><strong>$&</strong>');
      
      // Replace ". " with ".<br>" to create line breaks after each sentence
      formattedText = formattedText.replace(/\. /g, '.<br>');

      return formattedText;
    };

    // Computed property to get formatted guidelines
    const formattedGuidelines = computed(() => {
      return formatGuidelines(props.tasks.guidelines);
    });

    return {
      formattedGuidelines,
    };
  },
};
</script>

<style scoped>
/* Styling for Tasks and Guidelines */
.tasks-list {
  list-style: none;
  padding: 0;
}

.task-item {
  padding: 0.75rem;
  background-color: #f9f9f9;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
  border-left: 4px solid #ffc85b;
}
</style>