<template>
  <el-config-provider :locale="locale">
    <div class="app-container">
      <!-- 顶部导航栏 -->
      <el-header class="app-header" v-if="showHeader">
        <div class="header-content">
          <div class="logo" @click="goToHome">
            <span class="logo-icon">🌾</span>
            <span class="logo-text">现代农业赋能平台</span>
          </div>
          
          <el-menu 
            mode="horizontal" 
            :router="true" 
            :default-active="activeMenu"
            class="nav-menu"
            background-color="transparent"
            text-color="#fff"
            active-text-color="#ffd04b"
          >
            <el-menu-item index="/">首页</el-menu-item>
            <el-menu-item index="/dashboard">数据仪表盘</el-menu-item>
            <el-menu-item index="/products">产品管理</el-menu-item>
            <el-menu-item index="/categories">分类管理</el-menu-item>
            <el-menu-item index="/admin" v-if="authStore.isAdmin">管理后台</el-menu-item>
          </el-menu>
          
          <div class="user-section">
            <template v-if="authStore.isLoggedIn">
              <el-dropdown @command="handleUserCommand">
                <span class="user-info">
                  <el-avatar :size="32" :icon="User" />
                  <span class="username">{{ authStore.userInfo?.username || authStore.user?.username }}</span>
                </span>
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
              <el-button type="primary" @click="goToLogin">登录</el-button>
            </template>
          </div>
        </div>
      </el-header>
      
      <!-- 主内容区域 -->
      <el-main class="app-main" :class="{ 'no-header': !showHeader }">
        <router-view />
      </el-main>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { User, SwitchButton } from '@element-plus/icons-vue'
import { useAuthStore } from './stores/auth'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const locale = ref(zhCn)

// 不需要显示 header 的页面
const noHeaderRoutes = ['Login', 'Register']
const showHeader = computed(() => !noHeaderRoutes.includes(route.name as string))
const activeMenu = computed(() => route.path)

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
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}
</style>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  height: 60px;
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
  cursor: pointer;
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.logo-icon {
  font-size: 28px;
  margin-right: 10px;
}

.logo-text {
  white-space: nowrap;
}

.nav-menu {
  flex: 1;
  margin: 0 40px;
  border: none;
  background: transparent;
}

.nav-menu :deep(.el-menu-item) {
  border: none;
  font-size: 15px;
}

.nav-menu :deep(.el-menu-item:hover),
.nav-menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.1);
}

.user-section {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.3s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.1);
}

.username {
  margin-left: 8px;
  font-size: 14px;
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
    padding: 0 10px;
  }
  
  .header-content {
    height: 50px;
  }
  
  .logo-text {
    font-size: 14px;
    max-width: 90px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .logo-icon {
    font-size: 22px;
    margin-right: 5px;
  }
  
  .nav-menu {
    display: none;
  }
  
  .user-section .el-button {
    padding: 6px 10px;
    font-size: 12px;
  }
  
  .username {
    display: none;
  }
  
  .user-info {
    padding: 4px;
  }
}

</style>
