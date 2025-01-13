<template>
    <div v-if="campaign.influencers.length>0" class="campaign-component">
        <!-- Pie Chart for Average Task Progress -->

      <div class="d-flex align-items-end justify-content-end asyncjob">
        <ga4asyncExport v-if="campaign.trackingMethods.includes('utmLinks')" :campaign="campaign"/>
      </div>
      <div class="chart-container text-center" style="max-width: 500px;">
        <h4 class="alert alert-warning">Average Task Progress</h4>
        <canvas id="averageTaskProgressChart"></canvas>
      </div>
  
      <!-- Graphs for each influencer -->
      <h4 class="alert alert-warning">Influencer Wise Metrics</h4>
      <div class="d-flex align-items-center justify-content-around w-100 gap-2" style="overflow: scroll;">
        <div
          v-for="(influencer, index) in campaign.influencers"
          :key="index"
          class="influencer-chart"
        >
          <p class="fw-bold text-center">
            Metrics for {{ influencer.influencer_name || `Influencer ${index + 1}` }}
          </p>
          <div class="chart-container">
            <canvas :id="`chart-${index}`" width="300" height="300"></canvas>
          </div>
        </div>
      </div>

      <div v-if="campaign.brandTarget>0" class="w-100">
        <div class="progressbar w-100 d-flex flex-column gap-2 mt-5">
        <p class="alert alert-warning rounded-2 fw-bold text-center">Brand Social Progress</p>
        <div class="progress">
          <div :class="['progress-bar', 'progress-bar-striped', 'bg-info',  parseFloat(campaign.brandCurrent/campaign.brandTarget )*100 < 100 ? 'progress-bar-animated' : '']" role="progressbar" :style="{ width: parseFloat(campaign.brandCurrent/campaign.brandTarget ) *100 + '%' }" :aria-valuenow="campaign.brandCurrent" aria-valuemin="0" :aria-valuemax="campaign.brandTarget"><p class="mt-3 text-success fw-bold">{{ campaign.brandCurrent.toFixed(2) }}</p></div>
        </div>
       </div>
      </div>

      <div v-if="campaign.goalProgress" class="mt-2 p-2 w-100">
        <p class="alert alert-warning rounded-2 fw-bold text-center mt-2">Goal Progress Data</p>
        <div class="progress">
          <div :class="['progress-bar', 'progress-bar-striped', 'bg-info',  campaign.goalProgress*100 < 100 ? 'progress-bar-animated' : '']" role="progressbar" :style="{ width: parseFloat(campaign.goalProgress ) *100 + '%' }" :aria-valuenow="parseFloat(campaign.goalProgress ) *100" aria-valuemin="0" aria-valuemax="100"><p class="mt-3 text-success fw-bold">{{ campaign.goalProgress.toFixed(4) *100 }} %</p></div>
        </div>
      </div>
      <div class="mt-2 p-2 w-100">
        <p class="alert alert-warning rounded-2 fw-bold text-center mt-2">Campaign Progress</p>
        <div class="progress">
          <div :class="['progress-bar', 'progress-bar-striped', 'bg-warning',  campaign.progress*100 < 100 ? 'progress-bar-animated' : '']" role="progressbar" :style="{ width: parseFloat(campaign.progress ) *100 + '%' }" :aria-valuenow="parseFloat(campaign.progress ) *100" aria-valuemin="0" aria-valuemax="100"><p class="mt-3 text-success fw-bold">{{ campaign.progress.toFixed(4) *100 }} %</p></div>
        </div>
      </div>
    </div>
    <div v-else>
      <p class="fw-bold p-2 text-center alert alert-info">No Data available at this moment</p>
    </div>
  </template>
  
  
  <script>
  import { ref, onMounted, nextTick } from "vue";
  import { Chart, registerables } from "chart.js";
  import ga4asyncExport from "../campaignJobs/ga4asyncExport.vue";
  
  Chart.register(...registerables);
  
  export default {
    name: "analyticsCampaignComponent",
    props: {
      campaign: {
        type: Object,
        required: true,
      },
    },
    components: {
      ga4asyncExport,
    },
    setup(props) {
      // Reactive state
      const averageTaskProgress = ref(0);
  
      // Calculate Average Task Progress
      const calculateAverageTaskProgress = () => {
        const totalProgress = props.campaign.influencers.reduce(
          (sum, influencer) => sum + (influencer.taskProgress || 0) * 100,
          0
        );
        const avgProgress = totalProgress / props.campaign.influencers.length;
        averageTaskProgress.value = avgProgress;
      };
  
      // Process Metrics for Influencers
      const processMetrics = (metrics) => {
        const chartData = {};
  
        for (const platform in metrics) {
          const links = metrics[platform];
  
          links.forEach((linkData) => {
            for (const url in linkData) {
              const { metrics } = linkData[url];
  
              // Initialize platform data
              if (!chartData[platform]) {
                chartData[platform] = { views: 0, likes: 0, count: 0 };
              }
  
              // Collect views_obtained
              if (metrics.views_obtained) {
                chartData[platform].views += metrics.views_obtained;
                chartData[platform].count++;
              }
  
              // Collect likes_obtained
              if (metrics.likes_obtained) {
                chartData[platform].likes += metrics.likes_obtained;
                chartData[platform].count++;
              }
            }
          });
        }
  
        // Calculate averages for views and likes
        return Object.keys(chartData).map((platform) => ({
          platform,
          averageViews: chartData[platform].views / (chartData[platform].count || 1),
          averageLikes: chartData[platform].likes / (chartData[platform].count || 1),
        }));
      };
  
      // Render Average Task Progress Chart
      const renderAverageTaskProgressChart = async () => {
        await nextTick(); // Wait for DOM updates
        const canvas = document.getElementById("averageTaskProgressChart");
        if (!canvas) {
          console.error("Canvas for average task progress not found.");
          return;
        }
        const ctx = canvas.getContext("2d");
  
        new Chart(ctx, {
          type: "pie",
          data: {
            labels: ["Completed Tasks", "Pending Tasks"],
            datasets: [
              {
                data: [averageTaskProgress.value, 100 - averageTaskProgress.value],
                backgroundColor: ["turquoise", "orange"],
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              tooltip: {
                callbacks: {
                  label: (context) => `${context.label}: ${context.raw.toFixed(2)}%`,
                },
              },
            },
          },
        });
      };
  
      // Render Charts for Individual Influencers
      const renderChart = async (chartId, data) => {
        const canvas = document.getElementById(chartId);
        if (!canvas) {
          console.error(`Canvas with ID ${chartId} not found.`);
          return;
        }
        const ctx = canvas.getContext("2d");
  
        const labels = data.map((item) => item.platform);
        const views = data.map((item) => item.averageViews);
        const likes = data.map((item) => item.averageLikes);
  
        new Chart(ctx, {
          type: "bar",
          data: {
            labels,
            datasets: [
              {
                label: "Views Obtained",
                data: views,
                backgroundColor: "rgba(75, 192, 192, 0.6)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1,
              },
              {
                label: "Likes Obtained",
                data: likes,
                backgroundColor: "rgba(255, 99, 132, 0.6)",
                borderColor: "rgba(255, 99, 132, 1)",
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
              },
            },
          },
        });
      };
  
      // Lifecycle hook for initializing charts
      onMounted(async () => {
        calculateAverageTaskProgress();
        await renderAverageTaskProgressChart();
  
        await nextTick(); // Wait for DOM updates
  
        props.campaign.influencers.forEach((influencer, index) => {
          const chartData = processMetrics(influencer.postrackingMetric || {});
          if (chartData.length > 0) {
            renderChart(`chart-${index}`, chartData);
          } else {
            console.warn(`No data available for influencer ${index}`);
          }
        });
      });
  
      return {
        averageTaskProgress,
      };
    },
  };
  </script>
    
  
  <style scoped>
  .campaign-component {
    padding: 2rem;
    border: 1px solid #ccc;
    border-radius: 8px;
    margin: 0.2rem 0;
    background-color: #f9f9f9;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
  }
  
  .chart-container {
    margin: 1rem 0;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    /* height: 500px; */
    width: 100%;
    
  }
  
  .influencer-chart {
    margin-bottom: 2rem;
  }
  .asyncjob{
    margin-top: -2rem;
    margin-right: -2rem;
    /* border: 2px saddlebrown solid; */
  }
  </style>
  