<template>
  <div class="page-container">
    <PageHeader title="产品管理" subtitle="管理您的农产品库存与销售">
      <template v-if="isAdmin" #actions>
        <el-button type="primary" :icon="Plus" @click="showAddDialog">添加产品</el-button>
      </template>
    </PageHeader>

    <!-- 搜索和筛选 -->
    <div class="filters-bar">
      <el-input
        v-model="searchQuery"
        class="search-input"
        :prefix-icon="Search"
        placeholder="搜索产品名称"
        clearable
        @input="fetchProducts"
      />
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

    <el-alert v-if="loadError" :title="loadError" type="error" show-icon :closable="false" class="load-error" />

    <!-- 产品列表 -->
    <div class="products-content">
      <!-- 桌面端：表格视图 -->
      <div class="products-table-desktop">
        <el-table :data="products" v-loading="loading" :empty-text="loading ? '正在加载产品…' : '暂无产品'">
          <el-table-column prop="name" label="产品名称" min-width="150">
            <template #default="{ row }">
              <div class="product-name-cell">
                <el-image v-if="row.image_url" :src="row.image_url" fit="cover" class="product-thumb" />
                <span v-else class="product-thumb product-thumb-empty">暂无图片</span>
                <span class="product-name">{{ row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="category_name" label="分类" width="120">
            <template #default="{ row }">
              <el-tag type="info">{{ row.category_name || '未分类' }}</el-tag>
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
              <el-tag :type="row.is_active === 1 ? 'success' : 'info'">
                {{ row.is_active === 1 ? '在售' : '停售' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="130" fixed="right">
            <template #default="{ row }">
              <template v-if="isAdmin">
                <el-button type="primary" link @click="editProduct(row)">编辑</el-button>
                <el-button type="danger" link @click="deleteProduct(row)">删除</el-button>
              </template>
              <span v-else class="no-permission">-</span>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="!loading && !loadError" class="pagination-wrapper">
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
        <div v-if="loading" class="mobile-state">正在加载产品…</div>
        <div v-else-if="!loadError && products.length === 0" class="mobile-state">暂无产品</div>
        <div
          v-for="product in products"
          :key="product.id"
          class="product-card"
          :class="{ 'clickable': isAdmin }"
          @click="isAdmin && editProduct(product)"
        >
          <el-image v-if="product.image_url" :src="product.image_url" fit="cover" class="card-thumb" />
          <span v-else class="card-thumb product-thumb-empty">暂无图片</span>
          <div class="card-info">
            <h3 class="card-name">{{ product.name }}</h3>
            <div class="card-meta">
              <el-tag type="info">{{ product.category_name || '未分类' }}</el-tag>
              <span class="price-value">¥{{ product.price }}/{{ product.unit }}</span>
            </div>
            <div class="card-footer">
              <span class="stock-info">库存: {{ product.stock }}</span>
              <el-tag :type="product.is_active === 1 ? 'success' : 'info'">
                {{ product.is_active === 1 ? '在售' : '停售' }}
              </el-tag>
            </div>
          </div>
        </div>

        <div v-if="!loading && !loadError" class="pagination-mobile">
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
      class="dialog-md"
    >
      <el-form :model="productForm" label-width="80px">
        <el-form-item label="产品名称" required>
          <el-input v-model="productForm.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="产品分类">
          <el-select v-model="productForm.category_id" placeholder="选择分类" class="w-full">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="价格">
              <el-input-number v-model="productForm.price" :min="0" :precision="2" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="单位">
              <el-input v-model="productForm.unit" placeholder="斤/箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="库存">
          <el-input-number v-model="productForm.stock" :min="0" class="w-full" />
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
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { dataVersions } from '../utils/dataVersion'
import { useFreshOnActivate } from '../composables/useFreshOnActivate'
import { Plus, Search } from '@element-plus/icons-vue'
import axios from 'axios'
import ImageUpload from '../components/ImageUpload.vue'
import { useAuthStore } from '../stores/auth'
import { getErrorMessage } from '../utils/error'

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
const loading = ref(true)
const loadError = ref('')
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

// keep-alive 缓存：分类页新增分类、其他页改动产品后，回到本页自动刷新；无变化则保留筛选与分页
const loadAll = async () => {
  await Promise.all([fetchProducts(), fetchCategories()])
  fresh.markFresh()
}
const fresh = useFreshOnActivate(['products', 'categories'], loadAll)

onMounted(() => {
  window.scrollTo(0, 0)
  loadAll()
})

const fetchProducts = async () => {
  loading.value = true
  loadError.value = ''
  products.value = []
  total.value = 0
  try {
    const params: Record<string, string | number> = {
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
    products.value = []
    total.value = 0
    loadError.value = '产品加载失败，请稍后重试'
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
    dataVersions.bump('products')
    await fetchProducts()
    fresh.markFresh()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '操作失败'))
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
    dataVersions.bump('products')
    await fetchProducts()
    fresh.markFresh()
  } catch (e) {
    // 确认框点「取消」以 'cancel' 拒绝，不提示；真正的删除失败需要提示
    if (e !== 'cancel') ElMessage.error(getErrorMessage(e, '删除失败'))
  }
}
</script>

<style scoped>
.filters-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.category-select {
  width: 180px;
}

.load-error {
  margin-bottom: 16px;
}

.products-content {
  overflow: hidden;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}

.products-cards-mobile {
  display: none;
}

.product-name-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-thumb {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border-radius: var(--radius-sm);
  object-fit: cover;
}

.product-thumb-empty {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--text-tertiary);
  text-align: center;
  background: var(--bg-secondary);
}

.product-name {
  font-weight: 500;
  color: var(--text-primary);
}

.price-value {
  font-weight: 600;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 20px;
  border-top: 1px solid var(--border-color);
}

.mobile-state {
  padding: 24px;
  color: var(--text-secondary);
  text-align: center;
}

@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
    gap: 12px;
    margin-bottom: 16px;
  }

  .search-input {
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
    margin-bottom: 12px;
    padding: 16px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    transition: border-color 0.2s ease;
  }

  .product-card.clickable {
    cursor: pointer;
  }

  .product-card.clickable:hover {
    border-color: var(--primary);
  }

  .card-thumb {
    width: 72px;
    height: 72px;
    flex-shrink: 0;
    border-radius: var(--radius-sm);
    object-fit: cover;
  }

  .card-info {
    flex: 1;
    min-width: 0;
  }

  .card-name {
    margin: 0 0 8px;
    overflow: hidden;
    font-size: var(--font-md);
    font-weight: 600;
    color: var(--text-primary);
    white-space: nowrap;
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
    align-items: center;
    justify-content: space-between;
  }

  .stock-info {
    font-size: var(--font-xs);
    color: var(--text-secondary);
  }

  .pagination-mobile {
    display: flex;
    justify-content: center;
    padding-top: 16px;
  }
}
</style>
