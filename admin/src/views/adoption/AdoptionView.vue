<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adoptionApi } from '../../api/adoption'

const activeTab = ref('categories')
const categories = ref<any[]>([])
const configs = ref<any[]>([])
const orders = ref<any[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增分类')
const dialogType = ref<'category' | 'config'>('category')
const formRef = ref()

const categoryForm = ref({ name: '', code: '', icon: '', description: '' })
const configForm = ref({ category_id: '', name: '', price: 0, duration_days: 30, description: '', unit: 'year', stock: 0 })

const categoryRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入代码', trigger: 'blur' }]
}

const configRules = {
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  duration_days: [{ required: true, message: '请输入时长', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const [catRes, configRes, orderRes] = await Promise.all([
      adoptionApi.getCategories(),
      adoptionApi.getConfigs(),
      adoptionApi.getOrders({ page: 1, page_size: 100 })
    ])
    categories.value = catRes
    configs.value = configRes
    orders.value = orderRes.items
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const showAddCategory = () => {
  dialogTitle.value = '新增分类'
  dialogType.value = 'category'
  categoryForm.value = { name: '', code: '', icon: '', description: '' }
  dialogVisible.value = true
}

const showAddConfig = () => {
  dialogTitle.value = '新增配置'
  dialogType.value = 'config'
  configForm.value = { category_id: '', name: '', price: 0, duration_days: 30, description: '', unit: 'year', stock: 0 }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    if (dialogType.value === 'category') {
      await formRef.value.validate()
      await adoptionApi.createCategory(categoryForm.value)
      ElMessage.success('创建成功')
    } else {
      await formRef.value.validate()
      await adoptionApi.createConfig(configForm.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const statusOptions = [
  { label: '待支付', value: 'pending', type: 'warning' },
  { label: '已支付', value: 'paid', type: 'success' },
  { label: '进行中', value: 'active', type: 'primary' },
  { label: '已完成', value: 'completed', type: 'info' },
  { label: '已取消', value: 'cancelled', type: 'danger' }
]

const unitOptions = [
  { label: '年', value: 'year' },
  { label: '月', value: 'month' },
  { label: '季', value: 'season' }
]

onMounted(fetchData)
</script>

<template>
  <div class="adoption-view" v-loading="loading">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="认养分类" name="categories">
        <div class="toolbar">
          <el-button type="primary" @click="showAddCategory">新增分类</el-button>
        </div>
        <el-table :data="categories" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="code" label="代码" />
          <el-table-column prop="icon" label="图标" />
          <el-table-column prop="sort_order" label="排序" />
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="认养配置" name="configs">
        <div class="toolbar">
          <el-button type="primary" @click="showAddConfig">新增配置</el-button>
        </div>
        <el-table :data="configs" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="price" label="价格">
            <template #default="{ row }">¥{{ row.price }}/{{ row.unit }}</template>
          </el-table-column>
          <el-table-column prop="duration_days" label="时长(天)" />
          <el-table-column prop="stock" label="库存" />
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="认养订单" name="orders">
        <el-table :data="orders" stripe>
          <el-table-column prop="order_no" label="订单号" />
          <el-table-column prop="total_amount" label="金额">
            <template #default="{ row }">¥{{ row.total_amount }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态">
            <template #default="{ row }">
              <el-tag :type="statusOptions.find(s => s.value === row.status)?.type || 'info'">
                {{ statusOptions.find(s => s.value === row.status)?.label || row.status }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" />
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="dialogType === 'category' ? categoryForm : configForm"
        :rules="dialogType === 'category' ? categoryRules : configRules" label-width="100px">
        <template v-if="dialogType === 'category'">
          <el-form-item label="名称" prop="name">
            <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
          </el-form-item>
          <el-form-item label="代码" prop="code">
            <el-input v-model="categoryForm.code" placeholder="请输入唯一代码" />
          </el-form-item>
          <el-form-item label="图标">
            <el-input v-model="categoryForm.icon" placeholder="如: Crop" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="categoryForm.description" type="textarea" />
          </el-form-item>
        </template>
        <template v-else>
          <el-form-item label="所属分类" prop="category_id">
            <el-select v-model="configForm.category_id" placeholder="请选择分类" style="width: 100%">
              <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="名称" prop="name">
            <el-input v-model="configForm.name" placeholder="请输入配置名称" />
          </el-form-item>
          <el-form-item label="价格" prop="price">
            <el-input-number v-model="configForm.price" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item label="时长(天)" prop="duration_days">
            <el-input-number v-model="configForm.duration_days" :min="1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="单位">
            <el-select v-model="configForm.unit" style="width: 100%">
              <el-option v-for="u in unitOptions" :key="u.value" :label="u.label" :value="u.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="库存">
            <el-input-number v-model="configForm.stock" :min="0" style="width: 100%" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="configForm.description" type="textarea" />
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
.adoption-view { padding: 20px; }
.toolbar { margin-bottom: 20px; }
</style>
