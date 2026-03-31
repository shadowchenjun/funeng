<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { dashboardApi } from '../../api/dashboard'
import type { DashboardStats } from '../../types'
import * as echarts from 'echarts'

const stats = ref<DashboardStats | null>(null)
const chartRef = ref<HTMLDivElement>()
const revenueChartRef = ref<HTMLDivElement>()
const pieChartRef = ref<HTMLDivElement>()

const loading = ref(true)

const fetchStats = async () => {
  try {
    const [statsRes, chartsRes] = await Promise.all([
      dashboardApi.getStats(),
      dashboardApi.getCharts(7)
    ])
    stats.value = statsRes
    renderOrderChart(chartsRes.daily_orders)
    renderRevenueChart(chartsRes.daily_revenue)
    renderPieChart(chartsRes)
  } finally {
    loading.value = false
  }
}

const renderOrderChart = (data: any[]) => {
  if (!chartRef.value) return
  const chart = echarts.init(chartRef.value)
  chart.setOption({
    title: { text: '每日订单量', textStyle: { fontSize: 14, fontWeight: 'normal' }, left: 'center', top: 10 },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 10, data: ['认养订单', '租地订单'] },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)), axisLine: { lineStyle: { color: '#e0e0e0' } } },
    yAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#f0f0f0' } } },
    series: [
      { name: '认养订单', type: 'bar', data: data.map(d => d.adoption), itemStyle: { color: '#409eff' }, barWidth: '35%' },
      { name: '租地订单', type: 'bar', data: data.map(d => d.rental), itemStyle: { color: '#67c23a' }, barWidth: '35%' }
    ],
    grid: { top: 50, bottom: 50, left: 50, right: 20 }
  })
}

const renderRevenueChart = (data: any[]) => {
  if (!revenueChartRef.value) return
  const chart = echarts.init(revenueChartRef.value)
  chart.setOption({
    title: { text: '每日收入趋势', textStyle: { fontSize: 14, fontWeight: 'normal' }, left: 'center', top: 10 },
    tooltip: { trigger: 'axis' },
    legend: { bottom: 10, data: ['认养收入', '租地收入'] },
    xAxis: { type: 'category', data: data.map(d => d.date.slice(5)), axisLine: { lineStyle: { color: '#e0e0e0' } } },
    yAxis: { type: 'value', name: '金额(元)', axisLine: { show: false }, splitLine: { lineStyle: { color: '#f0f0f0' } } },
    series: [
      { name: '认养收入', type: 'line', smooth: true, data: data.map(d => d.adoption), itemStyle: { color: '#409eff' }, areaStyle: { color: 'rgba(64, 158, 255, 0.1)' } },
      { name: '租地收入', type: 'line', smooth: true, data: data.map(d => d.rental), itemStyle: { color: '#67c23a' }, areaStyle: { color: 'rgba(103, 194, 58, 0.1)' } }
    ],
    grid: { top: 50, bottom: 50, left: 60, right: 20 }
  })
}

const renderPieChart = (data: any) => {
  if (!pieChartRef.value) return
  const chart = echarts.init(pieChartRef.value)
  chart.setOption({
    title: { text: '土地状态分布', textStyle: { fontSize: 14, fontWeight: 'normal' }, left: 'center', top: 10 },
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 10 },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {c}' },
      data: data.land_usage.map((item: any, index: number) => ({
        name: item.status === 'available' ? '可用' : item.status === 'rented' ? '已租用' : item.status,
        value: item.count,
        itemStyle: { color: ['#67c23a', '#e6a23c', '#909399'][index] || '#409eff' }
      }))
    }]
  })
}

onMounted(fetchStats)
</script>

<template>
  <div class="dashboard" v-loading="loading">
    <el-row :gutter="24" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-user">
          <div class="stat-item">
            <div class="stat-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats?.users.total || 0 }}</div>
              <div class="stat-label">用户总数</div>
              <div class="stat-tips">今日+{{ stats?.users.new_today || 0 }} | 本月+{{ stats?.users.new_month || 0 }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-land">
          <div class="stat-item">
            <div class="stat-icon">
              <el-icon><MapLocation /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats?.land.total || 0 }}</div>
              <div class="stat-label">土地总数</div>
              <div class="stat-tips">可用 {{ stats?.land.available || 0 }} 块</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-adoption">
          <div class="stat-item">
            <div class="stat-icon">
              <el-icon><Crop /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats?.adoption_orders.active || 0 }}</div>
              <div class="stat-label">活跃认养</div>
              <div class="stat-tips">待处理 {{ stats?.adoption_orders.pending || 0 }} 单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-device">
          <div class="stat-item">
            <div class="stat-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats?.devices.online || 0 }} / {{ stats?.devices.total || 0 }}</div>
              <div class="stat-label">设备在线</div>
              <div class="stat-tips">离线 {{ stats?.devices.offline || 0 }} 台</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="charts-row">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <div ref="chartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <div ref="revenueChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="24" class="charts-row">
      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <div ref="pieChartRef" style="height: 280px"></div>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card shadow="hover" class="quick-card">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" plain class="quick-btn">认养订单</el-button>
            <el-button type="success" plain class="quick-btn">租地订单</el-button>
            <el-button type="warning" plain class="quick-btn">土地分配</el-button>
            <el-button type="danger" plain class="quick-btn">设备管理</el-button>
            <el-button type="info" plain class="quick-btn">溯源管理</el-button>
            <el-button type="danger" plain class="quick-btn">优惠券</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-row {
  margin-bottom: 24px;
}

.charts-row {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.stat-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 28px;
}

.stat-user .stat-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
}

.stat-land .stat-icon {
  background: linear-gradient(135deg, #67c23a 0%, #95d475 100%);
  color: #fff;
}

.stat-adoption .stat-icon {
  background: linear-gradient(135deg, #e6a23c 0%, #f3d19e 100%);
  color: #fff;
}

.stat-device .stat-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #fab6b6 100%);
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.stat-tips {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

.chart-card {
  border-radius: 12px;
  border: none;
}

.quick-card {
  border-radius: 12px;
  border: none;
  height: 100%;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.quick-btn {
  border-radius: 20px;
  padding: 8px 20px;
}
</style>
