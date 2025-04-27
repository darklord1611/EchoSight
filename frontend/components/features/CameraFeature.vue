<template>
  <div class="flex flex-col items-center space-y-6">
    <!-- Camera Container -->
    <div class="w-full max-w-[640px] h-auto aspect-video rounded-lg overflow-hidden shadow-lg bg-black">
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
import { ref, onMounted, onUnmounted, defineProps, defineEmits } from 'vue';
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
const cameraResolution = ref({ width: 640, height: 360 });

// Methods
const takeSnapshot = async () => {
  const blob = await cameraRef.value?.snapshot();
  if (blob) {
    emit('take-snapshot', blob);
  }
};

const updateCameraResolution = () => {
  if (window.innerWidth > 1024) {
    cameraResolution.value = { width: 1280, height: 720 }; // Desktop resolution
  } else if (window.innerWidth > 768) {
    cameraResolution.value = { width: 1024, height: 576 }; // Laptop resolution
  } else if (window.innerWidth > 480) {
    cameraResolution.value = { width: 960, height: 540 }; // Tablet resolution
  } else {
    cameraResolution.value = { width: 720, height: 405 }; // Mobile resolution
  }
};

// Lifecycle hooks
onMounted(() => {
  updateCameraResolution();
  window.addEventListener('resize', updateCameraResolution);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateCameraResolution);
});

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

.aspect-video {
  aspect-ratio: 16 / 9;
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