<template>
  <div class="page-skeleton" v-if="active">
    <!-- Banner骨架屏 -->
    <div class="skeleton-banner"></div>

    <!-- 内容骨架 -->
    <div class="skeleton-content">
      <div class="skeleton-section">
        <Skeleton variant="rect" :height="24" :border-radius="4" width="120px" />
        <div class="skeleton-rows">
          <Skeleton variant="text" :height="14" width="100%" />
          <Skeleton variant="text" :height="14" width="85%" />
          <Skeleton variant="text" :height="14" width="92%" />
        </div>
      </div>

      <div class="skeleton-section">
        <Skeleton variant="rect" :height="24" :border-radius="4" width="160px" />
        <div class="skeleton-grid">
          <div v-for="i in 4" :key="i" class="skeleton-card">
            <Skeleton variant="rect" :height="64" :border-radius="12" width="100%" />
            <Skeleton variant="text" :height="14" width="60%" style="margin-top: 8px" />
            <Skeleton variant="text" :height="12" width="80%" style="margin-top: 6px" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Skeleton from './Skeleton.vue'

interface Props {
  active?: boolean
}

withDefaults(defineProps<Props>(), {
  active: true
})
</script>

<style scoped>
.page-skeleton {
  padding: 0;
  min-height: 100vh;
  background: #f5f7fa;
}

.skeleton-banner {
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #e8eff8 0%, #d8e4f8 100%);
  animation: banner-pulse 1.5s ease-in-out infinite;
}

@keyframes banner-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.skeleton-content {
  padding: 16px;
}

.skeleton-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 12px;
}

.skeleton-rows {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 16px;
}

.skeleton-card {
  background: #f0f5ff;
  border-radius: 12px;
  padding: 12px;
}
</style>
