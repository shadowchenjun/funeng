import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { resolve } from 'path'
import viteCompression from 'vite-plugin-compression'

const allowedHosts = process.env.ALLOWED_HOSTS
  ? process.env.ALLOWED_HOSTS.split(',')
  : ['localhost', '127.0.0.1']

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      imports: ['vue', 'vue-router'],
      resolvers: [ElementPlusResolver()],
      dts: 'src/auto-imports.d.ts',
      eslintrc: false
    }),
    Components({
      resolvers: [ElementPlusResolver()],
      dts: 'src/components.d.ts'
    }),
    // gzip 压缩
    viteCompression({
      verbose: false,
      disable: false,
      threshold: 10240,
      algorithm: 'gzip',
      ext: '.gz'
    }),
    // brotli 压缩
    viteCompression({
      verbose: false,
      disable: false,
      threshold: 10240,
      algorithm: 'brotliCompress',
      ext: '.br'
    })
  ],
  base: '/',
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    cssCodeSplit: true,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        // 动态分 chunk，基于 node_modules 路径
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // Vue Router 独立 chunk（通常不需要首屏加载）
            if (id.includes('vue-router')) {
              return 'vue-router'
            }
            // Pinia 独立 chunk（异步加载）
            if (id.includes('pinia')) {
              return 'pinia'
            }
            // Element Plus 必须在 vue 之前检查，避免被误入 vue-core
            // element-plus/es/Alert 这类路径的 @vue 依赖会错误匹配 vue 条件
            if (id.includes('element-plus')) {
              return 'element-plus'
            }
            // Vue 核心（最小同步 chunk）
            if (id.includes('vue') || id.includes('@vue')) {
              return 'vue-core'
            }
            // 图标库（按需，只打包实际使用的图标）
            if (id.includes('@element-plus/icons-vue')) {
              return 'icons'
            }
            // axios
            if (id.includes('axios')) {
              return 'axios'
            }
          }
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    }
  },
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
    hmr: { overlay: true }
  },
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
