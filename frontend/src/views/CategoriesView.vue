<template>
  <div class="page-container">
    <PageHeader title="分类管理" subtitle="整理产品分类，方便用户浏览和搜索">
      <template v-if="isAdmin" #actions>
        <el-button type="primary" :icon="Plus" @click="showAddDialog">添加分类</el-button>
      </template>
    </PageHeader>

    <!-- 分类网格 -->
    <div class="categories-grid" v-loading="loading">
      <div
        v-for="category in categories"
        :key="category.id"
        class="category-card"
        :style="{ '--accent': category.color || '#165DFF' }"
      >
        <div class="card-glow"></div>
        <div class="card-content">
          <div class="category-icon-wrapper" :style="{ background: `${category.color || '#165DFF'}15` }">
            <span v-if="isEmoji(category.icon)" class="emoji-icon">{{ category.icon }}</span>
            <el-icon v-else :size="26" :color="category.color || '#165DFF'">
              <component :is="getIconComponent(category.icon)" />
            </el-icon>
          </div>
          <div class="category-info">
            <h3 class="category-name">{{ category.name }}</h3>
            <p class="category-count">{{ category.productCount || 0 }} 个产品</p>
          </div>
          <div class="card-actions" v-if="isAdmin">
            <el-button type="primary" link :icon="Edit" @click="editCategory(category)">编辑</el-button>
            <el-button type="danger" link :icon="Delete" @click="deleteCategory(category)">删除</el-button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <EmptyState
        v-if="loadError"
        class="grid-full"
        :icon="WarningFilled"
        title="分类加载失败"
        :description="loadError"
      >
        <template #action>
          <el-button type="primary" @click="fetchCategories">重试</el-button>
        </template>
      </EmptyState>
      <EmptyState
        v-else-if="categories.length === 0 && !loading"
        class="grid-full"
        :icon="FolderOpened"
        title="暂无分类"
        description="点击上方按钮添加第一个分类"
      />
    </div>

    <!-- 添加/编辑分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑分类' : '添加分类'"
      class="dialog-sm"
    >
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类图标">
          <el-select v-model="categoryForm.icon" placeholder="请选择图标" class="w-full">
            <el-option v-for="opt in iconOptions" :key="opt.value" :label="opt.label" :value="opt.value">
              <span class="icon-option">
                <el-icon><component :is="getIconComponent(opt.value)" /></el-icon>
                {{ opt.label }}
              </span>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="categoryForm.color" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCategory">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Apple, Box, Chicken, Crop, Delete, Edit, FolderOpened, Food, Plus, WarningFilled
} from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '../utils/error'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)

interface ApiCategory {
  id: number
  name: string
  icon?: string | null
  color?: string | null
}

interface Category {
  id: number
  name: string
  icon: string
  color: string
  productCount: number
}

const iconMap: Record<string, any> = {
  Apple,
  Food,
  Rice: Crop,
  Chicken,
  Box
}

const iconOptions = [
  { label: '水果', value: 'Apple' },
  { label: '蔬菜', value: 'Food' },
  { label: '粮食', value: 'Rice' },
  { label: '畜牧', value: 'Chicken' },
  { label: '其他', value: 'Box' }
]

const getIconComponent = (iconName: string) => {
  return iconMap[iconName] || Box
}

const isEmoji = (str: string) => {
  return /\p{Emoji}/u.test(str) && str.length <= 4
}

const categories = ref<Category[]>([])

// 加载分类和产品数量
const loading = ref(false)
const loadError = ref('')

const fetchCategories = async () => {
  loading.value = true
  loadError.value = ''
  try {
    // 后端聚合产品数量，单次请求
    const response = await axios.get<(ApiCategory & { product_count: number })[]>('/api/categories/with-count')
    categories.value = response.data.map((c) => ({
      id: c.id,
      name: c.name,
      icon: c.icon || 'Box',
      color: c.color || '#165DFF',
      productCount: c.product_count
    }))
  } catch (e) {
    console.error('加载分类失败', e)
    loadError.value = getErrorMessage(e, '无法获取分类数据，请稍后重试')
    categories.value = []
    ElMessage.error(loadError.value)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  window.scrollTo(0, 0)
  fetchCategories()
})

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number>()

const categoryForm = reactive({
  name: '',
  icon: 'Box',
  color: '#165DFF'
})

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(categoryForm, {
    name: '',
    icon: 'Box',
    color: '#165DFF'
  })
  dialogVisible.value = true
}

const editCategory = (category: Category) => {
  isEdit.value = true
  editingId.value = category.id
  Object.assign(categoryForm, {
    name: category.name,
    icon: category.icon,
    color: category.color
  })
  dialogVisible.value = true
}

const saveCategory = async () => {
  if (!categoryForm.name) {
    ElMessage.warning('请输入分类名称')
    return
  }
  try {
    if (isEdit.value && editingId.value) {
      await axios.put(`/api/categories/${editingId.value}`, {
        name: categoryForm.name,
        icon: categoryForm.icon,
        color: categoryForm.color
      })
      ElMessage.success('分类更新成功！')
    } else {
      await axios.post('/api/categories/', {
        name: categoryForm.name,
        icon: categoryForm.icon,
        color: categoryForm.color
      })
      ElMessage.success('分类添加成功！')
    }
    dialogVisible.value = false
    await fetchCategories()
  } catch (e) {
    ElMessage.error(getErrorMessage(e, '操作失败'))
  }
}

const deleteCategory = async (category: Category) => {
  try {
    await ElMessageBox.confirm(`确定要删除分类 "${category.name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`/api/categories/${category.id}`)
    ElMessage.success('分类删除成功！')
    await fetchCategories()
  } catch (e) {
    // 用户在确认框点「取消」时 ElMessageBox 以 'cancel' 拒绝，不应提示失败
    if (e !== 'cancel') ElMessage.error(getErrorMessage(e, '删除失败'))
  }
}
</script>

<style scoped>
.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.grid-full {
  grid-column: 1 / -1;
}

.category-card {
  position: relative;
  overflow: hidden;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.category-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
}

.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.category-card:hover .card-glow {
  transform: scaleX(1);
}

.card-content {
  padding: 24px;
}

.category-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  margin-bottom: 16px;
  border-radius: var(--radius-md);
}

.emoji-icon {
  font-size: 26px;
  line-height: 1;
}

.category-info {
  margin-bottom: 16px;
}

.category-name {
  margin: 0 0 4px;
  font-size: var(--font-lg);
  font-weight: 700;
  color: var(--text-primary);
}

.category-count {
  margin: 0;
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.card-actions {
  display: flex;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.icon-option {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 768px) {
  .categories-grid {
    grid-template-columns: minmax(0, 1fr);
    gap: 12px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .category-card,
  .card-glow {
    transition: none;
  }
}
</style>
