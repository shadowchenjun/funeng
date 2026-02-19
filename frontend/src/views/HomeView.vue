<template>
  <div class="home-container">
    <div class="hero-section">
      <h1>🌾 现代农业赋能平台</h1>
      <p>智能管理 · 高效运营 · 助力农业现代化</p>
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="$router.push('/login')">
          立即开始
        </el-button>
        <el-button size="large" @click="$router.push('/products')">
          浏览产品
        </el-button>
      </div>
    </div>
    
    <!-- 核心模块导航 -->
    <div class="modules-section">
      <h2>核心功能模块</h2>
      <el-row :gutter="20">
        <el-col :span="6" v-for="module in modules" :key="module.name">
          <el-card class="module-card" @click="goToModule(module.path)">
            <div class="module-icon">
              <el-icon :size="48" :color="module.color">
                <component :is="module.icon" />
              </el-icon>
            </div>
            <h3>{{ module.name }}</h3>
            <p>{{ module.description }}</p>
            <el-tag size="small" :type="module.auth ? 'warning' : 'success'">
              {{ module.auth ? '需登录' : '公开' }}
            </el-tag>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <div class="features-section">
      <h2>平台特色</h2>
      <el-row :gutter="20">
        <el-col :span="8" v-for="feature in features" :key="feature.title">
          <el-card class="feature-card">
            <el-icon :size="48" :color="feature.color">
              <component :is="feature.icon" />
            </el-icon>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 统计数据 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6" v-for="stat in stats" :key="stat.label">
          <div class="stat-item">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-label">{{ stat.label }}</span>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { 
  DataAnalysis, 
  Box, 
  TrendCharts,
  Management,
  ShoppingCart,
  UserFilled,
  Coin,
  Van,
  SetUp,
  Sell,
  ColdDrink,
  Wallet
} from '@element-plus/icons-vue'

const modules = [
  {
    name: '智慧农业',
    description: '土壤监测、气象数据、智能灌溉、病虫害预警',
    icon: SetUp,
    color: '#67C23A',
    path: '/smart-agriculture',
    auth: true
  },
  {
    name: '数字营销',
    description: '电商管理、直播带货、会员系统、营销活动',
    icon: Sell,
    color: '#E6A23C',
    path: '/digital-marketing',
    auth: true
  },
  {
    name: '数字冷链',
    description: '温度监控、运输追踪、仓储管理、质量追溯',
    icon: ColdDrink,
    color: '#409EFF',
    path: '/cold-chain',
    auth: true
  },
  {
    name: '供应链金融',
    description: '订单融资、应收账款、农业保险、信用评估',
    icon: Wallet,
    color: '#F56C6C',
    path: '/supply-chain-finance',
    auth: true
  }
]

const features = [
  {
    icon: DataAnalysis,
    title: '智能数据分析',
    description: '实时监控销售数据，智能分析市场趋势',
    color: '#409EFF'
  },
  {
    icon: Box,
    title: '产品管理',
    description: '高效管理农产品信息，支持批量操作',
    color: '#67C23A'
  },
  {
    icon: TrendCharts,
    title: '销售追踪',
    description: '完整的销售记录，精准的库存预测',
    color: '#E6A23C'
  },
  {
    icon: Management,
    title: '分类系统',
    description: '灵活的产品分类，支持多级分类',
    color: '#909399'
  },
  {
    icon: ShoppingCart,
    title: '订单处理',
    description: '快速处理订单，提升客户满意度',
    color: '#F56C6C'
  },
  {
    icon: UserFilled,
    title: '用户管理',
    description: '完善的权限系统，支持角色分配',
    color: '#409EFF'
  }
]

const stats = [
  { value: '1,028', label: '注册用户' },
  { value: '3,256', label: '订单数量' },
  { value: '¥128.5万', label: '总销售额' },
  { value: '156', label: '在售商品' }
]

const goToModule = (path: string) => {
  // 检查是否已登录
  const token = localStorage.getItem('token')
  if (!token) {
    // 未登录，跳转到登录页面
    window.location.href = '/login'
    return
  }
  window.location.href = path
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
}

.hero-section {
  text-align: center;
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.hero-section h1 {
  font-size: 42px;
  margin-bottom: 15px;
  font-weight: 700;
}

.hero-section p {
  font-size: 20px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.action-buttons .el-button {
  margin: 0 10px;
  padding: 18px 36px;
  font-size: 16px;
}

.modules-section {
  padding: 50px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.modules-section h2 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 30px;
  color: #303133;
}

.module-card {
  text-align: center;
  padding: 30px 20px;
  margin-bottom: 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.module-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.module-icon {
  margin-bottom: 15px;
}

.module-card h3 {
  margin: 10px 0;
  font-size: 20px;
  color: #303133;
}

.module-card p {
  margin: 10px 0;
  color: #909399;
  font-size: 14px;
  min-height: 40px;
}

.features-section {
  padding: 50px 40px;
  background: #f5f7fa;
  max-width: 1400px;
  margin: 0 auto;
}

.features-section h2 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 30px;
  color: #303133;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
  margin-bottom: 20px;
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.feature-card h3 {
  margin: 20px 0 10px;
  font-size: 20px;
  color: #303133;
}

.feature-card p {
  color: #909399;
  font-size: 14px;
}

.stats-section {
  padding: 50px 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  max-width: 1400px;
  margin: 0 auto;
  border-radius: 0;
}

.stat-item {
  text-align: center;
  color: white;
}

.stat-value {
  display: block;
  font-size: 36px;
  font-weight: bold;
}

.stat-label {
  font-size: 16px;
  opacity: 0.9;
}
</style>
