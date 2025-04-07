<template>
    <div class="w-full overflow-x-auto no-scrollbar">
        <div class="flex py-4">
            <button v-for="(button, index) in buttons" :key="index"
                :class="{ 'btn btn-lg btn-ghost flex flex-col items-center justify-center': 
                selectedButton !== index, 'btn btn-lg btn-ghost text-primary flex flex-col items-center justify-center': selectedButton === index }"
                @click="selectButton(index)">
                <i :class="button.icon"></i>
                <span>{{ button.name }}</span>
            </button>
        </div>
    </div>
</template>

<script setup lang="ts">
const props = defineProps({
    defaultSelected: {
        type: String,
        default: 'Text'
    }
});

const emits = defineEmits(['update:selectedButton']);

const selectedButton = ref<number | null>(null);
const buttons = [
    { name: 'Text', icon: 'fa-solid fa-quote-right' },
    { name: 'Currency', icon: 'fa-solid fa-dollar-sign' },
    { name: 'Object', icon: 'fa-solid fa-cube' },
    { name: 'Product', icon: 'fa-solid fa-shopping-cart' },
    { name: 'Distance', icon: 'fa-solid fa-ruler' },
    { name: 'Face', icon: 'fa-solid fa-smile' },
];

const selectButton = (index: number) => {
    selectedButton.value = index;
    emits('update:selectedButton', buttons[index].name);
};

selectedButton.value = buttons.findIndex(button => button.name === props.defaultSelected);
</script>