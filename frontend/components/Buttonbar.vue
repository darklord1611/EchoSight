<template>
    <div class="flex">
      <!-- Sidebar Buttons -->
      <div class="flex flex-col space-y-2 p-2 min-w-[100px] bg-base-200">
        <button
          v-for="(button, index) in buttons"
          :key="index"
          :class="[
            'btn btn-ghost flex flex-col items-center justify-center',
            selectedButton === index ? 'text-primary' : 'text-base-content'
          ]"
          @click="selectButton(index)"
        >
          <i :class="button.icon" class="text-xl"></i>
          <span class="text-sm mt-1">{{ button.name }}</span>
        </button>
      </div>
  
      <!-- Slot or main content could go here -->
      <div class="flex-1 p-4">
        <slot />
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watch } from 'vue';
  
  const props = defineProps({
    defaultSelected: {
      type: String,
      default: 'Text',
    },
  });
  
  const emits = defineEmits(['update:selectedButton']);
  
  const selectedButton = ref<number | null>(null);
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
  
  // Set initial selected button based on prop value
  selectedButton.value = buttons.findIndex((button) => button.name === props.defaultSelected);
  
  // Watch for changes in the `defaultSelected` prop and update selectedButton
  watch(() => props.defaultSelected, (newDefaultSelected) => {
    selectedButton.value = buttons.findIndex((button) => button.name === newDefaultSelected);
  });
  
  // Handle button click, update selected button, and emit change
  const selectButton = (index: number) => {
    selectedButton.value = index;
    emits('update:selectedButton', buttons[index].name);
  };
  </script>
  