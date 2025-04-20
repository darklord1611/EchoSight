<template>
  <div class="voice-command-container">
    <VoiceVisualizer :isRecording="isRecording" :decibelLevel="decibelLevel" />
    <div v-if="feedback" class="voice-feedback mt-2 text-sm">
      {{ feedback }}
    </div>
    <div v-if="props.selectedFeature" class="available-commands mt-2 text-xs opacity-70">
      <div>Available commands: {{ getAvailableCommands() }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useNuxtApp } from '#app';
import VoiceVisualizer from './VoiceVisualizer.vue';
import { useSpotifyStore } from '@/stores/spotify';
import { useNewsStore } from '@/stores/news';

import { MicVAD } from "@ricky0123/vad-web";

let vad: MicVAD | null = null;

const newsStore = useNewsStore();
const emit = defineEmits(['featureMatched']);
const { $sendAudioForCommand } = useNuxtApp();
const spotifyStore = useSpotifyStore();

const props = defineProps<{
  selectedFeature: string;
  cameraRef: Ref | null;
}>();

// State
const isRecording = ref(false);
const decibelLevel = ref(0);
const feedback = ref<string | null>(null);
let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];
let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let intervalId: ReturnType<typeof setInterval>;

// Constants
const DECIBEL_THRESHOLD = 10;
const SPEECH_MIN_DURATION = 1000;
const FEEDBACK_DURATION = 5000; // How long feedback messages stay visible (ms)
let speechDetected = false;
let speechStartTime: number | null = null;
let feedbackTimeout: number | null = null;  // Corrected type for browser-based code

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

const globalCommands = {
  stop: ['stop', 'mute', 'shut up', 'quiet'],
  help: ['help', 'what can i say', 'commands'],
  cancel: ['cancel', 'never mind'],
};

// Define available commands for each feature
const featureCommands = {
  'Text': {
    'read': ['read', 'read text', 'read aloud'],
    'translate': ['translate', 'translate text'],
    'save': ['save', 'save text', 'remember'],
    'capture': ['capture', 'take a picture', 'snapshot'],
  },
  'Currency': {
    'convert': ['convert', 'exchange', 'calculate'],
    'compare': ['compare', 'difference'],
    'capture': ['capture', 'take a picture', 'snapshot'],
  },
  'Object': {
    'identify': ['identify', 'what is this', 'object'],
    'describe': ['describe', 'details', 'tell me more'],
    'capture': ['capture', 'take a picture', 'snapshot'],
  },
  'Product': {
    'search': ['search', 'find similar', 'shop'],
    'price': ['price', 'how much', 'cost'],
    'reviews': ['reviews', 'ratings'],
    'capture': ['capture', 'take a picture', 'snapshot'],
  },
  'Distance': {
    'measure': ['measure', 'how far', 'distance'],
    'compare': ['compare', 'difference'],
    'capture': ['capture', 'take a picture', 'snapshot'],
  },
  'Face': {
    'identify': ['identify', 'who is this', 'recognize'],
    'remember': ['remember', 'save face', 'add person'],
    'capture': ['capture', 'take a picture', 'snapshot'],
  },
  'Music': {
    'detect': ['detect', 'what song', 'identify song', 'recognize'],
    'play': ['play', 'start', 'resume'],
    'pause': ['pause', 'stop', 'mute'],
  },
  'Chatbot': {
    'ask': ['ask', 'question', 'help me'],
    'chat': ['chat', 'talk', 'converse'],
  },
  'News': {
    'summarize': ['summarize', 'summary', 'brief'],
    'read': ['read', 'read aloud', 'narrate'],
  }
};

// Add this above setup block or with other functions
const cancelSpeech = () => {
  if (speechSynthesis.speaking) {
    speechSynthesis.cancel();
    console.log('🛑 Speech synthesis canceled due to user speaking.');
  }
};

// Helper to get all available commands for current feature
const getAvailableCommands = () => {
  const global = Object.keys(globalCommands).join(', ');
  if (!props.selectedFeature || !featureCommands[props.selectedFeature]) {
    return `Global: ${global}`;
  }

  const featureSpecific = Object.keys(featureCommands[props.selectedFeature]).join(', ');
  return `Feature: ${featureSpecific} | Global: ${global}`;
};


