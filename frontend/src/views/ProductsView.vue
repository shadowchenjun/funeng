<template>
  <div class="products-container">
    <!-- 移动端：紧凑表头 -->
    <div class="header-mobile">
      <h2>📦 产品</h2>
      <el-button type="primary" size="small" @click="showAddDialog">+</el-button>
    </div>
    
    <!-- 移动端：紧凑筛选 -->
    <div class="filter-mobile">
      <el-input 
        v-model="searchQuery" 
        placeholder="搜索..." 
        size="small" 
        clearable 
        @input="fetchProducts" 
        style="width: 60%;"
      />
      <el-select 
        v-model="categoryFilter" 
        placeholder="分类" 
        size="small" 
        clearable 
        @change="fetchProducts"
        style="width: 38%;"
      >
        <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
      </el-select>
    </div>
    
    <!-- 移动端：卡片列表 -->
    <div class="product-cards-mobile">
      <el-card 
        v-for="product in products" 
        :key="product.id" 
        class="product-card-mobile"
        @click="editProduct(product)"
      >
        <div class="card-content">
          <el-image 
            :src="product.image_url" 
            fit="cover"
            class="product-thumb"
          />
          <div class="product-info">
            <div class="product-name">{{ product.name }}</div>
            <div class="product-meta">
              <el-tag size="small" type="success">{{ product.category_name || '未分类' }}</el-tag>
              <span class="price">¥{{ product.price }}/{{ product.unit }}</span>
            </div>
            <div class="product-stock">
              库存: {{ product.stock }}
              <el-tag size="small" :type="product.is_active === 1 ? 'success' : 'info'" style="margin-left: 8px;">
                {{ product.is_active === 1 ? '在售' : '停售' }}
              </el-tag>
            </div>
          </div>
          <div class="card-actions" @click.stop>
            <el-button type="primary" link size="small">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteProduct(product)">删</el-button>
          </div>
        </div>
      </el-card>
    </div>
    
    <!-- 桌面端：表格视图 -->
    <div class="products-table-desktop">
      <!-- 桌面端：搜索和筛选工具栏 -->
      <div class="desktop-toolbar">
        <el-input 
          v-model="searchQuery" 
          placeholder="搜索产品名称..." 
          size="default" 
          clearable 
          @input="fetchProducts" 
          style="width: 300px;"
        >
          <template #prefix>🔍</template>
        </el-input>
        <el-select 
          v-model="categoryFilter" 
          placeholder="全部分类" 
          size="default" 
          clearable 
          @change="fetchProducts"
          style="width: 180px; margin-left: 10px;"
        >
          <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
        </el-select>
        <el-button type="primary" style="margin-left: 10px;" @click="showAddDialog">+ 添加产品</el-button>
      </div>
      
      <el-table :data="products" stripe style="width: 100%; margin-top: 15px;">
        <el-table-column prop="name" label="产品名称" min-width="150" />
        <el-table-column label="图片" width="80">
          <template #default="{ row }">
            <el-image 
              :src="row.image_url" 
              fit="cover"
              style="width: 50px; height: 50px; border-radius: 4px;"
            />
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ row.price }}/{{ row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="row.is_active === 1 ? 'success' : 'info'">
              {{ row.is_active === 1 ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editProduct(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteProduct(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="fetchProducts"
        style="margin-top: 20px; justify-content: center;"
      />
    </div>
    
    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="fetchProducts"
        small
      />
    </div>
    
    <!-- 添加/编辑产品对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑产品' : '添加产品'" width="95%" class="mobile-dialog">
      <el-form :model="productForm" label-width="70px" size="small">
        <el-form-item label="名称" required>
          <el-input v-model="productForm.name" placeholder="产品名称" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="productForm.category_id" placeholder="选择分类" style="width: 100%">
            <el-option v-for="cat in categories" :key="cat.id" :label="cat.name" :value="cat.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="价格" required style="margin-bottom: 10px;">
              <el-input-number v-model="productForm.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" style="margin-bottom: 10px;">
              <el-input v-model="productForm.unit" placeholder="斤/箱" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="库存" style="margin-bottom: 10px;">
          <el-input-number v-model="productForm.stock" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="图片">
          <ImageUpload v-model="productForm.image_url" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="productForm.is_active" :active-value="1" :inactive-value="0" active-text="在售" inactive-text="停售" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveProduct" :loading="saving" size="small">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import ImageUpload from '../components/ImageUpload.vue'

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
const pageSize = ref(20)
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
    products.value = response.data
    total.value = response.data.length
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
  padding: 8px;
}

/* 移动端表头 */
.header-mobile {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.header-mobile h2 {
  font-size: 16px;
  margin: 0;
}

/* 移动端筛选 */
.filter-mobile {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

/* 移动端卡片列表 */
.product-cards-mobile {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.product-card-mobile {
  margin-bottom: 0;
  border-radius: 8px;
}

.product-card-mobile :deep(.el-card__body) {
  padding: 10px;
}

.card-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.product-thumb {
  width: 50px;
  height: 50px;
  border-radius: 6px;
  flex-shrink: 0;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.product-meta .price {
  color: #f56c6c;
  font-weight: bold;
  font-size: 13px;
}

.product-stock {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}

.card-actions {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex-shrink: 0;
}

.pagination {
  margin-top: 10px;
  display: flex;
  justify-content: center;
}

/* 默认隐藏桌面表格 */
.products-table-desktop {
  display: none;
}

/* 桌面端工具栏 */
.desktop-toolbar {
  display: none;
  align-items: center;
  padding: 15px 0;
  flex-wrap: wrap;
  gap: 10px;
}

@media (min-width: 769px) {
  /* 桌面端使用表格 */
  .header-mobile,
  .filter-mobile,
  .product-cards-mobile {
    display: none;
  }
  
  .products-container {
    padding: 20px;
  }
  
  .products-table-desktop {
    display: block;
  }
  
  .desktop-toolbar {
    display: flex;
  }
  
  .pagination {
    display: none;
  }
}

/* 对话框移动端 */
.mobile-dialog :deep(.el-dialog__body) {
  padding: 10px;
}
</style>
