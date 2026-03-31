import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Global styles
import './assets/responsive.css'

// Create app
const app = createApp(App)

// Register Element Plus icons globally (used as <el-icon><component :is="iconName" /></el-icon>)
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Use plugins
app.use(createPinia())
app.use(router)

// Mount
app.mount('#app')
