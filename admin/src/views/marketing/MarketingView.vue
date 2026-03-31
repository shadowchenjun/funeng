<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marketingApi } from '../../api/marketing'

const coupons = ref<any[]>([])
const activities = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增优惠券')
const dialogType = ref<'coupon' | 'activity'>('coupon')
const formRef = ref()

const couponForm = ref({
  name: '',
  code: '',
  type: 'discount',
  discount_value: 0,
  min_amount: 0,
  total_count: 100,
  valid_from: '',
  valid_until: ''
})

const activityForm = ref({
  name: '',
  type: '',
  start_time: '',
  end_time: '',
  description: ''
})

const couponRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入代码', trigger: 'blur' }],
  discount_value: [{ required: true, message: '请输入优惠值', trigger: 'blur' }],
  valid_from: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  valid_until: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

const activityRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  type: [{ required: true, message: '请输入类型', trigger: 'blur' }],
  start_time: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  end_time: [{ required: true, message: '请选择结束时间', trigger: 'change' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const [couponRes, activityRes] = await Promise.all([
      marketingApi.getCoupons({ page: 1, page_size: 100 }),
      marketingApi.getActivities({ page: 1, page_size: 100 })
    ])
    coupons.value = couponRes.items
    activities.value = activityRes.items
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const showAddCoupon = () => {
  dialogTitle.value = '新增优惠券'
  dialogType.value = 'coupon'
  couponForm.value = { name: '', code: '', type: 'discount', discount_value: 0, min_amount: 0, total_count: 100, valid_from: '', valid_until: '' }
  dialogVisible.value = true
}

const showAddActivity = () => {
  dialogTitle.value = '新增活动'
  dialogType.value = 'activity'
  activityForm.value = { name: '', type: '', start_time: '', end_time: '', description: '' }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    if (dialogType.value === 'coupon') {
      await formRef.value.validate()
      await marketingApi.createCoupon(couponForm.value)
      ElMessage.success('创建成功')
    } else {
      await formRef.value.validate()
      await marketingApi.createActivity(activityForm.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const formatDate = (date: string) => {
  return date ? date.slice(0, 10) : '-'
}

onMounted(fetchData)
</script>

<template>
  <div class="marketing-view" v-loading="loading">
    <el-tabs>
      <el-tab-pane label="优惠券">
        <div class="toolbar">
          <el-button type="primary" @click="showAddCoupon">新增优惠券</el-button>
        </div>
        <el-table :data="coupons" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="code" label="代码" />
          <el-table-column prop="type" label="类型">
            <template #default="{ row }">{{ row.type === 'discount' ? '折扣' : '现金' }}</template>
          </el-table-column>
          <el-table-column prop="discount_value" label="优惠值">
            <template #default="{ row }">
              {{ row.type === 'discount' ? `${row.discount_value}折` : `¥${row.discount_value}` }}
            </template>
          </el-table-column>
          <el-table-column prop="total_count" label="总量" />
          <el-table-column prop="used_count" label="已用" />
          <el-table-column prop="valid_from" label="开始日期">
            <template #default="{ row }">{{ formatDate(row.valid_from) }}</template>
          </el-table-column>
          <el-table-column prop="valid_until" label="结束日期">
            <template #default="{ row }">{{ formatDate(row.valid_until) }}</template>
          </el-table-column>
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="活动管理">
        <div class="toolbar">
          <el-button type="primary" @click="showAddActivity">新增活动</el-button>
        </div>
        <el-table :data="activities" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="type" label="类型" />
          <el-table-column prop="start_time" label="开始时间">
            <template #default="{ row }">{{ formatDate(row.start_time) }}</template>
          </el-table-column>
          <el-table-column prop="end_time" label="结束时间">
            <template #default="{ row }">{{ formatDate(row.end_time) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : row.status === 'ended' ? 'info' : 'warning'">
                {{ row.status === 'active' ? '进行中' : row.status === 'ended' ? '已结束' : '待开始' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="dialogType === 'coupon' ? couponForm : activityForm"
        :rules="dialogType === 'coupon' ? couponRules : activityRules" label-width="100px">
        <template v-if="dialogType === 'coupon'">
          <el-form-item label="名称" prop="name">
            <el-input v-model="couponForm.name" placeholder="请输入优惠券名称" />
          </el-form-item>
          <el-form-item label="代码" prop="code">
            <el-input v-model="couponForm.code" placeholder="请输入唯一代码" />
          </el-form-item>
          <el-form-item label="类型">
            <el-select v-model="couponForm.type" style="width: 100%">
              <el-option label="折扣" value="discount" />
              <el-option label="现金" value="cash" />
            </el-select>
          </el-form-item>
          <el-form-item label="优惠值" prop="discount_value">
            <el-input-number v-model="couponForm.discount_value" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item label="最低消费">
            <el-input-number v-model="couponForm.min_amount" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item label="发放数量">
            <el-input-number v-model="couponForm.total_count" :min="1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="有效期" prop="valid_from">
            <el-date-picker v-model="couponForm.valid_from" type="date" value-format="YYYY-MM-DD" placeholder="开始日期" style="width: 48%" />
            <span style="padding: 0 4%">至</span>
            <el-date-picker v-model="couponForm.valid_until" type="date" value-format="YYYY-MM-DD" placeholder="结束日期" style="width: 48%" />
          </el-form-item>
        </template>
        <template v-else>
          <el-form-item label="名称" prop="name">
            <el-input v-model="activityForm.name" placeholder="请输入活动名称" />
          </el-form-item>
          <el-form-item label="类型" prop="type">
            <el-input v-model="activityForm.type" placeholder="如: flash_sale, group_buy" />
          </el-form-item>
          <el-form-item label="开始时间" prop="start_time">
            <el-date-picker v-model="activityForm.start_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
          </el-form-item>
          <el-form-item label="结束时间" prop="end_time">
            <el-date-picker v-model="activityForm.end_time" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" style="width: 100%" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="activityForm.description" type="textarea" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.marketing-view { padding: 20px; }
.toolbar { margin-bottom: 20px; }
</style>
