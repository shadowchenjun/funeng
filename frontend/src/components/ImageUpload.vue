<template>
  <div class="image-upload">
    <div class="upload-area" @click="triggerFileInput" @drop.prevent="handleDrop" @dragover.prevent>
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        @change="handleFileChange"
        style="display: none"
      />
      
      <template v-if="!imageUrl && !previewUrl">
        <el-icon class="upload-icon"><Plus /></el-icon>
        <div class="upload-text">点击或拖拽上传图片</div>
        <div class="upload-hint">支持 jpg, png, gif, webp 格式</div>
      </template>
      
      <template v-else>
        <div class="image-preview">
          <img :src="previewUrl || imageUrl" alt="预览图片" />
          <div class="image-overlay">
            <el-button type="danger" link @click.stop="removeImage">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </template>
    </div>
    
    <div v-if="uploading" class="upload-progress">
      <el-progress :percentage="uploadProgress" status="success" />
    </div>
    
    <div v-if="error" class="upload-error">
      <el-alert :title="error" type="error" :closable="false" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps<{
  modelValue?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const fileInput = ref<HTMLInputElement>()
const imageUrl = ref(props.modelValue || '')
const previewUrl = ref('')
const uploading = ref(false)
const uploadProgress = ref(0)
const error = ref('')

// 监听 v-model 变化
watch(() => props.modelValue, (newVal) => {
  imageUrl.value = newVal || ''
})

function triggerFileInput() {
  if (!uploading.value) {
    fileInput.value?.click()
  }
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    uploadFile(files[0])
  }
}

function handleDrop(event: DragEvent) {
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    if (file.type.startsWith('image/')) {
      uploadFile(file)
    } else {
      error.value = '请上传图片文件'
      setTimeout(() => { error.value = '' }, 3000)
    }
  }
}

async function uploadFile(file: File) {
  // 验证文件大小 (最大 5MB)
  if (file.size > 5 * 1024 * 1024) {
    error.value = '图片大小不能超过 5MB'
    setTimeout(() => { error.value = '' }, 3000)
    return
  }

  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    error.value = '仅支持 jpg, png, gif, webp 格式'
    setTimeout(() => { error.value = '' }, 3000)
    return
  }

  // 生成预览
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)

  // 上传文件
  uploading.value = true
  error.value = ''
  uploadProgress.value = 0

  try {
    const formData = new FormData()
    formData.append('file', file)

    const token = localStorage.getItem('token')
    
    const response = await axios.post('/api/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total) {
          uploadProgress.value = Math.round((progressEvent.loaded / progressEvent.total) * 100)
        }
      }
    })

    const { url } = response.data
    imageUrl.value = url
    emit('update:modelValue', url)
    
    ElMessage.success('图片上传成功')
  } catch (err: any) {
    error.value = err.response?.data?.detail || '上传失败，请重试'
    previewUrl.value = ''
    setTimeout(() => { error.value = '' }, 3000)
  } finally {
    uploading.value = false
    uploadProgress.value = 0
    // 清空 input 以便可以再次选择同一文件
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

function removeImage() {
  imageUrl.value = ''
  previewUrl.value = ''
  emit('update:modelValue', '')
}

// 暴露方法供父组件调用
defineExpose({
  uploadFile,
  removeImage
})
</script>

<style scoped>
.image-upload {
  width: 100%;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.upload-area:hover {
  border-color: #409eff;
  background: #f0f7ff;
}

.upload-icon {
  font-size: 48px;
  color: #8c939d;
  margin-bottom: 10px;
}

.upload-text {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.image-preview {
  position: relative;
  max-width: 100%;
  max-height: 300px;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  object-fit: contain;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s;
  border-radius: 8px;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

.image-overlay .el-button {
  color: white;
  font-size: 14px;
}

.upload-progress {
  margin-top: 15px;
}

.upload-error {
  margin-top: 10px;
}
</style>
