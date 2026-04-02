<template>
  <div
    class="nav-card"
    :style="{ '--accent': accentColor }"
    :class="{ 'is-hovered': isHovered }"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @click="$emit('click')"
  >
    <div class="nav-card-glow"></div>
    <div class="nav-card-content">
      <div class="nav-icon-wrapper">
        <el-icon :size="28" :color="accentColor">
          <component :is="icon" />
        </el-icon>
      </div>
      <span class="nav-label">{{ label }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Component } from 'vue'

defineProps<{
  icon: Component
  label: string
  accentColor?: string
}>()

defineEmits<{
  click: []
}>()

const isHovered = ref(false)
</script>

<style scoped>
.nav-card {
  position: relative;
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 14px;
  padding: 20px 16px;
  text-align: center;
  cursor: pointer;
  overflow: hidden;
  transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
  user-select: none;
}

.nav-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent, #3B82F6);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.nav-card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--accent, #3B82F6);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.nav-card:hover .nav-card-glow {
  transform: scaleX(1);
}

.nav-card-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.nav-icon-wrapper {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary, #F8FAFC);
  border-radius: 12px;
  transition: background 0.3s ease, transform 0.3s ease;
}

.nav-card:hover .nav-icon-wrapper {
  background: color-mix(in srgb, var(--accent, #3B82F6) 10%, transparent);
  transform: scale(1.05);
}

.nav-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #0F172A);
}

@media (prefers-reduced-motion: reduce) {
  .nav-card,
  .nav-card-glow,
  .nav-icon-wrapper {
    transition: none;
  }
}
</style>
