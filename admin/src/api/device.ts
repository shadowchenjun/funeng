import request from '../utils/request'
import type { DeviceType, Device, PageResponse } from '../types'

export const deviceApi = {
  // 设备类型
  getTypes() {
    return request.get<DeviceType[]>('/admin/device/types')
  },

  createType(data: { name: string; code: string; icon?: string; description?: string }) {
    return request.post('/admin/device/types', data)
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
    return request.post('/admin/device/devices', data)
  }
}
