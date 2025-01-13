<template>
    <div class="ga4-job-component">
      <button 
        class="btn btn-info asyncga4report"
        @click="triggerGA4Export"
        :disabled="isProcessing"
      ><i class="fa-solid fa-download"></i>  GA4 Report
      <i class="fa fa-file" aria-hidden="true"></i>
      </button>
      
      <!-- Show spinner when processing -->
      <div v-if="isProcessing" class="d-flex justify-content-center mt-3">
        <div class="spinner-border text-info" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <div v-if="jobStatus">
        <p class="mt-3 fw-bold text-warning">Job Status: {{ jobStatus }}</p>
      </div>
  
      <div v-if="error" class="text-danger mt-3">
        <h5>Oops:</h5>
        <pre>{{ error }}</pre>
      </div>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue';
  import { triggerga4export, retrieveGA4Report } from '../../../services/jobsandAsyncServices';
  import Tooltip from '../../utilities/Tooltip.vue';
  
  export default {
    name: 'Ga4JobComponent',
    props: {
      campaign: {
        type: Object,
        required: true
      },
     
    },
    components: {
        Tooltip
      },
    setup(props) {
      const isProcessing = ref(false);
      const jobStatus = ref('');
      const taskId = ref(null);
      const report = ref(null);
      const error = ref('')
  
      const triggerGA4Export = async () => {
        try {
          isProcessing.value = true;
          jobStatus.value = 'Starting export job...';
  
          // Trigger GA4 export for the specific campaign
          const response = await triggerga4export(props.campaign.id);
          taskId.value = response.data.task_id; // Assuming task_id is returned
          jobStatus.value = 'Export job triggered successfully. Fetching report...';
  
          // Poll for task status
          const pollInterval = 2000; // 2 seconds
          const maxAttempts = 30; // Polling timeout after ~1 minute
          let attempts = 0;
  
          const pollTaskStatus = async () => {
            try {
              const statusResponse = await retrieveGA4Report(taskId.value, {
                responseType: "blob", // Ensure binary data
              });
  
              if (statusResponse.status === 200) {
                const blob = new Blob([statusResponse.data], { type: "text/csv" }); // Change mime type to CSV
                console.log("Blob size:", blob.size); // Debugging step
  
                // Create a URL for the blob
                const url = window.URL.createObjectURL(blob);
  
                // Create a link element to trigger the download
                const link = document.createElement("a");
                link.href = url;
                link.download = `${props.campaign.name}.csv`; // Use campaign name and .csv extension
                document.body.appendChild(link);
                link.click();
  
                // Cleanup
                document.body.removeChild(link);
                window.URL.revokeObjectURL(url);
  
                jobStatus.value = "Report retrieved and downloaded successfully.";
                clearInterval(interval);
                isProcessing.value = false;
              } else if (statusResponse.status === 202) {
                jobStatus.value = "Export is still processing...";
              } else {
                throw new Error("Unexpected response status");
              }
            } catch (err) {
              console.error("Error during download:", err);
              jobStatus.value = "Error retrieving GA4 report.";
              error.value = err
              clearInterval(interval);
              isProcessing.value = false;
            }
          };
  
          const interval = setInterval(() => {
            if (attempts >= maxAttempts) {
              clearInterval(interval);
              jobStatus.value = "Task polling timed out.";
              isProcessing.value = false;
            } else {
              pollTaskStatus();
              attempts += 1;
            }
          }, pollInterval);
        } catch (error) {
          jobStatus.value = "Failed to fetch GA4 export.";
          error.value = err
          console.error(error);
          isProcessing.value = false;
        }
      };
  
      return {
        isProcessing,
        jobStatus,
        taskId,
        report,
        triggerGA4Export,
        Tooltip,
        error,
      };
    }
  };
  </script>
  
  <style scoped>
  .ga4-job-component {
    padding: 1rem;
  }
  
  .spinner-border {
    width: 3rem;
    height: 3rem;
  }
  
  button:disabled {
    cursor: not-allowed;
    opacity: 0.5;
  }
  </style>
  