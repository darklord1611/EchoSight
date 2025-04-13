// services/apiService.ts
import { v4 as uuidv4 } from 'uuid';
import { useAudioStore } from '@/stores/audio';

export function useApiService() {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
    const audioStore = useAudioStore();

    const endpoints: Record<string, string> = {
        'Text': '/document_recognition',
        'Currency': '/currency_detection',
        'Object': '/image_captioning',
        'Product': '/product_recognition',
        'Distance': '/distance_estimate',
        'Face': '/face_detection/recognize',
        'Music': '/',
    };

    const processImage = async (blob: Blob, buttonName: string) => {
        const endpoint = endpoints[buttonName];
        if (!endpoint) return;

        const fullUrl = `${BACKEND_URL}${endpoint}`;

        const id = uuidv4(); // Unique ID for this snapshot
        const timestamp = new Date().toISOString();
        const filename = `snapshot-${id}.jpg`;

        const file = new File([blob], filename, { type: "image/jpeg" });

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(fullUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const jsonResponse = await response.json();
            console.log('JSON Response:', jsonResponse);

            const audioPath = jsonResponse?.audio_path;
            if (audioPath) {
                const encodedAudioPath = encodeURIComponent(audioPath);
                const audioFileUrl = `${BACKEND_URL}/download_audio?audio_path=${encodedAudioPath}`;
                console.log('Audio File URL:', audioFileUrl);
                audioStore.setCurrentAudio(audioFileUrl);
            }

            return jsonResponse;
        } catch (error) {
            console.error('Error sending image to endpoint:', error);
            return null;
        }
    };

    return {
        processImage
    };
}