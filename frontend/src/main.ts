import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

// Global styles
import './assets/responsive.css'

// Create app
const app = createApp(App)

// Use plugins
app.use(createPinia())
app.use(router)

// Mount
app.mount('#app')
