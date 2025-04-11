<template>
    <div v-if="track" class="flex items-center bg-base-200 p-3 rounded-xl shadow-md gap-4 w-full max-w-md mx-auto">
        <img :src="track.album.images[0].url" class="w-16 h-16 rounded-lg object-cover" />
        <div class="flex flex-col flex-grow">
        <span class="font-semibold">{{ track.name }}</span>
        <span class="text-sm text-gray-500">{{ track.artists[0].name }}</span>
        </div>
        <button @click="togglePlayback" class="btn btn-sm btn-circle">
        <i :class="isPlaying ? 'fa-solid fa-pause' : 'fa-solid fa-play'"></i>
        </button>
    </div>
</template>

<script setup lang="ts">
defineProps<{
track: any;
isPlaying: boolean;
togglePlayback: () => void;
}>();
</script>
  