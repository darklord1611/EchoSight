<template>
    <div class="flex flex-col h-screen">
        <div class="navbar bg-base-100 h-[10%]">
            <div class="flex-none">
                <button class="btn btn-square btn-ghost" onclick="settings.showModal()">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                        class="inline-block h-5 w-5 stroke-current">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16">
                        </path>
                    </svg>
                </button>
            </div>
            <div class="flex-1">
                <a class="btn btn-ghost text-xl">EchoSight</a>
            </div>
            <div class="flex-none">
                <button class="btn btn-square btn-ghost" onclick="about.showModal()">
                    <i class="fa-regular fa-circle-question text-xl"></i>
                </button>
            </div>
        </div>

        <div class="flex-grow h-[70%]">
            <div class="w-full h-full">
                <Camera :resolution="cameraResolution" ref="camera" autoplay />
            </div>
            <!-- <Camera :resolution="cameraResolution" ref="camera" autoplay class="w-full h-full"></Camera> -->
        </div>
        <div class="flex justify-center mt-4">
            <button class="btn btn-primary" @click="snapshot">
                Take Snapshot
            </button>
        </div>

        <div class="h-[20%] md:m-auto">
            <Buttonbar :defaultSelected="selectedButtonName" @update:selectedButton="updateSelectedButton" class="w-full h-full" />
        </div>

        <audio v-if="audioUrl" :src="audioUrl" autoplay style="display: none;"></audio>

        <dialog id="settings" class="modal">
            <div class="modal-box">
                <h3 class="text-lg font-bold">Taluli talula!</h3>
                <p class="py-4">Taluli talula!</p>
            </div>
            <form method="dialog" class="modal-backdrop">
                <button>close</button>
            </form>
        </dialog>

        <dialog id="about" class="modal">
            <div class="modal-box">
                <h3 class="text-lg font-bold">Taluli talula!</h3>
                <p class="py-4">Taluli talula!</p>
            </div>
            <form method="dialog" class="modal-backdrop">
                <button>close</button>
            </form>
        </dialog>
    </div>
</template>

<script setup lang="ts">
import Camera from 'simple-vue-camera';
import { v4 as uuidv4 } from 'uuid';

const camera = ref<InstanceType<typeof Camera>>();
const snapshotUrl = ref<string | null>(null);
const selectedButtonName = ref<string>('Text');
const cameraResolution = ref<{ width: number, height: number }>({ width: 375, height: 600 });
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;


interface JsonResponse {
    audio_path?: string;
    [key: string]: any;
}

const jsonResponse = ref<JsonResponse | null>(null);
const audioUrl = ref<string | null>(null);
const snapshots = ref<{ id: string, filename: string, timestamp: string }[]>([]);

const endpoints: Record<string, string> = {
    'Text': '/document_recognition',
    'Currency': '/currency_detection',
    'Object': '/image_captioning',
    'Product': '/product_recognition',
    'Distance': '/distance_estimate',
    'Face': '/face_detection/recognize',
};

const snapshot = async () => {
    console.log('Taking snapshot...');
    const blob = await camera.value?.snapshot();
    if (blob) {
        snapshotUrl.value = URL.createObjectURL(blob);
        sendImageToEndpoint(blob);
    }
};

const sendImageToEndpoint = async (blob: Blob) => {
    const endpoint = endpoints[selectedButtonName.value];
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

        jsonResponse.value = await response.json();
        console.log('JSON Response:', jsonResponse.value);

        const audioPath = jsonResponse.value?.audio_path;
        if (audioPath) {
            const encodedAudioPath = encodeURIComponent(audioPath);
            const audioFileUrl = `${BACKEND_URL}/download_audio?audio_path=${encodedAudioPath}`;
            console.log('Audio File URL:', audioFileUrl);
            audioUrl.value = audioFileUrl;

            // Play audio immediately
            const audio = new Audio(audioFileUrl);
            audio.play().catch(err => {
                console.error("Audio playback failed:", err);
            });
        }
    } catch (error) {
        console.error('Error sending image to endpoint:', error);
    }
};

const playButtonText = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    speechSynthesis.speak(utterance);
};

const updateSelectedButton = (buttonName: string) => {
    selectedButtonName.value = buttonName;
    playButtonText(buttonName); 
};

const updateCameraResolution = () => {
    if (window.innerWidth > window.innerHeight) {
        cameraResolution.value = { width: 600, height: 375 };
    } else {
        cameraResolution.value = { width: 375, height: 600 };
    }
};

let intervalId: ReturnType<typeof setInterval> | undefined;

onMounted(() => {
    updateCameraResolution();
    window.addEventListener('resize', updateCameraResolution);
    // intervalId = setInterval(snapshot, 60000);
});

onUnmounted(() => {
    if (intervalId) {
        clearInterval(intervalId);
    }
    window.removeEventListener('resize', updateCameraResolution);
});
</script>

<style scoped></style>