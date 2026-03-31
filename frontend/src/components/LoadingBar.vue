<template>
  <Transition name="loading-bar">
    <div v-if="visible" class="loading-bar">
      <div class="loading-bar-progress" :style="{ width: progress + '%' }"></div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const visible = ref(false)
const progress = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

const start = () => {
  visible.value = true
  progress.value = 0
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    // 模拟进度增长，最大到 90%，等待真实加载完成
    if (progress.value < 90) {
      progress.value += Math.random() * 15
    }
  }, 200)
}

const finish = () => {
  if (timer) clearInterval(timer)
  progress.value = 100
  setTimeout(() => {
    visible.value = false
    progress.value = 0
  }, 300)
}

const error = () => {
  if (timer) clearInterval(timer)
  visible.value = false
  progress.value = 0
}

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
  background: rgba(102, 126, 234, 0.2);
}

.loading-bar-progress {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.2s ease;
  border-radius: 0 2px 2px 0;
  box-shadow: 0 0 8px rgba(102, 126, 234, 0.6);
}

.loading-bar-enter-active,
.loading-bar-leave-active {
  transition: opacity 0.3s ease;
}

.loading-bar-enter-from,
.loading-bar-leave-to {
  opacity: 0;
}
</style>
