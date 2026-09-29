import request from '../utils/request'
import type { CreatedResponse, DeviceType, Device, MessageResponse, PageResponse } from '../types'

/** 设备管理 API（/api/admin/device/*），写接口以 JSON body 提交。 */
export const deviceApi = {
  // 设备类型
  getTypes() {
    return request.get<DeviceType[]>('/admin/device/types')
  },

  createType(data: { name: string; code: string; icon?: string; description?: string; specifications?: object }) {
    return request.post<CreatedResponse>('/admin/device/types', data)
  },

  deleteType(id: number) {
    return request.delete<MessageResponse>(`/admin/device/types/${id}`)
  },

  // 设备
  getDevices(params?: {
    device_type_id?: number
    land_parcel_id?: number
    status?: string
    keyword?: string
    page?: number
    page_size?: number
  }) {
    return request.get<PageResponse<Device>>('/admin/device/devices', { params })
  },

  getDevice(id: number) {
    return request.get<Device>(`/admin/device/devices/${id}`)
  },

  createDevice(data: {
    name: string
    code: string
    device_type_id: number
    location?: string
    land_parcel_id?: number
    firmware_version?: string
  }) {
    return request.post<CreatedResponse>('/admin/device/devices', data)
  },

  updateDevice(id: number, data: Partial<{
    name: string
    location: string
    land_parcel_id: number
    firmware_version: string
    status: string
  }>) {
    return request.put<MessageResponse>(`/admin/device/devices/${id}`, data)
  },

  deleteDevice(id: number) {
    return request.delete<MessageResponse>(`/admin/device/devices/${id}`)
  }
}
