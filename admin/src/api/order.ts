import request from '../utils/request'
import type { OrderStatus, StatusUpdateBody, AdoptionConfig, AdoptionOrder, LandParcel, OrderQuery, PageResponse, RentalOrder } from '../types'

/**
 * 订单中心 API：聚合认养订单（/admin/adoption/orders）与租地订单（/admin/land/rental-orders）。
 *
 * request 的方法直接返回后端 JSON（见 utils/request.ts）。
 * 状态更新 / 分配土地接口以 JSON body 提交：{ status, remark? } / { land_parcel_id }。
 */
export const orderApi = {
  // ============ 认养订单 ============
  getAdoptionOrders(params?: OrderQuery & { config_id?: number }) {
    return request.get<PageResponse<AdoptionOrder>>('/admin/adoption/orders', { params })
  },

  getAdoptionOrder(id: number) {
    return request.get<AdoptionOrder>(`/admin/adoption/orders/${id}`)
  },

  updateAdoptionStatus(id: number, status: OrderStatus, remark?: string) {
    const body: StatusUpdateBody = { status, remark: remark || undefined }
    return request.put<{ message: string }>(`/admin/adoption/orders/${id}/status`, body)
  },

  allocateLand(id: number, landParcelId: number) {
    return request.put<{ message: string }>(`/admin/adoption/orders/${id}/allocate`, { land_parcel_id: landParcelId })
  },

  // ============ 租地订单 ============
  getRentalOrders(params?: OrderQuery & { land_parcel_id?: number }) {
    return request.get<PageResponse<RentalOrder>>('/admin/land/rental-orders', { params })
  },

  getRentalOrder(id: number) {
    return request.get<RentalOrder>(`/admin/land/rental-orders/${id}`)
  },

  updateRentalStatus(id: number, status: OrderStatus, remark?: string) {
    const body: StatusUpdateBody = { status, remark: remark || undefined }
    return request.put<{ message: string }>(`/admin/land/rental-orders/${id}/status`, body)
  },

  // ============ 筛选项 ============
  getAdoptionConfigs() {
    return request.get<AdoptionConfig[]>('/admin/adoption/configs')
  },

  getLandParcels(params?: { status?: string; page?: number; page_size?: number }) {
    return request.get<PageResponse<LandParcel>>('/admin/land/parcels', { params })
  }
}
