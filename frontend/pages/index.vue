<!-- App.vue -->
<template>
  <div class="flex flex-col h-screen">
    <NavBar />

    <!-- Main Content: Vertical Button Bar + Feature Components -->
    <div class="flex flex-grow">
      <!-- Vertical Button Bar -->
      <div class="bg-base-200 p-2 flex flex-col space-y-2 min-w-[100px]">
        <ButtonBar 
          :defaultSelected="selectedFeature" 
          @update:selectedButton="updateSelectedFeature" 
        />
      </div>

      <!-- Feature Area -->
      <div class="flex flex-1 justify-center items-center">
        <!-- Camera Feature -->
        <CameraFeature 
          v-if="selectedFeature === 'Text' || selectedFeature === 'Currency' || selectedFeature === 'Object' || selectedFeature === 'Distance' || selectedFeature === 'Product'" 
          ref="cameraFeatureRef"
          :featureType="selectedFeature"
          @take-snapshot="handleSnapshot"
        />
        
        <!-- Other features -->
        <SpotifyFeature v-if="selectedFeature === 'Spotify'" />
        <NewsFeature v-if="selectedFeature === 'News'" />
        <ChatFeature v-if="selectedFeature === 'Chat'" />
      </div>
    </div>

    <!-- Always visible components like voice command -->
    <div class="fixed bottom-20 right-5">
      <VoiceCommand @featureMatched="updateSelectedFeature" />
    </div>

    <!-- Audio Player -->
    <audio v-if="audioStore.currentAudio" :src="audioStore.currentAudio" autoplay style="display: none;"></audio>

    <!-- Spotify Mini Player - only shown when in Music feature and a track is playing -->
    <SpotifyMiniPlayer 
      v-if="spotifyStore.currentTrack && selectedFeature === 'Music'" 
      @open-spotify-feature="openSpotifyFeature" 
    />

    <!-- Modals -->
    <SettingsModal :show="isSettingsModalOpen" @close="isSettingsModalOpen = false" />
    <AboutModal :show="isAboutModalOpen" @close="isAboutModalOpen = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import NavBar from '@/components/NavBar.vue';
import ButtonBar from '@/components/ButtonBar.vue';
import VoiceCommand from '@/components/VoiceCommand.vue';
import SpotifyMiniPlayer from '@/components/SpotifyMiniPlayer.vue';
import SettingsModal from '@/components/modals/SettingsModal.vue';
import AboutModal from '@/components/modals/AboutModal.vue';
import { useSpotifyStore } from '@/stores/spotify';
import { useAudioStore } from '@/stores/audio';
import { useApiService } from '@/services/apiService';

// Feature components
import CameraFeature from '@/components/features/CameraFeature.vue';
import SpotifyFeature from '@/components/features/SpotifyFeature.vue';
import NewsFeature from '@/components/features/NewsFeature.vue';
import ChatFeature from '@/components/features/ChatFeature.vue';

// Refs
const cameraFeatureRef = ref();
const selectedFeature = ref<string>('Text');
const isSettingsModalOpen = ref(false);
const isAboutModalOpen = ref(false);

// Stores
const spotifyStore = useSpotifyStore();
const audioStore = useAudioStore();
const apiService = useApiService();

// Methods
const updateSelectedFeature = (featureName: string) => {
  selectedFeature.value = featureName;
  console.log(`Selected feature: ${featureName}`);
};

const handleSnapshot = async (blob: Blob) => {
  if (blob) {
    apiService.processImage(blob, selectedFeature.value);
  }
};

const openSpotifyFeature = () => {
  selectedFeature.value = 'Spotify';
};

// Lifecycle hooks
onMounted(() => {
  // Initialize player with tokens from environment variables
  spotifyStore.initializePlayerWithEnvTokens();
});
</script>