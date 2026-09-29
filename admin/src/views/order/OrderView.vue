<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orderApi } from '../../api/order'
import type { AdoptionConfig, AdoptionOrder, LandParcel, OrderStatus, RentalOrder } from '../../types'

type OrderTab = 'adoption' | 'rental'
type TagType = 'primary' | 'success' | 'warning' | 'info' | 'danger'

const activeTab = ref<OrderTab>('adoption')

// 订单状态（认养 / 租地共用）
const statusOptions: { label: string; value: string; type: TagType }[] = [
  { label: '待支付', value: 'pending', type: 'warning' },
  { label: '已支付', value: 'paid', type: 'success' },
  { label: '进行中', value: 'active', type: 'primary' },
  { label: '已完成', value: 'completed', type: 'info' },
  { label: '已取消', value: 'cancelled', type: 'danger' },
  { label: '已退款', value: 'refunded', type: 'danger' }
]

// 各状态下允许的流转操作
const statusActions: Record<string, { label: string; value: OrderStatus; danger?: boolean }[]> = {
  pending: [
    { label: '确认支付', value: 'paid' },
    { label: '取消订单', value: 'cancelled', danger: true }
  ],
  paid: [
    { label: '开始履约', value: 'active' },
    { label: '退款', value: 'refunded', danger: true }
  ],
  active: [
    { label: '完成订单', value: 'completed' },
    { label: '退款', value: 'refunded', danger: true }
  ]
}

const statusLabel = (s: string) => statusOptions.find(o => o.value === s)?.label || s
const statusType = (s: string): TagType => statusOptions.find(o => o.value === s)?.type || 'info'

const formatDate = (v?: string | null, withTime = true) => {
  if (!v) return '-'
  const text = v.replace('T', ' ').split('.')[0]
  return withTime ? text : text.slice(0, 10)
}

const formatMoney = (v?: number | null) => (v == null ? '-' : `¥${Number(v).toFixed(2)}`)

// ============ 筛选项 ============
const configs = ref<AdoptionConfig[]>([])
const parcels = ref<LandParcel[]>([])

const fetchOptions = async () => {
  try {
    const [configRes, parcelRes] = await Promise.all([
      orderApi.getAdoptionConfigs(),
      orderApi.getLandParcels({ page: 1, page_size: 100 })
    ])
    configs.value = configRes
    parcels.value = parcelRes.items
  } catch {
    // 筛选项加载失败不影响订单列表，错误提示由拦截器处理
  }
}

// ============ 认养订单 ============
const adoptionFilter = reactive({
  status: '',
  config_id: undefined as number | undefined,
  user_id: undefined as number | undefined,
  dateRange: [] as string[]
})
const adoptionPage = reactive({ page: 1, page_size: 20, total: 0 })
const adoptionOrders = ref<AdoptionOrder[]>([])
const adoptionLoading = ref(false)

const fetchAdoptionOrders = async () => {
  adoptionLoading.value = true
  try {
    const [start, end] = adoptionFilter.dateRange || []
    const res = await orderApi.getAdoptionOrders({
      status: adoptionFilter.status || undefined,
      config_id: adoptionFilter.config_id || undefined,
      user_id: adoptionFilter.user_id || undefined,
      start_date: start || undefined,
      end_date: end || undefined,
      page: adoptionPage.page,
      page_size: adoptionPage.page_size
    })
    adoptionOrders.value = res.items
    adoptionPage.total = res.total
  } catch {
    adoptionOrders.value = []
  } finally {
    adoptionLoading.value = false
  }
}

const searchAdoption = () => {
  adoptionPage.page = 1
  fetchAdoptionOrders()
}

const resetAdoption = () => {
  adoptionFilter.status = ''
  adoptionFilter.config_id = undefined
  adoptionFilter.user_id = undefined
  adoptionFilter.dateRange = []
  searchAdoption()
}

