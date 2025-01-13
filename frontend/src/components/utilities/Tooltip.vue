<template>
  <div
    v-if="visible"
    :class="['tooltipp', position]"
    class="tooltip-container"
    :style="tooltipStyles"
  >
    {{ text }}
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from "vue";

export default {
  name: "Tooltip",
  props: {
    text: {
      type: String,
      required: true,
    },
    position: {
      type: String,
      default: "top", // top, bottom, left, right
    },
    triggerClass: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const visible = ref(false);
    const tooltipStyles = computed(() => {
      let styles = {};
      const triggerElements = document.querySelectorAll(`.${props.triggerClass}`);

      if (triggerElements.length > 0) {
        // We will only calculate the tooltip position for the first matched element.
        const rect = triggerElements[0].getBoundingClientRect();

        // Positioning logic based on the trigger element's position
        if (props.position === "top") {
          styles = {
            top: `${rect.top - 1}px`,
            left: `${rect.left + rect.width / 2}px`,
            transform: "translateX(-50%)",
          };
        } else if (props.position === "bottom") {
          styles = {
            top: `${rect.bottom + 10}px`,
            left: `${rect.left + rect.width / 2}px`,
            transform: "translateX(-50%)",
          };
        } else if (props.position === "left") {
          styles = {
            top: `${rect.top + rect.height / 2}px`,
            left: `${rect.left - 50}px`,
            transform: "translateY(-50%)",
          };
        } else if (props.position === "right") {
          styles = {
            top: `${rect.top + rect.height / 2}px`,
            left: `${rect.right + 10}px`,
            transform: "translateY(-50%)",
          };
        }
      }

      return styles;
    });

    const showTooltip = () => {
      visible.value = true;
    };

    const hideTooltip = () => {
      visible.value = false;
    };

    const setupEventListeners = () => {
      const triggerElements = document.querySelectorAll(`.${props.triggerClass}`);
      triggerElements.forEach((element) => {
        element.addEventListener("mouseenter", showTooltip);
        element.addEventListener("mouseleave", hideTooltip);
      });
    };

    // Setup event listeners on mounted
    onMounted(() => {
      setupEventListeners();
    });

    // Cleanup event listeners
    watch(
      () => props.triggerClass,
      (newClass, oldClass) => {
        if (oldClass) {
          const oldElements = document.querySelectorAll(`.${oldClass}`);
          oldElements.forEach((element) => {
            element.removeEventListener("mouseenter", showTooltip);
            element.removeEventListener("mouseleave", hideTooltip);
          });
        }
        if (newClass) {
          setupEventListeners();
        }
      },
      { immediate: true }
    );

    return {
      visible,
      tooltipStyles,
    };
  },
};
</script>

<style scoped>
.tooltip-container {
  position: absolute;
  background-color: rgb(255, 221, 149);
  color: #ce7a0d;
  padding: 0.2rem;
  border: 2px solid rgb(170, 170, 170);
  box-shadow: 1px 1px 0.2rem rgba(146, 146, 146, 0.528);
  border-radius: 1rem 1rem 0.2rem 1rem;
  font-size: 12px;
  /* white-space: nowrap; */
  z-index: 10;
  width: 7rem;
  transition: opacity 0.2s ease;
  margin: -5% 0%;
  text-wrap:wrap;
  text-overflow:clip;
  overflow: scroll;
  text-align: center;
}

.tooltipp.top {
  left: -80%;
  /* transform: translateX(-50%) translateY(-200px); */
  position: absolute;
}

.tooltipp.bottom {
  top: 100%;
  left: -50%;
  position: absolute;
  /* transform: translateX(-50%) translateY(10px); */
}

.tooltipp.left {
  /* top: -80%; */
  left: 20rem;
  position: absolute;
  border: 2px solid khaki;
}

.tooltipp.right {
  top: 50%;
  left: 100%;
  transform: translateY(-50%) translateX(10px);
}
</style>
