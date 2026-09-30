<template>
  <section class="ui-section-card">
    <header v-if="title || $slots.header || $slots.extra" class="section-header">
      <slot name="header">
        <div class="section-title">
          <el-icon v-if="icon" :size="18" class="section-icon">
            <component :is="icon" />
          </el-icon>
          <h3>{{ title }}</h3>
        </div>
      </slot>
      <div v-if="$slots.extra" class="section-extra">
        <slot name="extra" />
      </div>
    </header>
    <div class="section-body" :class="{ 'no-padding': noPadding }">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

/** 唯一区块卡：标题头（可选图标 + 右侧 extra 插槽）+ 底分隔线 + 内容区；替代裸 el-card */
defineProps<{
  title?: string
  icon?: Component
  /** 内容区去掉内边距（整宽表格等） */
  noPadding?: boolean
}>()
</script>

<style scoped>
.ui-section-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.section-title h3 {
  margin: 0;
  font-size: var(--font-md);
  font-weight: 600;
  color: var(--text-primary);
}

.section-icon {
  color: var(--primary);
}

.section-extra {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.section-body {
  padding: 20px 24px;
}

.section-body.no-padding {
  padding: 0;
}

@media (max-width: 768px) {
  .section-header {
    flex-wrap: wrap;
    padding: 16px;
  }

  .section-body {
    padding: 16px;
  }
}
</style>
