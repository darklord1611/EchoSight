<!-- components/ButtonBar.vue -->
<template>
  <div class="flex flex-col space-y-2">
    <button 
      v-for="button in buttons" 
      :key="button.name"
      @click="selectButton(button.name)"
      class="btn btn-circle"
      :class="selectedButton === button.name ? 'btn-primary' : 'btn-ghost'"
    >
      <i :class="button.icon"></i>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps({
  defaultSelected: {
    type: String,
    default: 'Text'
  }
});

const emit = defineEmits(['update:selectedButton']);

const selectedButton = ref(props.defaultSelected);

const buttons = [
  { name: 'Text', icon: 'fa-solid fa-quote-right' },
  { name: 'Currency', icon: 'fa-solid fa-dollar-sign' },
  { name: 'Object', icon: 'fa-solid fa-cube' },
  { name: 'Product', icon: 'fa-solid fa-shopping-cart' },
  { name: 'Distance', icon: 'fa-solid fa-ruler' },
  { name: 'Face', icon: 'fa-solid fa-smile' },
  { name: 'Music', icon: 'fa-solid fa-music' },
  { name: 'Chatbot', icon: 'fa-solid fa-comments' },
  { name: 'Article', icon: 'fa-solid fa-newspaper' },
];

const selectButton = (name: string) => {
  selectedButton.value = name;
  emit('update:selectedButton', name);
};
</script>