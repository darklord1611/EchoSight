import axios from 'axios'

export default defineNuxtPlugin(() => {
    const sendAudioForCommand = async (currentFeature: string, audioBlob: Blob): Promise<any> => {
        const formData = new FormData();
        formData.append("file", new File([audioBlob], "voice-input.webm", { type: "audio/webm" }));
        formData.append("current_feature", currentFeature);

        console.log("Detecting voice command...");

        try {
            const response = await axios.post(`${import.meta.env.VITE_BACKEND_URL}/transcribe_audio`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });

            console.log(response.data);
            return response.data;
        } catch (err) {
            console.error("❌ Failed to send audio for voice command:", err);
            return '';
        }
    };

    return {
        provide: {
            sendAudioForCommand,
        }
    };
});
