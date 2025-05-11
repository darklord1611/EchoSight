// REMOVE speechSynthesis calls and just return the message for VoiceCommand to handle
import { v4 as uuidv4 } from 'uuid'
import axios from 'axios'

const speak = (text: string): Promise<void> => {
    return new Promise(resolve => {
        const utterance = new SpeechSynthesisUtterance(text)
        utterance.onend = () => resolve()
        speechSynthesis.speak(utterance)
    })
}

export function useApiService() {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL

    const endpoints: Record<string, string> = {
        'Text': '/document_recognition',
        'Currency': '/currency_detection',
        'Object': '/image_captioning',
        'Product': '/product_recognition',
        'Distance': '/distance_estimate_v2',
        'Face': '/face_detection/recognize',
        'Music': '/',
    }

    const processImage = async (blob: Blob, buttonName: string) => {
        const endpoint = endpoints[buttonName]
        if (!endpoint) return null

        const fullUrl = `${BACKEND_URL}${endpoint}`
        const id = uuidv4()
        const filename = `snapshot-${id}.jpg`
        const file = new File([blob], filename, { type: 'image/jpeg' })

        const formData = new FormData()
        formData.append('file', file)

        try {
            const { data } = await axios.post(fullUrl, formData, {
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'multipart/form-data',
                }
            })

            console.log(data)
            speak(data.text)

            return data
        } catch (error) {
            console.error('Axios error:', error)
            return { data: null, textToSpeak: 'Sorry, something went wrong processing the image.' }
        }
    }

    return {
        processImage
    }
}
