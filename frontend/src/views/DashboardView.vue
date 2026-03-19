<template>
  <div class="dashboard-container">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">📊 数据仪表盘</h1>
        <p class="page-subtitle">实时监控业务数据，了解整体运营状况</p>
      </div>
      <div class="header-right">
        <button class="btn-refresh" @click="refreshData">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
          </svg>
          刷新数据
        </button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div
        v-for="(stat, index) in stats"
        :key="stat.title"
        class="stat-card"
        :style="{ '--accent': stat.color, '--delay': `${index * 0.1}s` }"
      >
        <div class="stat-card-glow"></div>
        <div class="stat-card-content">
          <div class="stat-icon-wrapper">
            <el-icon :size="28" :color="stat.color">
              <component :is="stat.icon" />
            </el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ stat.value }}</span>
            <span class="stat-title">{{ stat.title }}</span>
            <span :class="['stat-trend', stat.trend >= 0 ? 'up' : 'down']">
              <svg v-if="stat.trend >= 0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 15l-6-6-6 6"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M6 9l6 6 6-6"/>
              </svg>
              {{ Math.abs(stat.trend) }}% 较上周
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">📈 销售趋势</h3>
          <div class="chart-actions">
            <button class="chart-btn active">月度</button>
            <button class="chart-btn">季度</button>
          </div>
        </div>
        <div class="chart-body">
          <el-table :data="salesData" style="width: 100%" :header-cell-style="{ background: '#F8FAFC', color: '#475569' }">
            <el-table-column prop="month" label="月份" width="120" />
            <el-table-column prop="sales" label="销售额 (万元)" />
            <el-table-column prop="orders" label="订单数" />
            <el-table-column label="趋势">
              <template #default="{ row }">
                <span :class="['mini-trend', row.sales >= 20 ? 'up' : 'down']">
                  {{ row.sales >= 20 ? '📈' : '📉' }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">🥧 产品分类占比</h3>
        </div>
        <div class="chart-body">
          <el-table :data="categoryData" style="width: 100%" :header-cell-style="{ background: '#F8FAFC', color: '#475569' }">
            <el-table-column prop="name" label="分类" />
            <el-table-column prop="percentage" label="占比" width="100" />
            <el-table-column prop="amount" label="销售额 (万元)" />
            <el-table-column label="趋势">
              <template #default="{ row }">
                <span class="category-bar">
                  <span class="category-fill" :style="{ width: row.percentage, background: row.color }"></span>
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>

    <!-- 最近订单 -->
    <div class="orders-section">
      <div class="section-header">
        <h3 class="section-title">📋 最近订单</h3>
        <router-link to="/products" class="section-link">
          查看全部
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </router-link>
      </div>
      <div class="orders-card">
        <el-table :data="recentOrders" style="width: 100%" :header-cell-style="{ background: '#F8FAFC', color: '#475569' }">
          <el-table-column prop="id" label="订单号" width="120" />
          <el-table-column prop="customer" label="客户" />
          <el-table-column prop="product" label="产品" />
          <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">
              <span class="amount-value">¥{{ row.amount }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <span :class="['status-badge', `status-${row.statusType}`]">
                {{ row.status }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="日期" width="120" />
        </el-table>
      </div>
    </div>
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
  { title: '总销售额', value: '¥128.5万', icon: Money, color: '#10B981', trend: 12.5 },
  { title: '订单数量', value: '3,256', icon: ShoppingCart, color: '#3B82F6', trend: 8.2 },
  { title: '客户数量', value: '1,028', icon: User, color: '#F59E0B', trend: 15.3 },
  { title: '转化率', value: '4.8%', icon: DataAnalysis, color: '#EF4444', trend: -2.1 }
])

const salesData = [
  { month: '1月', sales: 18.5, orders: 420 },
  { month: '2月', sales: 22.3, orders: 512 },
  { month: '3月', sales: 25.8, orders: 589 },
  { month: '4月', sales: 28.2, orders: 645 },
  { month: '5月', sales: 33.7, orders: 780 }
]

const categoryData = [
  { name: '水果', percentage: '35%', amount: 45.0, color: '#10B981' },
  { name: '蔬菜', percentage: '28%', amount: 36.0, color: '#3B82F6' },
  { name: '粮食', percentage: '22%', amount: 28.3, color: '#F59E0B' },
  { name: '畜牧', percentage: '15%', amount: 19.2, color: '#8B5CF6' }
]

const recentOrders = ref([
  { id: 'ORD001', customer: '张先生', product: '有机苹果 10斤', amount: 125, status: '已完成', statusType: 'success', date: '2026-02-17' },
  { id: 'ORD002', customer: '李女士', product: '新鲜胡萝卜 5斤', amount: 25, status: '配送中', statusType: 'warning', date: '2026-02-17' },
  { id: 'ORD003', customer: '王先生', product: '散养土鸡 2只', amount: 180, status: '待发货', statusType: 'info', date: '2026-02-16' },
  { id: 'ORD004', customer: '赵女士', product: '优质大米 20斤', amount: 160, status: '已完成', statusType: 'success', date: '2026-02-16' },
  { id: 'ORD005', customer: '刘先生', product: '有机西红柿 5斤', amount: 37.5, status: '已取消', statusType: 'danger', date: '2026-02-15' }
])

const refreshData = () => {
  // 模拟刷新数据
}
</script>

<style scoped>
.dashboard-container {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  background: var(--bg-secondary, #F8FAFC);
  min-height: calc(100vh - 64px);
}

/* ========== 页面头部 ========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #0F172A);
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 15px;
  color: var(--text-secondary, #475569);
  margin: 0;
}

.btn-refresh {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary, #475569);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-refresh:hover {
  border-color: var(--primary, #165DFF);
  color: var(--primary, #165DFF);
}

.btn-refresh svg {
  width: 16px;
  height: 16px;
}

/* ========== 统计卡片 ========== */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 16px;
  padding: 24px;
  overflow: hidden;
  transition: all 0.3s ease;
  animation: fadeInUp 0.5s ease forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: var(--accent);
}

.stat-card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.stat-card:hover .stat-card-glow {
  transform: scaleX(1);
}

.stat-card-content {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.stat-icon-wrapper {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary, #F8FAFC);
  border-radius: 12px;
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #0F172A);
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.stat-title {
  font-size: 14px;
  color: var(--text-secondary, #475569);
  margin: 4px 0 8px 0;
}

.stat-trend {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.stat-trend svg {
  width: 14px;
  height: 14px;
}

.stat-trend.up {
  color: #10B981;
}

.stat-trend.down {
  color: #EF4444;
}

/* ========== 图表区域 ========== */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 16px;
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #E2E8F0);
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #0F172A);
  margin: 0;
}

.chart-actions {
  display: flex;
  gap: 4px;
}

.chart-btn {
  padding: 6px 12px;
  border: none;
  background: transparent;
  font-size: 13px;
  color: var(--text-secondary, #475569);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chart-btn:hover {
  background: var(--bg-secondary, #F8FAFC);
}

.chart-btn.active {
  background: var(--primary-light, rgba(22, 93, 255, 0.08));
  color: var(--primary, #165DFF);
  font-weight: 500;
}

.chart-body {
  padding: 20px 24px;
}

.mini-trend {
  font-size: 16px;
}

.category-bar {
  display: block;
  width: 60px;
  height: 6px;
  background: var(--bg-secondary, #F8FAFC);
  border-radius: 3px;
  overflow: hidden;
}

.category-fill {
  display: block;
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

/* ========== 订单区域 ========== */
.orders-section {
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 16px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #E2E8F0);
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary, #0F172A);
  margin: 0;
}

.section-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  color: var(--primary, #165DFF);
  text-decoration: none;
  transition: gap 0.2s ease;
}

.section-link:hover {
  gap: 10px;
}

.section-link svg {
  width: 16px;
  height: 16px;
}

.orders-card {
  padding: 0;
}

.amount-value {
  font-weight: 600;
  color: #EF4444;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 500;
}

.status-success {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.status-warning {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.status-info {
  background: rgba(59, 130, 246, 0.1);
  color: #3B82F6;
}

.status-danger {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

/* ========== 响应式 ========== */
@media (max-width: 1200px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 20px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .stat-grid {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
