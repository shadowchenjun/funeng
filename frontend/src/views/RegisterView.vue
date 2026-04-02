<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <h2>用户注册</h2>
      </template>
      
      <el-form :model="registerForm" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="registerForm.username" prefix-icon="User" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="registerForm.email" prefix-icon="Message" placeholder="请输入邮箱" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="registerForm.password" type="password" prefix-icon="Lock" placeholder="请输入密码" show-password />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="registerForm.confirmPassword" type="password" prefix-icon="Lock" placeholder="请确认密码" show-password />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" style="width: 100%">
            注册
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <el-link type="primary" @click="$router.push('/login')">
            已有账户？立即登录
          </el-link>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePassword = (_rule: any, value: any, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3-50个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在6-50个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePassword, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 调用后端API注册
        const result = await authStore.register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          full_name: registerForm.username
        })
        
        if (result.success) {
          ElMessage.success('注册成功！请登录')
          router.push('/login')
        } else {
          ElMessage.error(result.message || '注册失败')
        }
      } catch (error: any) {
        ElMessage.error(error.message || '注册失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 400px;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.register-card :deep(.el-card__header) {
  text-align: center;
  padding: 30px 20px;
  border-bottom: 1px solid #ebeef5;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.register-card h2 {
  color: white;
  margin: 0;
  font-size: 24px;
}

.register-card :deep(.el-form-item__label) {
  font-weight: 500;
}
</style>
