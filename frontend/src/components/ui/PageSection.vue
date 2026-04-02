<template>
  <section class="page-section">
    <div class="section-header" v-if="title">
      <h2 class="section-title">{{ title }}</h2>
      <p class="section-subtitle" v-if="subtitle">{{ subtitle }}</p>
    </div>
    <div class="section-content">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title?: string
  subtitle?: string
}>()
</script>

<style scoped>
.page-section {
  margin-bottom: 24px;
}

.section-header {
  margin-bottom: 20px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #0F172A);
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.section-subtitle {
  font-size: 15px;
  color: var(--text-secondary, #475569);
  margin: 0;
}

@media (max-width: 768px) {
  .section-title {
    font-size: 22px;
  }
}
</style>
