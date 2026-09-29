import request from '../utils/request'
import type { DashboardStats } from '../types'

export interface ChartData {
  daily_orders: Array<{
    date: string
    adoption: number
    rental: number
    total: number
  }>
  daily_revenue: Array<{
    date: string
    adoption: number
    rental: number
    total: number
  }>
  land_usage: Array<{ status: string; count: number }>
  device_status: Array<{ status: string; count: number }>
  category_data: Array<{ name: string; count: number }>
}

export interface RecentOrderItem {
  id: number
  order_no: string
  user: string
  total_amount: number
  status: string
  created_at: string
}

export interface RecentOrders {
  adoption_orders: RecentOrderItem[]
  rental_orders: RecentOrderItem[]
}

/** 数据看板 API（/api/admin/dashboard/*） */
export const dashboardApi = {
  getStats() {
    return request.get<DashboardStats>('/admin/dashboard/stats')
  },

  getCharts(days: number = 7) {
    return request.get<ChartData>('/admin/dashboard/charts', { params: { days } })
  },

  getRecentOrders(limit: number = 10) {
    return request.get<RecentOrders>('/admin/dashboard/recent-orders', { params: { limit } })
  }
}
