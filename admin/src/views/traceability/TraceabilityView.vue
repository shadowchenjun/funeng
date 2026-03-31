<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { traceabilityApi } from '../../api/traceability'

const configs = ref<any[]>([])
const nodes = ref<any[]>([])
const records = ref<any[]>([])
const loading = ref(false)
const activeTab = ref('configs')
const selectedConfigId = ref<string>('')
const configDialogVisible = ref(false)
const nodeDialogVisible = ref(false)
const dialogTitle = ref('新增配置')
const isEdit = ref(false)
const currentId = ref('')
const formRef = ref()
const nodeFormRef = ref()

const configForm = ref({
  name: '',
  code: '',
  description: ''
})

const nodeForm = ref({
  config_id: '',
  name: '',
  node_type: '',
  icon: '',
  description: '',
  sort_order: 0,
  data_fields: ''
})

const configRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入代码', trigger: 'blur' }]
}

const nodeRules = {
  config_id: [{ required: true, message: '请选择配置', trigger: 'change' }],
  name: [{ required: true, message: '请输入节点名称', trigger: 'blur' }],
  node_type: [{ required: true, message: '请选择节点类型', trigger: 'change' }]
}

const nodeTypeOptions = [
  { label: '种植', value: 'planting' },
  { label: '生长', value: 'growing' },
  { label: '采收', value: 'harvesting' },
  { label: '加工', value: 'processing' },
  { label: '包装', value: 'packaging' },
  { label: '运输', value: 'transport' }
]

const fetchConfigs = async () => {
  loading.value = true
  try {
    configs.value = await traceabilityApi.getConfigs()
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const fetchNodes = async (configId: string) => {
  selectedConfigId.value = configId
  try {
    nodes.value = await traceabilityApi.getNodes(configId)
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  }
}

const fetchRecords = async () => {
  loading.value = true
  try {
    records.value = await traceabilityApi.getRecords({ page: 1, page_size: 50 })
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const handleTabChange = async (tab: string) => {
  if (tab === 'configs') {
    await fetchConfigs()
  } else if (tab === 'records') {
    await fetchRecords()
  }
}

const showAddConfig = () => {
  dialogTitle.value = '新增配置'
  isEdit.value = false
  configForm.value = { name: '', code: '', description: '' }
  configDialogVisible.value = true
}

const showEditConfig = (row: any) => {
  dialogTitle.value = '编辑配置'
  isEdit.value = true
  currentId.value = row.id
  configForm.value = { ...row }
  configDialogVisible.value = true
}

const handleSubmitConfig = async () => {
  try {
    await formRef.value.validate()
    if (isEdit.value) {
      await traceabilityApi.updateConfig(currentId.value, configForm.value)
      ElMessage.success('更新成功')
    } else {
      await traceabilityApi.createConfig(configForm.value)
      ElMessage.success('创建成功')
    }
    configDialogVisible.value = false
    fetchConfigs()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const handleDeleteConfig = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' })
    await traceabilityApi.updateConfig(row.id, { is_active: false })
    ElMessage.success('删除成功')
    fetchConfigs()
  } catch (e: any) {
    if (e !== 'cancel') if (e.message) ElMessage.error(e.message)
  }
}

const showAddNode = () => {
  if (!selectedConfigId.value) {
    ElMessage.warning('请先选择一个配置查看节点')
    return
  }
  isEdit.value = false
  nodeForm.value = {
    config_id: selectedConfigId.value,
    name: '',
    node_type: '',
    icon: '',
    description: '',
    sort_order: nodes.value.length,
    data_fields: ''
  }
  nodeDialogVisible.value = true
}

const showEditNode = (row: any) => {
  isEdit.value = true
  currentId.value = row.id
  nodeForm.value = { ...row }
  nodeDialogVisible.value = true
}

const handleSubmitNode = async () => {
  try {
    await nodeFormRef.value.validate()
    if (isEdit.value) {
      await traceabilityApi.updateNode(currentId.value, nodeForm.value)
      ElMessage.success('更新成功')
    } else {
      await traceabilityApi.createNode(nodeForm.value)
      ElMessage.success('创建成功')
    }
    nodeDialogVisible.value = false
    if (selectedConfigId.value) {
      fetchNodes(selectedConfigId.value)
    }
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const handleDeleteNode = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' })
    await traceabilityApi.deleteNode(row.id)
    ElMessage.success('删除成功')
    if (selectedConfigId.value) {
      fetchNodes(selectedConfigId.value)
    }
  } catch (e: any) {
    if (e !== 'cancel') if (e.message) ElMessage.error(e.message)
  }
}

const formatDate = (date: string) => {
  return date ? date.slice(0, 19) : '-'
}

onMounted(fetchConfigs)
</script>

<template>
  <div class="traceability-view" v-loading="loading">
    <el-tabs @tab-change="handleTabChange">
      <el-tab-pane label="溯源配置" name="configs">
        <div class="toolbar">
          <el-button type="primary" @click="showAddConfig">新增配置</el-button>
        </div>
        <el-table :data="configs" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="code" label="代码" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button link type="primary" @click="fetchNodes(row.id)">查看节点</el-button>
              <el-button link type="primary" @click="showEditConfig(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDeleteConfig(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-divider v-if="selectedConfigId" />

        <div v-if="selectedConfigId">
          <h4>溯源节点</h4>
          <div class="toolbar">
            <el-button type="primary" @click="showAddNode">新增节点</el-button>
          </div>
          <el-table :data="nodes" stripe style="margin-top: 10px">
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="node_type" label="类型">
              <template #default="{ row }">
                {{ nodeTypeOptions.find(t => t.value === row.node_type)?.label || row.node_type }}
              </template>
            </el-table-column>
            <el-table-column prop="icon" label="图标" />
            <el-table-column prop="sort_order" label="排序" />
            <el-table-column prop="is_active" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button link type="primary" @click="showEditNode(row)">编辑</el-button>
                <el-button link type="danger" @click="handleDeleteNode(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>

      <el-tab-pane label="溯源记录" name="records">
        <el-table :data="records.items || []" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="node_name" label="节点" />
          <el-table-column prop="order_no" label="订单号" width="180" />
          <el-table-column prop="operator" label="操作人" />
          <el-table-column prop="timestamp" label="时间" width="180" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button link type="primary">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="configDialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="configForm" :rules="configRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="configForm.name" placeholder="请输入配置名称" />
        </el-form-item>
        <el-form-item label="代码" prop="code">
          <el-input v-model="configForm.code" placeholder="请输入唯一代码" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="configForm.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="configDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitConfig">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="nodeDialogVisible" :title="isEdit ? '编辑节点' : '新增节点'" width="500px">
      <el-form ref="nodeFormRef" :model="nodeForm" :rules="nodeRules" label-width="100px">
        <el-form-item label="节点名称" prop="name">
          <el-input v-model="nodeForm.name" placeholder="请输入节点名称" />
        </el-form-item>
        <el-form-item label="节点类型" prop="node_type">
          <el-select v-model="nodeForm.node_type" placeholder="请选择节点类型" style="width: 100%">
            <el-option v-for="t in nodeTypeOptions" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="nodeForm.icon" placeholder="如: Plant" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="nodeForm.sort_order" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="数据字段">
          <el-input v-model="nodeForm.data_fields" type="textarea" placeholder="如: temperature,humidity" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="nodeForm.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="nodeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitNode">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.traceability-view { padding: 20px; }
.toolbar { margin-bottom: 20px; }
</style>
