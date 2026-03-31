<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deviceApi } from '../../api/device'

const deviceTypes = ref<any[]>([])
const devices = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增设备类型')
const dialogType = ref<'type' | 'device'>('type')
const formRef = ref()

const formData = ref({
  name: '',
  code: '',
  icon: '',
  description: '',
  device_type_id: '',
  location: '',
  firmware_version: ''
})

const typeRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入代码', trigger: 'blur' }]
}

const deviceRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编号', trigger: 'blur' }],
  device_type_id: [{ required: true, message: '请选择设备类型', trigger: 'change' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const [typeRes, deviceRes] = await Promise.all([
      deviceApi.getTypes(),
      deviceApi.getDevices({ page: 1, page_size: 100 })
    ])
    deviceTypes.value = typeRes
    devices.value = deviceRes.items
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const showAddType = () => {
  dialogTitle.value = '新增设备类型'
  dialogType.value = 'type'
  formData.value = { name: '', code: '', icon: '', description: '', device_type_id: '', location: '', firmware_version: '' }
  dialogVisible.value = true
}

const showAddDevice = () => {
  dialogTitle.value = '新增设备'
  dialogType.value = 'device'
  formData.value = { name: '', code: '', icon: '', description: '', device_type_id: '', location: '', firmware_version: '' }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    const rules = dialogType.value === 'type' ? typeRules : deviceRules
    await formRef.value.validate()

    if (dialogType.value === 'type') {
      await deviceApi.createType({
        name: formData.value.name,
        code: formData.value.code,
        icon: formData.value.icon,
        description: formData.value.description
      })
      ElMessage.success('创建成功')
    } else {
      await deviceApi.createDevice({
        name: formData.value.name,
        code: formData.value.code,
        device_type_id: formData.value.device_type_id,
        location: formData.value.location,
        firmware_version: formData.value.firmware_version
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const statusOptions = [
  { label: '在线', value: 'online', type: 'success' },
  { label: '离线', value: 'offline', type: 'danger' },
  { label: '异常', value: 'error', type: 'warning' },
  { label: '维护', value: 'maintenance', type: 'info' }
]

onMounted(fetchData)
</script>

<template>
  <div class="device-view" v-loading="loading">
    <el-tabs>
      <el-tab-pane label="设备类型">
        <div class="toolbar">
          <el-button type="primary" @click="showAddType">新增类型</el-button>
        </div>
        <el-table :data="deviceTypes" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="code" label="代码" />
          <el-table-column prop="icon" label="图标" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="设备管理">
        <div class="toolbar">
          <el-button type="primary" @click="showAddDevice">新增设备</el-button>
        </div>
        <el-table :data="devices" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="code" label="编号" />
          <el-table-column prop="device_type_id" label="类型">
            <template #default="{ row }">
              {{ deviceTypes.find(t => t.id === row.device_type_id)?.name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="location" label="位置" />
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="statusOptions.find(s => s.value === row.status)?.type || 'info'">
                {{ statusOptions.find(s => s.value === row.status)?.label || row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="firmware_version" label="固件版本" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="formData" :rules="dialogType === 'type' ? typeRules : deviceRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="编号/代码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入编号" />
        </el-form-item>
        <el-form-item v-if="dialogType === 'device'" label="设备类型" prop="device_type_id">
          <el-select v-model="formData.device_type_id" placeholder="请选择类型" style="width: 100%">
            <el-option v-for="t in deviceTypes" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="dialogType === 'device'" label="位置">
          <el-input v-model="formData.location" placeholder="请输入位置" />
        </el-form-item>
        <el-form-item v-if="dialogType === 'device'" label="固件版本">
          <el-input v-model="formData.firmware_version" placeholder="如: v1.0.0" />
        </el-form-item>
        <el-form-item v-if="dialogType === 'type'" label="图标">
          <el-input v-model="formData.icon" placeholder="如: Monitor" />
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
.device-view { padding: 20px; }
.toolbar { margin-bottom: 20px; }
</style>
