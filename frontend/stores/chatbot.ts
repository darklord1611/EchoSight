import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { babelParse } from 'vue/compiler-sfc'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

export const useChatbotStore = defineStore('chatbot', () => {
    const messages = ref<{ sender: 'user' | 'bot'; text: string }[]>([])
    const loading = ref(false)

    const sendMessage = async (text: string): Promise<string | null> => {
        const content = text.trim()
        if (!content) return null

        messages.value.push({ sender: 'user', text: content })
        loading.value = true

        try {
            const formData = new FormData();
            formData.append("message", content);

            const { data } = await axios.post(
                `${BACKEND_URL}/general_question_answering`,
                formData,
                {
                    headers: {
                        // Let the browser set the correct multipart/form-data headers
                        "Content-Type": "multipart/form-data",
                    },
                }
            );
            const reply = data.reply || "Hmm... I didn't quite get that."
            messages.value.push({ sender: 'bot', text: reply })

            // speak(reply)
            return reply
        } catch (err) {
            console.error('Chatbot API failed:', err)
            messages.value.push({ sender: 'bot', text: '❌ Failed to get a response. Try again later.' })
            return null
        } finally {
            loading.value = false
        }
    }

    const speak = (text: string): Promise<void> => {
        return new Promise(resolve => {
            const utterance = new SpeechSynthesisUtterance(text)
            utterance.onend = () => resolve()
            speechSynthesis.speak(utterance)
        })
    }

    const resetChat = () => {
        messages.value = []
    }

    return {
        messages,
        loading,
        sendMessage,
        resetChat
    }
})
