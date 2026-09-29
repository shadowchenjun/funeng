<template>
  <div class="admin-container">
    <div class="header">
      <h2>⚙️ 管理后台</h2>
      <el-button type="primary" :loading="loading" @click="refreshData">
        刷新数据
      </el-button>
    </div>

    <!-- 功能模块入口 -->
    <el-card class="section-card">
      <template #header>
        <h3>📦 功能模块</h3>
      </template>
      <div class="module-grid">
        <div
          v-for="module in modules"
          :key="module.path"
          class="module-card"
          :style="{ '--accent': module.color }"
          @click="goToModule(module.path)"
        >
          <div class="module-icon" :style="{ background: `${module.color}15` }">
            <el-icon :size="28" :color="module.color">
              <component :is="module.icon" />
            </el-icon>
          </div>
          <div class="module-info">
            <h4>{{ module.name }}</h4>
            <p>{{ module.desc }}</p>
          </div>
          <el-icon class="module-arrow"><ArrowRight /></el-icon>
        </div>
      </div>
    </el-card>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card class="stat-card" :style="{ borderLeft: `4px solid ${stat.color}` }">
          <div class="stat-info">
            <h3>{{ stat.value }}</h3>
            <p>{{ stat.title }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 用户管理 -->
    <el-card class="section-card">
      <template #header>
        <div class="card-header">
          <h3>👥 用户管理</h3>
          <el-input
            v-model="search"
            placeholder="搜索用户名 / 邮箱 / 姓名"
            size="small"
            clearable
            style="width: 240px"
            @keyup.enter="fetchUsers"
            @clear="fetchUsers"
          />
        </div>
      </template>
      <el-table :data="users" v-loading="loading" empty-text="暂无用户" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_admin ? 'danger' : 'success'">
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
    </el-card>
    
    <el-alert
      type="info"
      :closable="false"
      show-icon
      title="认养、土地、设备、溯源、营销及系统配置等运营管理，请使用独立的管理后台（admin/）。"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { getErrorMessage } from '../utils/error'
import { ArrowRight, DataAnalysis, TrendCharts, Van, Wallet } from '@element-plus/icons-vue'

const router = useRouter()

const modules = [
  {
    name: '智慧农业',
    desc: '设备管理、地块管理、作物监控',
    path: '/smart-agriculture',
    icon: DataAnalysis,
    color: '#10B981'
  },
  {
    name: '数字营销',
    desc: '会员管理、营销活动',
    path: '/digital-marketing',
    icon: TrendCharts,
    color: '#8B5CF6'
  },
  {
    name: '冷链物流',
    desc: '车辆管理、仓库管理',
    path: '/cold-chain',
    icon: Van,
    color: '#3B82F6'
  },
  {
    name: '供应链金融',
    desc: '金融服务管理',
    path: '/supply-chain-finance',
    icon: Wallet,
    color: '#F59E0B'
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

const stats = ref([
  { title: '总用户数', value: '—', color: '#409EFF' },
  { title: '活跃用户', value: '—', color: '#67C23A' },
  { title: '管理员', value: '—', color: '#E6A23C' },
  { title: '总订单', value: '—', color: '#F56C6C' }
])

const formatDate = (value: string) => value.replace('T', ' ').slice(0, 19)

const fetchStats = async () => {
  const [userRes, publicRes] = await Promise.all([
    axios.get<UserStats>('/api/users/stats'),
    axios.get<{ order_count: number }>('/api/public/stats')
  ])
  const n = (v: number) => v.toLocaleString('zh-CN')
  stats.value = [
    { title: '总用户数', value: n(userRes.data.total_users), color: '#409EFF' },
    { title: '活跃用户', value: n(userRes.data.active_users), color: '#67C23A' },
    { title: '管理员', value: n(userRes.data.admin_users), color: '#E6A23C' },
    { title: '总订单', value: n(publicRes.data.order_count), color: '#F56C6C' }
  ]
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
.admin-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  font-size: 24px;
  color: #303133;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  padding: 20px;
}

.stat-info h3 {
  font-size: 28px;
  margin: 0 0 5px;
  color: #303133;
}

.stat-info p {
  margin: 0;
  color: #909399;
}

.section-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

/* 功能模块样式 */
.module-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.module-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f8fafc;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.module-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.module-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  flex-shrink: 0;
}

.module-info {
  flex: 1;
}

.module-info h4 {
  margin: 0 0 4px;
  font-size: 16px;
  color: #303133;
}

.module-info p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.module-arrow {
  color: #c0c4cc;
  font-size: 18px;
}

@media (max-width: 768px) {
  .module-grid {
    grid-template-columns: 1fr;
  }
}
</style>
