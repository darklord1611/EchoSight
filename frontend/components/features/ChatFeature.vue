<template>
  <div class="flex flex-col items-center w-full p-4">
    <h2 class="text-2xl font-bold mb-4 text-gray-800">💬 Chat Assistant</h2>

    <div class="bg-white rounded-xl shadow-lg w-full max-w-lg p-4 border border-gray-200">
      <!-- Chat Messages -->
      <div
        ref="chatContainer"
        class="bg-gray-100 rounded-md p-3 h-80 overflow-y-auto space-y-2 mb-4 scroll-smooth"
        aria-live="polite"
        aria-label="Chat messages"
      >
        <template v-if="chatbot.messages.length">
          <div
            v-for="(msg, i) in chatbot.messages"
            :key="i"
            class="flex"
            :class="msg.sender === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              :class="msg.sender === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-900'"
              class="max-w-[80%] rounded-xl px-4 py-2 shadow"
              :aria-label="msg.sender === 'user' ? 'Your message' : 'Assistant message'"
            >
              {{ msg.text }}
            </div>
          </div>
        </template>
        <p v-else class="text-center text-gray-500 opacity-70">Chat messages will appear here</p>
      </div>

      <!-- Input and Send Button -->
      <div class="flex items-center">
        <input
          v-model="input"
          @keyup.enter="handleSend"
          type="text"
          placeholder="Type your message..."
          class="bg-white text-gray-800 flex-grow px-4 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Type your message"
        />
        <button
          class="px-4 py-2 bg-blue-500 text-white rounded-r-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          :disabled="chatbot.loading"
          @click="handleSend"
          aria-label="Send message"
        >
          {{ chatbot.loading ? '...' : 'Send' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import { useChatbotStore } from '@/stores/chatbot';

const chatbot = useChatbotStore();
const chatContainer = ref<HTMLDivElement | null>(null);
const input = ref('');

// Local send handler
const handleSend = () => {
  if (input.value.trim()) {
    chatbot.sendMessage(input.value);
    input.value = '';
  }
};

// Auto scroll
watch(
  () => chatbot.messages,
  async () => {
    await nextTick();
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  },
  { deep: true }
);
</script>

<style scoped>
/* Chat container styles */
.bg-gray-100 {
  background-color: #f3f4f6;
}

.bg-gray-200 {
  background-color: #e5e7eb;
}

.text-gray-800 {
  color: #1f2937;
}

.text-gray-500 {
  color: #6b7280;
}

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

.shadow-lg {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.rounded-xl {
  border-radius: 0.75rem;
}
</style>