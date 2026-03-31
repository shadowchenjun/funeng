<script setup lang="ts">
/**
 * LazyImage.vue - WebP + Lazy Loading Image Component
 * 
 * Features:
 * - Automatic WebP format detection
 * - Native lazy loading (loading="lazy")
 * - Async decoding for non-blocking decode
 * - Skeleton placeholder during load
 * - Error fallback
 */
import { ref, computed, onMounted } from 'vue'

const props = defineProps<{
  src: string
  alt?: string
  placeholderType?: 'skeleton' | 'blur' | 'none'
  className?: string
  loading?: 'lazy' | 'eager'
  width?: string | number
  height?: string | number
}>()

const isLoaded = ref(false)
const isError = ref(false)
const imgRef = ref<HTMLImageElement | null>(null)

// Generate WebP src (if source image is jpg/png)
const webpSrc = computed(() => {
  if (!props.src) return ''
  // If already webp, return as-is
  if (props.src.toLowerCase().includes('.webp')) return props.src
  // Try to use CDN image service for WebP conversion
  // For picsum.photos, use the built-in format parameter
  if (props.src.includes('picsum.photos')) {
    return props.src.replace('picsum.photos', 'picsum.photos.webp')
  }
  // For other images, return original (browser will use native WebP support if available)
  return props.src
})

const normalSrc = computed(() => props.src || '')

const placeholder = computed(() => {
  if (props.placeholderType === 'skeleton') return ''
  if (props.placeholderType === 'blur') return props.src
  return ''
})

function handleLoad() {
  isLoaded.value = true
}

function handleError() {
  isError.value = true
  isLoaded.value = true
}

onMounted(() => {
  // Use Intersection Observer for better lazy loading control
  if ('IntersectionObserver' in window && imgRef.value && props.loading !== 'eager') {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Image is now visible, let native loading handle it
            observer.disconnect()
          }
        })
      },
      { rootMargin: '50px 0px' }
    )
    if (imgRef.value) {
      observer.observe(imgRef.value)
    }
  }
})
</script>

<template>
  <div
    class="lazy-image-wrapper"
    :class="[placeholderType === 'skeleton' && !isLoaded ? 'loading' : 'loaded', className]"
    :style="{ width: width || '100%', height: height || 'auto' }"
  >
    <!-- Skeleton placeholder -->
    <div v-if="placeholderType === 'skeleton' && !isLoaded" class="skeleton-bg"></div>

    <!-- Picture element with WebP support -->
    <picture v-if="!isError">
      <source :srcset="webpSrc" type="image/webp" />
      <source :srcset="normalSrc" type="image/jpeg" />
      <img
        ref="imgRef"
        :src="placeholder || normalSrc"
        :alt="alt || ''"
        :loading="loading || 'lazy'"
        decoding="async"
        :class="['lazy-img', { 'img-loaded': isLoaded }]"
        @load="handleLoad"
        @error="handleError"
      />
    </picture>

    <!-- Error fallback -->
    <div v-else class="error-fallback">
      <span>🖼️ 图片加载失败</span>
    </div>

    <!-- Loaded state overlay -->
    <div v-if="isLoaded" class="loaded-indicator"></div>
  </div>
</template>

<style scoped>
.lazy-image-wrapper {
  position: relative;
  overflow: hidden;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.skeleton-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.lazy-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.lazy-img.img-loaded {
  opacity: 1;
}

.error-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  min-height: 60px;
  background: #f5f7fa;
  color: #909399;
  font-size: 12px;
}

.loaded-indicator {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
}
</style>
