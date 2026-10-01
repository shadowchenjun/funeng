<template>
  <button
    type="button"
    class="ui-nav-card"
    :class="{ active }"
    :aria-pressed="active"
    @click="$emit('click')"
  >
    <span class="nav-card-glow"></span>
    <span class="nav-icon-wrapper">
      <el-icon :size="26">
        <component :is="icon" />
      </el-icon>
    </span>
    <span class="nav-label">{{ label }}</span>
  </button>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

/** 板块内导航卡：hover/选中时出现 4px 顶光条，全站统一品牌蓝 */
defineProps<{
  icon: Component
  label: string
  active?: boolean
}>()

defineEmits<{
  click: []
}>()
</script>

<style scoped>
.ui-nav-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 20px 16px;
  font: inherit;
  text-align: center;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  overflow: hidden;
  user-select: none;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
}

.ui-nav-card:hover,
.ui-nav-card.active {
  border-color: var(--primary);
}

.ui-nav-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.ui-nav-card:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.nav-card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--primary);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.ui-nav-card:hover .nav-card-glow,
.ui-nav-card.active .nav-card-glow {
  transform: scaleX(1);
}

.nav-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  transition: background 0.3s ease, color 0.3s ease;
}

.ui-nav-card:hover .nav-icon-wrapper,
.ui-nav-card.active .nav-icon-wrapper {
  color: var(--primary);
  background: var(--primary-light);
}

.nav-label {
  font-size: var(--font-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.ui-nav-card.active .nav-label {
  color: var(--primary);
}

@media (max-width: 768px) {
  .ui-nav-card {
    gap: 8px;
    padding: 14px 6px;
  }

  .nav-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .nav-label {
    font-size: var(--font-xs);
  }
}

@media (prefers-reduced-motion: reduce) {
  .ui-nav-card,
  .nav-card-glow,
  .nav-icon-wrapper {
    transition: none;
  }
}
</style>
