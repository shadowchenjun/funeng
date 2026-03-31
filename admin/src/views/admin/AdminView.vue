<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { adminApi } from '../../api/admin'

const admins = ref<any[]>([])
const roles = ref<any[]>([])
const loading = ref(false)
const activeTab = ref('admins')
const dialogVisible = ref(false)
const roleDialogVisible = ref(false)
const dialogTitle = ref('新增管理员')
const isEdit = ref(false)
const currentId = ref('')
const formRef = ref()
const roleFormRef = ref()

const adminForm = ref({
  username: '',
  password: '',
  full_name: '',
  email: '',
  phone: '',
  role_id: ''
})

const roleForm = ref({
  name: '',
  code: '',
  description: '',
  permissions: ''
})

const adminRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const roleRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色代码', trigger: 'blur' }]
}

const fetchData = async () => {
  loading.value = true
  try {
    const [adminRes, roleRes] = await Promise.all([
      adminApi.getAdmins({ page: 1, page_size: 100 }),
      adminApi.getRoles()
    ])
    admins.value = adminRes.items
    roles.value = roleRes
  } catch (e: any) {
    ElMessage.error(e.message || '加载失败')
  } finally {
    loading.value = false
  }
}

const showAddAdmin = () => {
  dialogTitle.value = '新增管理员'
  isEdit.value = false
  adminForm.value = { username: '', password: '', full_name: '', email: '', phone: '', role_id: '' }
  dialogVisible.value = true
}

const handleSubmitAdmin = async () => {
  try {
    await formRef.value.validate()
    await adminApi.createAdmin(adminForm.value)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const handleDeleteAdmin = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' })
    await adminApi.deleteAdmin(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e: any) {
    if (e !== 'cancel') if (e.message) ElMessage.error(e.message)
  }
}

const handleStatusChange = async (admin: any) => {
  try {
    await adminApi.updateAdmin(admin.id, { is_active: !admin.is_active })
    ElMessage.success('状态更新成功')
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

// Role management
const showAddRole = () => {
  isEdit.value = false
  roleForm.value = { name: '', code: '', description: '', permissions: '' }
  roleDialogVisible.value = true
}

const showEditRole = (row: any) => {
  isEdit.value = true
  currentId.value = row.id
  roleForm.value = { ...row }
  roleDialogVisible.value = true
}

const handleSubmitRole = async () => {
  try {
    await roleFormRef.value.validate()
    if (isEdit.value) {
      await adminApi.updateRole(currentId.value, roleForm.value)
      ElMessage.success('更新成功')
    } else {
      await adminApi.createRole(roleForm.value)
      ElMessage.success('创建成功')
    }
    roleDialogVisible.value = false
    fetchData()
  } catch (e: any) {
    if (e.message) ElMessage.error(e.message)
  }
}

const handleDeleteRole = async (id: number) => {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' })
    await adminApi.deleteRole(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e: any) {
    if (e !== 'cancel') if (e.message) ElMessage.error(e.message)
  }
}

onMounted(fetchData)
</script>

<template>
  <div class="admin-view" v-loading="loading">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="管理员" name="admins">
        <div class="toolbar">
          <el-button type="primary" @click="showAddAdmin">新增管理员</el-button>
        </div>
        <el-table :data="admins" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="full_name" label="姓名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column prop="phone" label="电话" />
          <el-table-column prop="role_name" label="角色" />
          <el-table-column prop="last_login" label="最后登录" width="180" />
          <el-table-column prop="is_active" label="状态">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleStatusChange(row)">
                {{ row.is_active ? '禁用' : '启用' }}
              </el-button>
              <el-button link type="danger" @click="handleDeleteAdmin(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="角色" name="roles">
        <div class="toolbar">
          <el-button type="primary" @click="showAddRole">新增角色</el-button>
        </div>
        <el-table :data="roles" stripe>
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
              <el-button link type="primary" @click="showEditRole(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDeleteRole(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form ref="formRef" :model="adminForm" :rules="adminRules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="adminForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="adminForm.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="adminForm.full_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="adminForm.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="adminForm.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="adminForm.role_id" placeholder="请选择角色" style="width: 100%">
            <el-option v-for="r in roles" :key="r.id" :label="r.name" :value="r.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitAdmin">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="roleDialogVisible" :title="isEdit ? '编辑角色' : '新增角色'" width="500px">
      <el-form ref="roleFormRef" :model="roleForm" :rules="roleRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="代码" prop="code">
          <el-input v-model="roleForm.code" placeholder="请输入唯一代码" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="roleForm.description" type="textarea" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="权限">
          <el-input v-model="roleForm.permissions" type="textarea" placeholder="如: user:read,user:write" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitRole">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.admin-view { padding: 20px; }
.toolbar { margin-bottom: 20px; }
</style>
