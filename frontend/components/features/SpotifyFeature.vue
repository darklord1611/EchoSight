<!-- src/components/features/SpotifyFeature.vue -->
<template>
    <div class="flex flex-col items-center w-full max-w-2xl px-4">
      <div class="w-full bg-gradient-to-br from-green-900 via-green-800 to-green-700 rounded-xl shadow-xl overflow-hidden">
        <!-- Header -->
        <div class="p-6 text-white text-center border-b border-green-600">
          <div class="flex items-center justify-center mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
              <circle cx="12" cy="12" r="10"></circle>
              <circle cx="12" cy="12" r="4"></circle>
              <line x1="4.93" y1="4.93" x2="9.17" y2="9.17"></line>
              <line x1="14.83" y1="14.83" x2="19.07" y2="19.07"></line>
              <line x1="14.83" y1="9.17" x2="19.07" y2="4.93"></line>
              <line x1="4.93" y1="19.07" x2="9.17" y2="14.83"></line>
            </svg>
            <h2 class="text-2xl font-bold">Spotify Music</h2>
          </div>
          <p class="text-green-200">Search, discover and play your favorite music</p>
        </div>
        
        <div class="p-6">
          <div v-if="spotifyStore.isAuthenticated">
            <!-- Currently playing section -->
            <div v-if="spotifyStore.currentTrack" class="mb-8">
              <div class="text-lg font-semibold text-white mb-3">Now Playing</div>
              <div class="bg-black bg-opacity-30 rounded-lg p-4">
                <div class="flex items-center">
                  <img 
                    v-if="spotifyStore.currentTrack.album?.images?.[0]?.url" 
                    :src="spotifyStore.currentTrack.album.images[0].url" 
                    alt="Album cover" 
                    class="w-32 h-32 rounded-lg shadow-lg" 
                  />
                  <div class="ml-4 text-white">
                    <div class="text-xl font-bold">{{ spotifyStore.currentTrack.name }}</div>
                    <div class="text-green-300">{{ spotifyStore.currentTrack.artists.map(a => a.name).join(', ') }}</div>
                    <div class="text-sm text-green-200 mt-1">{{ spotifyStore.currentTrack.album?.name }}</div>
                    
                    <!-- Track metadata -->
                    <div class="flex flex-wrap mt-3 gap-2">
                      <span v-if="spotifyStore.currentTrack.explicit" class="px-2 py-1 bg-red-500 rounded text-xs">
                        Explicit
                      </span>
                      <span class="px-2 py-1 bg-green-800 rounded text-xs">
                        {{ formatDuration(spotifyStore.currentTrack.duration_ms) }}
                      </span>
                      <span v-if="spotifyStore.currentTrack.popularity" class="px-2 py-1 bg-green-800 rounded text-xs">
                        Popularity: {{ spotifyStore.currentTrack.popularity }}/100
                      </span>
                    </div>
                  </div>
                </div>
                
                <!-- Player controls -->
                <div class="flex justify-center mt-6 space-x-6">
                  <button @click="spotifyStore.previousTrack" class="text-white hover:text-green-300 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polygon points="19 20 9 12 19 4 19 20"></polygon>
                      <line x1="5" y1="19" x2="5" y2="5"></line>
                    </svg>
                  </button>
                  
                  <button 
                    @click="spotifyStore.isPlaying ? spotifyStore.pausePlayback() : spotifyStore.resumePlayback()" 
                    class="bg-green-500 text-white rounded-full p-3 hover:bg-green-400 transition-colors"
                  >
                    <svg v-if="spotifyStore.isPlaying" xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="6" y="4" width="4" height="16"></rect>
                      <rect x="14" y="4" width="4" height="16"></rect>
                    </svg>
                    <svg v-else xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polygon points="5 3 19 12 5 21 5 3"></polygon>
                    </svg>
                  </button>
                  
                  <button @click="spotifyStore.nextTrack" class="text-white hover:text-green-300 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polygon points="5 4 15 12 5 20 5 4"></polygon>
                      <line x1="19" y1="5" x2="19" y2="19"></line>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
  
            <!-- Search section -->
            <div class="bg-black bg-opacity-20 rounded-lg p-5">
              <div class="text-lg font-semibold text-white mb-3">Search Music</div>
              <div class="flex flex-col md:flex-row gap-2">
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="Search for songs, artists, or albums" 
                  class="input bg-black bg-opacity-40 text-white border-green-800 flex-grow" 
                  @keyup.enter="searchSpotify"
                />
                <button 
                  @click="searchSpotify" 
                  class="btn bg-green-600 hover:bg-green-500 border-0 text-white"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  </svg>
                  Search
                </button>
              </div>
              
              <!-- Search loading indicator -->
              <div v-if="isSearching" class="mt-4 flex justify-center">
                <div class="animate-spin rounded-full h-6 w-6 border-t-2 border-l-2 border-green-500"></div>
              </div>
              
              <!-- Search results -->
              <div v-if="searchResults.length > 0" class="mt-4">
                <div class="text-green-300 text-sm mb-2">{{ searchResults.length }} results found</div>
                <div class="max-h-96 overflow-y-auto pr-2 space-y-2">
                  <div 
                    v-for="(track, index) in searchResults" 
                    :key="index"
                    class="flex items-center p-3 rounded-lg bg-black bg-opacity-30 hover:bg-opacity-50 cursor-pointer transition-colors"
                    @click="playTrack(track)"
                  >
                    <img 
                      v-if="track.album?.images?.[2]?.url" 
                      :src="track.album.images[2].url" 
                      alt="Album cover" 
                      class="w-12 h-12 rounded-md" 
                    />
                    <div class="ml-3 text-white">
                      <div class="font-medium">{{ track.name }}</div>
                      <div class="flex items-center text-sm text-green-300">
                        <span>{{ track.artists.map(a => a.name).join(', ') }}</span>
                        <span class="mx-2">•</span>
                        <span>{{ track.album.name }}</span>
                        <span v-if="track.explicit" class="ml-2 px-1 py-0.5 bg-red-500 rounded-sm text-xs">E</span>
                      </div>
                    </div>
                    <div class="ml-auto text-sm text-green-400">
                      {{ formatDuration(track.duration_ms) }}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- No results message -->
              <div v-else-if="searchPerformed && !isSearching" class="mt-4 text-center text-green-200">
                No results found. Try different keywords.
              </div>
            </div>
          </div>
          
          <!-- Not authenticated state -->
          <div v-else class="text-center p-6">
            <div class="mb-6">
              <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="mx-auto text-green-300">
                <path d="M9 18V5l12-2v13"></path>
                <circle cx="6" cy="18" r="3"></circle>
                <circle cx="18" cy="16" r="3"></circle>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watchEffect } from 'vue';
  import { useSpotifyStore } from '@/stores/spotify';
  
  const spotifyStore = useSpotifyStore();
  const searchQuery = ref('');
  const searchResults = ref([]);
  const isSearching = ref(false);
  const searchPerformed = ref(false);
  
  // Format milliseconds to MM:SS
  const formatDuration = (ms: number) => {
    if (!ms) return '0:00';
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };
  
  const searchSpotify = async () => {
    if (!searchQuery.value.trim()) return;
    
    try {
      isSearching.value = true;
      searchResults.value = await spotifyStore.searchTracks(searchQuery.value);
      searchPerformed.value = true;
    } catch (error) {
      console.error('Error searching Spotify:', error);
    } finally {
      isSearching.value = false;
    }
  };
  
  const playTrack = (track) => {
    spotifyStore.playTrack(track);
  };
  </script>