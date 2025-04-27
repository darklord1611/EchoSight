<template>
  <div class="flex flex-col items-center space-y-3">
    <!-- Recording indicator with enhanced animation -->
    <div class="relative">
      <div 
        :class="[
          'w-10 h-10 rounded-full transition-all duration-200 flex items-center justify-center',
          isRecording ? 'bg-red-500' : 'bg-blue-100'
        ]"
      >
        <div 
          v-if="isRecording" 
          class="absolute w-10 h-10 rounded-full bg-red-500 animate-ping opacity-75"
        ></div>
        <i 
          :class="[
            'text-lg',
            isRecording ? 'fas fa-microphone text-white animate-pulse' : 'fas fa-microphone text-blue-500'
          ]"
        ></i>
      </div>
    </div>
    
    <!-- Enhanced sound wave visualization -->
    <div class="flex items-center space-x-1 h-6">
      <div 
        v-for="i in 7" 
        :key="i"
        :class="[
          'w-1.5 rounded-full transition-all duration-100',
          isRecording ? 'bg-blue-500' : 'bg-gray-300'
        ]"
        :style="{
          height: isRecording 
            ? `${Math.min(Math.max(decibelLevel * (0.5 + (i % 4) * 0.25), 4), 24)}px` 
            : '4px'
        }"
      ></div>
    </div>
    
    <!-- Status text with better visibility -->
    <div class="text-center">
      <p 
        :class="[
          'text-sm font-medium transition-all duration-300',
          isRecording ? 'text-blue-600' : 'text-gray-400'
        ]"
      >
        {{ isRecording ? 'Listening...' : 'Tap to speak' }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  isRecording: boolean;
  decibelLevel: number;
}>();
</script>

<style scoped>
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}
</style>