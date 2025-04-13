<!-- App.vue -->
<template>
  <div class="flex flex-col h-screen">
    <NavBar />

    <!-- Main Content: Vertical Button Bar + Camera -->
    <div class="flex flex-grow">
      <!-- Vertical Button Bar -->
      <div class="bg-base-200 p-2 flex flex-col space-y-2 min-w-[100px]">
        <ButtonBar 
          :defaultSelected="selectedButtonName" 
          @update:selectedButton="updateSelectedButton" 
        />
      </div>

      <!-- Camera Area (Smaller & Centered) -->
      <div class="flex flex-1 justify-center items-center">
        <div class="flex flex-col items-center">
          <div class="w-[320px] h-[240px] rounded overflow-hidden shadow-lg">
            <Camera 
              :resolution="cameraResolution" 
              ref="cameraRef" 
              autoplay 
              class="w-full h-full" 
            />
          </div>
          <div class="mt-4">
            <button class="btn btn-primary" @click="handleSnapshot">
              Take Snapshot
            </button>
          </div>
          <div class="mt-4">
            <VoiceCommand @featureMatched="updateSelectedButton" />
          </div>
        </div>
      </div>
    </div>

    <!-- Audio Player -->
    <audio v-if="audioStore.currentAudio" :src="audioStore.currentAudio" autoplay style="display: none;"></audio>

    <!-- Spotify Mini Player -->
    <SpotifyMiniPlayer v-if="spotifyStore.currentTrack" />

    <!-- Modals -->
    <SettingsModal :show="isSettingsModalOpen" @close="isSettingsModalOpen = false" />
    <AboutModal :show="isAboutModalOpen" @close="isAboutModalOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import Camera from 'simple-vue-camera';
import NavBar from '@/components/NavBar.vue';
import ButtonBar from '@/components/ButtonBar.vue';
import VoiceCommand from '@/components/VoiceCommand.vue';
import SpotifyMiniPlayer from '@/components/SpotifyMiniPlayer.vue';
import SettingsModal from '@/components/modals/SettingsModal.vue';
import AboutModal from '@/components/modals/AboutModal.vue';
import { useSpotifyStore } from '@/stores/spotify';
import { useAudioStore } from '@/stores/audio';
import { useApiService } from '@/services/apiService';

// Refs
const cameraRef = ref<InstanceType<typeof Camera>>();
const selectedButtonName = ref<string>('Text');
const cameraResolution = ref({ width: 375, height: 600 });
const isSettingsModalOpen = ref(false);
const isAboutModalOpen = ref(false);

// Stores
const spotifyStore = useSpotifyStore();
const audioStore = useAudioStore();
const apiService = useApiService();

// Methods
const updateSelectedButton = (buttonName: string) => {
  selectedButtonName.value = buttonName;
  console.log(`Selected button: ${buttonName}`);
};

const handleSnapshot = async () => {
  if (selectedButtonName.value === 'Music') {
    await spotifyStore.detectMusic();
    return;
  }

  const blob = await cameraRef.value?.snapshot();
  if (blob) {
    apiService.processImage(blob, selectedButtonName.value);
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
  spotifyStore.initializePlayer();
});

onUnmounted(() => {
  window.removeEventListener('resize', updateCameraResolution);
});
</script>