<template>
  <div class="flex flex-col space-y-4">
    <button 
      v-for="button in buttons" 
      :key="button.name"
      @click="selectButton(button.name)"
      class="btn btn-circle focus:outline-none focus:ring-2 focus:ring-blue-500"
      :class="props.selectedFeature === button.name ? 'btn-primary' : 'btn-ghost'"
      :aria-label="`Switch to ${button.name} mode`"
      :title="`Switch to ${button.name} mode`"
    >
      <i :class="button.icon" class="text-lg"></i>
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
  { name: 'Distance', icon: 'fa-solid fa-ruler' },
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

<style scoped>
/* Enhance button styles for better accessibility */
.btn {
  width: 60px;
  height: 60px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  font-size: 1.25rem;
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.btn:hover {
  transform: scale(1.1);
}

.btn-primary {
  background-color: #2563eb; /* Bright blue */
  color: white;
  border: none;
}

.btn-primary:hover {
  background-color: #1d4ed8; /* Darker blue */
}

.btn-ghost {
  background-color: transparent;
  color: #6b7280; /* Gray */
  border: 1px solid #d1d5db; /* Light gray */
}

.btn-ghost:hover {
  background-color: #f3f4f6; /* Light hover effect */
  color: #374151; /* Darker gray */
}

.focus\:ring-2 {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5); /* Blue focus ring */
}
</style>