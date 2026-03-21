<template>
  <el-config-provider :locale="locale">
    <div class="app-container">
      <!-- 顶部导航栏 -->
      <header class="app-header" v-if="showHeader">
        <div class="header-content">
          <div class="logo" @click="goToHome">
            <span class="logo-icon">🌾</span>
            <span class="logo-text">FunEng</span>
          </div>

          <nav class="nav-menu">
            <router-link
              v-for="item in navItems"
              :key="item.path"
              :to="item.path"
              class="nav-item"
              :class="{ active: isActive(item.path) }"
            >
              {{ item.label }}
            </router-link>
            <router-link
              v-if="authStore.isAdmin"
              to="/admin"
              class="nav-item"
              :class="{ active: isActive('/admin') }"
            >
              管理后台
            </router-link>
          </nav>

          <div class="user-section">
            <template v-if="authStore.isLoggedIn">
              <el-dropdown @command="handleUserCommand" trigger="click">
                <button class="user-btn">
                  <el-avatar :size="32" :icon="User" />
                  <span class="username">{{ authStore.userInfo?.username || authStore.user?.username }}</span>
                  <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
                </button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item disabled>
                      <el-icon><User /></el-icon>
                      {{ authStore.userInfo?.username || authStore.user?.username }}
                    </el-dropdown-item>
                    <el-dropdown-item divided command="logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button type="primary" @click="goToLogin" class="login-btn">登录</el-button>
            </template>
          </div>
        </div>
      </header>

      <!-- 主内容区域 -->
      <main class="app-main" :class="{ 'no-header': !showHeader }">
        <router-view />
      </main>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, SwitchButton, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from './stores/auth'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const locale = ref(zhCn)

const navItems = [
  { path: '/', label: '首页' },
  { path: '/products', label: '产品' },
  { path: '/categories', label: '分类' }
]

// 不需要显示 header 的页面
const noHeaderRoutes = ['Login', 'Register', 'ClaudeCodeAssistant']
const showHeader = computed(() => !noHeaderRoutes.includes(route.name as string))

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

onMounted(() => {
  authStore.init()
})

const goToHome = () => {
  router.push('/')
}

const goToLogin = () => {
  router.push('/login')
}

const handleUserCommand = (command: string) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style>
/* 全局 CSS 变量 */
:root {
  --primary: #165DFF;
  --primary-light: rgba(22, 93, 255, 0.08);
  --primary-dark: #0F4AE6;
  --accent-green: #10B981;
  --accent-amber: #F59E0B;
  --accent-blue: #3B82F6;
  --accent-red: #EF4444;

  --bg-primary: #FFFFFF;
  --bg-secondary: #F8FAFC;
  --bg-tertiary: #F1F5F9;

  --text-primary: #0F172A;
  --text-secondary: #475569;
  --text-tertiary: #94A3B8;

  --border-color: #E2E8F0;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: 'Inter', 'PingFang SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-secondary);
  color: var(--text-primary);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

#app {
  min-height: 100vh;
}

/* 全局滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-tertiary);
}

/* 全局选中样式 */
::selection {
  background: var(--primary-light);
  color: var(--primary);
}
</style>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border-color);
  padding: 0 24px;
}

.header-content {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  text-decoration: none;
}

.logo-icon {
  font-size: 26px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent-blue) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-item {
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.nav-item:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.nav-item.active {
  color: var(--primary);
  background: var(--primary-light);
}

.user-section {
  display: flex;
  align-items: center;
}

.user-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px 6px 6px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: 100px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-btn:hover {
  background: var(--bg-secondary);
  border-color: var(--text-tertiary);
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.dropdown-arrow {
  font-size: 12px;
  color: var(--text-tertiary);
}

.login-btn {
  padding: 10px 20px;
  font-weight: 600;
  border-radius: var(--radius-sm);
}

.app-main {
  flex: 1;
  padding: 0;
  background: transparent;
}

.app-main.no-header {
  padding: 0;
}

/* 移动端适配 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 16px;
  }

  .header-content {
    height: 56px;
  }

  .logo-text {
    display: none;
  }

  .nav-menu {
    display: flex;
    gap: 2px;
  }

  .nav-item {
    padding: 8px 10px;
    font-size: 13px;
  }

  .username {
    display: none;
  }

  .user-btn {
    padding: 6px;
  }

  .dropdown-arrow {
    display: none;
  }
}
</style>
