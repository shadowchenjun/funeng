<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { systemApi } from '../../api/system'

const configs = ref<any[]>([])
const logs = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const currentKey = ref('')
const formRef = ref()

const formData = ref({
  key: '',
  value: '',
  type: 'string',
  group_name: '',
  description: '',
  is_public: false
})

const rules = {
  key: [{ required: true, message: '请输入键', trigger: 'blur' }],
  value: [{ required: true, message: '请输入值', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const [configRes, logRes] = await Promise.all([
      systemApi.getConfigs(),
      systemApi.getLogs({ page: 1, page_size: 50 })
    ])
    configs.value = configRes
    logs.value = logRes.items
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const showAddConfig = () => {
  isEdit.value = false
  formData.value = { key: '', value: '', type: 'string', group_name: '', description: '', is_public: false }
  dialogVisible.value = true
}

const showEditConfig = (row: any) => {
  isEdit.value = true
  currentKey.value = row.key
  formData.value = { ...row }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    if (isEdit.value) {
      await systemApi.updateConfig(currentKey.value, formData.value.value)
      ElMessage.success('更新成功')
    } else {
      await systemApi.createConfig(formData.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const formatDate = (date: string) => {
  return date ? date.slice(0, 19) : '-'
}

onMounted(fetchData)
</script>

<template>
  <div class="settings-view" v-loading="loading">
    <el-tabs>
      <el-tab-pane label="系统配置">
        <div class="toolbar">
          <el-button type="primary" @click="showAddConfig">新增配置</el-button>
        </div>
        <el-table :data="configs" stripe>
          <el-table-column prop="key" label="键" width="200" />
          <el-table-column prop="value" label="值">
            <template #default="{ row }">
              <span v-if="row.type === 'json'">{{ JSON.stringify(row.value) }}</span>
              <span v-else-if="row.type === 'boolean'">{{ row.value ? '是' : '否' }}</span>
              <span v-else>{{ row.value }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="类型" width="100" />
          <el-table-column prop="group_name" label="分组" width="120" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="is_public" label="公开">
            <template #default="{ row }">
              <el-tag :type="row.is_public ? 'success' : 'info'">{{ row.is_public ? '是' : '否' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button link type="primary" @click="showEditConfig(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="操作日志">
        <el-table :data="logs" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="admin_username" label="管理员" width="120" />
          <el-table-column prop="action" label="操作" width="150" />
          <el-table-column prop="resource" label="资源" width="120" />
          <el-table-column prop="detail" label="详情" />
          <el-table-column prop="ip_address" label="IP" width="150" />
          <el-table-column prop="created_at" label="时间" width="180">
            <template #default="{ row }">{{ formatDate(row.created_at) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑配置' : '新增配置'" width="500px">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="键" prop="key">
          <el-input v-model="formData.key" :disabled="isEdit" placeholder="请输入配置键" />
        </el-form-item>
        <el-form-item label="值" prop="value">
          <el-input v-model="formData.value" type="textarea" placeholder="请输入配置值" />
        </el-form-item>
        <el-form-item label="分组">
          <el-input v-model="formData.group_name" placeholder="如: basic, seo" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="formData.type" style="width: 100%">
            <el-option label="字符串" value="string" />
            <el-option label="数字" value="number" />
            <el-option label="布尔" value="boolean" />
            <el-option label="JSON" value="json" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="公开">
          <el-switch v-model="formData.is_public" />
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
.settings-view { padding: 20px; }
.toolbar { margin-bottom: 20px; }
</style>