const startRecordingV2 = async () => {
  console.log("Starting VAD...");
  if (isRecording.value) return;

  try {
    vad = await MicVAD.new({
      onSpeechStart: () => {
        console.log('🗣 Speech started');
      },
      onSpeechEnd: async (audio: Float32Array) => {
        console.log('🛑 Speech ended');
        isRecording.value = false;

        if (!speechDetected) {
          console.log('❌ No significant speech detected. Skipping request.');
          return;
        }

        // Convert Float32Array to Blob
        const blob = new Blob([audio.buffer], { type: 'audio/webm' });
        // Process the audio for commands
        const data = await $sendAudioForCommand(props.selectedFeature, blob);


        const commandText = data.command;

        // if the current feature matched the command then it is a query of the feature
        if (props.selectedFeature === data.command && data.intent === "query") {
          if (props.selectedFeature === "News") {
            showFeedback("Fetching required articles...")
            newsStore.fetchNews(data.query);
            return
          } else if (props.selectedFeature === "Chatbot") {
            showFeedback("Fetching required response...")
            return;
          }
        }

        if (!commandText) {
          showFeedback("Sorry, I didn't understand that.");
          return;
        }

        const lowerCommand = commandText.toLowerCase();
        console.log('Voice command recognized:', lowerCommand);


        // Check if command is a feature selection
        const featureMatch = Object.keys(featureCommands).find(
          feature => feature.toLowerCase() === lowerCommand
        );

        console.log('Feature match:', featureMatch);
        console.log('Selected feature:', props.selectedFeature);
        console.log("cameraRef:", props.cameraRef);

        if (featureMatch) {
          // User is selecting a feature
          showFeedback(`Switched to ${featureMatch} mode`);
          emit('featureMatched', featureMatch);
        }
        else if (props.selectedFeature) {
          // User is using a feature specific command
          await handleFeatureCommand(lowerCommand);
        }
        else {
          // No feature selected yet
          showFeedback(`Please select a feature first. Say one of: ${Object.keys(featureCommands).join(', ')}`);
        }
      }
    });
  } catch (error) {
    console.error('Error starting VAD:', error);
    showFeedback('Unable to access microphone. Please check permissions.');
  }
};

//////////////// ARTICLE_SECTION //////////////////////

const ordinalMap: Record<string, number> = {
  first: 0,
  second: 1,
  third: 2,
  fourth: 3,
  fifth: 4,
  sixth: 5,
  seventh: 6,
  eighth: 7,
  ninth: 8,
  tenth: 9
};
const getArticleIndexFromCommand = (command: string): number | null => {
  const lower = command.toLowerCase();

  // Match "first", "second", etc.
  for (const key in ordinalMap) {
    console.log(key)
    if (lower.includes(key)) return ordinalMap[key];
  }

  // Match digits (e.g. "read article 3")
  const match = lower.match(/(?:article\s*)?(\d+)/);
  if (match && match[1]) {
    const num = parseInt(match[1]);
    if (!isNaN(num) && num >= 1 && num <= newsStore.articles.length) {
      return num - 1;
    }
  }

  return null;
};

const findArticleByQuery = (query: string) => {
  const lowerQuery = query.toLowerCase();
  return newsStore.articles.find(article =>
    article.title.toLowerCase().includes(lowerQuery) ||
    article.summary?.toLowerCase().includes(lowerQuery)
  );
};

const speakArticle = async (article: { title: string; summary: string }) => {
  const utterance = new SpeechSynthesisUtterance(`${article.title}. ${article.summary}`);
  utterance.lang = 'en-US';
  speechSynthesis.speak(utterance);
};

/////////////////////////////////////////////////////

