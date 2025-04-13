// stores/audio.ts
import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useAudioStore = defineStore('audio', () => {
  const currentAudio = ref<string | null>(null);

  const setCurrentAudio = (url: string) => {
    currentAudio.value = url;
    
    // Play audio immediately
    const audio = new Audio(url);
    audio.play().catch(err => {
      console.error("Audio playback failed:", err);
    });
  };

  return {
    currentAudio,
    setCurrentAudio
  };
});