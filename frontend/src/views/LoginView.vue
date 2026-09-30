<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <img class="auth-logo" src="/logo-transparent.png" alt="FunEng Logo" @click="$router.push('/')" />
        <h2>用户登录</h2>
        <p class="auth-subtitle">登录赋能平台，进入业务控制台</p>
      </template>
      
      <el-form :model="loginForm" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" :prefix-icon="User" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" :prefix-icon="Lock" placeholder="请输入密码" show-password />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleLogin" :loading="loading" class="auth-btn">
            登录
          </el-button>
        </el-form-item>
        
        <el-form-item>
          <el-button @click="handleRegister" class="auth-btn">
            注册新账户
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度在3-50个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在6-50个字符之间', trigger: 'blur' }
  ]
}

onMounted(() => {
  // 如果已登录，跳转到首页
  if (authStore.isLoggedIn) {
    router.push('/')
  }
})

const handleLogin = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const result = await authStore.login(loginForm.username, loginForm.password)
        
        if (result.success) {
          ElMessage.success('登录成功！')
          // 跳转到之前尝试访问的页面或首页
          const redirect = route.query.redirect as string
          router.push(redirect || '/dashboard')
        } else {
          ElMessage.error(result.message || '登录失败')
        }
      } catch (error) {
        ElMessage.error('登录失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleRegister = () => {
  router.push('/register')
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  background:
    radial-gradient(circle at 20% 0%, rgba(22, 93, 255, 0.10), transparent 45%),
    radial-gradient(circle at 100% 100%, rgba(16, 185, 129, 0.08), transparent 40%),
    var(--bg-secondary);
}

.login-card {
  width: 100%;
  max-width: 400px;
  --el-card-border-radius: var(--radius-lg);
  --el-card-padding: 32px;
  border: 1px solid var(--border-color);
  box-shadow: 0 20px 40px -16px rgba(15, 23, 42, 0.16);
}

.login-card :deep(.el-card__header) {
  padding: 32px 32px 0;
  border-bottom: none;
  text-align: center;
}

.auth-logo {
  width: 72px;
  height: 72px;
  object-fit: contain;
  cursor: pointer;
}

.login-card h2 {
  margin: 8px 0 0;
  font-size: var(--font-lg);
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.auth-subtitle {
  margin: 6px 0 0;
  font-size: var(--font-sm);
  color: var(--text-secondary);
}

.login-card :deep(.el-form-item__label) {
  font-weight: 500;
}

.auth-btn {
  width: 100%;
}

@media (max-width: 768px) {
  .login-container {
    padding: 16px;
  }

  .login-card {
    --el-card-padding: 24px;
  }

  .login-card :deep(.el-card__header) {
    padding: 24px 24px 0;
  }
}
</style>
