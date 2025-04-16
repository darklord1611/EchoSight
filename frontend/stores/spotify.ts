// src/stores/spotify.ts
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
}

export const useSpotifyStore = defineStore('spotify', {
    state: () => ({
        accessToken: null as string | null,
        refreshToken: null as string | null,
        isPlaying: false,
        currentTrack: null as SpotifyTrack | null,
        playbackPosition: 0,
        playerReady: false,
    }),

    actions: {
        async initializePlayerWithEnvTokens() {
            // Get tokens directly from environment variables
            this.accessToken = import.meta.env.VITE_SPOTIFY_ACCESS_TOKEN;
            this.refreshToken = import.meta.env.VITE_SPOTIFY_REFRESH_TOKEN;

            if (!this.accessToken || !this.refreshToken) {
                console.error('Spotify tokens not found in environment variables');
                return;
            }

            await this.refreshTokenIfNeeded();
            this.playerReady = true;
            console.log('Spotify player initialized with env tokens');
        },

        async refreshTokenIfNeeded() {
            if (!this.refreshToken) return;

            try {
                // This would typically be a server-side call to protect your client secret
                const response = await axios.post('/api/spotify/refresh-token', {
                    refresh_token: this.refreshToken
                });

                this.accessToken = response.data.access_token;
                // Sometimes the refresh token is also rotated
                if (response.data.refresh_token) {
                    this.refreshToken = response.data.refresh_token;
                }
            } catch (error) {
                console.error('Failed to refresh Spotify token:', error);
            }
        },

        async searchTracks(query: string) {
            if (!this.accessToken) {
                await this.refreshTokenIfNeeded();
                if (!this.accessToken) return [];
            }

            try {
                const response = await axios.get('https://api.spotify.com/v1/search', {
                    params: {
                        q: query,
                        type: 'track',
                        limit: 20
                    },
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`
                    }
                });

                return response.data.tracks.items;
            } catch (error) {
                if (axios.isAxiosError(error) && error.response?.status === 401) {
                    await this.refreshTokenIfNeeded();
                    // Try once more after token refresh
                    return this.searchTracks(query);
                }
                console.error('Error searching Spotify:', error);
                return [];
            }
        },

        async playTrack(track: SpotifyTrack) {
            if (!this.accessToken) await this.refreshTokenIfNeeded();

            try {
                // Start playback on Spotify
                await axios.put('https://api.spotify.com/v1/me/player/play',
                    { uris: [`spotify:track:${track.id}`] },
                    { headers: { 'Authorization': `Bearer ${this.accessToken}` } }
                );

                this.currentTrack = track;
                this.isPlaying = true;
                this.playbackPosition = 0;
            } catch (error) {
                if (axios.isAxiosError(error) && error.response?.status === 401) {
                    await this.refreshTokenIfNeeded();
                    // Try once more after token refresh
                    return this.playTrack(track);
                }
                console.error('Error playing track:', error);
            }
        },

        async pausePlayback() {
            if (!this.accessToken) await this.refreshTokenIfNeeded();

            try {
                await axios.put('https://api.spotify.com/v1/me/player/pause', {},
                    { headers: { 'Authorization': `Bearer ${this.accessToken}` } }
                );

                this.isPlaying = false;
            } catch (error) {
                console.error('Error pausing playback:', error);
            }
        },

        async resumePlayback() {
            if (!this.accessToken) await this.refreshTokenIfNeeded();

            try {
                await axios.put('https://api.spotify.com/v1/me/player/play', {},
                    { headers: { 'Authorization': `Bearer ${this.accessToken}` } }
                );

                this.isPlaying = true;
            } catch (error) {
                console.error('Error resuming playback:', error);
            }
        },

        async nextTrack() {
            if (!this.accessToken) await this.refreshTokenIfNeeded();

            try {
                await axios.post('https://api.spotify.com/v1/me/player/next', {},
                    { headers: { 'Authorization': `Bearer ${this.accessToken}` } }
                );

                // Get the now playing track
                await this.getCurrentPlayback();
            } catch (error) {
                console.error('Error skipping to next track:', error);
            }
        },

        async previousTrack() {
            if (!this.accessToken) await this.refreshTokenIfNeeded();

            try {
                await axios.post('https://api.spotify.com/v1/me/player/previous', {},
                    { headers: { 'Authorization': `Bearer ${this.accessToken}` } }
                );

                // Get the now playing track
                await this.getCurrentPlayback();
            } catch (error) {
                console.error('Error going to previous track:', error);
            }
        },

        async getCurrentPlayback() {
            if (!this.accessToken) await this.refreshTokenIfNeeded();

            try {
                const response = await axios.get('https://api.spotify.com/v1/me/player',
                    { headers: { 'Authorization': `Bearer ${this.accessToken}` } }
                );

                if (response.data && response.data.item) {
                    this.currentTrack = response.data.item;
                    this.isPlaying = response.data.is_playing;
                    this.playbackPosition = response.data.progress_ms;
                }
            } catch (error) {
                console.error('Error getting current playback:', error);
            }
        },

        async detectMusic() {
            try {
                // Step 1: Record 10 seconds of audio
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

                        if (data?.result?.spotify?.uri) {
                            const trackUri = data.result.spotify.uri;

                            // Step 2: Make sure a device is available
                            await this.refreshTokenIfNeeded();
                            const devicesRes = await axios.get('https://api.spotify.com/v1/me/player/devices', {
                                headers: {
                                    'Authorization': `Bearer ${this.accessToken}`
                                }
                            });

                            const devices = devicesRes.data.devices;
                            if (!devices || devices.length === 0) {
                                alert("No active Spotify devices found. Please open Spotify on a device.");
                                return;
                            }

                            const activeDevice = devices.find((device: any) => device.is_active) || devices[0];

                            // Step 3: Play the identified track
                            await axios.put(
                                'https://api.spotify.com/v1/me/player/play',
                                { uris: [trackUri] },
                                {
                                    headers: {
                                        'Authorization': `Bearer ${this.accessToken}`,
                                    },
                                    params: {
                                        device_id: activeDevice.id
                                    }
                                }
                            );

                            this.currentTrack = {
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
                            };
                            this.isPlaying = true;
                            this.playbackPosition = 0;

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
                }, 10000); // Record for 10 seconds

            } catch (err) {
                console.error("Microphone error:", err);
            }
        }
    }
});



// const detectMusic = async () => {
//     try {
//         const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//         const mediaRecorder = new MediaRecorder(stream);
//         const chunks: Blob[] = [];

//         mediaRecorder.ondataavailable = (e) => chunks.push(e.data);

//         mediaRecorder.onstop = async () => {
//             const audioBlob = new Blob(chunks, { type: 'audio/webm' });
//             const file = new File([audioBlob], 'recording.webm');

//             const formData = new FormData();
//             formData.append("file", file);
//             formData.append("return", "spotify");
//             formData.append("api_token", import.meta.env.VITE_AUDD_API_KEY);

//             try {
//                 const response = await fetch("https://api.audd.io/", {
//                     method: "POST",
//                     body: formData
//                 });

//                 const data = await response.json();
//                 console.log("Audd.io Response:", data);

//                 if (data?.result?.spotify?.external_urls?.spotify) {
//                     if (data?.result?.spotify?.uri) {
//                         await activateAndPlay(data.result.spotify.uri);
//                     }
//                 } else {
//                     alert("Could not recognize any song.");
//                 }
//             } catch (error) {
//                 console.error("Music recognition error:", error);
//             }
//         };

//         mediaRecorder.start();

//         setTimeout(() => {
//             mediaRecorder.stop();
//         }, 10000); // Record for 10 seconds
//     } catch (err) {
//         console.error("Microphone error:", err);
//     }
// };