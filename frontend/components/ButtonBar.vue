<!-- components/ButtonBar.vue -->
<template>
  <div class="flex flex-col space-y-2">
    <button 
      v-for="button in buttons" 
      :key="button.name"
      @click="selectButton(button.name)"
      class="btn btn-circle"
      :class="props.selectedFeature === button.name ? 'btn-primary' : 'btn-ghost'"
    >
      <i :class="button.icon"></i>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps({
  selectedFeature: {
    type: String,
    default: 'Text'
  }
});

const emit = defineEmits(['update:selectedFeature']);

const buttons = [
  { name: 'Text', icon: 'fa-solid fa-quote-right' },
  { name: 'Currency', icon: 'fa-solid fa-dollar-sign' },
  { name: 'Object', icon: 'fa-solid fa-cube' },
  { name: 'Product', icon: 'fa-solid fa-shopping-cart' },
  { name: 'Distance', icon: 'fa-solid fa-ruler' },
  { name: 'Face', icon: 'fa-solid fa-smile' },
  { name: 'Music', icon: 'fa-solid fa-music' },
  { name: 'Chatbot', icon: 'fa-solid fa-comments' },
  { name: 'News', icon: 'fa-solid fa-newspaper' },
];

const selectButton = (name: string) => {
  // Voiceover using SpeechSynthesis
  const message = new SpeechSynthesisUtterance(`Switched to ${name} mode`);
  speechSynthesis.speak(message);
  emit('update:selectedFeature', name);
};
</script>