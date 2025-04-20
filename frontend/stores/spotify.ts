import { defineStore } from 'pinia';
import axios from 'axios';

interface SpotifyTrack {
    id: string;
    name: string;
    artists: { name: string }[];
    album: {
        name: string;
        images: { url: string }[];
        release_date?: string;
    };
    duration_ms: number;
    explicit: boolean;
    popularity?: number;
    uri: string;
}

export const useSpotifyStore = defineStore('spotify', {
    state: () => ({
        accessToken: import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN || null,
        refreshToken: import.meta.env.VITE_SPOTIFY_REFRESH_TOKEN || null,
        currentTrack: null as SpotifyTrack | null,
        isPlaying: false,
        playbackPosition: 0,  // Added to track the current position in the track
    }),

    actions: {
        async detectMusic() {
            this.isPlaying = false;
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const mediaRecorder = new MediaRecorder(stream);
                const chunks: Blob[] = [];

                const audioBlob: Blob = await new Promise((resolve, reject) => {
                    mediaRecorder.ondataavailable = (e) => chunks.push(e.data);

                    mediaRecorder.onstop = () => {
                        const blob = new Blob(chunks, { type: 'audio/webm' });
                        resolve(blob);
                    };

                    mediaRecorder.onerror = reject;

                    mediaRecorder.start();
                    setTimeout(() => mediaRecorder.stop(), 10000); // 10 seconds
                });

                const file = new File([audioBlob], 'recording.webm');

                const formData = new FormData();
                formData.append("file", file);
                formData.append("return", "spotify");
                formData.append("api_token", import.meta.env.VITE_AUDD_API_KEY);

                const response = await fetch("https://api.audd.io/", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();
                console.log("Audd.io Response:", data);

                if (data?.result?.spotify?.uri) {
                    const track = {
                        id: data.result.spotify.id,
                        name: data.result.title,
                        artists: [{ name: data.result.artist }],
                        album: {
                            name: data.result.album,
                            images: [{ url: data.result.spotify.album?.images?.[0]?.url || '' }],
                            release_date: data.result.release_date || '',
                        },
                        duration_ms: data.result.spotify.duration_ms,
                        explicit: data.result.spotify.explicit || false,
                        popularity: data.result.spotify.popularity || 0,
                        uri: data.result.spotify.uri
                    };

                    this.currentTrack = track;
                    this.isPlaying = false;
                    this.playbackPosition = 0; // Reset position
                } else {
                    alert("Could not recognize any song.");
                }
            } catch (err) {
                console.error("Microphone error:", err);
            }
        },

        async playMusic() {
            if (!this.accessToken || !this.currentTrack) return;

            try {
                const deviceRes = await axios.get('https://api.spotify.com/v1/me/player/devices', {
                    headers: { 'Authorization': `Bearer ${this.accessToken}` }
                });

                const device = deviceRes.data.devices.find((d: any) => d.is_active) || deviceRes.data.devices[0];
                if (!device) {
                    alert("No active Spotify devices found. Please open Spotify.");
                    return;
                }

                await axios.put(`https://api.spotify.com/v1/me/player/play?device_id=${device.id}`,
                    { uris: [this.currentTrack.uri] },
                    { headers: { 'Authorization': `Bearer ${this.accessToken}` } }
                );

                this.isPlaying = true;
            } catch (error) {
                console.error("Error playing track:", error);
            }
        },

        async pauseMusic() {
            if (!this.accessToken) return;

            try {
                await axios.put('https://api.spotify.com/v1/me/player/pause', {},
                    { headers: { 'Authorization': `Bearer ${this.accessToken}` } }
                );
                this.isPlaying = false;
            } catch (error) {
                console.error("Error pausing music:", error);
            }
        },

        // New method to resume playback from the current position
        async resumePlayback() {
            if (!this.accessToken || !this.currentTrack || !this.playbackPosition) return;

            try {
                const deviceRes = await axios.get('https://api.spotify.com/v1/me/player/devices', {
                    headers: { 'Authorization': `Bearer ${this.accessToken}` }
                });

                const device = deviceRes.data.devices.find((d: any) => d.is_active) || deviceRes.data.devices[0];
                if (!device) {
                    alert("No active Spotify devices found. Please open Spotify.");
                    return;
                }

                await axios.put(`https://api.spotify.com/v1/me/player/play?device_id=${device.id}`,
                    {
                        uris: [this.currentTrack.uri],
                        position_ms: this.playbackPosition // Start from the current position
                    },
                    { headers: { 'Authorization': `Bearer ${this.accessToken}` } }
                );

                this.isPlaying = true;
            } catch (error) {
                console.error("Error resuming track:", error);
            }
        }
    }
});
