import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

const allowedHosts = process.env.ALLOWED_HOSTS
  ? process.env.ALLOWED_HOSTS.split(',')
  : ['localhost', '127.0.0.1']

export default defineConfig({
  plugins: [vue()],
  base: '/',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // 开启 rollup 高级拆分选项
    rollupOptions: {
      output: {
        // 手动分包策略
        manualChunks: {
          // Vue 核心库（独立 chunk）
          vue: ['vue', 'vue-router'],
          // Element Plus（独立 chunk，按需 import 会自动 tree-shaking）
          element: ['element-plus'],
          // 图标库
          icons: ['@element-plus/icons-vue'],
          // axios（独立 chunk）
          axios: ['axios']
        },
        // 分 chunk 文件名模板
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    },
    // 启用 gzip 压缩（需要 vite-plugin-compression 或类似插件）
    // chunkSizeWarningLimit: 500 // KB
  },
  // 开发服务器优化
  server: {
    port: 3000,
    host: '0.0.0.0',
    allowedHosts,
    proxy: {
      '/api': {
        target: process.env.API_TARGET || 'http://localhost:8000',
        changeOrigin: true
      }
    },
    // 开启热更新压缩，减少传输体积
    hmr: { overlay: true }
  },
  // 预加载优化
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'element-plus',
      '@element-plus/icons-vue',
      'axios'
    ]
  }
})
