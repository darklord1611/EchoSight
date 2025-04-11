export const useSpotifySDK = () => {
    const loadSpotifySDK = () => {
        return new Promise<void>((resolve, reject) => {
            if (window.Spotify) {
                resolve();
                return;
            }

            // Define global callback BEFORE loading the script
            window.onSpotifyWebPlaybackSDKReady = () => {
                resolve();
            };

            console.log("Injecting Spotify SDK script...");

            const script = document.createElement('script');
            script.src = 'https://sdk.scdn.co/spotify-player.js';
            script.async = true;
            script.onerror = reject;

            document.head.appendChild(script);
        });
    };

    return {
        loadSpotifySDK,
    };
};
