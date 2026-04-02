<template>
  <div
    class="stat-card"
    :style="{ '--accent': accentColor }"
  >
    <div class="stat-icon" v-if="icon">
      <el-icon :size="28" :color="accentColor">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-content">
      <div class="stat-value">{{ value }}</div>
      <div class="stat-title">{{ title }}</div>
      <div class="stat-trend" v-if="trend !== undefined" :class="trend >= 0 ? 'up' : 'down'">
        <span class="trend-icon">{{ trend >= 0 ? '↑' : '↓' }}</span>
        <span>{{ Math.abs(trend) }}%</span>
      </div>
    </div>
    <div class="accent-bar"></div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  value: string | number
  title: string
  trend?: number
  icon?: Component
  accentColor?: string
}>()
</script>

<style scoped>
.stat-card {
  position: relative;
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg, 0 10px 15px -3px rgba(0, 0, 0, 0.1));
}

.accent-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: var(--accent, #3B82F6);
}

.stat-icon {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: color-mix(in srgb, var(--accent, #3B82F6) 10%, transparent);
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary, #0F172A);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.stat-title {
  font-size: 13px;
  color: var(--text-secondary, #475569);
  margin-top: 4px;
}

.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  margin-top: 8px;
  padding: 2px 8px;
  border-radius: 100px;
}

.stat-trend.up {
  color: #67C23A;
  background: rgba(103, 194, 58, 0.1);
}

.stat-trend.down {
  color: #F56C6C;
  background: rgba(245, 108, 108, 0.1);
}

.trend-icon {
  font-size: 10px;
}

@media (prefers-reduced-motion: reduce) {
  .stat-card {
    transition: none;
  }
}
</style>
