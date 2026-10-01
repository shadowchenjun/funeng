<template>
  <div class="page-container">
    <PageHeader title="管理后台" subtitle="用户管理与平台运营概览">
      <template #actions>
        <el-button :icon="Refresh" :loading="loading" @click="refreshData">刷新数据</el-button>
      </template>
    </PageHeader>

    <div class="section-stack">
      <!-- 功能模块入口 -->
      <SectionCard title="业务板块" :icon="Grid">
        <div class="module-grid">
          <button
            v-for="module in modules"
            :key="module.path"
            type="button"
            class="module-card"
            @click="goToModule(module.path)"
          >
            <span class="module-icon">
              <el-icon :size="24"><component :is="module.icon" /></el-icon>
            </span>
            <span class="module-info">
              <span class="module-name">{{ module.name }}</span>
              <span class="module-desc">{{ module.desc }}</span>
            </span>
            <el-icon class="module-arrow"><ArrowRight /></el-icon>
          </button>
        </div>
      </SectionCard>

      <!-- 统计概览 -->
      <div class="stat-grid stat-grid--flush">
        <StatCard
          v-for="stat in stats"
          :key="stat.title"
          :value="stat.value"
          :title="stat.title"
          :type="stat.type"
          :icon="stat.icon"
        />
      </div>

      <!-- 用户管理 -->
      <SectionCard title="用户管理" :icon="User">
        <template #extra>
          <el-input
            v-model="search"
            placeholder="搜索用户名 / 邮箱 / 姓名"
            :prefix-icon="Search"
            clearable
            class="user-search"
            @keyup.enter="fetchUsers"
            @clear="fetchUsers"
          />
        </template>
        <el-table :data="users" v-loading="loading" empty-text="暂无用户">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" min-width="140" />
          <el-table-column prop="email" label="邮箱" min-width="200" />
          <el-table-column label="角色" width="120">
            <template #default="{ row }">
              <el-tag :type="row.is_admin ? 'primary' : 'info'">
                {{ row.is_admin ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="140">
            <template #default="{ row }">
              <el-switch
                v-model="row.is_active"
                active-text="启用"
                inactive-text="禁用"
                :disabled="row.id === currentUserId"
                @change="handleStatusChange(row)"
              />
            </template>
          </el-table-column>
          <el-table-column label="注册时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </SectionCard>

      <el-alert
        type="info"
        :closable="false"
        show-icon
        title="认养、土地、设备、溯源、营销及系统配置等运营管理，请使用独立的管理后台（admin/）。"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { getErrorMessage } from '../utils/error'
import type { Component } from 'vue'
import {
  ArrowRight, CircleCheck, DataAnalysis, Document, Grid, Refresh, Search, TrendCharts, User, UserFilled, Van, Wallet
} from '@element-plus/icons-vue'

const router = useRouter()

const modules = [
  {
    name: '智慧农业',
    desc: '设备管理、地块管理、作物监控',
    path: '/smart-agriculture',
    icon: DataAnalysis
  },
  {
    name: '数字营销',
    desc: '会员管理、营销活动',
    path: '/digital-marketing',
    icon: TrendCharts
  },
  {
    name: '冷链物流',
    desc: '车辆管理、仓库管理',
    path: '/cold-chain',
    icon: Van
  },
  {
    name: '供应链金融',
    desc: '金融服务管理',
    path: '/supply-chain-finance',
    icon: Wallet
  }
]

const goToModule = (path: string) => {
  router.push(path)
}

interface UserRow {
  id: number
  username: string
  email: string | null
  full_name: string | null
  is_active: boolean
  is_admin: boolean
  created_at: string
}

interface UserStats {
  total_users: number
  active_users: number
  inactive_users: number
  admin_users: number
}

const loading = ref(false)
const search = ref('')
const users = ref<UserRow[]>([])
const currentUserId = (JSON.parse(localStorage.getItem('user') || 'null') as { id?: number } | null)?.id

interface AdminStat {
  title: string
  value: string
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info'
  icon: Component
}

const statMeta: Omit<AdminStat, 'value'>[] = [
  { title: '总用户数', type: 'primary', icon: User },
  { title: '活跃用户', type: 'success', icon: CircleCheck },
  { title: '管理员', type: 'primary', icon: UserFilled },
  { title: '总订单', type: 'primary', icon: Document }
]

const stats = ref<AdminStat[]>(statMeta.map((m) => ({ ...m, value: '—' })))

const formatDate = (value: string) => value.replace('T', ' ').slice(0, 19)

const fetchStats = async () => {
  const [userRes, publicRes] = await Promise.all([
    axios.get<UserStats>('/api/users/stats'),
    axios.get<{ order_count: number }>('/api/public/stats')
  ])
  const n = (v: number) => v.toLocaleString('zh-CN')
  const values = [
    userRes.data.total_users,
    userRes.data.active_users,
    userRes.data.admin_users,
    publicRes.data.order_count
  ]
  stats.value = statMeta.map((m, i) => ({ ...m, value: n(values[i]) }))
}

const fetchUsers = async () => {
  const { data } = await axios.get<UserRow[]>('/api/users/', {
    params: { limit: 100, search: search.value || undefined }
  })
  users.value = data
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([fetchStats(), fetchUsers()])
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '加载数据失败'))
  } finally {
    loading.value = false
  }
}

const handleStatusChange = async (user: UserRow) => {
  try {
    await axios.patch(`/api/users/${user.id}/status`, null, { params: { is_active: user.is_active } })
    ElMessage.success(`用户 ${user.username} 已${user.is_active ? '启用' : '禁用'}`)
    await fetchStats()
  } catch (e) {
    user.is_active = !user.is_active // 回滚开关状态
    ElMessage.error(getErrorMessage(e, '状态更新失败'))
  }
}

onMounted(refreshData)
</script>

<style scoped>
.stat-grid--flush {
  margin-bottom: 0;
}

.user-search {
  width: 240px;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.module-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  font: inherit;
  text-align: left;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.module-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(15, 23, 42, 0.06);
}

.module-card:focus-visible {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.module-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  color: var(--primary);
  background: var(--primary-light);
  border-radius: var(--radius-md);
}

.module-info {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.module-name {
  font-size: var(--font-md);
  font-weight: 600;
  color: var(--text-primary);
}

.module-desc {
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.module-arrow {
  font-size: 16px;
  color: var(--text-tertiary);
  transition: transform 0.2s ease, color 0.2s ease;
}

.module-card:hover .module-arrow {
  color: var(--primary);
  transform: translateX(2px);
}

@media (max-width: 768px) {
  .module-grid {
    grid-template-columns: minmax(0, 1fr);
  }

  .user-search {
    width: 100%;
  }
}

@media (prefers-reduced-motion: reduce) {
  .module-card,
  .module-arrow {
    transition: none;
  }
}
</style>
