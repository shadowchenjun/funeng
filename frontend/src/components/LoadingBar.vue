<template>
  <Transition name="loading-bar">
    <div v-if="visible" class="loading-bar">
      <div class="loading-bar-progress" :style="{ width: progress + '%' }"></div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'

const visible = ref(false)
const progress = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

const start = () => {
  visible.value = true
  progress.value = 0
  if (timer) clearInterval(timer)
  // 确定性进度：每200ms前进10%，最大到90%
  let p = 0
  timer = setInterval(() => {
    p = Math.min(p + 10, 90)
    progress.value = p
  }, 200)
}

const finish = () => {
  if (timer) clearInterval(timer)
  timer = null
  progress.value = 100
  setTimeout(() => {
    visible.value = false
    progress.value = 0
  }, 200)
}

const error = () => {
  if (timer) clearInterval(timer)
  timer = null
  visible.value = false
  progress.value = 0
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})

defineExpose({ start, finish, error })
</script>

<style scoped>
.loading-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  z-index: 99999;
  background: rgba(22, 93, 255, 0.2);
}

.loading-bar-progress {
  height: 100%;
  background: linear-gradient(90deg, #165DFF 0%, #3B82F6 100%);
  transition: width 0.2s ease;
  border-radius: 0 2px 2px 0;
  box-shadow: 0 0 8px rgba(22, 93, 255, 0.6);
}

.loading-bar-enter-active,
.loading-bar-leave-active {
  transition: opacity 0.2s ease;
}

.loading-bar-enter-from,
.loading-bar-leave-to {
  opacity: 0;
}
</style>
