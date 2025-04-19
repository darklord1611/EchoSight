export default defineNuxtPlugin(() => {
    const sendAudioForCommand = async (audioBlob: Blob): Promise<string> => {
        const formData = new FormData();
        // Change the file extension to .webm as we are working with .webm format
        formData.append("file", new File([audioBlob], "voice-input.webm", { type: "audio/webm" }));

        console.log("Detecting voice command...");
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/transcribe_audio`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            console.log(data);

            return data?.command || '';
        } catch (err) {
            console.error("❌ Failed to send audio for voice command:", err);
            return '';
        }
    };

    const sendAudioForNews = async (audioBlob: Blob): Promise<string> => {
        const formData = new FormData();
        // Change the file extension to .webm as we are working with .webm format
        formData.append("file", new File([audioBlob], "voice-input.webm", { type: "audio/webm" }));

        console.log("Sending audio for news...");
        try {
            const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/article_reading`, {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            console.log(data);

            return data;
        } catch (err) {
            console.error("❌ Failed to send audio for voice command:", err);
            return '';
        }
    }

    return {
        provide: {
            sendAudioForCommand,
            sendAudioForNews,
        }
    };
});
