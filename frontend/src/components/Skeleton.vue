<template>
  <div class="skeleton" :style="skeletonStyle">
    <div class="skeleton-shimmer" :class="`skeleton-${variant}`"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  width?: string | number
  height?: string | number
  borderRadius?: string | number
  variant?: 'text' | 'circular' | 'rect' | 'card'
}

const props = withDefaults(defineProps<Props>(), {
  width: '100%',
  height: '16px',
  borderRadius: '4px',
  variant: 'text'
})

const skeletonStyle = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width,
  height: typeof props.height === 'number' ? `${props.height}px` : props.height,
  borderRadius: typeof props.borderRadius === 'number' ? `${props.borderRadius}px` : props.borderRadius
}))
</script>

<style scoped>
.skeleton {
  position: relative;
  overflow: hidden;
  background: #f0f0f5;
}

.skeleton-shimmer::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.6) 50%,
    transparent 100%
  );
  animation: shimmer 1.5s infinite;
  background-size: 200% 100%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-text { height: 16px; }
.skeleton-circular { border-radius: 50%; }
.skeleton-rect { border-radius: 8px; }
.skeleton-card {
  border-radius: 16px;
  height: 120px;
}
</style>
