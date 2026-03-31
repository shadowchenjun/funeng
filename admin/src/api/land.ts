import request from '../utils/request'
import type { LandParcel, PageResponse } from '../types'

export const landApi = {
  getParcels(params?: {
    status?: string
    type?: string
    keyword?: string
    page?: number
    page_size?: number
  }) {
    return request.get<PageResponse<LandParcel>>('/admin/land/parcels', { params })
  },

  getParcel(id: number) {
    return request.get(`/admin/land/parcels/${id}`)
  },

  createParcel(data: {
    name: string
    code: string
    area: number
    location?: string
    type?: string
    description?: string
    image_url?: string
  }) {
    return request.post('/admin/land/parcels', data)
  },

  updateParcel(id: number, data: Partial<{
    name: string
    area: number
    location: string
    type: string
    description: string
    image_url: string
    status: string
  }>) {
    return request.put(`/admin/land/parcels/${id}`, data)
  },

  deleteParcel(id: number) {
    return request.delete(`/admin/land/parcels/${id}`)
  },

  // 租地订单
  getRentalOrders(params?: {
    status?: string
    user_id?: number
    land_parcel_id?: number
    start_date?: string
    end_date?: string
    page?: number
    page_size?: number
  }) {
    return request.get<PageResponse<any>>('/admin/land/rental-orders', { params })
  },

  getRentalOrder(id: number) {
    return request.get(`/admin/land/rental-orders/${id}`)
  },

  updateRentalStatus(id: number, status: string, remark?: string) {
    return request.put(`/admin/land/rental-orders/${id}/status`, { status, remark })
  }
}