// Start voice recording
const startRecording = async () => {
  // If recording is already active, do nothing
  if (isRecording.value) return;

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];

    // Set up audio analysis - handle possible existing audioContext
    if (audioContext && audioContext.state === 'suspended') {
      await audioContext.resume();
    } else {
      audioContext = new AudioContext();
    }

    analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    analyser.fftSize = 256;
    source.connect(analyser);

    const dataArray = new Uint8Array(analyser.frequencyBinCount);

    // Track audio levels for visualization and speech detection
    const trackDecibels = () => {
      if (!analyser || !isRecording.value || speechSynthesis.speaking) return;

      analyser.getByteTimeDomainData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        const normalized = dataArray[i] - 128;
        sum += normalized * normalized;
      }
      const rms = Math.sqrt(sum / dataArray.length);
      decibelLevel.value = Math.min(100, rms * 10);

      const now = Date.now();
      if (decibelLevel.value > DECIBEL_THRESHOLD) {
        // cancelSpeech(); // 💥 Interrupt system speech when user starts speaking
        if (!speechStartTime) speechStartTime = now;
        else if (now - speechStartTime > SPEECH_MIN_DURATION) {
          speechDetected = true;
        }
      } else {
        speechStartTime = null;
      }

      if (isRecording.value) requestAnimationFrame(trackDecibels);
    };

    // Set up media recorder
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);

    mediaRecorder.onstop = async () => {

      // Don't process if we manually stopped recording for music detection
      if (!isRecording.value) {
        console.log('Recording stopped manually. Skipping processing.');
        return;
      }

      if(speechSynthesis.speaking) {
        console.log('🛑 Speech synthesis is active. Skipping processing.');
        return;
      }

      if (!speechDetected) {
        console.log('❌ No significant speech detected. Skipping request.');
        resetSpeechFlags();
        return;
      }

      // Process the audio for commands
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const data = await $sendAudioForCommand(props.selectedFeature, blob);


      const commandText = data.command;

      if (data.query === "") {
        console.log("Nothing to record")
        resetSpeechFlags();
        return;
      }

      // if the current feature matched the command then it is a query of the feature
      if (props.selectedFeature === data.command && data.command === "News") {
        if (data.intent === "read" || commandText.toLowerCase().includes("read")) {
          const articleIndex = getArticleIndexFromCommand(data.query);
          if (articleIndex !== null && newsStore.articles[articleIndex]) {
            const article = newsStore.articles[articleIndex];
            showFeedback(`Reading article ${articleIndex + 1}...`);
            await speakArticle(article);
          } else {
            showFeedback("Sorry, I couldn't find which article you wanted me to read.");
          }
          return;
        }

        // Normal query intent
        if (data.intent === "query" && data.command === "News") {
          showFeedback("Fetching required articles...");
          await newsStore.fetchNews(data.query);
          showFeedback("Articles updated.");
          return;
        }
      }

      if (!commandText) {
        showFeedback("Sorry, I didn't understand that.");
        resetSpeechFlags();
        return;
      }

      const lowerCommand = commandText.toLowerCase();
      console.log('Voice command recognized:', lowerCommand);

      // Check if command is a feature selection
      const featureMatch = Object.keys(featureCommands).find(
        feature => feature.toLowerCase() === lowerCommand
      );

      console.log('Feature match:', featureMatch);
      console.log('Selected feature:', props.selectedFeature);
      console.log("cameraRef:", props.cameraRef);

      if (featureMatch) {
        // User is selecting a feature
        showFeedback(`Switched to ${featureMatch} mode`);
        emit('featureMatched', featureMatch);
      }
      else if (props.selectedFeature) {
        // User is using a feature-specific command
        await handleFeatureCommand(lowerCommand);
      }
      else {
        // No feature selected yet
        showFeedback(`Please select a feature first. Say one of: ${Object.keys(featureCommands).join(', ')}`);
      }

      resetSpeechFlags();
    };

    const resetSpeechFlags = () => {
      speechDetected = false;
      speechStartTime = null;
      audioChunks = [];
    };

    // Start recording and analysis
    isRecording.value = true;
    mediaRecorder.start();
    trackDecibels();

    // Restart recording every 5 seconds
    intervalId = setInterval(() => {
      if (mediaRecorder?.state === 'recording') {
        mediaRecorder.stop();
        mediaRecorder.start();
      }
    }, 5000);
  } catch (error) {
    console.error('Error starting voice recording:', error);
    showFeedback('Unable to access microphone. Please check permissions.');
  }
};

const handleFeatureCommand = async (command: string) => {
  // 🔍 Check for global commands first
  for (const action in globalCommands) {
    if (globalCommands[action].some(phrase => command.includes(phrase))) {
      await executeGlobalCommand(action);
      return;
    }
  }

  const currentFeature = props.selectedFeature;
  if (!currentFeature || !featureCommands[currentFeature]) {
    showFeedback(`The command "${command}" doesn't match any available feature.`);
    return;
  }

  const commands = featureCommands[currentFeature];
  let matchedAction = null;

  for (const action in commands) {
    if (commands[action].some(phrase => command.includes(phrase))) {
      matchedAction = action;
      break;
    }
  }

  if (matchedAction) {
    await executeCommand(currentFeature, matchedAction, command);
  } else {
    showFeedback(`The command "${command}" is not valid for ${currentFeature} mode. Try: ${getAvailableCommands()}`);
  }
};

