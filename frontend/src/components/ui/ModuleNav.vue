<template>
  <nav class="ui-module-nav" :aria-label="ariaLabel">
    <div
      v-for="group in groups"
      :key="group.label || group.items[0]?.key"
      class="nav-group"
      :style="{ '--count': group.items.length }"
    >
      <div v-if="group.label" class="nav-group-label">{{ group.label }}</div>
      <div class="nav-group-items">
        <NavCard
          v-for="item in group.items"
          :key="item.key"
          :icon="item.icon"
          :label="item.label"
          :active="item.key === modelValue"
          @click="emit('update:modelValue', item.key)"
        />
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import NavCard from './NavCard.vue'

export interface ModuleNavItem {
  key: string
  label: string
  icon: Component
}

export interface ModuleNavGroup {
  /** 分组标题；单组时可省略 */
  label?: string
  items: ModuleNavItem[]
}

/** 板块内导航：NavCard 按业务分组排列，宽屏一行、窄屏按组换行；v-model 为当前项 key */
withDefaults(defineProps<{
  groups: ModuleNavGroup[]
  modelValue: string
  ariaLabel?: string
}>(), {
  ariaLabel: '板块导航'
})

const emit = defineEmits<{
  'update:modelValue': [key: string]
}>()
</script>

<style scoped>
.ui-module-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 16px 24px;
  margin-bottom: 24px;
}

/* 组宽与项数成正比，保证各卡等宽 */
.nav-group {
  flex: var(--count) 1 calc(var(--count) * 104px);
  min-width: 0;
}

.nav-group-label {
  margin-bottom: 8px;
  font-size: var(--font-xs);
  font-weight: 500;
  color: var(--text-tertiary);
}

.nav-group-items {
  display: grid;
  grid-template-columns: repeat(var(--count), minmax(0, 1fr));
  gap: 8px;
}

@media (max-width: 768px) {
  .ui-module-nav {
    gap: 12px;
    margin-bottom: 16px;
  }

  .nav-group {
    flex-basis: 100%;
  }

  .nav-group-items {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}
</style>
