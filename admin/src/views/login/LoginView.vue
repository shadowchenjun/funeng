<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)

const handleLogin = async () => {
  if (!form.value.username || !form.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-bg">
      <div class="login-box">
        <div class="login-header">
          <h1 class="title">汤原农文旅云</h1>
          <p class="subtitle">后台管理系统</p>
        </div>
        <el-form :model="form" class="login-form">
          <el-form-item>
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              prefix-icon="User"
              size="large"
              class="login-input"
            />
          </el-form-item>
          <el-form-item>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              prefix-icon="Lock"
              size="large"
              class="login-input"
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
        <div class="tips">
          <p>默认账号: admin / admin123456</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 50%, #409eff 100%);
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.login-box {
  width: 420px;
  padding: 50px 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  position: relative;
  z-index: 1;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.title {
  font-size: 32px;
  color: #1e3a5f;
  margin-bottom: 8px;
  font-weight: 700;
  letter-spacing: 2px;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.login-form {
  margin-top: 20px;
}

.login-input :deep(.el-input__wrapper) {
  padding: 16px 20px;
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
}

.login-input :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.login-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2) inset, 0 0 0 1px #409eff inset;
}

.login-btn {
  width: 100%;
  height: 50px;
  font-size: 18px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409eff 0%, #3a8bd9 100%);
  border: none;
  font-weight: 600;
  letter-spacing: 4px;
}

.login-btn:hover {
  background: linear-gradient(135deg, #66b1ff 0%, #409eff 100%);
}

.tips {
  text-align: center;
  margin-top: 24px;
  color: #999;
  font-size: 13px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}
</style>
