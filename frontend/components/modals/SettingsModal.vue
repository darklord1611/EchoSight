<template>
    <div v-if="show" class="modal modal-open">
      <div class="modal-box">
        <h3 class="text-lg font-bold">Settings</h3>
        <p class="py-4">Taluli talula!</p>
        <div class="modal-action">
          <button class="btn" @click="$emit('close')">Close</button>
        </div>
      </div>
      <div class="modal-backdrop" @click="$emit('close')"></div>
    </div>
  </template>
  
  <script setup lang="ts">
  defineProps({
    show: {
      type: Boolean,
      default: false
    }
  });
  
  defineEmits(['close']);
  </script>