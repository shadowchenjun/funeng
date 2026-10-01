<template>
  <div class="page-container">
    <PageHeader title="数据看板" subtitle="实时监控业务数据，了解整体运营状况">
      <template #actions>
        <el-button :icon="Refresh" :loading="loading" @click="refreshData">刷新数据</el-button>
      </template>
    </PageHeader>

    <div class="stat-grid" v-loading="loading">
      <StatCard
        v-for="stat in stats"
        :key="stat.title"
        :value="stat.value"
        :title="stat.title"
        :type="stat.type"
        :icon="stat.icon"
      />
    </div>

    <div class="section-stack">
      <div class="section-split">
        <SectionCard title="库存预警" :icon="Warning" no-padding>
          <el-table :data="lowStockProducts" v-loading="loading" empty-text="暂无库存不足的产品">
            <el-table-column prop="name" label="产品" min-width="120" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="stock" label="库存" width="100">
              <template #default="{ row }">
                <el-tag :type="row.stock === 0 ? 'danger' : 'warning'">{{ row.stock }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </SectionCard>

        <SectionCard title="产品分类占比" :icon="PieChart" no-padding>
          <el-table :data="categoryData" v-loading="loading" empty-text="暂无分类数据">
            <el-table-column prop="name" label="分类" min-width="100" />
            <el-table-column prop="percentage" label="占比" width="80" />
            <el-table-column prop="count" label="产品数" width="80" />
            <el-table-column label="分布" min-width="120">
              <template #default="{ row }">
                <span class="category-bar">
                  <span class="category-fill" :style="{ width: row.percentage }"></span>
                </span>
              </template>
            </el-table-column>
          </el-table>
        </SectionCard>
      </div>

      <SectionCard title="最新上架产品" :icon="Goods" no-padding>
        <template #extra>
          <router-link to="/products" class="section-link">
            查看全部 <el-icon><ArrowRight /></el-icon>
          </router-link>
        </template>
        <el-table :data="recentProducts" v-loading="loading" empty-text="暂无产品">
          <el-table-column prop="id" label="编号" width="100" />
          <el-table-column prop="name" label="产品" min-width="140" />
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
      </SectionCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, markRaw } from 'vue'
import type { Component } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ArrowRight, Box, Goods, Menu, Money, PieChart, Refresh, Warning } from '@element-plus/icons-vue'
import { formatMoneyCompact } from '../utils/format'

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

interface DashboardStat {
  title: string
  value: string
  type: 'primary'
  icon: Component
}

interface CategoryRow {
  name: string
  count: number
  percentage: string
}

const loading = ref(false)
const stats = ref<DashboardStat[]>([])
const categoryData = ref<CategoryRow[]>([])
const recentProducts = ref<RecentProduct[]>([])
const lowStockProducts = ref<LowStockProduct[]>([])


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
      { title: '产品总数', value: data.total_products.toLocaleString(), type: 'primary', icon: markRaw(Goods) },
      { title: '分类数量', value: data.total_categories.toLocaleString(), type: 'primary', icon: markRaw(Menu) },
      { title: '总库存', value: data.total_stock.toLocaleString(), type: 'primary', icon: markRaw(Box) },
      { title: '库存总价值', value: formatMoneyCompact(data.total_value), type: 'primary', icon: markRaw(Money) }
    ]
    const totalCount = data.category_stats.reduce((sum, c) => sum + c.count, 0)
    categoryData.value = data.category_stats.map((c) => ({
      name: c.name,
      count: c.count,
      percentage: totalCount ? `${Math.round((c.count / totalCount) * 100)}%` : '0%'
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
.section-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-sm);
  font-weight: 500;
  color: var(--primary);
  text-decoration: none;
}

.section-link:hover {
  color: var(--primary-dark);
}

.amount-value {
  font-weight: 600;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.category-bar {
  display: block;
  width: 100%;
  height: 6px;
  overflow: hidden;
  background: var(--bg-tertiary);
  border-radius: var(--radius-pill);
}

.category-fill {
  display: block;
  height: 100%;
  background: var(--primary);
  border-radius: var(--radius-pill);
}
</style>
