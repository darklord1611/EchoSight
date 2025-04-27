<template>
    <div class="navbar bg-gradient-to-r from-blue-500 via-blue-400 to-blue-300 text-white shadow-lg">
      <!-- Settings Button -->
      <div class="flex-none">
        <button 
          class="btn btn-square btn-ghost focus:outline-none focus:ring-2 focus:ring-white" 
          @click="openSettingsModal"
          aria-label="Open settings"
          title="Open settings"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
            class="inline-block h-6 w-6 stroke-current">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
          </svg>
        </button>
      </div>
  
      <!-- App Title -->
      <div class="flex-1 text-center">
        <a class="text-2xl font-bold tracking-wide" href="#" aria-label="EchoSight Home">EchoSight</a>
      </div>
  
      <!-- About Button -->
      <div class="flex-none">
        <button 
          class="btn btn-square btn-ghost focus:outline-none focus:ring-2 focus:ring-white" 
          @click="openAboutModal"
          aria-label="Open about"
          title="Open about"
        >
          <i class="fa-regular fa-circle-question text-2xl"></i>
        </button>
      </div>
    </div>
  
    <!-- Settings Modal -->
    <dialog id="settings" class="modal">
      <div class="modal-box">
        <h3 class="text-lg font-bold">Settings</h3>
        <p class="py-4">Configure your preferences here.</p>
        <form method="dialog" class="modal-action">
          <button class="btn btn-primary">Close</button>
        </form>
      </div>
    </dialog>
  
    <!-- About Modal -->
    <dialog id="about" class="modal">
      <div class="modal-box">
        <h3 class="text-lg font-bold">About EchoSight</h3>
        <p class="py-4">EchoSight is an accessible app designed to enhance your experience.</p>
        <form method="dialog" class="modal-action">
          <button class="btn btn-primary">Close</button>
        </form>
      </div>
    </dialog>
  </template>
  
  <script setup lang="ts">
  const openSettingsModal = () => {
    const settingsModal = document.getElementById('settings') as HTMLDialogElement;
    settingsModal?.showModal();
  };
  
  const openAboutModal = () => {
    const aboutModal = document.getElementById('about') as HTMLDialogElement;
    aboutModal?.showModal();
  };
  </script>
  
  <style scoped>
  /* Navbar styles */
  .navbar {
    padding: 0.5rem 1rem;
  }
  
  /* Modal styles */
  .modal-box {
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
  
  .modal-action button {
    margin-top: 1rem;
  }
  </style>