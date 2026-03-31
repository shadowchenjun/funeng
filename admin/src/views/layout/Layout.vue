<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const collapsed = ref(false)

const activeMenu = computed(() => route.path)

const menuItems = [
  { path: '/dashboard', title: '数据看板', icon: 'DataAnalysis' },
  { path: '/adoption', title: '认养管理', icon: 'Crop' },
  { path: '/land', title: '土地管理', icon: 'MapLocation' },
  { path: '/device', title: '设备管理', icon: 'Monitor' },
  { path: '/traceability', title: '溯源管理', icon: 'Connection' },
  { path: '/user', title: '用户管理', icon: 'User' },
  { path: '/marketing', title: '营销管理', icon: 'PriceTag' },
  { path: '/admin', title: '管理员管理', icon: 'Setting' },
  { path: '/settings', title: '系统设置', icon: 'Tools' }
]

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await authStore.logout()
    router.push('/login')
  } catch (e) {
    // cancelled
  }
}

onMounted(() => {
  authStore.fetchProfile()
})
</script>

<template>
  <el-container class="layout-container">
    <el-aside :width="collapsed ? '64px' : '220px'" class="aside">
      <div class="logo">
        <span v-if="!collapsed">农文旅云</span>
        <span v-else>管理</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="collapsed"
        :router="true"
        class="menu"
        background-color="#1e3a5f"
        text-color="#a8c8e8"
        active-text-color="#ffffff"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
          class="menu-item"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="collapsed = !collapsed">
            <Fold v-if="!collapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title">
              {{ route.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleLogout">
            <span class="user-info">
              <el-avatar :size="32" style="margin-right: 8px; background: #1e3a5f;">
                {{ authStore.user?.full_name?.[0] || authStore.user?.username?.[0] || 'A' }}
              </el-avatar>
              <span>{{ authStore.user?.full_name || authStore.user?.username }}</span>
              <el-icon style="margin-left: 4px"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background: linear-gradient(180deg, #1e3a5f 0%, #152a45 100%);
  transition: width 0.3s;
  overflow-x: hidden;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 20px;
  font-weight: bold;
  background: linear-gradient(180deg, #243b55 0%, #1e3a5f 100%);
  border-bottom: 1px solid rgba(255,255,255,0.1);
  letter-spacing: 2px;
}

.menu {
  border-right: none;
  background: transparent;
}

.menu:not(.el-menu--collapse) {
  width: 220px;
}

.menu-item {
  height: 56px;
  line-height: 56px;
  margin: 4px 8px;
  border-radius: 8px;
}

.menu-item:hover {
  background: rgba(255,255,255,0.1) !important;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #409eff 0%, #3a8bd9 100%) !important;
  color: #ffffff !important;
  font-weight: 600;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  margin-right: 20px;
  color: #666;
}

.collapse-btn:hover {
  color: #409eff;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background 0.3s;
}

.user-info:hover {
  background: #f5f7fa;
}

.main {
  background: linear-gradient(180deg, #f5f7fa 0%, #ffffff 100%);
  padding: 24px;
  min-height: calc(100vh - 60px);
}
</style>
