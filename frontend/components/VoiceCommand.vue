<template>
  <div>
    <VoiceVisualizer :isRecording="isRecording" :decibelLevel="decibelLevel" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useNuxtApp } from '#app';
import VoiceVisualizer from './VoiceVisualizer.vue';

const emit = defineEmits(['featureMatched']);
const { $sendAudioForCommand } = useNuxtApp();

const isRecording = ref(false);
const decibelLevel = ref(0);
let mediaRecorder: MediaRecorder | null = null;
let audioChunks: Blob[] = [];
let audioContext: AudioContext | null = null;
let analyser: AnalyserNode | null = null;
let intervalId: ReturnType<typeof setInterval>;

// Silence detection settings
const DECIBEL_THRESHOLD = 10;
const SPEECH_MIN_DURATION = 1000;
let speechDetected = false;
let speechStartTime: number | null = null;

const startRecording = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  audioChunks = [];

  audioContext = new AudioContext();
  analyser = audioContext.createAnalyser();
  const source = audioContext.createMediaStreamSource(stream);
  analyser.fftSize = 256;
  source.connect(analyser);

  const dataArray = new Uint8Array(analyser.frequencyBinCount);
  const trackDecibels = () => {
    if (!analyser) return;

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
      if (!speechStartTime) speechStartTime = now;
      else if (now - speechStartTime > SPEECH_MIN_DURATION) {
        speechDetected = true;
      }
    } else {
      speechStartTime = null;
    }

    if (isRecording.value) requestAnimationFrame(trackDecibels);
  };

  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);

  mediaRecorder.onstop = async () => {
    if (!speechDetected) {
      console.log('❌ No significant speech detected. Skipping request.');
      resetSpeechFlags();
      return;
    }

    const blob = new Blob(audioChunks, { type: 'audio/webm' });
    const match = await $sendAudioForCommand(blob);
    if (match) {
      speak(`Activated ${match} mode`);
      emit('featureMatched', match);
    }

    resetSpeechFlags();
  };

  const resetSpeechFlags = () => {
    speechDetected = false;
    speechStartTime = null;
    audioChunks = [];
  };

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
};

const stopRecording = () => {
  isRecording.value = false;
  mediaRecorder?.stop();
  clearInterval(intervalId);
  audioContext?.close();
};

const speak = (text: string) => {
  const utterance = new SpeechSynthesisUtterance(text);
  speechSynthesis.speak(utterance);
};

onMounted(() => {
  startRecording();
});

onUnmounted(() => {
  stopRecording();
});
</script>
