<template>
  <div class="empty-state">
    <div class="empty-icon">
      <el-icon :size="48" :color="iconColor">
        <component :is="icon" />
      </el-icon>
    </div>
    <h3 class="empty-title">{{ title }}</h3>
    <p class="empty-description" v-if="description">{{ description }}</p>
    <div class="empty-action" v-if="$slots.action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Folder } from '@element-plus/icons-vue'
import type { Component } from 'vue'

const props = withDefaults(defineProps<{
  icon?: Component
  title: string
  description?: string
  iconColor?: string
}>(), {
  icon: Folder,
  iconColor: '#94A3B8'
})

const icon = computed(() => props.icon)
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-icon {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary, #F8FAFC);
  border-radius: 50%;
  margin-bottom: 20px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #0F172A);
  margin: 0 0 8px;
}

.empty-description {
  font-size: 14px;
  color: var(--text-secondary, #475569);
  margin: 0;
  max-width: 300px;
}

.empty-action {
  margin-top: 20px;
}
</style>
