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

const emit = defineEmits(['featureMatched']);
const { $sendAudioForCommand } = useNuxtApp();
const spotifyStore = useSpotifyStore();

const props = defineProps({
  selectedFeature: String,
});

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

// Define available commands for each feature
const featureCommands = {
  'Text': {
    'read': ['read', 'read text', 'read aloud'],
    'translate': ['translate', 'translate text'],
    'save': ['save', 'save text', 'remember'],
  },
  'Currency': {
    'convert': ['convert', 'exchange', 'calculate'],
    'compare': ['compare', 'difference'],
  },
  'Object': {
    'identify': ['identify', 'what is this', 'object'],
    'describe': ['describe', 'details', 'tell me more'],
  },
  'Product': {
    'search': ['search', 'find similar', 'shop'],
    'price': ['price', 'how much', 'cost'],
    'reviews': ['reviews', 'ratings'],
  },
  'Distance': {
    'measure': ['measure', 'how far', 'distance'],
    'compare': ['compare', 'difference'],
  },
  'Face': {
    'identify': ['identify', 'who is this', 'recognize'],
    'remember': ['remember', 'save face', 'add person'],
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
  'Article': {
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
  if (!props.selectedFeature.value || !featureCommands[props.selectedFeature.value]) {
    return '';
  }
  
  return Object.keys(featureCommands[props.selectedFeature.value])
    .map(command => command)
    .join(', ');
};

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
      if (!analyser || !isRecording.value) return;

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
        return;
      }

      if (!speechDetected) {
        console.log('❌ No significant speech detected. Skipping request.');
        resetSpeechFlags();
        return;
      }

      // Process the audio for commands
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const commandText = await $sendAudioForCommand(blob);
      
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

      if (featureMatch) {
        // User is selecting a feature
        showFeedback(`Switched to ${featureMatch} mode`);
        emit('featureMatched', featureMatch);
      } 
      else if (props.selectedFeature.value) {
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

// Handle feature-specific commands
const handleFeatureCommand = async (command: string) => {
  const currentFeature = props.selectedFeature.value;
  if (!currentFeature || !featureCommands[currentFeature]) {
    showFeedback(`The command "${command}" doesn't match any available feature.`);
    return;
  }

  // Look for command match in the current feature
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

// Execute the matched command
const executeCommand = async (feature: string, action: string, originalCommand: string) => {
  showFeedback(`Executing: ${action} for ${feature}`);
  
  switch (feature) {
    case 'Music':
      await executeMusicCommand(action);
      break;
    case 'Text':
      await executeTextCommand(action);
      break;
    case 'Currency':
      await executeCurrencyCommand(action);
      break;
    case 'Object':
      await executeObjectCommand(action);
      break;
    case 'Product':
      await executeProductCommand(action);
      break;
    case 'Distance':
      await executeDistanceCommand(action);
      break;
    case 'Face':
      await executeFaceCommand(action);
      break;
    case 'Chatbot':
      await executeChatbotCommand(action);
      break;
    case 'Article':
      await executeArticleCommand(action);
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
const executeTextCommand = async (action: string) => {
  speak(`Executing ${action} for text feature`);
  // Implementation would depend on your text feature capabilities
};

const executeCurrencyCommand = async (action: string) => {
  speak(`Executing ${action} for currency feature`);
  // Implementation would depend on your currency feature capabilities
};

const executeObjectCommand = async (action: string) => {
  speak(`Executing ${action} for object recognition feature`);
  // Implementation would depend on your object recognition feature capabilities
};

const executeProductCommand = async (action: string) => {
  speak(`Executing ${action} for product feature`);
  // Implementation would depend on your product feature capabilities
};

const executeDistanceCommand = async (action: string) => {
  speak(`Executing ${action} for distance feature`);
  // Implementation would depend on your distance feature capabilities
};

const executeFaceCommand = async (action: string) => {
  speak(`Executing ${action} for face recognition feature`);
  // Implementation would depend on your face recognition feature capabilities
};

const executeChatbotCommand = async (action: string) => {
  speak(`Executing ${action} for chatbot feature`);
  // Implementation would depend on your chatbot feature capabilities
};

const executeArticleCommand = async (action: string) => {
  speak(`Executing ${action} for article feature`);
  // Implementation would depend on your article feature capabilities
};

// Display feedback and speak it
const showFeedback = (message: string) => {
  feedback.value = message;
  speak(message);
  
  // Clear feedback after a delay
  if (feedbackTimeout) {
    clearTimeout(feedbackTimeout);
  }
  
  feedbackTimeout = setTimeout(() => {
    feedback.value = null;
  }, FEEDBACK_DURATION);
};

// Text-to-speech
const speak = (text: string) => {
  const utterance = new SpeechSynthesisUtterance(text);
  speechSynthesis.speak(utterance);
};

// Stop recording
const stopRecording = () => {
  isRecording.value = false;
  
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
  }
  
  clearInterval(intervalId);
  
  if (audioContext) {
    audioContext.suspend(); // Use suspend instead of close for temporary stopping
  }
  
  // Release media tracks
  if (mediaRecorder?.stream) {
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
  }
  
  // Clear the recorder
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