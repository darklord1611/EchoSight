export default defineNuxtPlugin(() => {
    return {
        provide: {
            loadSpotifySDK: () =>
                new Promise<void>((resolve) => {
                    if (window.Spotify) return resolve();

                    const script = document.createElement('script');
                    script.src = 'https://sdk.scdn.co/spotify-player.js';
                    script.onload = () => resolve();
                    document.head.appendChild(script);
                }),
        },
    };
});