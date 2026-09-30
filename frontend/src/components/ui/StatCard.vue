<template>
  <div class="ui-stat-card" :style="{ '--accent': accent }">
    <div class="accent-bar"></div>
    <div class="stat-body">
      <div class="stat-content">
        <div class="stat-value">
          {{ value }}<span v-if="unit" class="stat-unit">{{ unit }}</span>
        </div>
        <div class="stat-title">{{ title }}</div>
        <div v-if="trend !== undefined" class="stat-trend" :class="trend >= 0 ? 'up' : 'down'">
          <span>{{ trend >= 0 ? '↑' : '↓' }} {{ Math.abs(trend) }}%</span>
        </div>
      </div>
      <div v-if="icon" class="stat-icon">
        <el-icon :size="24" :color="accent">
          <component :is="icon" />
        </el-icon>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Component } from 'vue'

/** 唯一统计卡：顶部 4px 语义色条 + 数值 + 标签 + 可选图标 chip / 趋势 pill */
const props = withDefaults(defineProps<{
  value: string | number
  title: string
  unit?: string
  /** 同比/环比百分比，正数为升 */
  trend?: number
  icon?: Component
  /** 语义色，决定色条与图标颜色 */
  type?: 'primary' | 'success' | 'warning' | 'danger' | 'info'
}>(), {
  type: 'primary'
})

const accent = computed(() =>
  props.type === 'primary' ? 'var(--primary)' : `var(--color-${props.type})`
)
</script>

<style scoped>
.ui-stat-card {
  position: relative;
  height: 100%;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.ui-stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.accent-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--accent);
}

.stat-body {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 24px 20px 20px;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-value {
  font-size: var(--font-xl);
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

.stat-unit {
  margin-left: 4px;
  font-size: var(--font-sm);
  font-weight: 500;
  color: var(--text-secondary);
}

.stat-title {
  margin-top: 6px;
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.stat-trend {
  display: inline-flex;
  margin-top: 10px;
  padding: 2px 8px;
  font-size: var(--font-xs);
  font-weight: 500;
  border-radius: var(--radius-pill);
}

.stat-trend.up {
  color: var(--color-success);
  background: var(--color-success-bg);
}

.stat-trend.down {
  color: var(--color-danger);
  background: var(--color-danger-bg);
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

@media (prefers-reduced-motion: reduce) {
  .ui-stat-card {
    transition: none;
  }
}
</style>
