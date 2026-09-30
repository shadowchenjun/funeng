<template>
  <header class="ui-page-header">
    <div class="page-heading">
      <h1 class="page-title">{{ title }}</h1>
      <p v-if="subtitle" class="page-subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="page-actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup lang="ts">
/** 唯一页面头：标题 + 副标题 + 右侧 actions 插槽 */
defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped>
.ui-page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.page-heading {
  min-width: 0;
}

.page-title {
  margin: 0;
  font-size: var(--font-2xl);
  font-weight: 700;
  line-height: 1.25;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.page-subtitle {
  margin: 8px 0 0;
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .ui-page-header {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 16px;
  }

  .page-title {
    font-size: var(--font-lg);
  }

  .page-actions {
    flex-wrap: wrap;
  }
}
</style>
