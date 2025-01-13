<template>
  <div class="mb-3">
    <!-- <label :for="id" class="form-label">{{ label }}:</label> -->
    <multiselect
      :modelValue="modelValue"
      @update:modelValue="$emit('update:modelValue', $event)"
      :options="options"
      :multiple="true"
      :close-on-select="false"
      :clear-on-select="false"
      :hide-selected="true"
      :placeholder="label"
      class="border multiselectcustom hide-scrollbar"
    />
  </div>
</template>

<script>
import Multiselect from 'vue-multiselect';

export default {
  name: 'EnhancedMultiselect',
  components: {
    Multiselect,
  },
  props: {
    id: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
    modelValue: {
      type: Array,
      default: () => [],
    },
  },
  emits: ['update:modelValue'],
};
</script>

<style scoped>

.multiselectcustom:deep(.multiselect__tags){
  border: 0.1rem solid rgb(255, 226, 141);
}
.multiselectcustom:deep(.multiselect__option--highlight){
  background-color: #ffe9b7;
  color: rgb(255, 255, 255);
  font-weight: bold;
  width:90rem;
}

.multiselectcustom:deep(.multiselect__option--highlight .multiselect__option){
  background-color: #ffe9b7;
  color: rgb(255, 255, 255);
  font-weight: bold;

}


.multiselectcustom:deep(input:hover){
  transition: 0.45s;
  color: black;


}



.multiselectcustom:deep(.multiselect__tag-icon){
  background-color: #ffdc8b;
  color: rgb(255, 179, 0); /* Optional: Change icon color */
}

.multiselectcustom:deep(.multiselect__tag-text){
  color: black; /* Change this color to your preference */
}

.multiselectcustom:deep(.multiselect__input){
  color: black; /* Adjust the text color */
}
</style>
