<!-- components/SpotifyMiniPlayer.vue -->
<template>
    <div class="fixed bottom-4 right-4 bg-base-200 p-3 rounded-lg shadow-lg flex items-center gap-3 w-64">
      <img 
        v-if="spotifyStore.currentTrack?.album?.images?.[0]?.url" 
        :src="spotifyStore.currentTrack.album.images[0].url" 
        class="w-12 h-12 rounded" 
        alt="Album Art"
      />
      <div class="flex-1 overflow-hidden">
        <p class="font-bold text-sm truncate">{{ spotifyStore.currentTrack?.name }}</p>
        <p class="text-xs truncate">{{ spotifyStore.currentTrack?.artists?.[0]?.name }}</p>
      </div>
      <button @click="spotifyStore.togglePlayback" class="btn btn-circle btn-xs">
        <i :class="spotifyStore.isPlaying ? 'fa-solid fa-pause' : 'fa-solid fa-play'"></i>
      </button>
    </div>
  </template>
  
  <script setup lang="ts">
  import { useSpotifyStore } from '@/stores/spotify';
  
  const spotifyStore = useSpotifyStore();
  </script>