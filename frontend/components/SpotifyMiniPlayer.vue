<template>
  <div class="fixed bottom-0 left-0 right-0 bg-gradient-to-r from-green-900 to-green-700 text-white shadow-lg z-10 rounded-t-lg">
    <div class="container mx-auto">
      <div class="p-3">
        <!-- Track info with progress bar -->
        <div class="flex items-center mb-2">
          <img 
            v-if="spotifyStore.currentTrack?.album?.images?.[1]?.url" 
            :src="spotifyStore.currentTrack.album.images[1].url" 
            alt="Album cover" 
            class="w-16 h-16 mr-4 rounded-md shadow-md" 
          />
          <div class="flex-grow">
            <div class="flex justify-between items-center">
              <div>
                <div class="font-bold text-lg">{{ spotifyStore.currentTrack?.name }}</div>
                <div class="text-sm opacity-90">{{ spotifyStore.currentTrack?.artists.map(a => a.name).join(', ') }}</div>
                <div class="text-xs opacity-80 mt-1">{{ spotifyStore.currentTrack?.album?.name }}</div>
              </div>
              <div class="text-xs opacity-80">
                {{ formatTime(playbackPosition) }} / {{ formatTime(spotifyStore.currentTrack?.duration_ms) }}
              </div>
            </div>
            
            <!-- Progress bar -->
            <div class="w-full bg-gray-600 rounded-full h-1.5 mt-2">
              <div 
                class="bg-green-400 h-1.5 rounded-full" 
                :style="{ width: `${(playbackPosition / spotifyStore.currentTrack?.duration_ms) * 100}%` }"
              ></div>
            </div>
          </div>
        </div>
        
        <!-- Controls -->
        <div class="flex justify-center items-center space-x-6">
          <!-- Previous button -->
          <button class="text-white hover:text-green-300 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="19 20 9 12 19 4 19 20"></polygon>
              <line x1="5" y1="19" x2="5" y2="5"></line>
            </svg>
          </button>
          
          <!-- Play/Pause button -->
          <button 
            @click="togglePlayback()" 
            class="bg-white text-green-800 rounded-full p-3 hover:bg-green-100 transition-colors"
          >
            <svg v-if="spotifyStore.isPlaying" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="6" y="4" width="4" height="16"></rect>
              <rect x="14" y="4" width="4" height="16"></rect>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
          </button>
          
          <!-- Next button -->
          <button class="text-white hover:text-green-300 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polygon points="5 4 15 12 5 20 5 4"></polygon>
              <line x1="19" y1="5" x2="19" y2="19"></line>
            </svg>
          </button>
        </div>
        
        <!-- Additional track details -->
        <div class="mt-3 flex justify-between text-xs opacity-80">
          <div v-if="spotifyStore.currentTrack?.popularity">
            <span class="font-medium">Popularity:</span> {{ spotifyStore.currentTrack.popularity }}/100
          </div>
          <div v-if="spotifyStore.currentTrack?.explicit" class="px-1.5 py-0.5 bg-red-500 rounded text-white text-xs">
            Explicit
          </div>
          <div v-if="releaseYear">
            <span class="font-medium">Released:</span> {{ releaseYear }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watchEffect } from 'vue';
import { useSpotifyStore } from '@/stores/spotify';

const emit = defineEmits(['open-spotify-feature']);
const spotifyStore = useSpotifyStore();
const playbackPosition = ref(0);
let playbackTimer: number | null = null;

// Extract release year from release_date if available
const releaseYear = computed(() => {
  if (spotifyStore.currentTrack?.album?.release_date) {
    return spotifyStore.currentTrack.album.release_date.split('-')[0];
  }
  return null;
});

// Format milliseconds to MM:SS
const formatTime = (ms: number) => {
  if (!ms) return '0:00';
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
};

// Simulate playback progress
const startPlaybackTimer = () => {
  if (playbackTimer) clearInterval(playbackTimer);

  // Start from current position or 0
  playbackPosition.value = spotifyStore.playbackPosition || 0;

  // Update every second if playing
  if (spotifyStore.isPlaying) {
    playbackTimer = window.setInterval(() => {
      if (playbackPosition.value < spotifyStore.currentTrack?.duration_ms) {
        playbackPosition.value += 1000;
      } else {
        // Reset at end of track
        playbackPosition.value = 0;
      }
    }, 1000);
  }
};

// Watch for playback state changes
watchEffect(() => {
  if (spotifyStore.isPlaying) {
    startPlaybackTimer();
  } else if (playbackTimer) {
    clearInterval(playbackTimer);
  }
});

onMounted(() => {
  startPlaybackTimer();
});

onUnmounted(() => {
  if (playbackTimer) clearInterval(playbackTimer);
});

const togglePlayback = () => {
  if (spotifyStore.isPlaying) {
    spotifyStore.pauseMusic();
  } else {
    if (spotifyStore.playbackPosition > 0) {
      // If there is a saved playback position, call resumePlayback instead of playMusic
      spotifyStore.resumePlayback();
    } else {
      spotifyStore.playMusic();
    }
  }
};

const openSpotifyFeature = () => {
  emit('open-spotify-feature');
};
</script>
