<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { landApi } from '../../api/land'

const parcels = ref<any[]>([])
const rentalOrders = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增土地')
const isEdit = ref(false)
const currentId = ref<string>('')
const formRef = ref()

const formData = ref({
  name: '',
  code: '',
  area: 0,
  location: '',
  type: 'farm',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编号', trigger: 'blur' }],
  area: [{ required: true, message: '请输入面积', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const [parcelRes, orderRes] = await Promise.all([
      landApi.getParcels({ page: 1, page_size: 100 }),
      landApi.getRentalOrders({ page: 1, page_size: 20 })
    ])
    parcels.value = parcelRes.items
    rentalOrders.value = orderRes.items
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  dialogTitle.value = '新增土地'
  isEdit.value = false
  formData.value = { name: '', code: '', area: 0, location: '', type: 'farm', description: '' }
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  dialogTitle.value = '编辑土地'
  isEdit.value = true
  currentId.value = row.id
  formData.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    if (isEdit.value) {
      await landApi.updateParcel(currentId.value, formData.value)
      ElMessage.success('更新成功')
    } else {
      await landApi.createParcel(formData.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' })
    await landApi.deleteParcel(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

const statusOptions = [
  { label: '可用', value: 'available', type: 'success' },
  { label: '已租用', value: 'rented', type: 'warning' },
  { label: '预留', value: 'reserved', type: 'info' }
]

const typeOptions = [
  { label: '农田', value: 'farm' },
  { label: '果园', value: 'orchard' },
  { label: '大棚', value: 'greenhouse' }
]

onMounted(fetchData)
</script>

<template>
  <div class="land-view" v-loading="loading">
    <el-tabs>
      <el-tab-pane label="土地管理">
        <div class="toolbar">
          <el-button type="primary" @click="handleAdd">新增土地</el-button>
        </div>
        <el-table :data="parcels" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="code" label="编号" />
          <el-table-column prop="area" label="面积(m²)" />
          <el-table-column prop="location" label="位置" />
          <el-table-column prop="type" label="类型">
            <template #default="{ row }">
              {{ typeOptions.find(t => t.value === row.type)?.label || row.type }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="statusOptions.find(s => s.value === row.status)?.type || 'info'">
                {{ statusOptions.find(s => s.value === row.status)?.label || row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="租地订单">
        <el-table :data="rentalOrders" stripe>
          <el-table-column prop="order_no" label="订单号" />
          <el-table-column prop="area" label="面积(m²)" />
          <el-table-column prop="unit_price" label="单价">
            <template #default="{ row }">¥{{ row.unit_price }}/m²</template>
          </el-table-column>
          <el-table-column prop="total_amount" label="总金额">
            <template #default="{ row }">¥{{ row.total_amount }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="statusOptions.find(s => s.value === row.status)?.type || 'info'">
                {{ statusOptions.find(s => s.value === row.status)?.label || row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="start_date" label="开始日期" />
          <el-table-column prop="end_date" label="结束日期" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入土地名称" />
        </el-form-item>
        <el-form-item label="编号" prop="code">
          <el-input v-model="formData.code" placeholder="请输入唯一编号" />
        </el-form-item>
        <el-form-item label="面积(m²)" prop="area">
          <el-input-number v-model="formData.area" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="formData.location" placeholder="请输入位置" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="formData.type" style="width: 100%">
            <el-option v-for="t in typeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.land-view { padding: 20px; }
.toolbar { margin-bottom: 20px; }
</style>
