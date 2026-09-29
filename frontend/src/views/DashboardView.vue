<template>
  <div class="dashboard-container">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">📊 数据仪表盘</h1>
        <p class="page-subtitle">实时监控业务数据，了解整体运营状况</p>
      </div>
      <div class="header-right">
        <button class="btn-refresh" :disabled="loading" @click="refreshData">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M23 4v6h-6M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
          </svg>
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
      </div>
    </header>

    <!-- 统计卡片 -->
    <div class="stat-grid" v-loading="loading">
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
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <div class="chart-card">
        <div class="chart-header">
          <h3 class="chart-title">⚠️ 库存预警</h3>
        </div>
        <div class="chart-body">
          <el-table
            :data="lowStockProducts"
            v-loading="loading"
            empty-text="暂无库存不足的产品"
            style="width: 100%"
            :header-cell-style="{ background: '#F8FAFC', color: '#475569' }"
          >
            <el-table-column prop="name" label="产品" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="stock" label="库存" width="100">
              <template #default="{ row }">
                <span :class="['status-badge', row.stock === 0 ? 'status-danger' : 'status-warning']">
                  {{ row.stock }}
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
          <el-table
            :data="categoryData"
            v-loading="loading"
            empty-text="暂无分类数据"
            style="width: 100%"
            :header-cell-style="{ background: '#F8FAFC', color: '#475569' }"
          >
            <el-table-column prop="name" label="分类" />
            <el-table-column prop="percentage" label="占比" width="100" />
            <el-table-column prop="count" label="产品数" />
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

    <!-- 最新产品 -->
    <div class="orders-section">
      <div class="section-header">
        <h3 class="section-title">📋 最新上架产品</h3>
        <router-link to="/products" class="section-link">
          查看全部
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </router-link>
      </div>
      <div class="orders-card">
        <el-table
          :data="recentProducts"
          v-loading="loading"
          empty-text="暂无产品"
          style="width: 100%"
          :header-cell-style="{ background: '#F8FAFC', color: '#475569' }"
        >
          <el-table-column prop="id" label="编号" width="100" />
          <el-table-column prop="name" label="产品" />
          <el-table-column prop="price" label="价格" width="120">
            <template #default="{ row }">
              <span class="amount-value">¥{{ row.price }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="stock" label="库存" width="100" />
          <el-table-column label="上架时间" width="140">
            <template #default="{ row }">{{ row.created_at.slice(0, 10) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, markRaw } from 'vue'
import type { Component } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import {
  Goods,
  Menu,
  Box,
  Money
} from '@element-plus/icons-vue'

interface DashboardStats {
  total_products: number
  total_categories: number
  total_stock: number
  total_value: number
  category_stats: { name: string; count: number }[]
}

interface RecentProduct {
  id: number
  name: string
  price: number
  stock: number
  created_at: string
}

interface LowStockProduct {
  id: number
  name: string
  stock: number
  category: string
}

interface StatCard {
  title: string
  value: string
  icon: Component
  color: string
}

interface CategoryRow {
  name: string
  count: number
  percentage: string
  color: string
}

const CATEGORY_COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#8B5CF6', '#EF4444', '#06B6D4']

const loading = ref(false)
const stats = ref<StatCard[]>([])
const categoryData = ref<CategoryRow[]>([])
const recentProducts = ref<RecentProduct[]>([])
const lowStockProducts = ref<LowStockProduct[]>([])

const formatValue = (value: number) =>
  value >= 10000 ? `¥${(value / 10000).toFixed(1)}万` : `¥${value.toLocaleString()}`

const fetchData = async () => {
  loading.value = true
  try {
    const [statsRes, recentRes, lowStockRes] = await Promise.all([
      axios.get<DashboardStats>('/api/dashboard/stats'),
      axios.get<RecentProduct[]>('/api/dashboard/recent-products'),
      axios.get<LowStockProduct[]>('/api/dashboard/low-stock-products')
    ])
    const data = statsRes.data
    stats.value = [
      { title: '产品总数', value: data.total_products.toLocaleString(), icon: markRaw(Goods), color: '#10B981' },
      { title: '分类数量', value: data.total_categories.toLocaleString(), icon: markRaw(Menu), color: '#3B82F6' },
      { title: '总库存', value: data.total_stock.toLocaleString(), icon: markRaw(Box), color: '#F59E0B' },
      { title: '库存总价值', value: formatValue(data.total_value), icon: markRaw(Money), color: '#EF4444' }
    ]
    const totalCount = data.category_stats.reduce((sum, c) => sum + c.count, 0)
    categoryData.value = data.category_stats.map((c, i) => ({
      name: c.name,
      count: c.count,
      percentage: totalCount ? `${Math.round((c.count / totalCount) * 100)}%` : '0%',
      color: CATEGORY_COLORS[i % CATEGORY_COLORS.length]
    }))
    recentProducts.value = recentRes.data
    lowStockProducts.value = lowStockRes.data
  } catch (e) {
    const detail = axios.isAxiosError(e) ? e.response?.data?.detail : undefined
    ElMessage.error(detail || '加载仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

const refreshData = async () => {
  await fetchData()
}

onMounted(fetchData)
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

.btn-refresh:disabled {
  cursor: not-allowed;
  opacity: 0.6;
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

.chart-body {
  padding: 20px 24px;
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
