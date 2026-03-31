<template>
  <div class="skeleton-group" :style="groupStyle">
    <slot>
      <Skeleton
        v-for="i in count"
        :key="i"
        :variant="variant"
        :width="width"
        :height="height"
        :border-radius="borderRadius"
      />
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Skeleton from './Skeleton.vue'

interface Props {
  count?: number
  variant?: 'text' | 'circular' | 'rect' | 'card'
  width?: string | number
  height?: string | number
  borderRadius?: string | number
  gap?: string | number
  direction?: 'column' | 'row'
}

const props = withDefaults(defineProps<Props>(), {
  count: 3,
  variant: 'text',
  width: '100%',
  height: '16px',
  borderRadius: '4px',
  gap: '8px',
  direction: 'column'
})

const groupStyle = computed(() => ({
  display: 'flex',
  flexDirection: props.direction === 'row' ? 'row' : 'column',
  gap: typeof props.gap === 'number' ? `${props.gap}px` : props.gap
}))
</script>
