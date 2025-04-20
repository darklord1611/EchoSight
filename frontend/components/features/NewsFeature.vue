<script setup lang="ts">
import { useNewsStore } from '@/stores/news';
import { computed } from 'vue';

const newsStore = useNewsStore();

const articles = computed(() => newsStore.articles);
const loading = computed(() => newsStore.loading);
const error = computed(() => newsStore.error);

// Read article aloud
const readArticle = (article: { title: string; summary: string }) => {
  const utterance = new SpeechSynthesisUtterance(`${article.title}. ${article.summary}`);
  utterance.lang = 'en-US';
  speechSynthesis.speak(utterance);
};

// Optional: helper to stop current speech
const stopSpeaking = () => {
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel();
  }
};

// Expose for external voice commands
defineExpose({
  readArticle,
  stopSpeaking,
});
</script>

<template>
  <div class="p-4 w-full">
    <h2 class="text-xl font-bold mb-4">News Results for "{{ newsStore.query }}"</h2>

    <div v-if="loading">Loading news...</div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="article in articles"
        :key="article.url"
        class="bg-white shadow-md rounded-2xl p-4 border border-gray-200 transition hover:shadow-lg"
      >
        <h3 class="text-lg font-semibold mb-2">{{ article.title }}</h3>
        <p class="text-sm text-gray-700 mb-3">{{ article.summary }}</p>
        <div class="flex items-center justify-between">
          <a
            :href="article.url"
            target="_blank"
            class="text-blue-600 underline text-sm hover:text-blue-800"
          >
            Read Full Article
          </a>
          <button
            @click="readArticle(article)"
            class="text-sm px-3 py-1 rounded bg-blue-500 text-white hover:bg-blue-600"
          >
            🔊 Read Aloud
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
