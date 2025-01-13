<template>
    <div>
        <div class="ga4-data-visualization" v-if="!isLoading">
      <!-- <h1>GA4 Data for Campaign: {{ campaign.name }}</h1> -->
  
      <!-- Aggregated Influencer Data Cards -->
      <div v-if="aggregatedInfluencerData.length > 0">
        <h2>Influencer Traffic</h2>
        <div class="data-cards">
          <div v-for="(row, index) in aggregatedInfluencerData" :key="index">
              <button  @click="toggleInfluencerCard(row.sessionManualTerm)"
              class="clickable" :class="{ active: isInfluencerCardExpanded(row.sessionManualTerm) }">{{ getInfluencerName(parseInt(row.sessionManualTerm)) }} <i :class="!isInfluencerCardExpanded(row.sessionManualTerm)?'fa-solid fa-eye':'fa-solid fa-eye-slash'"></i></button>
            <div v-if="isInfluencerCardExpanded(row.sessionManualTerm)" class="data-card">
              <p><strong>Total Sessions:</strong> {{ row.total_sessions }}</p>
              <p><strong>Average Bounce Rate:</strong> {{ row.avg_bounce_rate.toFixed(2) }}</p>
              <p><strong>Average Engagement Rate:</strong> {{ row.avg_engagement_rate.toFixed(2) }}</p>
              <p><strong>Total Active Users:</strong> {{ row.total_active_users }}</p>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Aggregated External Data Cards -->
      <div v-if="aggregatedExternalData.length > 0" class="mt-2">
        <h2>External Organic Traffic</h2>
        <div class="data-cards">
          <div v-for="(row, index) in aggregatedExternalData" :key="index">
            <button  @click="toggleExternalCard(row.sessionManualTerm)"
            class="clickable" :class="{ active: isExternalCardExpanded(row.sessionManualTerm) }">{{ row.sessionManualTerm }} <i :class="!isExternalCardExpanded(row.sessionManualTerm)?'fa-solid fa-eye':'fa-solid fa-eye-slash'"></i></button>
            <div v-if="isExternalCardExpanded(row.sessionManualTerm)" class="data-card">
              <p><strong>Total Sessions: {{ row.total_sessions }}</strong></p>
              <p><strong>Average Bounce Rate:{{ row.avg_bounce_rate.toFixed(2) }}</strong></p>
              <p><strong>Average Engagement Rate: {{ row.avg_engagement_rate.toFixed(2) }}</strong></p>
              <p><strong>Total Active Users: {{ row.total_active_users }}</strong></p>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Raw Data Line Chart -->
      <div
        v-if="rawInfluencerData.length > 0 || rawExternalData.length > 0"
        class="chartSection d-flex flex-column align-items-center justify-content-around gap-2 mt-5"
      >
        <!-- <h2>Raw Data Line Chart (Total Users by Month and Day)</h2> -->
        <plotlyChart
          :data="lineChartData(rawInfluencerData, 'Influencer')"
          :layout="layout('User Traffic: Influencer generated')"
        />
        <plotlyChart
          :data="lineChartData(rawExternalData, 'External')"
          :layout="layout('User Traffic: External organic')"
        />
      </div>
  
      <!-- Error Handling -->
      <div v-if="error">
        <p class="error">{{ error }}</p>
      </div>
    </div>
    <div v-else>
        <i :class="isLoading?'spinner-border text-info':''"></i>
    </div>

    </div>
    

  </template>
  
  
  
  <script>
  import { ref, onMounted } from "vue";
  import { retrieveGa4Data } from "../../../services/campaignService";
  import plotlyChart from "../../utilities/Plots/plotlyChart.vue";
  
  export default {
    name: "Ga4DataVisualization",
    components: {
      plotlyChart,
    },
    props: {
      campaign: {
        type: Object,
        required: true,
      },
    },
    setup(props) {
      const aggregatedInfluencerData = ref([]);
      const aggregatedExternalData = ref([]);
      const rawInfluencerData = ref([]);
      const rawExternalData = ref([]);
      const error = ref(null);
  
      // State for toggling
      const expandedInfluencerCards = ref([]);
      const expandedExternalCards = ref([]);
      const isLoading = ref(false);
  
      const fetchData = async () => {
        try {
          isLoading.value=true;
          const response = await retrieveGa4Data(props.campaign.id);
          aggregatedInfluencerData.value = response.data.aggregated_influencer_data;
          aggregatedExternalData.value = response.data.aggregated_external_data;
          rawInfluencerData.value = response.data.raw_influencer_data;
          rawExternalData.value = response.data.raw_external_data;
          isLoading.value=false;
        } catch (err) {
          isLoading.value=false;
          error.value = err.response ? err.response.data.error : err.message;
        }
      };
  
      // Methods to handle toggling for Influencer Cards
      const toggleInfluencerCard = (sessionManualTerm) => {
        if (expandedInfluencerCards.value.includes(sessionManualTerm)) {
          expandedInfluencerCards.value = expandedInfluencerCards.value.filter(
            (term) => term !== sessionManualTerm
          );
        } else {
          expandedInfluencerCards.value.push(sessionManualTerm);
        }
      };
  
      const isInfluencerCardExpanded = (sessionManualTerm) => {
        return expandedInfluencerCards.value.includes(sessionManualTerm);
      };
  
      // Methods to handle toggling for External Cards
      const toggleExternalCard = (sessionManualTerm) => {
        if (expandedExternalCards.value.includes(sessionManualTerm)) {
          expandedExternalCards.value = expandedExternalCards.value.filter(
            (term) => term !== sessionManualTerm
          );
        } else {
          expandedExternalCards.value.push(sessionManualTerm);
        }
      };
  
      const isExternalCardExpanded = (sessionManualTerm) => {
        return expandedExternalCards.value.includes(sessionManualTerm);
      };
  
      const getInfluencerName = (id) => {
        const influencer = props.campaign.influencers.find(
          (influencer) => parseInt(influencer.influencer_id) === id
        );
        return influencer ? influencer.influencer_name : "Unknown Influencer";
      };
  
      const lineChartData = (data, type) => {
        // Process data for line charts
        const groupedData = data.reduce((acc, item) => {
          const label = `${item.month}-${item.dayOfWeekName}`;
          if (!acc[label]) acc[label] = 0;
          acc[label] += item.totalUsers;
          return acc;
        }, {});
        const labels = Object.keys(groupedData);
        const values = Object.values(groupedData);
        return [
          {
            x: labels,
            y: values,
            type: "scatter",
            mode: "lines+markers",
            name: `${type} - Total Users`,
          },
        ];
      };
  
      const layout = (title) => ({
        title: {
            text: title,
            font: {
            size: 12, // Smaller title font size
            },
        },
        xaxis: {
            title: {
            text: "Month - Day of Week",
            font: {
                size: 11, // Smaller axis title font size
            },
            },
            tickfont: {
            size: 8, // Smaller axis tick labels
            },
        },
        yaxis: {
            title: {
            text: "Total Users",
            font: {
                size: 10, // Smaller axis title font size
            },
            },
            tickfont: {
            size: 8, // Smaller axis tick labels
            },
        },
        legend: {
            font: {
            size: 8, // Smaller legend font size
            },
        },
        margin: {
            l: 40, // Reduce left margin
            r: 40, // Reduce right margin
            t: 40, // Reduce top margin
            b: 80, // Reduce bottom margin
        },
        width: 300, // Adjust chart width
        height: 300, // Adjust chart height
        });
  
      onMounted(fetchData);
  
      return {
        aggregatedInfluencerData,
        aggregatedExternalData,
        rawInfluencerData,
        rawExternalData,
        error,
        lineChartData,
        layout,
        toggleInfluencerCard,
        isInfluencerCardExpanded,
        toggleExternalCard,
        isExternalCardExpanded,
        getInfluencerName,
        isLoading
      };
    },
  };
  </script>
    
  
  <style scoped>
  .ga4-data-visualization {
    margin: 20px;
  }
  
  h1,
  h2 {
    margin-bottom: 10px;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
  }
  
  table th,
  table td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: center;
  }
  
  table th {
    background-color: #f4f4f4;
  }
  
  .error {
    color: red;
    font-weight: bold;
  }
  .data-cards{
    display: flex;
    justify-content: start;
    overflow: scroll;
    gap: 2rem;
    border: 1px solid rgba(92, 92, 92, 0.108);
    box-shadow: 1px 1px 1rem rgba(78, 78, 78, 0.076);
    border-radius: 0.5rem;
  }

.data-cards .data-card{
    position: inherit;
    margin-right: 0;
    border: 2px solid rgba(0, 0, 0, 0);
    display: flex;
    align-items: start;
    justify-content: start;
    flex-direction: column;
    width: 20rem;
    padding: 1rem;
}

.data-cards .data-card p{
    background-color: #ff7944ca;
    border-radius: 0.2rem;
    box-shadow: 1px 1px 0.5rem rgba(0, 0, 0, 0.493);
}
.data-cards .data-card p strong{
 padding: 0.5rem;
}

.data-cards .data-card p:hover{
    background-color: #ddd;
    border-radius: 0.5rem;
    box-shadow: none;
}
  </style>
  