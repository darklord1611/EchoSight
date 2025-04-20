<template>
  <div class="flex flex-col items-center w-full">
    <h2 class="text-2xl font-bold mb-4">💬 Chat Assistant</h2>

    <div class="bg-base-200 rounded-xl shadow-lg w-full max-w-lg p-4">
      <div
        ref="chatContainer"
        class="bg-base-100 rounded-md p-3 h-80 overflow-y-auto space-y-2 mb-4 scroll-smooth"
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
            >
              {{ msg.text }}
            </div>
          </div>
        </template>
        <p v-else class="text-center text-base-content opacity-70">Chat messages will appear here</p>
      </div>

      <div class="flex items-center">
        <input
          v-model="input"
          @keyup.enter="handleSend"
          type="text"
          placeholder="Type your message..."
          class="input input-bordered flex-grow mr-2"
        />
        <button class="btn btn-primary" :disabled="chatbot.loading" @click="handleSend">
          {{ chatbot.loading ? '...' : 'Send' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatbotStore } from '@/stores/chatbot'

const chatbot = useChatbotStore()
const chatContainer = ref<HTMLDivElement | null>(null)
const input = ref('')

// Local send handler
const handleSend = () => {
  if (input.value.trim()) {
    chatbot.sendMessage(input.value)
    input.value = ''
  }
}

// Auto scroll
watch(() => chatbot.messages, async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}, { deep: true })
</script>
