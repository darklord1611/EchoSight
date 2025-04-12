<template>
    <div class="flex flex-col items-center space-y-2">
      <div :class="['w-6 h-6 rounded-full transition-all duration-200', isRecording ? 'bg-red-500 animate-ping' : 'bg-gray-300']"></div>
      <div class="w-24 h-2 bg-gray-300 rounded-full overflow-hidden">
        <div
          class="h-full bg-green-500 transition-all duration-100"
          :style="{ width: `${Math.min(decibelLevel, 100)}%` }"
        ></div>
      </div>
      <p v-if="isRecording" class="text-sm text-gray-500">Listening...</p>
    </div>
  </template>
  
  <script setup lang="ts">
  const props = defineProps<{
    isRecording: boolean;
    decibelLevel: number;
  }>();
  </script>
  