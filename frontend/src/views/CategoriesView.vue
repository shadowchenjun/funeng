<template>
  <div class="categories-container">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">📁 分类管理</h1>
        <p class="page-subtitle">整理产品分类，方便用户浏览和搜索</p>
      </div>
      <div class="header-right" v-if="isAdmin">
        <button class="btn-primary" @click="showAddDialog">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          添加分类
        </button>
      </div>
    </header>

    <!-- 分类网格 -->
    <div class="categories-grid">
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
            <el-icon v-else :size="32" :color="category.color || '#165DFF'">
              <component :is="getIconComponent(category.icon)" />
            </el-icon>
          </div>
          <div class="category-info">
            <h3 class="category-name">{{ category.name }}</h3>
            <p class="category-count">{{ category.productCount || 0 }} 个产品</p>
            <div class="category-status">
              <span :class="['status-dot', category.status === 'active' ? 'active' : 'inactive']"></span>
              {{ category.status === 'active' ? '启用' : '禁用' }}
            </div>
          </div>
          <div class="card-actions" v-if="isAdmin">
            <button class="action-btn edit" @click="editCategory(category)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              编辑
            </button>
            <button class="action-btn delete" @click="deleteCategory(category)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3,6 5,6 21,6"/>
                <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
              </svg>
              删除
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="categories.length === 0" class="empty-state">
        <div class="empty-icon">📂</div>
        <h3>暂无分类</h3>
        <p>点击上方按钮添加第一个分类</p>
      </div>
    </div>

    <!-- 添加/编辑分类对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑分类' : '添加分类'"
      width="420px"
      class="category-dialog"
    >
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类图标">
          <el-select v-model="categoryForm.icon" placeholder="请选择图标" style="width: 100%">
            <el-option label="🍎 水果" value="Apple" />
            <el-option label="🥬 蔬菜" value="Food" />
            <el-option label="🌾 粮食" value="Rice" />
            <el-option label="🐔 畜牧" value="Chicken" />
            <el-option label="📦 其他" value="Box" />
          </el-select>
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="categoryForm.color" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="categoryForm.status"
            active-value="active"
            inactive-value="inactive"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="dialogVisible = false">取消</button>
          <button class="btn-primary" @click="saveCategory">保存</button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Apple, Food, Crop, Chicken, Box } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)

interface Category {
  id: number
  name: string
  icon: string
  color: string
  productCount: number
  status: string
}

const iconMap: Record<string, any> = {
  Apple,
  Food,
  Rice: Crop,
  Chicken,
  Box
}

const getIconComponent = (iconName: string) => {
  return iconMap[iconName] || Box
}

const isEmoji = (str: string) => {
  return /\p{Emoji}/u.test(str) && str.length <= 4
}

const categories = ref<Category[]>([])

// 加载分类和产品数量
const fetchCategories = async () => {
  try {
    // 并行获取分类和产品数据
    const [catRes, prodRes] = await Promise.all([
      axios.get('/api/categories/'),
      axios.get('/api/products/', { params: { limit: 1000 } })
    ])

    // 统计每个分类的产品数量
    const productCounts: Record<number, number> = {}
    const products = prodRes.data.items || prodRes.data || []
    products.forEach((p: any) => {
      const catId = p.category_id
      if (catId) {
        productCounts[catId] = (productCounts[catId] || 0) + 1
      }
    })

    categories.value = catRes.data.map((c: any) => ({
      id: c.id,
      name: c.name,
      icon: c.icon || 'Box',
      color: c.color || '#409eff',
      productCount: productCounts[c.id] || 0,
      status: 'active'
    }))
  } catch (e) {
    console.error('加载分类失败', e)
    // 使用模拟数据
    categories.value = [
      { id: 1, name: '水果', icon: 'Apple', color: '#f56c6c', productCount: 25, status: 'active' },
      { id: 2, name: '蔬菜', icon: 'Food', color: '#67c23a', productCount: 42, status: 'active' },
      { id: 3, name: '粮食', icon: 'Rice', color: '#e6a23c', productCount: 18, status: 'active' },
      { id: 4, name: '畜牧', icon: 'Chicken', color: '#909399', productCount: 12, status: 'active' },
      { id: 5, name: '其他', icon: 'Box', color: '#409eff', productCount: 8, status: 'active' }
    ]
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
  color: '#409eff',
  status: 'active'
})

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(categoryForm, {
    name: '',
    icon: 'Box',
    color: '#409eff',
    status: 'active'
  })
  dialogVisible.value = true
}

const editCategory = (category: Category) => {
  isEdit.value = true
  editingId.value = category.id
  Object.assign(categoryForm, {
    name: category.name,
    icon: category.icon,
    color: category.color,
    status: category.status
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
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
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
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}
</script>

<style scoped>
.categories-container {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  background: var(--bg-secondary, #F8FAFC);
  min-height: calc(100vh - 64px);
}

/* ========== 页面头部 ========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #0F172A);
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 15px;
  color: var(--text-secondary, #475569);
  margin: 0;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--primary, #165DFF);
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--primary-dark, #0F4AE6);
  transform: translateY(-1px);
}

.btn-primary svg {
  width: 18px;
  height: 18px;
}

/* ========== 分类网格 ========== */
.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.category-card {
  position: relative;
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.category-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.08);
  border-color: var(--accent);
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
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  margin-bottom: 20px;
}

.emoji-icon {
  font-size: 32px;
  line-height: 1;
}

.category-info {
  margin-bottom: 20px;
}

.category-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary, #0F172A);
  margin: 0 0 8px 0;
}

.category-count {
  font-size: 14px;
  color: var(--text-secondary, #475569);
  margin: 0 0 8px 0;
}

.category-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-tertiary, #94A3B8);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.active {
  background: #10B981;
}

.status-dot.inactive {
  background: #94A3B8;
}

.card-actions {
  display: flex;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color, #E2E8F0);
}

.action-btn {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn svg {
  width: 15px;
  height: 15px;
}

.action-btn.edit {
  background: var(--primary-light, rgba(22, 93, 255, 0.08));
  color: var(--primary, #165DFF);
}

.action-btn.edit:hover {
  background: var(--primary, #165DFF);
  color: white;
}

.action-btn.delete {
  background: rgba(239, 68, 68, 0.08);
  color: #EF4444;
}

.action-btn.delete:hover {
  background: #EF4444;
  color: white;
}

/* ========== 空状态 ========== */
.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #0F172A);
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  color: var(--text-secondary, #475569);
  margin: 0;
}

/* ========== 对话框 ========== */
:deep(.category-dialog) {
  border-radius: 16px;
}

:deep(.category-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #E2E8F0);
}

:deep(.category-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
}

:deep(.category-dialog .el-dialog__body) {
  padding: 24px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-cancel {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary, #475569);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: var(--bg-secondary, #F8FAFC);
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .categories-container {
    padding: 20px;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
  }

  .page-title {
    font-size: 24px;
  }

  .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .categories-grid {
    grid-template-columns: 1fr;
  }
}
</style>
