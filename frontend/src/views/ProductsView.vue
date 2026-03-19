<template>
  <div class="products-container">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">📦 产品管理</h1>
        <p class="page-subtitle">管理您的农产品库存与销售</p>
      </div>
      <div class="header-right" v-if="isAdmin">
        <button class="btn-primary" @click="showAddDialog">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          添加产品
        </button>
      </div>
    </header>

    <!-- 搜索和筛选 -->
    <div class="filters-bar">
      <div class="search-wrapper">
        <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/>
          <path d="M21 21l-4.35-4.35"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="搜索产品名称..."
          @input="fetchProducts"
        />
      </div>
      <el-select
        v-model="categoryFilter"
        placeholder="全部分类"
        clearable
        @change="fetchProducts"
        class="category-select"
      >
        <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
      </el-select>
    </div>

    <!-- 产品列表 -->
    <div class="products-content">
      <!-- 桌面端：表格视图 -->
      <div class="products-table-desktop">
        <el-table :data="products" stripe style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="产品名称" min-width="150">
            <template #default="{ row }">
              <div class="product-name-cell">
                <el-image :src="row.image_url" fit="cover" class="product-thumb" />
                <span class="product-name">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="category_name" label="分类" width="120">
            <template #default="{ row }">
              <span class="category-tag">{{ row.category_name || '未分类' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="price" label="价格" width="140">
            <template #default="{ row }">
              <span class="price-value">¥{{ row.price }}/{{ row.unit }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="stock" label="库存" width="100" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <span :class="['status-badge', row.is_active === 1 ? 'active' : 'inactive']">
                {{ row.is_active === 1 ? '在售' : '停售' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="140" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons" v-if="isAdmin">
                <button class="action-btn edit" @click="editProduct(row)">编辑</button>
                <button class="action-btn delete" @click="deleteProduct(row)">删除</button>
              </div>
              <span v-else class="no-permission">-</span>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrapper">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="fetchProducts"
          />
        </div>
      </div>

      <!-- 移动端：卡片视图 -->
      <div class="products-cards-mobile">
        <div
          v-for="product in products"
          :key="product.id"
          class="product-card"
          :class="{ 'clickable': isAdmin }"
          @click="isAdmin && editProduct(product)"
        >
          <el-image :src="product.image_url" fit="cover" class="card-thumb" />
          <div class="card-info">
            <h3 class="card-name">{{ product.name }}</h3>
            <div class="card-meta">
              <span class="category-tag">{{ product.category_name || '未分类' }}</span>
              <span class="price-value">¥{{ product.price }}/{{ product.unit }}</span>
            </div>
            <div class="card-footer">
              <span class="stock-info">库存: {{ product.stock }}</span>
              <span :class="['status-badge', product.is_active === 1 ? 'active' : 'inactive']">
                {{ product.is_active === 1 ? '在售' : '停售' }}
              </span>
            </div>
          </div>
        </div>

        <div class="pagination-mobile">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="total"
            layout="prev, pager, next"
            small
            @current-change="fetchProducts"
          />
        </div>
      </div>
    </div>

    <!-- 添加/编辑产品对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑产品' : '添加产品'"
      width="90%"
      class="product-dialog"
    >
      <el-form :model="productForm" label-width="80px" size="default">
        <el-form-item label="产品名称" required>
          <el-input v-model="productForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="产品分类">
          <el-select v-model="productForm.category_id" placeholder="选择分类" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="价格">
              <el-input-number v-model="productForm.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="productForm.unit" placeholder="斤/箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="库存">
          <el-input-number v-model="productForm.stock" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="产品图片">
          <ImageUpload v-model="productForm.image_url" />
        </el-form-item>
        <el-form-item label="产品状态">
          <el-switch
            v-model="productForm.is_active"
            :active-value="1"
            :inactive-value="0"
            active-text="在售"
            inactive-text="停售"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <button class="btn-cancel" @click="dialogVisible = false">取消</button>
          <button class="btn-primary" @click="saveProduct" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import ImageUpload from '../components/ImageUpload.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)

interface Product {
  id: number
  name: string
  description?: string
  price: number
  unit: string
  stock: number
  image_url?: string
  category_id?: number
  category_name?: string
  origin?: string
  brand?: string
  is_active: number
}

interface Category {
  id: number
  name: string
}

const products = ref<Product[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const categoryFilter = ref<number | undefined>(undefined)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number>()
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const productForm = reactive({
  name: '',
  description: '',
  price: 0,
  unit: '斤',
  stock: 0,
  image_url: '',
  category_id: undefined as number | undefined,
  origin: '',
  brand: '',
  is_active: 1
})

const API_BASE = '/api'

onMounted(() => {
  window.scrollTo(0, 0)
  fetchProducts()
  fetchCategories()
})

const fetchProducts = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (categoryFilter.value !== undefined && categoryFilter.value !== null) {
      params.category_id = categoryFilter.value
    }

    const response = await axios.get(`${API_BASE}/products/`, { params })
    products.value = response.data.items
    total.value = response.data.total
  } catch (error) {
    console.error('获取产品列表失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const response = await axios.get(`${API_BASE}/categories/`)
    categories.value = response.data
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(productForm, {
    name: '',
    description: '',
    price: 0,
    unit: '斤',
    stock: 0,
    image_url: '',
    category_id: undefined,
    origin: '',
    brand: '',
    is_active: 1
  })
  dialogVisible.value = true
}

const editProduct = (product: Product) => {
  isEdit.value = true
  editingId.value = product.id
  Object.assign(productForm, {
    name: product.name,
    description: product.description || '',
    price: product.price,
    unit: product.unit,
    stock: product.stock,
    image_url: product.image_url || '',
    category_id: product.category_id,
    origin: product.origin || '',
    brand: product.brand || '',
    is_active: product.is_active
  })
  dialogVisible.value = true
}

const saveProduct = async () => {
  if (!productForm.name || productForm.price <= 0) {
    ElMessage.warning('请填写产品名称和价格')
    return
  }

  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      await axios.put(`${API_BASE}/products/${editingId.value}`, productForm)
      ElMessage.success('产品更新成功！')
    } else {
      await axios.post(`${API_BASE}/products/`, productForm)
      ElMessage.success('产品添加成功！')
    }
    dialogVisible.value = false
    fetchProducts()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  } finally {
    saving.value = false
  }
}

const deleteProduct = async (product: Product) => {
  try {
    await ElMessageBox.confirm(`确定删除 "${product.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`${API_BASE}/products/${product.id}`)
    ElMessage.success('删除成功')
    fetchProducts()
  } catch {
    // 取消
  }
}
</script>

<style scoped>
.products-container {
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
  margin-bottom: 24px;
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

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark, #0F4AE6);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary svg {
  width: 18px;
  height: 18px;
}

/* ========== 搜索筛选 ========== */
.filters-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.search-wrapper {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  color: var(--text-tertiary, #94A3B8);
}

.search-input {
  width: 100%;
  padding: 12px 14px 12px 44px;
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 10px;
  font-size: 14px;
  background: var(--bg-primary, #FFFFFF);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary, #165DFF);
  box-shadow: 0 0 0 3px var(--primary-light, rgba(22, 93, 255, 0.08));
}

.search-input::placeholder {
  color: var(--text-tertiary, #94A3B8);
}

.category-select {
  width: 180px;
}

/* ========== 产品内容区 ========== */
.products-content {
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 16px;
  overflow: hidden;
}

.products-table-desktop {
  display: block;
}

.products-cards-mobile {
  display: none;
}

/* ========== 表格样式 ========== */
.product-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-thumb {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  object-fit: cover;
}

.product-name {
  font-weight: 500;
  color: var(--text-primary, #0F172A);
}

.category-tag {
  display: inline-block;
  padding: 4px 10px;
  background: var(--bg-secondary, #F8FAFC);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary, #475569);
}

.price-value {
  font-weight: 600;
  color: #EF4444;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.status-badge.inactive {
  background: rgba(148, 163, 184, 0.15);
  color: #64748B;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
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

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px;
  border-top: 1px solid var(--border-color, #E2E8F0);
}

/* ========== 移动端卡片 ========== */
@media (max-width: 768px) {
  .products-container {
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

  .filters-bar {
    flex-direction: column;
  }

  .search-wrapper {
    max-width: none;
  }

  .category-select {
    width: 100%;
  }

  .products-table-desktop {
    display: none;
  }

  .products-cards-mobile {
    display: block;
    padding: 16px;
  }

  .product-card {
    display: flex;
    gap: 12px;
    padding: 16px;
    background: var(--bg-primary, #FFFFFF);
    border: 1px solid var(--border-color, #E2E8F0);
    border-radius: 12px;
    margin-bottom: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .product-card:hover {
    border-color: var(--primary, #165DFF);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }

  .card-thumb {
    width: 72px;
    height: 72px;
    border-radius: 8px;
    object-fit: cover;
    flex-shrink: 0;
  }

  .card-info {
    flex: 1;
    min-width: 0;
  }

  .card-name {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary, #0F172A);
    margin: 0 0 8px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .card-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
  }

  .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .stock-info {
    font-size: 13px;
    color: var(--text-secondary, #475569);
  }

  .pagination-mobile {
    display: flex;
    justify-content: center;
    padding-top: 16px;
  }
}

/* ========== 对话框 ========== */
:deep(.product-dialog) {
  border-radius: 16px;
}

:deep(.product-dialog .el-dialog__header) {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color, #E2E8F0);
}

:deep(.product-dialog .el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
}

:deep(.product-dialog .el-dialog__body) {
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
</style>
