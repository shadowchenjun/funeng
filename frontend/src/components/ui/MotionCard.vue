<template>
  <div class="ui-motion-card" :class="{ 'no-padding': noPadding }">
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  noPadding?: boolean
}>()
</script>

<style scoped>
.ui-motion-card {
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 16px;
  padding: 24px;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.ui-motion-card:hover {
  box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1));
  transform: translateY(-2px);
}

.ui-motion-card.no-padding {
  padding: 0;
}

@media (prefers-reduced-motion: reduce) {
  .ui-motion-card {
    transition: none;
  }

  .ui-motion-card:hover {
    transform: none;
  }
}
</style>
