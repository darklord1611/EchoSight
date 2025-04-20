// spotify-token-cli.js
import express from 'express';
import open from 'open';
import dotenv from 'dotenv';
import fs from 'fs';
import path from 'path';
import fetch from 'node-fetch';

dotenv.config();

const clientId = process.env.SPOTIFY_CLIENT_ID;
const clientSecret = process.env.SPOTIFY_CLIENT_SECRET;
const redirectUri = 'https://8888-01jqra6238a6wpepek4ygtdb3f.cloudspaces.litng.ai/callback';
const scopes = [
    "streaming",
    "user-read-email",
    "user-read-private",
    "user-modify-playback-state",
    "user-read-playback-state",
    "user-read-currently-playing",
    "app-remote-control"
].join(' ');

const app = express();
const port = 8888;

app.get('/callback', async (req, res) => {
    const code = req.query.code;
    if (!code) {
        return res.send('Missing code in query.');
    }

    try {
        const body = new URLSearchParams({
            grant_type: 'authorization_code',
            code,
            redirect_uri: redirectUri,
        });

        const authHeader = Buffer.from(`${clientId}:${clientSecret}`).toString('base64');

        const tokenRes = await fetch('https://accounts.spotify.com/api/token', {
            method: 'POST',
            headers: {
                Authorization: `Basic ${authHeader}`,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body,
        });

        const data = await tokenRes.json();
        if (data.error) throw new Error(data.error_description);

        const envPath = path.resolve(process.cwd(), '.env');
        let envContent = '';

        // Read and filter out any existing token lines
        if (fs.existsSync(envPath)) {
            const originalEnv = fs.readFileSync(envPath, 'utf8').split('\n');
            envContent = originalEnv
                .filter(line =>
                    !line.startsWith('VITE_SPOTIFY_ACCESS_TOKEN=') &&
                    !line.startsWith('VITE_SPOTIFY_REFRESH_TOKEN='))
                .join('\n');
        }

        // Append the new tokens
        const newVars = `
VITE_SPOTIFY_ACCESS_TOKEN=${data.access_token}
VITE_SPOTIFY_REFRESH_TOKEN=${data.refresh_token}
`.trim();

        envContent += `\n${newVars}\n`;

        fs.writeFileSync(envPath, envContent);

        res.send(`
            <h2>✅ Success!</h2>
            <p>Access and refresh tokens have been written to your <code>.env</code> file.</p>
            <pre>${newVars}</pre>
        `);

        console.log('✅ Tokens overwritten in .env!');
        process.exit(0);
    } catch (err) {
        console.error('❌ Error fetching token:', err.message);
        res.status(500).send('Something went wrong.');
    }
});

app.listen(port, () => {
    const authUrl = `https://accounts.spotify.com/authorize?client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(
        redirectUri
    )}&scope=${encodeURIComponent(scopes)}`;

    console.log('🔑 Opening browser for Spotify login...');
    open(authUrl);
});
