<template>
  <div class="admin-container">
    <div class="header">
      <h2>⚙️ 管理后台</h2>
      <el-button type="primary" @click="refreshData">
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
          <el-button type="primary" size="small">添加用户</el-button>
        </div>
      </template>
      <el-table :data="users" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'success'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-switch 
              v-model="row.status" 
              active-text="启用" 
              inactive-text="禁用"
              @change="handleStatusChange(row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="注册时间" />
        <el-table-column label="操作" width="150">
          <template #default="">
            <el-button type="primary" link>编辑</el-button>
            <el-button type="danger" link>删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 系统设置 -->
    <el-card class="section-card">
      <template #header>
        <h3>🔧 系统设置</h3>
      </template>
      <el-form :model="systemSettings" label-width="150px">
        <el-form-item label="系统名称">
          <el-input v-model="systemSettings.systemName" />
        </el-form-item>
        <el-form-item label="系统描述">
          <el-input v-model="systemSettings.systemDesc" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="维护模式">
          <el-switch v-model="systemSettings.maintenanceMode" active-text="开启" inactive-text="关闭" />
        </el-form-item>
        <el-form-item label="用户注册">
          <el-switch v-model="systemSettings.allowRegister" active-text="允许" inactive-text="禁止" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
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

const stats = ref([
  { title: '总用户数', value: '1,028', color: '#409EFF' },
  { title: '活跃用户', value: '856', color: '#67C23A' },
  { title: '管理员', value: '5', color: '#E6A23C' },
  { title: '总订单', value: '3,256', color: '#F56C6C' }
])

const users = ref([
  { id: 1, username: 'admin', email: 'admin@funeng.com', role: 'admin', status: true, createdAt: '2026-01-01' },
  { id: 2, username: 'zhangsan', email: 'zhangsan@example.com', role: 'user', status: true, createdAt: '2026-01-15' },
  { id: 3, username: 'lisi', email: 'lisi@example.com', role: 'user', status: true, createdAt: '2026-02-01' },
  { id: 4, username: 'wangwu', email: 'wangwu@example.com', role: 'user', status: false, createdAt: '2026-02-10' }
])

const systemSettings = reactive({
  systemName: '现代农业赋能平台',
  systemDesc: '专业的农产品管理和销售平台',
  maintenanceMode: false,
  allowRegister: true
})

const refreshData = () => {
  ElMessage.success('数据已刷新')
}

const handleStatusChange = (user: any) => {
  ElMessage.success(`用户 ${user.username} 状态已更新`)
}

const saveSettings = () => {
  ElMessage.success('系统设置已保存')
}
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
