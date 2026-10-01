<template>
  <el-config-provider :locale="locale">
    <div id="app-root">
      <!-- 全局顶部加载进度条（Sprint 3） -->
      <LoadingBar ref="loadingBarRef" />

      <!-- 页面骨架屏（路由切换时显示，Sprint 3） -->
      <Transition name="page">
        <PageSkeleton v-if="showPageSkeleton" />
      </Transition>

      <!-- 主内容 -->
      <template v-if="!showPageSkeleton">
        <!-- 顶部导航栏 -->
        <header class="app-header" v-if="showHeader">
          <div class="header-content">
            <div class="logo" @click="goToHome">
              <img class="logo-icon" src="/logo-transparent.png" alt="FunEng Logo" />
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
              <button class="menu-toggle" aria-label="打开导航菜单" @click="drawerVisible = true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true">
                  <path d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </header>

        <!-- <1200px 导航抽屉 -->
        <el-drawer
          v-model="drawerVisible"
          direction="rtl"
          size="280px"
          :with-header="false"
          class="nav-drawer"
        >
          <nav class="drawer-nav">
            <router-link
              v-for="item in allNavItems"
              :key="item.path"
              :to="item.path"
              class="drawer-item"
              :class="{ active: isActive(item.path) }"
            >
              {{ item.label }}
            </router-link>
          </nav>
          <div class="drawer-user">
            <template v-if="authStore.isLoggedIn">
              <div class="drawer-username">
                <el-avatar :size="28" :icon="User" />
                <span>{{ authStore.userInfo?.username || authStore.user?.username }}</span>
              </div>
              <el-button @click="handleUserCommand('logout')">退出登录</el-button>
            </template>
            <el-button v-else type="primary" @click="goToLogin">登录</el-button>
          </div>
        </el-drawer>

        <!-- 主内容区域 -->
        <main class="app-main" :class="{ 'no-header': !showHeader }">
          <router-view v-slot="{ Component, route }">
            <keep-alive :include="cacheInclude" :max="5">
              <component :is="Component" :key="route.path" />
            </keep-alive>
          </router-view>
        </main>
      </template>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, SwitchButton, ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from './stores/auth'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import LoadingBar from './components/LoadingBar.vue'
import PageSkeleton from './components/PageSkeleton.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const locale = ref(zhCn)
const loadingBarRef = ref<InstanceType<typeof LoadingBar> | null>(null)
const showPageSkeleton = ref(false)

// 需要缓存的视图（保留状态，避免重复加载）
// include 匹配组件名（<script setup> 由文件名推断），不是路由名
const cachedViews = ['ProductsView', 'CategoriesView', 'DashboardView']

// 按用户隔离页面缓存：用户变化（退出、换账号、token 失效后重新登录）时短暂清空 include，
// 让 KeepAlive 丢弃其他页面的缓存实例；当前页不重新挂载，避免退出瞬间用失效 token 发请求
const cacheEnabled = ref(true)
const cacheInclude = computed(() => (cacheEnabled.value ? cachedViews : []))
watch(
  () => authStore.user?.id,
  async () => {
    cacheEnabled.value = false
    await nextTick()
    cacheEnabled.value = true
  }
)

const navItems = [
  { path: '/', label: '首页' },
  { path: '/products', label: '产品' },
  { path: '/categories', label: '分类' },
  { path: '/dashboard', label: '看板' },
  { path: '/industry-dashboard', label: '产业大屏' },
  { path: '/smart-agriculture', label: '智慧农业' },
  { path: '/digital-marketing', label: '数字营销' },
  { path: '/cold-chain', label: '冷链物流' },
  { path: '/supply-chain-finance', label: '供应链金融' }
]

// 抽屉内含全部入口（含 admin-only 的管理后台）
const allNavItems = computed(() =>
  authStore.isAdmin ? [...navItems, { path: '/admin', label: '管理后台' }] : navItems
)

const drawerVisible = ref(false)

// 不需要显示 header 的页面
const noHeaderRoutes = ['Login', 'Register', 'ClaudeCodeAssistant']
const showHeader = computed(() => !noHeaderRoutes.includes(route.name as string))

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}

// 监听路由变化，显示加载条（Sprint 3）
watch(
  () => route.path,
  () => {
    drawerVisible.value = false
    loadingBarRef.value?.start()
    // 路由组件加载是异步的，不需要骨架屏
    setTimeout(() => {
      loadingBarRef.value?.finish()
    }, 200)
  }
)

