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

export const dashboardApi = {
  getStats() {
    return request.get<DashboardStats>('/admin/dashboard/stats')
  },

  getCharts(days: number = 7) {
    return request.get<ChartData>('/admin/dashboard/charts', { params: { days } })
  },

  getRecentOrders(limit: number = 10) {
    return request.get('/admin/dashboard/recent-orders', { params: { limit } })
  }
}
