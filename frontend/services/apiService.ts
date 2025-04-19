import { v4 as uuidv4 } from 'uuid';

export function useApiService() {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

    const endpoints: Record<string, string> = {
        'Text': '/document_recognition',
        'Currency': '/currency_detection',
        'Object': '/image_captioning',
        'Product': '/product_recognition',
        'Distance': '/distance_estimate',
        'Face': '/face_detection/recognize',
        'Music': '/',
    };

    const speakText = (text: string) => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US'; // You can customize this
        speechSynthesis.speak(utterance);
    };

    const processImage = async (blob: Blob, buttonName: string) => {
        const endpoint = endpoints[buttonName];
        if (!endpoint) return;

        const fullUrl = `${BACKEND_URL}${endpoint}`;
        const id = uuidv4();
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

            // 👇 Use speech synthesis to speak the text
            const textToSpeak = jsonResponse?.text || jsonResponse?.description || jsonResponse?.result || 'No description available.';
            speakText(textToSpeak);

            return jsonResponse;
        } catch (error) {
            console.error('Error sending image to endpoint:', error);
            speakText("Sorry, something went wrong processing the image.");
            return null;
        }
    };

    return {
        processImage
    };
}