onMounted(() => {
  authStore.init()
  // 首屏完成后移除骨架屏
  setTimeout(() => {
    showPageSkeleton.value = false
  }, 300)
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
  --accent-blue: #3B82F6;

  /* 语义色（正源）：彩色仅用于状态，不做板块身份色 */
  --color-success: #10B981;
  --color-success-bg: rgba(16, 185, 129, 0.1);
  --color-warning: #F59E0B;
  --color-warning-bg: rgba(245, 158, 11, 0.1);
  --color-danger: #EF4444;
  --color-danger-bg: rgba(239, 68, 68, 0.1);
  --color-info: #64748B;
  --color-info-bg: #F1F5F9;

  /* 已废弃：语义色别名，新代码请用 --color-* */
  --accent-green: var(--color-success);
  --accent-amber: var(--color-warning);
  --accent-red: var(--color-danger);

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
  --radius-pill: 100px;

  /* 字阶（6 档收死，首页 hero 除外） */
  --font-xs: 12px;
  --font-sm: 14px;
  --font-md: 16px;
  --font-lg: 20px;
  --font-xl: 24px;
  --font-2xl: 28px;
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

/* ====== 页面布局（UI 统一 spec §3.1 间距基准） ====== */
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* 统计卡网格：4 → 2 列 */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

/* 3 项统计 */
.stat-grid--3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

/* 区块内的信息小卡（卡中卡统一形态：浅底、12px、无阴影） */
.tile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
}

.tile {
  padding: 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.tile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.tile-title {
  font-size: var(--font-sm);
  font-weight: 600;
  color: var(--text-primary);
}

/* 标签: 值 的信息行 */
.tile-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0;
  font-size: var(--font-xs);
  color: var(--text-secondary);
}

.tile-actions {
  display: flex;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 10px;
}

/* 区块内的指标小块（区块外用 StatCard，区块内用 metric，避免卡中卡） */
.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.metric {
  padding: 14px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

.metric-value {
  display: block;
  font-size: var(--font-lg);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.metric-label {
  display: block;
  margin-top: 2px;
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

/* 区块内的小节标题（替代带 emoji 的 el-divider） */
.subsection-title {
  margin: 24px 0 12px;
  font-size: var(--font-sm);
  font-weight: 600;
  color: var(--text-primary);
}

.subsection-title:first-child {
  margin-top: 0;
}

.w-full {
  width: 100%;
}

/* 区块纵向间距 */
.section-stack {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 两栏区块，<1024px 堆叠 */
.section-split {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
}

@media (max-width: 1024px) {
  .stat-grid:not(.stat-grid--3) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .section-split {
    grid-template-columns: minmax(0, 1fr);
  }
}

@media (max-width: 768px) {
  .page-container {
    padding: 16px;
  }

  .stat-grid {
    gap: 12px;
    margin-bottom: 16px;
  }

  .section-stack,
  .section-split {
    gap: 16px;
  }
}

/* 页面切换动画（Sprint 3） */
.page-enter-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* 路由切换时隐藏旧页面，避免重排 */
.page-leave-active {
  position: absolute;
  width: 100%;
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
  gap: 0;
  cursor: pointer;
  text-decoration: none;
}

.logo-icon {
  width: 96px;
  height: 96px;
  object-fit: contain;
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

.menu-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin-left: 8px;
  color: var(--text-secondary);
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
}

.menu-toggle:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.drawer-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.drawer-item {
  padding: 12px 16px;
  font-size: var(--font-sm);
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: var(--radius-sm);
}

.drawer-item:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.drawer-item.active {
  color: var(--primary);
  background: var(--primary-light);
}

.drawer-user {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.drawer-username {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-sm);
  color: var(--text-primary);
}

.app-main {
  flex: 1;
  padding: 0;
  background: transparent;
}

.app-main.no-header {
  padding: 0;
}

/* <1200px：平铺导航收进抽屉 */
@media (max-width: 1199px) {
  .nav-menu {
    display: none;
  }

  .menu-toggle {
    display: inline-flex;
  }
}

/* 移动端适配 */
@media (max-width: 768px) {
  .app-header {
    padding: 0 16px;
  }

  .header-content {
    height: 56px;
  }

  .logo-icon {
    width: 56px;
    height: 56px;
  }

  .logo-text {
    display: none;
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
