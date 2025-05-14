# EchoSight

This repository contains an application designed to assist visually impaired individuals by providing essential functionalities such as text recognition, object detection, article searching, music detection, and more. The application leverages advanced AI models and APIs to deliver a seamless and accessible user experience.

## Features

### 1. Article Searching

Empowers users to search for news articles using voice commands or text input. The application fetches articles from reliable sources and reads them aloud, ensuring accessibility for visually impaired users.
![Article Searching](https://rqrfqewauxwlizbxuekr.supabase.co/storage/v1/object/public/echo-sight-demo//article_searching.PNG)

### 2. Chatbot

Offers a conversational AI assistant capable of answering user queries, providing guidance, and performing tasks. The chatbot integrates seamlessly with other features, enhancing the overall user experience.
![Chatbot](https://rqrfqewauxwlizbxuekr.supabase.co/storage/v1/object/public/echo-sight-demo//chatbot.PNG)

### 3. Music Detection

Leverages Spotify's API to identify and play music tracks. Users can explore songs, view track details, and enjoy a personalized music experience.
![Music Detection](https://rqrfqewauxwlizbxuekr.supabase.co/storage/v1/object/public/echo-sight-demo//music_detection.png)

### 4. Currency Detection

Utilizes advanced image recognition to detect and identify currency notes. This feature ensures users can handle cash transactions with confidence and ease.
![Currency Detection](https://rqrfqewauxwlizbxuekr.supabase.co/storage/v1/object/public/echo-sight-demo//currency_detection.PNG)

### 5. Distance Estimation

Assists users in navigating their surroundings by estimating the distance to nearby objects. This feature enhances spatial awareness and safety for visually impaired individuals.
![Distance Estimation](https://rqrfqewauxwlizbxuekr.supabase.co/storage/v1/object/public/echo-sight-demo//distance_estimation.PNG)

### 6. Product Recognition

Identifies products and provides detailed information, including brand and specifications. This feature is particularly useful for shopping and daily tasks.
![Product Recognition](https://rqrfqewauxwlizbxuekr.supabase.co/storage/v1/object/public/echo-sight-demo//product_recognition.PNG)

### 7. Text Recognition

Extracts text from images or documents using OCR technology. The recognized text is read aloud, enabling users to access printed or handwritten content effortlessly.
![Text Recognition](https://rqrfqewauxwlizbxuekr.supabase.co/storage/v1/object/public/echo-sight-demo//text_recognition.PNG)

---

## Setup and Installation

### Prerequisites

- Node.js (v16 or higher)
- Python (v3.8 or higher)
- Docker (optional, for containerized deployment)

### Frontend Setup

1. Navigate to the `frontend` directory:

    ```bash
    cd frontend
    ```

2. Install the required dependencies:

    ```bash
    npm install
    ```

3. Create a `.env` file in the `frontend` directory and configure the following environment variables:

    ```properties
    VITE_BACKEND_URL=<your_backend_url>
    VITE_AUDD_API_KEY=<your_audd_api_key>
    SPOTIFY_CLIENT_ID=<your_spotify_client_id>
    SPOTIFY_CLIENT_SECRET=<your_spotify_client_secret>
    ```

4. Start the development server:

    ```bash
    npm run dev
    ```

### Backend Setup

1. Navigate to the `ml_service` directory:

    ```bash
    cd ml_service
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the `ml_service` directory and configure the following environment variables:

    ```properties
    SERPAPI_API_KEY=<your_serpapi_api_key>
    GOOGLE_API_KEY=<your_google_api_key>
    GROQ_API_KEY=<your_groq_api_key>
    ```

5. Start the backend server:

    ```bash
    python main.py
    ```

### Additional Notes
- Ensure that the `.gitignore` file excludes sensitive files like `.env` to prevent accidental commits.
- For Spotify integration, run the command `node spotify_token_cli.js` script to generate and update the necessary tokens in the `.env` file.
- To test the application, navigate to `http://localhost:3000` for the frontend and `http://localhost:8000` for the backend.