// ============ 租地订单 ============
const rentalFilter = reactive({
  status: '',
  land_parcel_id: undefined as number | undefined,
  user_id: undefined as number | undefined,
  dateRange: [] as string[]
})
const rentalPage = reactive({ page: 1, page_size: 20, total: 0 })
const rentalOrders = ref<RentalOrder[]>([])
const rentalLoading = ref(false)

const fetchRentalOrders = async () => {
  rentalLoading.value = true
  try {
    const [start, end] = rentalFilter.dateRange || []
    const res = await orderApi.getRentalOrders({
      status: rentalFilter.status || undefined,
      land_parcel_id: rentalFilter.land_parcel_id || undefined,
      user_id: rentalFilter.user_id || undefined,
      start_date: start || undefined,
      end_date: end || undefined,
      page: rentalPage.page,
      page_size: rentalPage.page_size
    })
    rentalOrders.value = res.items
    rentalPage.total = res.total
  } catch {
    rentalOrders.value = []
  } finally {
    rentalLoading.value = false
  }
}

const searchRental = () => {
  rentalPage.page = 1
  fetchRentalOrders()
}

const resetRental = () => {
  rentalFilter.status = ''
  rentalFilter.land_parcel_id = undefined
  rentalFilter.user_id = undefined
  rentalFilter.dateRange = []
  searchRental()
}

const refreshCurrent = (type: OrderTab) => (type === 'adoption' ? fetchAdoptionOrders() : fetchRentalOrders())

// ============ 订单详情 ============
const drawerVisible = ref(false)
const detailLoading = ref(false)
const detailType = ref<OrderTab>('adoption')
const adoptionDetail = ref<AdoptionOrder | null>(null)
const rentalDetail = ref<RentalOrder | null>(null)

const showDetail = async (type: OrderTab, id: number) => {
  detailType.value = type
  adoptionDetail.value = null
  rentalDetail.value = null
  drawerVisible.value = true
  detailLoading.value = true
  try {
    if (type === 'adoption') {
      adoptionDetail.value = await orderApi.getAdoptionOrder(id)
    } else {
      rentalDetail.value = await orderApi.getRentalOrder(id)
    }
  } catch {
    drawerVisible.value = false
  } finally {
    detailLoading.value = false
  }
}

const currentDetail = () => (detailType.value === 'adoption' ? adoptionDetail.value : rentalDetail.value)

// ============ 状态变更 ============
const handleStatusChange = async (type: OrderTab, row: { id: number; order_no: string }, target: OrderStatus) => {
  let remark = ''
  try {
    const res = await ElMessageBox.prompt(
      `确定将订单 ${row.order_no} 变更为「${statusLabel(target)}」吗？可填写备注（选填）`,
      '变更订单状态',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputType: 'textarea',
        inputPlaceholder: '备注（选填）',
        type: ['cancelled', 'refunded'].includes(target) ? 'warning' : 'info'
      }
    )
    remark = (res.value || '').trim()
  } catch {
    return // 取消
  }

  try {
    if (type === 'adoption') {
      await orderApi.updateAdoptionStatus(row.id, target, remark)
    } else {
      await orderApi.updateRentalStatus(row.id, target, remark)
    }
    ElMessage.success('状态更新成功')
    await refreshCurrent(type)
    if (drawerVisible.value && currentDetail()?.id === row.id) {
      showDetail(type, row.id)
    }
    // 租地订单完成/取消会释放土地，刷新土地筛选项
    if (type === 'rental') fetchOptions()
  } catch {
    // 错误提示由拦截器处理
  }
}

// ============ 认养订单分配土地 ============
const allocateVisible = ref(false)
const allocateOrder = ref<AdoptionOrder | null>(null)
const allocateParcelId = ref<number | undefined>()
const availableParcels = ref<LandParcel[]>([])
const allocating = ref(false)

const showAllocate = async (row: AdoptionOrder) => {
  allocateOrder.value = row
  allocateParcelId.value = undefined
  allocateVisible.value = true
  try {
    const res = await orderApi.getLandParcels({ status: 'available', page: 1, page_size: 100 })
    availableParcels.value = res.items
  } catch {
    availableParcels.value = []
  }
}

