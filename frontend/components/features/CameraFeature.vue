<template>
  <div class="flex flex-col items-center space-y-6">
    <!-- Camera Container -->
    <div 
      class="w-[320px] h-[240px] rounded-lg overflow-hidden shadow-lg bg-black"
    >
      <Camera 
        :resolution="cameraResolution" 
        ref="cameraRef" 
        autoplay
      />
    </div>

    <!-- Snapshot Button -->
    <div>
      <button 
        class="btn btn-primary px-6 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        @click="takeSnapshot"
        aria-label="Take a snapshot"
        title="Take a snapshot"
      >
        Take Snapshot
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits } from 'vue';
import Camera from 'simple-vue-camera';

const props = defineProps({
  featureType: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['take-snapshot']);

// Refs
const cameraRef = ref<InstanceType<typeof Camera>>();
const cameraResolution = ref({ width: 320, height: 240 }); // Fixed resolution for laptop screens

// Methods
const takeSnapshot = async () => {
  const blob = await cameraRef.value?.snapshot();
  if (blob) {
    emit('take-snapshot', blob);
  }
};

// Expose snapshot method to parent
defineExpose({
  takeSnapshot
});
</script>

<style scoped>
/* Camera container styles */
.bg-black {
  background-color: #000;
}

.shadow-lg {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Button styles */
.btn-primary {
  background-color: #2563eb; /* Bright blue */
  color: white;
  border: none;
  border-radius: 0.5rem;
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.btn-primary:hover {
  background-color: #1d4ed8; /* Darker blue */
  transform: scale(1.05);
}

.focus\:ring-2 {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5); /* Blue focus ring */
}
</style>