const executeGlobalCommand = async (action: string) => {
  switch (action) {
    case 'stop':
      showFeedback('Stopping all audio...');
      speechSynthesis.cancel();
      if (spotifyStore.isPlaying) {
        spotifyStore.togglePlayback();
      }
      break;

    case 'help':
      showFeedback(`Say one of these global commands: ${Object.keys(globalCommands).join(', ')}`);
      break;

    case 'cancel':
      showFeedback('Okay, canceled.');
      break;

    default:
      showFeedback(`Unknown global command: ${action}`);
  }
};



// Execute the matched command
const executeCommand = async (feature: string, action: string, originalCommand: string) => {
  showFeedback(`Executing: ${action} for ${feature}`);

  console.log(`Executing command: ${action} for feature: ${feature}`);

  switch (feature) {
    case 'Music':
      await executeMusicCommand(action);
      break;
    case 'Text':
    case 'Currency':
    case 'Object':
    case 'Product':
    case 'Distance':
    case 'Face':
      await executeCameraCommand(feature);
      break;
    case 'Chatbot':
      await executeChatbotCommand(action);
      break;
    case 'News':
      await executeNewsCommand(action);
      break;
    default:
      showFeedback(`Feature ${feature} not yet implemented`);
  }
};

// Execute music-specific commands
const executeMusicCommand = async (action: string) => {
  switch (action) {
    case 'detect':
      showFeedback('Detecting music...');

      // Stop the microphone before music detection
      stopRecording();

      try {
        await spotifyStore.detectMusic();
        showFeedback('Music detection complete.');
      } catch (error) {
        showFeedback('Failed to detect music. Please try again.');
        console.error('Music detection error:', error);
      } finally {
        // Restart the microphone after music detection is complete
        startRecording();
      }
      break;

    case 'play':
      showFeedback('Playing music');
      if (spotifyStore.currentTrack) {
        spotifyStore.togglePlayback();
      } else {
        speak('No music is currently loaded.');
      }
      break;

    case 'pause':
      showFeedback('Pausing music');
      if (spotifyStore.isPlaying) {
        spotifyStore.togglePlayback();
      } else {
        speak('Music is already paused.');
      }
      break;
  }
};

// Function stubs for other feature commands
const executeCameraCommand = async (action: string) => {
  console.log("Taking a snapshot with current feature:", action);
  if (props.cameraRef) {
    props.cameraRef.takeSnapshot();
    showFeedback(`Capturing snapshot for ${action}...`);
  } else {
    showFeedback(`Camera not ready.`);
  }
  return;
};

const executeChatbotCommand = async (action: string) => {
  speak(`Executing ${action} for chatbot feature`);
  // Implementation would depend on your chatbot feature capabilities
};

const executeNewsCommand = async (action: string) => {
  speak(`Executing ${action} for News feature`);
  // Implementation would depend on your News feature capabilities
};

// Display feedback and speak it
const showFeedback = async (message: string, delayAfter: number = 1000) => {
  feedback.value = message;

  // Stop listening before speaking
  if (isRecording.value) {
    stopRecording();
  }

  await speak(message);
  await sleep(delayAfter);

  // Restart listening after speaking
  startRecording();

  if (feedbackTimeout) clearTimeout(feedbackTimeout);
  feedbackTimeout = setTimeout(() => {
    feedback.value = null;
  }, FEEDBACK_DURATION);
};

// Text-to-speech
const speak = (text: string): Promise<void> => {
  return new Promise(resolve => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => resolve();
    speechSynthesis.speak(utterance);
  });
};


const stopRecording = async () => {
  isRecording.value = false;

  // Stop the recorder if active
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }

  // Stop refreshing audio chunks
  clearInterval(intervalId);

  // Suspend audio context
  if (audioContext) {
    await audioContext.suspend(); // Wait for suspend to complete
  }

  // Release media tracks
  if (mediaRecorder?.stream) {
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
  }

  // Reset everything
  audioChunks = [];
  mediaRecorder = null;
};

// Lifecycle hooks
onMounted(() => {
  startRecording();
});

onUnmounted(() => {
  stopRecording();
  if (feedbackTimeout) {
    clearTimeout(feedbackTimeout);
  }
});
</script>

<style scoped>
.voice-command-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.voice-feedback {
  text-align: center;
  color: var(--color-text-primary);
}

.available-commands {
  text-align: center;
  color: var(--color-text-secondary);
  font-style: italic;
}
</style>