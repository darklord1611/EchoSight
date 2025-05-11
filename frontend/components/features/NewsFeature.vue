<script setup lang="ts">
import { computed, ref } from 'vue';
import { useNewsStore } from '@/stores/news';

const newsStore = useNewsStore();

const articles = computed(() => newsStore.articles);
const loading = computed(() => newsStore.loading);
const error = computed(() => newsStore.error);

// Query input for normal users
const userQuery = ref(newsStore.query);

// Update query and fetch news
const updateQuery = () => {
  if (userQuery.value.trim()) {
    const query = userQuery.value.trim();
    newsStore.fetchNews(query);
  }
};

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
    <!-- Query Input -->
    <div class="mb-6 flex flex-col items-center">
    <label for="query" class="text-lg font-semibold mb-2 text-gray-800">Search News</label>
    <div class="flex w-full max-w-md">
      <input
        id="query"
        v-model="userQuery"
        type="text"
        placeholder="Type your query here..."
        class="flex-1 px-4 text-gray-800 py-2 border border-gray-300 rounded-l-lg bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button
        @click="updateQuery"
        class="px-4 py-2 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-label="Search news"
      >
        Search
      </button>
    </div>
  </div>

  <!-- News Results -->
  <div>
    <div v-if="loading" class="text-center text-gray-500">Loading news...</div>
    <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="article in articles"
        :key="article.url"
        class="bg-white shadow-lg rounded-lg p-6 border border-gray-200 transition hover:shadow-xl focus-within:ring-2 focus-within:ring-blue-500"
        tabindex="0"
        aria-label="News article card"
      >
        <h3 class="text-lg font-semibold mb-3 text-gray-900">{{ article.title }}</h3>
        <p class="text-sm text-gray-700 mb-4">{{ article.summary }}</p>
        <div class="flex items-center justify-between">
          <a
            :href="article.url"
            target="_blank"
            class="text-blue-600 underline text-sm hover:text-blue-800"
            aria-label="Read full article"
          >
            Read Full Article
          </a>
          <button
            @click="readArticle(article)"
            class="text-sm px-4 py-2 rounded bg-blue-500 text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Read article aloud"
          >
            🔊 Read Aloud
          </button>
        </div>
      </div>
    </div>
  </div>
  </div>
</template>

<style scoped>
/* Responsive grid layout */
.grid {
  display: grid;
  gap: 1.5rem;
}

/* Card styles */
.bg-white {
  background-color: #ffffff;
}

.shadow-lg {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.shadow-xl:hover {
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
}

.rounded-lg {
  border-radius: 0.5rem;
}

.transition {
  transition: all 0.2s ease-in-out;
}

/* Button styles */
.bg-blue-500 {
  background-color: #2563eb;
}

.bg-blue-500:hover {
  background-color: #1d4ed8;
}

.focus\:ring-2:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.5);
}
</style>