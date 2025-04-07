<template>
    <div class="navbar bg-base-100">
        <div class="flex-none">
            <button class="btn btn-square btn-ghost" onclick="settings.showModal()">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"
                    class="inline-block h-5 w-5 stroke-current">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16">
                    </path>
                </svg>
            </button>
        </div>
        <div class="flex-1">
            <a class="btn btn-ghost text-xl">Vision Mate</a>
        </div>
        <div class="flex-none">
            <button class="btn btn-square btn-ghost" onclick="about.showModal()">
                <i class="fa-regular fa-circle-question text-xl"></i>
            </button>
        </div>
    </div>

    <dialog id="settings" class="modal">
        <div class="modal-box">
            <h3 class="text-lg font-bold">Taluli talula!</h3>
            <p class="py-4">Taluli talula!</p>
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    </dialog>

    <dialog id="about" class="modal">
        <div class="modal-box">
            <h3 class="text-lg font-bold">Taluli talula!</h3>
            <p class="py-4">Taluli talula!</p>
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    </dialog>
</template>

<script setup lang="ts">

</script>

<style scoped></style>