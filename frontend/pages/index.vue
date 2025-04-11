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

        <SpotifyMiniPlayer
            v-if="currentTrack"
            :track="currentTrack"
            :isPlaying="isPlaying"
            :togglePlayback="togglePlayback"
        />

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


const currentTrack = ref<any | null>(null);
const isPlaying = ref(false);


interface JsonResponse {
    audio_path?: string;
    [key: string]: any;
}

const jsonResponse = ref<JsonResponse | null>(null);
const audioUrl = ref<string | null>(null);
const snapshots = ref<{ id: string, filename: string, timestamp: string }[]>([]);

import { useSpotifySDK } from '@/composables/useSpotifySDK';

const spotifyDeviceId = ref<string | null>(null);
let spotifyPlayer: any;

watch(spotifyDeviceId, (val) => {
  console.log('🛰 Spotify Device ID updated:', val);
});

onMounted(async () => {
  try {
    const { loadSpotifySDK } = useSpotifySDK();

    await loadSpotifySDK(); // <-- This waits for the SDK to load and callback to fire
    console.log("✅ Spotify SDK fully loaded");

    // Now it's safe to initialize the player
    spotifyPlayer = new window.Spotify.Player({
      name: 'EchoSight Player',
      getOAuthToken: (cb: any) => cb(import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN),
      volume: 0.8,
    });

    spotifyPlayer.addListener('ready', ({ device_id }: any) => {
      console.log('🎶 Spotify Player ready with device ID:', device_id);
      spotifyDeviceId.value = device_id;
    });

    spotifyPlayer.addListener('initialization_error', ({ message }: any) =>
      console.error('❌ Initialization error:', message)
    );

    spotifyPlayer.addListener('authentication_error', ({ message }: any) =>
      console.error('❌ Authentication error:', message)
    );

    spotifyPlayer.addListener('account_error', ({ message }: any) =>
      console.error('❌ Account error:', message)
    );

    spotifyPlayer.addListener('playback_error', ({ message }: any) =>
      console.error('❌ Playback error:', message)
    );

    spotifyPlayer.connect();
  } catch (err) {
    console.error("❌ Failed to initialize Spotify SDK or Player:", err);
  }
});

const activateAndPlay = async (spotifyUri: string) => {
  const token = import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN;

  if (!spotifyDeviceId.value || !spotifyPlayer) {
    console.warn('Spotify player or device not ready.');
    return;
  }

  try {
    // Must be triggered by a user action (e.g., button click)
    await spotifyPlayer.activateElement();
    console.log('✅ Player element activated');

    await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${spotifyDeviceId.value}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        uris: [spotifyUri],
      }),
    });

    console.log('🎶 Song request sent to Spotify');
  } catch (error) {
    console.error('❌ Error playing song via Spotify API:', error);
  }
};




const endpoints: Record<string, string> = {
    'Text': '/document_recognition',
    'Currency': '/currency_detection',
    'Object': '/image_captioning',
    'Product': '/product_recognition',
    'Distance': '/distance_estimate',
    'Face': '/face_detection/recognize',
    'Music': '/',
};


const playSpotifySong = async (spotifyUri: string) => {
  const token = import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN;

  if (!spotifyDeviceId.value) {
    console.warn('Spotify device ID not ready yet.');
    return;
  }

  try {
    await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${spotifyDeviceId.value}`, {
      method: 'PUT',
      body: JSON.stringify({ uris: [spotifyUri] }),
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });
    console.log('🎶 Song started playing on Spotify device:', spotifyDeviceId.value);
  } catch (err) {
    console.error('❌ Failed to play Spotify song:', err);
  }
};

const fetchTrackInfo = async (uri: string) => {
  const trackId = uri.split(':').pop();
  const res = await fetch(`https://api.spotify.com/v1/tracks/${trackId}`, {
    headers: {
      Authorization: `Bearer ${import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN}`,
    },
  });
  currentTrack.value = await res.json();
};

const snapshot = async () => {
    if (selectedButtonName.value === 'Music') {
        detectMusic();
        return;
    }

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


const detectMusic = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        const chunks: Blob[] = [];

        mediaRecorder.ondataavailable = (e) => chunks.push(e.data);

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(chunks, { type: 'audio/webm' });
            const file = new File([audioBlob], 'recording.webm');

            const formData = new FormData();
            formData.append("file", file);
            formData.append("return", "spotify");
            formData.append("api_token", import.meta.env.VITE_AUDD_API_KEY);

            try {
                const response = await fetch("https://api.audd.io/", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();
                console.log("Audd.io Response:", data);

                if (data?.result?.spotify?.external_urls?.spotify) {
                    if (data?.result?.spotify?.uri) {
                        const uri = data.result.spotify.uri;
                        await activateAndPlay(data.result.spotify.uri);
                        await fetchTrackInfo(uri);
                    }
                } else {
                    alert("Could not recognize any song.");
                }
            } catch (error) {
                console.error("Music recognition error:", error);
            }
        };

        mediaRecorder.start();

        setTimeout(() => {
            mediaRecorder.stop();
        }, 5000); // Record for 5 seconds
    } catch (err) {
        console.error("Microphone error:", err);
    }
};

const togglePlayback = async () => {
  const endpoint = isPlaying.value ? 'pause' : 'play';
  await fetch(`https://api.spotify.com/v1/me/player/${endpoint}?device_id=${spotifyDeviceId.value}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN}`,
    },
  });
  isPlaying.value = !isPlaying.value;
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