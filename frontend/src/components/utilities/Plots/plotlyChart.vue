<template>
  <div ref="chartContainer" class="border chartcontainer"></div>
</template>

<script>
import Plotly from "plotly.js-dist";

export default {
  props: ["data", "layout"],
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      const chartContainer = this.$refs.chartContainer;

      if (!chartContainer) {
        console.error("Chart container is not defined.");
        return;
      }

      Plotly.newPlot(chartContainer, this.data, this.layout)
        .then(() => console.log("Chart rendered successfully"))
        .catch((err) => {
          console.error("Error rendering chart:", err);
        });
    },
  },
};
</script>

<style scoped>
.chartcontainer {
  width: auto;
}
</style>