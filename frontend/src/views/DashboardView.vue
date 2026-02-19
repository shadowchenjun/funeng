<template>
  <div class="dashboard-container">
    <div class="header">
      <h2>📊 数据仪表盘</h2>
      <el-button type="primary" @click="refreshData">
        刷新数据
      </el-button>
    </div>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card class="stat-card" :style="{ borderLeft: `4px solid ${stat.color}` }">
          <div class="stat-icon">
            <el-icon :size="40" :color="stat.color">
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stat-info">
            <h3>{{ stat.value }}</h3>
            <p>{{ stat.title }}</p>
            <span :class="['trend', stat.trend > 0 ? 'up' : 'down']">
              {{ stat.trend > 0 ? '↑' : '↓' }} {{ Math.abs(stat.trend) }}% 较上周
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-section">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <h3>📈 销售趋势</h3>
          </template>
          <div class="chart-placeholder">
            <el-table :data="salesData" style="width: 100%">
              <el-table-column prop="month" label="月份" />
              <el-table-column prop="sales" label="销售额 (万元)" />
              <el-table-column prop="orders" label="订单数" />
            </el-table>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <h3>🥧 产品分类占比</h3>
          </template>
          <div class="chart-placeholder">
            <el-table :data="categoryData" style="width: 100%">
              <el-table-column prop="name" label="分类" />
              <el-table-column prop="percentage" label="占比" />
              <el-table-column prop="amount" label="销售额 (万元)" />
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 最近订单 -->
    <el-card class="recent-orders">
      <template #header>
        <h3>📋 最近订单</h3>
      </template>
      <el-table :data="recentOrders" style="width: 100%">
        <el-table-column prop="id" label="订单号" width="120" />
        <el-table-column prop="customer" label="客户" />
        <el-table-column prop="product" label="产品" />
        <el-table-column prop="amount" label="金额">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: bold;">¥{{ row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="date" label="日期" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { 
  DataAnalysis, 
  ShoppingCart, 
  Money, 
  User 
} from '@element-plus/icons-vue'

const stats = ref([
  { title: '总销售额', value: '¥128.5万', icon: Money, color: '#67c23a', trend: 12.5 },
  { title: '订单数量', value: '3,256', icon: ShoppingCart, color: '#409eff', trend: 8.2 },
  { title: '客户数量', value: '1,028', icon: User, color: '#e6a23c', trend: 15.3 },
  { title: '转化率', value: '4.8%', icon: DataAnalysis, color: '#f56c6c', trend: -2.1 }
])

const salesData = [
  { month: '1月', sales: 18.5, orders: 420 },
  { month: '2月', sales: 22.3, orders: 512 },
  { month: '3月', sales: 25.8, orders: 589 },
  { month: '4月', sales: 28.2, orders: 645 },
  { month: '5月', sales: 33.7, orders: 780 }
]

const categoryData = [
  { name: '水果', percentage: '35%', amount: 45.0 },
  { name: '蔬菜', percentage: '28%', amount: 36.0 },
  { name: '粮食', percentage: '22%', amount: 28.3 },
  { name: '畜牧', percentage: '15%', amount: 19.2 }
]

const recentOrders = ref([
  { id: 'ORD001', customer: '张先生', product: '有机苹果 10斤', amount: 125, status: '已完成', date: '2026-02-17' },
  { id: 'ORD002', customer: '李女士', product: '新鲜胡萝卜 5斤', amount: 25, status: '配送中', date: '2026-02-17' },
  { id: 'ORD003', customer: '王先生', product: '散养土鸡 2只', amount: 180, status: '待发货', date: '2026-02-16' },
  { id: 'ORD004', customer: '赵女士', product: '优质大米 20斤', amount: 160, status: '已完成', date: '2026-02-16' },
  { id: 'ORD005', customer: '刘先生', product: '有机西红柿 5斤', amount: 37.5, status: '已取消', date: '2026-02-15' }
])

const refreshData = () => {
  // 模拟刷新数据
}

const getStatusType = (status: string) => {
  switch (status) {
    case '已完成':
      return 'success'
    case '配送中':
      return 'warning'
    case '待发货':
      return 'info'
    case '已取消':
      return 'danger'
    default:
      return 'info'
  }
}
</script>

<style scoped>
.dashboard-container {
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
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  margin-right: 15px;
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

.stat-info .trend {
  font-size: 12px;
  margin-top: 5px;
  display: inline-block;
}

.trend.up {
  color: #67c23a;
}

.trend.down {
  color: #f56c6c;
}

.charts-section {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
}

.chart-card h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.chart-placeholder {
  min-height: 200px;
}

.recent-orders {
  border-radius: 12px;
}

.recent-orders h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}
</style>
