<template>
  <div class="flex flex-col h-screen bg-gradient-to-br from-blue-100 via-white to-green-100">
    <NavBar />

    <!-- Main Content: Vertical Button Bar + Feature Components -->
    <div class="flex flex-grow">
      <!-- Vertical Button Bar -->
      <div class="bg-blue-200 p-2 flex flex-col space-y-2 min-w-[100px] shadow-lg">
        <ButtonBar :selectedFeature="selectedFeature" @update:selectedFeature="updateSelectedFeature" />
      </div>

      <!-- Feature Area -->
      <div class="flex flex-1 flex-col justify-center items-center space-y-6">
        <!-- Camera Feature -->
        <CameraFeature
          v-if="['Text', 'Currency', 'Object', 'Distance', 'Product'].includes(selectedFeature)"
          ref="cameraFeatureRef"
          :featureType="selectedFeature"
          @take-snapshot="handleSnapshot"
        />

        <!-- Response from camera -->
        <div v-if="cameraResponseText" class="bg-green-100 rounded-lg p-4 shadow-md max-w-xl text-center">
          <p class="text-green-800 font-medium">{{ cameraResponseText }}</p>
        </div>

        <!-- Other Features -->
        <SpotifyFeature v-if="selectedFeature === 'Music'" />
        <NewsFeature v-if="selectedFeature === 'News'" />
        <ChatFeature v-if="selectedFeature === 'Chatbot'" />

        <!-- Voice Command and Visualizer -->
        <div class="flex flex-col items-center w-full max-w-md">
          <VoiceCommand
            :selectedFeature="selectedFeature"
            :cameraRef="cameraFeatureRef"
            @featureMatched="updateSelectedFeature"
          />
        </div>
      </div>
    </div>

    <!-- Spotify Mini Player -->
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
import VoiceVisualizer from '@/components/VoiceVisualizer.vue';
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
const isSettingsModalOpen = ref<boolean>(false);
const isAboutModalOpen = ref<boolean>(false);
const cameraResponseText = ref<string>('');

// Stores
const spotifyStore = useSpotifyStore();
const audioStore = useAudioStore();
const apiService = useApiService();

// Methods
const updateSelectedFeature = (featureName: string) => {
  selectedFeature.value = featureName;
  cameraResponseText.value = ''; // Clear result when switching features
  console.log(`Selected feature: ${featureName}`);
};

const handleSnapshot = async (blob: Blob) => {
  if (blob) {
    const result = await apiService.processImage(blob, selectedFeature.value);
    if (result?.text) {
      cameraResponseText.value = result.text;
    } else {
      cameraResponseText.value = 'No description available.';
    }
  }
};

const openSpotifyFeature = () => {
  selectedFeature.value = 'Music';
};

// Lifecycle
onMounted(() => {
});
</script>

<style scoped>
/* Add custom styles for brighter colors */
.bg-blue-200 {
  background-color: #cce7ff;
}

.bg-green-100 {
  background-color: #d4f8d4;
}

.text-green-800 {
  color: #2d6a2d;
}

.shadow-lg {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>