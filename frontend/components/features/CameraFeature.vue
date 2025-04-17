<!-- src/components/features/CameraFeature.vue -->
<template>
    <div class="flex flex-col items-center">
      <div class="w-[320px] h-[240px] rounded overflow-hidden shadow-lg">
        <Camera 
          :resolution="cameraResolution" 
          ref="cameraRef" 
          autoplay
        />
      </div>
      <div class="mt-4">
        <button class="btn btn-primary" @click="takeSnapshot">
          Take Snapshot
        </button>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, onUnmounted, defineProps, defineEmits } from 'vue';
  import Camera from 'simple-vue-camera';
  import { useSpotifyStore } from '@/stores/spotify';
  
  const props = defineProps({
    featureType: {
      type: String,
      required: true
    }
  });
  
  const emit = defineEmits(['take-snapshot']);
  
  // Refs
  const cameraRef = ref<InstanceType<typeof Camera>>();
  const cameraResolution = ref({ width: 320, height: 240 });
  
  // Stores
  const spotifyStore = useSpotifyStore();
  
  // Methods
  const takeSnapshot = async () => {
    if (props.featureType === 'Music') {
      await spotifyStore.detectMusic();
      return;
    }
  
    const blob = await cameraRef.value?.snapshot();
    if (blob) {
      emit('take-snapshot', blob);
    }
  };
  
  const updateCameraResolution = () => {
    if (window.innerWidth > window.innerHeight) {
      cameraResolution.value = { width: 600, height: 375 };
    } else {
      cameraResolution.value = { width: 375, height: 600 };
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