<template>
  <div class="categories-container">
    <div class="header">
      <h2>📁 分类管理</h2>
      <el-button type="primary" @click="showAddDialog">
        添加分类
      </el-button>
    </div>
    
    <el-row :gutter="20">
      <el-col :span="8" v-for="category in categories" :key="category.id">
        <el-card class="category-card" :body-style="{ padding: '20px' }">
          <div class="category-icon">
            <el-icon :size="48" :color="category.color">
              <component :is="category.icon" />
            </el-icon>
          </div>
          <div class="category-info">
            <h3>{{ category.name }}</h3>
            <p>产品数量: {{ category.productCount }}</p>
            <p>状态: 
              <el-tag :type="category.status === 'active' ? 'success' : 'info'" size="small">
                {{ category.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </p>
          </div>
          <div class="category-actions">
            <el-button type="primary" link @click="editCategory(category)">
              编辑
            </el-button>
            <el-button type="danger" link @click="deleteCategory(category)">
              删除
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 添加/编辑分类对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '添加分类'" width="400px">
      <el-form :model="categoryForm" label-width="80px">
        <el-form-item label="分类名称">
          <el-input v-model="categoryForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类图标">
          <el-select v-model="categoryForm.icon" placeholder="请选择图标">
            <el-option label="水果" value="Apple" />
            <el-option label="蔬菜" value="Food" />
            <el-option label="粮食" value="Rice" />
            <el-option label="畜牧" value="Chicken" />
            <el-option label="其他" value="Box" />
          </el-select>
        </el-form-item>
        <el-form-item label="颜色">
          <el-color-picker v-model="categoryForm.color" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="categoryForm.status" active-text="启用" inactive-text="禁用" />
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
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Apple, Food, Rice, Chicken, Box } from '@element-plus/icons-vue'

interface Category {
  id: number
  name: string
  icon: string
  color: string
  productCount: number
  status: string
}

const categories = ref<Category[]>([
  { id: 1, name: '水果', icon: 'Apple', color: '#f56c6c', productCount: 25, status: 'active' },
  { id: 2, name: '蔬菜', icon: 'Food', color: '#67c23a', productCount: 42, status: 'active' },
  { id: 3, name: '粮食', icon: 'Rice', color: '#e6a23c', productCount: 18, status: 'active' },
  { id: 4, name: '畜牧', icon: 'Chicken', color: '#909399', productCount: 12, status: 'active' },
  { id: 5, name: '其他', icon: 'Box', color: '#409eff', productCount: 8, status: 'active' }
])

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
  Object.assign(categoryForm, category)
  dialogVisible.value = true
}

const saveCategory = () => {
  if (isEdit.value && editingId.value) {
    const index = categories.value.findIndex(c => c.id === editingId.value)
    if (index !== -1) {
      categories.value[index] = { ...categoryForm, id: editingId.value, productCount: categories.value[index].productCount }
    }
    ElMessage.success('分类更新成功！')
  } else {
    const newId = Math.max(...categories.value.map(c => c.id)) + 1
    categories.value.push({ ...categoryForm, id: newId, productCount: 0 })
    ElMessage.success('分类添加成功！')
  }
  dialogVisible.value = false
}

const deleteCategory = async (category: Category) => {
  try {
    await ElMessageBox.confirm(`确定要删除分类 "${category.name}" 吗？`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const index = categories.value.findIndex(c => c.id === category.id)
    if (index !== -1) {
      categories.value.splice(index, 1)
      ElMessage.success('分类删除成功！')
    }
  } catch {
    // 用户取消
  }
}
</script>

<style scoped>
.categories-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  font-size: 24px;
  color: #303133;
}

.category-card {
  margin-bottom: 20px;
  border-radius: 12px;
  transition: transform 0.3s, box-shadow 0.3s;
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.category-icon {
  text-align: center;
  padding: 20px 0;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  border-radius: 8px;
  margin-bottom: 15px;
}

.category-info {
  text-align: center;
}

.category-info h3 {
  margin: 0 0 10px;
  font-size: 18px;
  color: #303133;
}

.category-info p {
  margin: 5px 0;
  color: #909399;
  font-size: 14px;
}

.category-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}
</style>
