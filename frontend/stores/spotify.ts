import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useSpotifySDK } from '@/composables/useSpotifySDK';

export const useSpotifyStore = defineStore('spotify', () => {
    const deviceId = ref<string | null>(null);
    const currentTrack = ref<any | null>(null);
    const isPlaying = ref(false);
    let spotifyPlayer: any;

    const initializePlayer = async () => {
        try {
            const { loadSpotifySDK } = useSpotifySDK();
            await loadSpotifySDK();
            console.log("✅ Spotify SDK fully loaded");

            // Initialize player
            spotifyPlayer = new window.Spotify.Player({
                name: 'EchoSight Player',
                getOAuthToken: (cb: any) => cb(import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN),
                volume: 0.8,
            });

            // Add listeners
            spotifyPlayer.addListener('ready', ({ device_id }: any) => {
                console.log('🎶 Spotify Player ready with device ID:', device_id);
                deviceId.value = device_id;
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
    };

    const activateAndPlay = async (spotifyUri: string) => {
        const token = import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN;

        if (!deviceId.value || !spotifyPlayer) {
            console.warn('Spotify player or device not ready.');
            return;
        }

        try {
            // Must be triggered by a user action (e.g., button click)
            await spotifyPlayer.activateElement();
            console.log('✅ Player element activated');

            // await fetch(`https://api.spotify.com/v1/me/player/play?device_id=${deviceId.value}`, {
            //     method: 'PUT',
            //     headers: {
            //         Authorization: `Bearer ${token}`,
            //         'Content-Type': 'application/json',
            //     },
            //     body: JSON.stringify({
            //         uris: [spotifyUri],
            //     }),
            // });

            console.log('🎶 Song request sent to Spotify');

            // Fetch track info
            await fetchTrackInfo(spotifyUri);
            isPlaying.value = false;
        } catch (error) {
            console.error('❌ Error playing song via Spotify API:', error);
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

    const togglePlayback = async () => {
        const endpoint = isPlaying.value ? 'pause' : 'play';
        await fetch(`https://api.spotify.com/v1/me/player/${endpoint}?device_id=${deviceId.value}`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN}`,
            },
        });
        isPlaying.value = !isPlaying.value;
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
                            await activateAndPlay(data.result.spotify.uri);
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
            }, 10000); // Record for 5 seconds
        } catch (err) {
            console.error("Microphone error:", err);
        }
    };

    return {
        deviceId,
        currentTrack,
        isPlaying,
        initializePlayer,
        activateAndPlay,
        togglePlayback,
        detectMusic
    };
});