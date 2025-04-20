<!-- src/components/features/SpotifyFeature.vue -->
<template>
  <div class="flex flex-col items-center w-full max-w-2xl px-4">
    <div class="w-full bg-gradient-to-br from-green-900 via-green-800 to-green-700 rounded-xl shadow-xl overflow-hidden">
      <!-- Header -->
      <div class="p-6 text-white text-center border-b border-green-600">
        <div class="flex items-center justify-center mb-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
            <circle cx="12" cy="12" r="10"></circle>
            <circle cx="12" cy="12" r="4"></circle>
            <line x1="4.93" y1="4.93" x2="9.17" y2="9.17"></line>
            <line x1="14.83" y1="14.83" x2="19.07" y2="19.07"></line>
            <line x1="14.83" y1="9.17" x2="19.07" y2="4.93"></line>
            <line x1="4.93" y1="19.07" x2="9.17" y2="14.83"></line>
          </svg>
          <h2 class="text-2xl font-bold">EchoSight Music</h2>
        </div>
        <p class="text-green-200">Detect and play music instantly</p>
      </div>

      <div class="p-6">
        <!-- Detect Button -->
        <div class="flex justify-center mb-6">
          <button
            @click="detectMusic"
            :disabled="isDetecting"
            class="btn bg-green-600 hover:bg-green-500 text-white px-6 py-2 rounded-full shadow-md transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <svg
              v-if="isDetecting"
              class="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            <span>{{ isDetecting ? 'Listening...' : 'Detect Music' }}</span>
          </button>
        </div>

        <!-- Currently Playing -->
        <div v-if="spotifyStore.currentTrack" class="bg-black bg-opacity-30 rounded-lg p-5">
          <div class="flex items-center">
            <img 
              v-if="spotifyStore.currentTrack.album?.images?.[0]?.url" 
              :src="spotifyStore.currentTrack.album.images[0].url" 
              alt="Album cover" 
              class="w-28 h-28 rounded-lg shadow-lg" 
            />
            <div class="ml-4 text-white">
              <div class="text-xl font-bold">{{ spotifyStore.currentTrack.name }}</div>
              <div class="text-green-300">{{ spotifyStore.currentTrack.artists.map(a => a.name).join(', ') }}</div>
              <div class="text-sm text-green-200 mt-1">{{ spotifyStore.currentTrack.album?.name }}</div>

              <!-- Metadata -->
              <div class="flex flex-wrap mt-3 gap-2">
                <span v-if="spotifyStore.currentTrack.explicit" class="px-2 py-1 bg-red-500 rounded text-xs">Explicit</span>
                <span class="px-2 py-1 bg-green-800 rounded text-xs">{{ formatDuration(spotifyStore.currentTrack.duration_ms) }}</span>
                <span v-if="spotifyStore.currentTrack.popularity" class="px-2 py-1 bg-green-800 rounded text-xs">
                  Popularity: {{ spotifyStore.currentTrack.popularity }}/100
                </span>
              </div>
            </div>
          </div>

          <!-- Play/Pause Buttons -->
          <div class="flex justify-center mt-6">
            <button 
              @click="spotifyStore.isPlaying ? spotifyStore.pauseMusic() : spotifyStore.playMusic()" 
              class="bg-green-500 text-white rounded-full p-4 hover:bg-green-400 transition-colors"
            >
              <svg v-if="spotifyStore.isPlaying" xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="6" y="4" width="4" height="16"></rect>
                <rect x="14" y="4" width="4" height="16"></rect>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
            </button>
          </div>
        </div>

        <!-- Empty state -->
        <div v-else class="text-center text-green-100 mt-6">
          No song detected yet. Click the button above to listen and identify.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useSpotifyStore } from '@/stores/spotify';

const spotifyStore = useSpotifyStore();
const isDetecting = ref(false);

const detectMusic = async () => {
  try {
    isDetecting.value = true;
    await spotifyStore.detectMusic();
  } catch (error) {
    console.error('Music detection failed:', error);
  } finally {
    isDetecting.value = false;
  }
};

const formatDuration = (ms: number) => {
  const minutes = Math.floor(ms / 60000);
  const seconds = Math.floor((ms % 60000) / 1000);
  return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
};
</script>