const handleAllocate = async () => {
  if (!allocateOrder.value || !allocateParcelId.value) {
    ElMessage.warning('请选择土地')
    return
  }
  allocating.value = true
  try {
    await orderApi.allocateLand(allocateOrder.value.id, allocateParcelId.value)
    ElMessage.success('土地分配成功')
    allocateVisible.value = false
    const orderId = allocateOrder.value.id
    await fetchAdoptionOrders()
    fetchOptions()
    if (drawerVisible.value && currentDetail()?.id === orderId) {
      showDetail('adoption', orderId)
    }
  } catch {
    // 错误提示由拦截器处理
  } finally {
    allocating.value = false
  }
}

const canAllocate = (row: AdoptionOrder) => !row.land_parcel_id && ['paid', 'active'].includes(row.status)

onMounted(() => {
  fetchOptions()
  fetchAdoptionOrders()
  fetchRentalOrders()
})
</script>

<template>
  <div class="order-view">
    <el-tabs v-model="activeTab">
      <!-- 认养订单 -->
      <el-tab-pane :label="`认养订单 (${adoptionPage.total})`" name="adoption">
        <el-form :inline="true" class="filter-bar" @submit.prevent>
          <el-form-item label="状态">
            <el-select v-model="adoptionFilter.status" placeholder="全部" clearable style="width: 130px">
              <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="认养项目">
            <el-select v-model="adoptionFilter.config_id" placeholder="全部" clearable filterable style="width: 180px">
              <el-option v-for="c in configs" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="用户ID">
            <el-input-number v-model="adoptionFilter.user_id" :min="1" :controls="false" placeholder="用户ID" style="width: 110px" />
          </el-form-item>
          <el-form-item label="下单日期">
            <el-date-picker
              v-model="adoptionFilter.dateRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchAdoption">查询</el-button>
            <el-button @click="resetAdoption">重置</el-button>
          </el-form-item>
        </el-form>

        <el-table :data="adoptionOrders" v-loading="adoptionLoading" stripe>
          <el-table-column prop="order_no" label="订单号" min-width="170" show-overflow-tooltip />
          <el-table-column prop="user_name" label="用户" min-width="100" />
          <el-table-column prop="config_name" label="认养项目" min-width="130" show-overflow-tooltip />
          <el-table-column prop="quantity" label="数量" width="70" />
          <el-table-column label="金额" min-width="100">
            <template #default="{ row }">{{ formatMoney(row.total_amount) }}</template>
          </el-table-column>
          <el-table-column label="分配土地" min-width="110">
            <template #default="{ row }">{{ row.land_parcel_name || '未分配' }}</template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="下单时间" min-width="160">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="showDetail('adoption', row.id)">详情</el-button>
              <el-button
                v-for="a in statusActions[row.status] || []"
                :key="a.value"
                link
                :type="a.danger ? 'danger' : 'primary'"
                @click="handleStatusChange('adoption', row, a.value)"
              >{{ a.label }}</el-button>
              <el-button v-if="canAllocate(row)" link type="success" @click="showAllocate(row)">分配土地</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          class="pagination"
          v-model:current-page="adoptionPage.page"
          v-model:page-size="adoptionPage.page_size"
          :total="adoptionPage.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="fetchAdoptionOrders"
          @size-change="searchAdoption"
        />
      </el-tab-pane>

      <!-- 租地订单 -->
      <el-tab-pane :label="`租赁订单 (${rentalPage.total})`" name="rental">
        <el-form :inline="true" class="filter-bar" @submit.prevent>
          <el-form-item label="状态">
            <el-select v-model="rentalFilter.status" placeholder="全部" clearable style="width: 130px">
              <el-option v-for="s in statusOptions" :key="s.value" :label="s.label" :value="s.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="土地">
            <el-select v-model="rentalFilter.land_parcel_id" placeholder="全部" clearable filterable style="width: 180px">
              <el-option v-for="p in parcels" :key="p.id" :label="`${p.name}（${p.code}）`" :value="p.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="用户ID">
            <el-input-number v-model="rentalFilter.user_id" :min="1" :controls="false" placeholder="用户ID" style="width: 110px" />
          </el-form-item>
          <el-form-item label="下单日期">
            <el-date-picker
              v-model="rentalFilter.dateRange"
              type="daterange"
              value-format="YYYY-MM-DD"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 240px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="searchRental">查询</el-button>
            <el-button @click="resetRental">重置</el-button>
          </el-form-item>
        </el-form>

        <el-table :data="rentalOrders" v-loading="rentalLoading" stripe>
          <el-table-column prop="order_no" label="订单号" min-width="170" show-overflow-tooltip />
          <el-table-column prop="user_name" label="用户" min-width="100" />
          <el-table-column prop="land_parcel_name" label="土地" min-width="120" show-overflow-tooltip />
          <el-table-column prop="area" label="面积(m²)" min-width="90" />
          <el-table-column label="单价" min-width="100">
            <template #default="{ row }">¥{{ row.unit_price }}/m²</template>
          </el-table-column>
          <el-table-column label="总金额" min-width="100">
            <template #default="{ row }">{{ formatMoney(row.total_amount) }}</template>
          </el-table-column>
          <el-table-column label="租期" min-width="190">
            <template #default="{ row }">{{ formatDate(row.start_date, false) }} ~ {{ formatDate(row.end_date, false) }}</template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="showDetail('rental', row.id)">详情</el-button>
              <el-button
                v-for="a in statusActions[row.status] || []"
                :key="a.value"
                link
                :type="a.danger ? 'danger' : 'primary'"
                @click="handleStatusChange('rental', row, a.value)"
              >{{ a.label }}</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          class="pagination"
          v-model:current-page="rentalPage.page"
          v-model:page-size="rentalPage.page_size"
          :total="rentalPage.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="fetchRentalOrders"
          @size-change="searchRental"
        />
      </el-tab-pane>
    </el-tabs>

    <!-- 订单详情 -->
    <el-drawer v-model="drawerVisible" :title="detailType === 'adoption' ? '认养订单详情' : '租地订单详情'" size="520px">
      <div v-loading="detailLoading" class="detail">
        <template v-if="detailType === 'adoption' && adoptionDetail">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="订单号">{{ adoptionDetail.order_no }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="statusType(adoptionDetail.status)">{{ statusLabel(adoptionDetail.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="用户">
              {{ adoptionDetail.user_name }}（ID: {{ adoptionDetail.user_id }}）
            </el-descriptions-item>
            <el-descriptions-item label="用户邮箱">{{ adoptionDetail.user_email || '-' }}</el-descriptions-item>
            <el-descriptions-item label="认养项目">{{ adoptionDetail.config_name }}</el-descriptions-item>
            <el-descriptions-item label="数量">{{ adoptionDetail.quantity }}</el-descriptions-item>
            <el-descriptions-item label="金额">{{ formatMoney(adoptionDetail.total_amount) }}</el-descriptions-item>
            <el-descriptions-item label="分配土地">{{ adoptionDetail.land_parcel_name || '未分配' }}</el-descriptions-item>
            <el-descriptions-item label="开始时间">{{ formatDate(adoptionDetail.start_date) }}</el-descriptions-item>
            <el-descriptions-item label="结束时间">{{ formatDate(adoptionDetail.end_date) }}</el-descriptions-item>
            <el-descriptions-item label="收获信息">
              <pre v-if="adoptionDetail.harvest_info" class="json">{{ JSON.stringify(adoptionDetail.harvest_info, null, 2) }}</pre>
              <span v-else>-</span>
            </el-descriptions-item>
            <el-descriptions-item label="备注">{{ adoptionDetail.remark || '-' }}</el-descriptions-item>
            <el-descriptions-item label="下单时间">{{ formatDate(adoptionDetail.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ formatDate(adoptionDetail.updated_at) }}</el-descriptions-item>
          </el-descriptions>
          <div class="detail-actions">
            <el-button
              v-for="a in statusActions[adoptionDetail.status] || []"
              :key="a.value"
              :type="a.danger ? 'danger' : 'primary'"
              plain
              @click="handleStatusChange('adoption', adoptionDetail, a.value)"
            >{{ a.label }}</el-button>
            <el-button v-if="canAllocate(adoptionDetail)" type="success" plain @click="showAllocate(adoptionDetail)">分配土地</el-button>
          </div>
        </template>

        <template v-else-if="detailType === 'rental' && rentalDetail">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="订单号">{{ rentalDetail.order_no }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="statusType(rentalDetail.status)">{{ statusLabel(rentalDetail.status) }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="用户">
              {{ rentalDetail.user_name }}（ID: {{ rentalDetail.user_id }}）
            </el-descriptions-item>
            <el-descriptions-item label="用户邮箱">{{ rentalDetail.user_email || '-' }}</el-descriptions-item>
            <el-descriptions-item label="土地">{{ rentalDetail.land_parcel_name }}</el-descriptions-item>
            <el-descriptions-item label="面积">{{ rentalDetail.area }} m²</el-descriptions-item>
            <el-descriptions-item label="单价">¥{{ rentalDetail.unit_price }}/m²</el-descriptions-item>
            <el-descriptions-item label="总金额">{{ formatMoney(rentalDetail.total_amount) }}</el-descriptions-item>
            <el-descriptions-item label="租期">
              {{ formatDate(rentalDetail.start_date, false) }} ~ {{ formatDate(rentalDetail.end_date, false) }}
            </el-descriptions-item>
            <el-descriptions-item label="种植计划">{{ rentalDetail.crop_plan || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ rentalDetail.remark || '-' }}</el-descriptions-item>
            <el-descriptions-item label="下单时间">{{ formatDate(rentalDetail.created_at) }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ formatDate(rentalDetail.updated_at) }}</el-descriptions-item>
          </el-descriptions>
          <div class="detail-actions">
            <el-button
              v-for="a in statusActions[rentalDetail.status] || []"
              :key="a.value"
              :type="a.danger ? 'danger' : 'primary'"
              plain
              @click="handleStatusChange('rental', rentalDetail, a.value)"
            >{{ a.label }}</el-button>
          </div>
        </template>
      </div>
    </el-drawer>

    <!-- 分配土地 -->
    <el-dialog v-model="allocateVisible" title="分配土地" width="460px">
      <el-form label-width="90px">
        <el-form-item label="订单号">{{ allocateOrder?.order_no }}</el-form-item>
        <el-form-item label="认养项目">{{ allocateOrder?.config_name }}</el-form-item>
        <el-form-item label="选择土地" required>
          <el-select v-model="allocateParcelId" placeholder="请选择可用土地" filterable style="width: 100%">
            <el-option
              v-for="p in availableParcels"
              :key="p.id"
              :label="`${p.name}（${p.code}，${p.area}m²）`"
              :value="p.id"
            />
          </el-select>
          <div v-if="!availableParcels.length" class="hint">暂无可用土地</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="allocateVisible = false">取消</el-button>
        <el-button type="primary" :loading="allocating" @click="handleAllocate">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.order-view { padding: 20px; }
.filter-bar { margin-bottom: 4px; }
.pagination { margin-top: 16px; justify-content: flex-end; }
.detail { min-height: 200px; }
.detail-actions { margin-top: 20px; display: flex; gap: 8px; flex-wrap: wrap; }
.detail-actions .el-button + .el-button { margin-left: 0; }
.json { margin: 0; white-space: pre-wrap; word-break: break-all; font-size: 12px; }
.hint { color: #909399; font-size: 12px; margin-top: 4px; }
</style>
