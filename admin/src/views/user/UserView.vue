<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { userApi } from '../../api/user'

const users = ref<any[]>([])
const groups = ref<any[]>([])
const loading = ref(false)
const activeTab = ref('users')
const dialogVisible = ref(false)
const dialogTitle = ref('新增分组')
const dialogType = ref<'group'>('group')
const formRef = ref()
const isEdit = ref(false)
const currentId = ref('')

const groupForm = ref({
  name: '',
  code: '',
  description: '',
  criteria: ''
})

const groupRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入代码', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const [userRes, groupRes] = await Promise.all([
      userApi.getUsers({ page: 1, page_size: 100 }),
      userApi.getGroups()
    ])
    users.value = userRes.items
    groups.value = groupRes
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const handleStatusChange = async (user: any) => {
  try {
    await userApi.updateUserStatus(user.id, !user.is_active)
    ElMessage.success('状态更新成功')
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const showAddGroup = () => {
  dialogTitle.value = '新增分组'
  dialogType.value = 'group'
  isEdit.value = false
  groupForm.value = { name: '', code: '', description: '', criteria: '' }
  dialogVisible.value = true
}

const showEditGroup = (row: any) => {
  dialogTitle.value = '编辑分组'
  dialogType.value = 'group'
  isEdit.value = true
  currentId.value = row.id
  groupForm.value = { ...row }
  dialogVisible.value = true
}

const handleDeleteGroup = async (row: any) => {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' })
    await userApi.deleteGroup(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e: any) {
    if (e !== 'cancel') if (e.message) ElMessage.error(e.message)
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    if (isEdit.value) {
      await userApi.updateGroup(currentId.value, groupForm.value)
      ElMessage.success('更新成功')
    } else {
      await userApi.createGroup(groupForm.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="user-view" v-loading="loading">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="用户列表" name="users">
        <el-table :data="users" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="full_name" label="姓名" />
          <el-table-column prop="phone" label="手机" />
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="is_admin" label="管理员">
            <template #default="{ row }">
              <el-tag :type="row.is_admin ? 'warning' : 'info'">{{ row.is_admin ? '是' : '否' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" width="180" />
          <el-table-column label="操作" width="150">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleStatusChange(row)">
                {{ row.is_active ? '禁用' : '启用' }}
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="用户分组" name="groups">
        <div class="toolbar">
          <el-button type="primary" @click="showAddGroup">新增分组</el-button>
        </div>
        <el-table :data="groups" stripe>
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="code" label="代码" />
          <el-table-column prop="description" label="描述" />
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180">
            <template #default="{ row }">
              <el-button link type="primary" @click="showEditGroup(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDeleteGroup(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="groupForm" :rules="groupRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="groupForm.name" placeholder="请输入分组名称" />
        </el-form-item>
        <el-form-item label="代码" prop="code">
          <el-input v-model="groupForm.code" placeholder="请输入唯一代码" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="groupForm.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="条件">
          <el-input v-model="groupForm.criteria" type="textarea" placeholder="如: orders_count > 10" />
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
.user-view { padding: 20px; }
.toolbar { margin-bottom: 20px; }
</style>
