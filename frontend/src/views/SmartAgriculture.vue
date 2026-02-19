<template>
  <div class="smart-agri-container">
    <div class="header-mobile">
      <h2>🌱 智慧农业</h2>
    </div>
    
    <!-- 快捷入口 -->
    <el-row :gutter="10" class="quick-nav">
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'land'">
          <el-icon><MapLocation /></el-icon>
          <span>地块管理</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'farm'">
          <el-icon><OfficeBuilding /></el-icon>
          <span>农场信息</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'crop'">
          <el-icon><Grape /></el-icon>
          <span>作物管理</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'device'">
          <el-icon><Cpu /></el-icon>
          <span>物联网设备</span>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10" class="quick-nav">
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'monitor'">
          <el-icon><DataAnalysis /></el-icon>
          <span>环境监测</span>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 地块管理 -->
    <el-card v-if="activeTab === 'land'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🗺️ 地块管理</span>
          <el-button type="primary" size="small" @click="showLandDialog()">+ 添加地块</el-button>
        </div>
      </template>
      
      <!-- 统计 -->
      <el-row :gutter="10" class="stats-row">
        <el-col :span="8">
          <div class="stat-box">
            <span class="num">{{ lands.length }}</span>
            <span class="label">地块数</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-box">
            <span class="num">{{ totalLandArea }}</span>
            <span class="label">总面积(亩)</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-box">
            <span class="num">{{ lands.filter(l => l.status === 'normal').length }}</span>
            <span class="label">正常</span>
          </div>
        </el-col>
      </el-row>
      
      <div class="land-grid">
        <el-card v-for="land in lands" :key="land.id" class="land-card">
          <div class="land-info">
            <h4>{{ land.name }}</h4>
            <p>🏠 农场: {{ land.farm_name || '未分配' }}</p>
            <p>📐 面积: {{ land.area }}亩</p>
            <p>🌾 作物: {{ land.crops && land.crops.length ? land.crops.join(', ') : (land.crop || '未设置') }}</p>
            <p>状态: 
              <el-tag size="small" :type="land.status === 'normal' ? 'success' : 'warning'">
                {{ land.status === 'normal' ? '正常' : '预警' }}
              </el-tag>
            </p>
          </div>
          <div class="land-actions">
            <el-button type="primary" link size="small" @click="editLand(land)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteLand(land)">删除</el-button>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 作物管理 -->
    <el-card v-if="activeTab === 'crop'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🌾 作物管理</span>
          <el-button type="primary" size="small" @click="showCropDialog()">+ 添加作物</el-button>
        </div>
      </template>
      
      <div class="crop-list">
        <el-card v-for="crop in crops" :key="crop.id" class="crop-card">
          <div class="crop-header">
            <el-icon :size="24" color="#67C23A"><Grape /></el-icon>
            <div class="crop-info">
              <h4>{{ crop.name }}</h4>
              <p>分类: {{ crop.category }} | 种植季节: {{ crop.planting_season }}</p>
            </div>
          </div>
          <div class="crop-details">
            <span>🌱 生长周期: {{ crop.growth_days }}天</span>
            <span>📈 亩产量: {{ crop.yield_per_mu }}斤</span>
            <el-tag size="small" :type="crop.status === 'active' ? 'success' : 'info'">
              {{ crop.status === 'active' ? '活跃' : '停用' }}
            </el-tag>
          </div>
          <div class="crop-actions">
            <el-button type="primary" link size="small" @click="editCrop(crop)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteCrop(crop)">删除</el-button>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 农场管理 -->
    <el-card v-if="activeTab === 'farm'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🏠 农场管理</span>
          <el-button type="primary" size="small" @click="showFarmDialog()">+ 添加农场</el-button>
        </div>
      </template>
      
      <!-- 农场选择器 -->
      <div v-if="farms.length > 1" class="farm-selector">
        <el-select v-model="currentFarmId" placeholder="选择农场" @change="onFarmChange" style="width: 100%; margin-bottom: 10px;">
          <el-option v-for="f in farms" :key="f.id" :label="f.name" :value="f.id" />
        </el-select>
      </div>
      
      <!-- 当前农场详情 -->
      <div v-if="currentFarm" class="farm-detail">
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="农场名称">{{ currentFarm.name }}</el-descriptions-item>
          <el-descriptions-item label="农场地址">{{ currentFarm.address }}</el-descriptions-item>
          <el-descriptions-item label="总面积">{{ currentFarm.totalArea }}亩</el-descriptions-item>
          <el-descriptions-item label="地块数量">{{ currentFarm.landCount }}块</el-descriptions-item>
          <el-descriptions-item label="负责人">{{ currentFarm.manager }}</el-descriptions-item>
          <el-descriptions-item label="联系电话">{{ currentFarm.phone }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentFarm.status === 'normal' ? 'success' : 'warning'" size="small">
              {{ currentFarm.status === 'normal' ? '正常' : '预警' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="farm-actions" style="margin-top: 10px;">
          <el-button type="primary" size="small" @click="editFarm(currentFarm)">编辑</el-button>
          <el-button type="danger" size="small" @click="deleteFarm(currentFarm)">删除农场</el-button>
        </div>
        
        <el-divider>地图概览</el-divider>
        <div class="farm-map">
          <iframe 
            width="100%" 
            height="200" 
            frameborder="0" 
            scrolling="no" 
            src="https://www.openstreetmap.org/export/embed.html?bbox=117.0%2C36.5%2C117.3%2C36.8&amp;layer=mapnik&amp;marker=36.65%2C117.12"
            style="border-radius: 8px;">
          </iframe>
          <p class="coords">{{ currentFarm.coords }}</p>
        </div>
        
        <!-- 该农场下的地块 -->
        <el-divider>所属地块 ({{ lands.filter(l => l.farm_id === currentFarm.id).length }})</el-divider>
        <div class="farm-lands">
          <el-tag v-for="land in lands.filter(l => l.farm_id === currentFarm.id)" :key="land.id" style="margin: 5px;">
            {{ land.name }} ({{ land.area }}亩)
          </el-tag>
          <div v-if="lands.filter(l => l.farm_id === currentFarm.id).length === 0" class="empty-tip">
            暂无地块，请添加
          </div>
        </div>
      </div>
    </el-card>
    
    <!-- 物联网设备 -->
    <el-card v-if="activeTab === 'device'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>📡 物联网设备</span>
          <el-button type="primary" size="small" @click="showDeviceDialog()">+ 添加设备</el-button>
        </div>
      </template>
      
      <!-- 设备统计 -->
      <el-row :gutter="10" class="device-stats">
        <el-col :span="6">
          <div class="stat-item online">
            <span class="num">{{ deviceStats.online }}</span>
            <span class="label">在线</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item offline">
            <span class="num">{{ deviceStats.offline }}</span>
            <span class="label">离线</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item warning">
            <span class="num">{{ deviceStats.warning }}</span>
            <span class="label">预警</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item total">
            <span class="num">{{ deviceStats.total }}</span>
            <span class="label">总计</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 设备列表 -->
      <div class="device-list">
        <el-card v-for="device in devices" :key="device.id" class="device-card">
          <div class="device-icon">
            <el-icon :size="32" :class="device.status">
              <component :is="device.icon" />
            </el-icon>
          </div>
          <div class="device-info">
            <h4>{{ device.name }}</h4>
            <p>位置: {{ device.location }}</p>
            <p>最后更新: {{ device.lastUpdate }}</p>
          </div>
          <div class="device-status">
            <el-tag :type="device.status === 'online' ? 'success' : device.status === 'warning' ? 'warning' : 'info'">
              {{ device.status === 'online' ? '在线' : device.status === 'warning' ? '预警' : '离线' }}
            </el-tag>
          </div>
        </el-card>
      </div>
      
      <el-divider>设备分布地图</el-divider>
      <div class="device-map">
        <iframe 
          width="100%" 
          height="200" 
          frameborder="0" 
          scrolling="no" 
          src="https://www.openstreetmap.org/export/embed.html?bbox=117.0%2C36.5%2C117.3%2C36.8&amp;layer=mapnik&amp;marker=36.65%2C117.12"
          style="border-radius: 8px;">
        </iframe>
        <p class="coords">共 {{ devices.length }} 个设备</p>
      </div>
    </el-card>
    
    <!-- 环境监测 -->
    <el-card v-if="activeTab === 'monitor'" class="section-card">
      <template #header>
        <span>📊 环境监测数据</span>
      </template>
      
      <!-- 实时数据 -->
      <el-row :gutter="10" class="monitor-stats">
        <el-col :span="8">
          <div class="monitor-item">
            <div class="monitor-icon temp">
              <el-icon :size="24"><Sunny /></el-icon>
            </div>
            <div class="monitor-value">{{ monitorData.temperature }}°C</div>
            <div class="monitor-label">空气温度</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="monitor-item">
            <div class="monitor-icon humidity">
              <el-icon :size="24"><Cloudy /></el-icon>
            </div>
            <div class="monitor-value">{{ monitorData.humidity }}%</div>
            <div class="monitor-label">空气湿度</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="monitor-item">
            <div class="monitor-icon soil">
              <el-icon :size="24"><Grid /></el-icon>
            </div>
            <div class="monitor-value">{{ monitorData.soilMoisture }}%</div>
            <div class="monitor-label">土壤湿度</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="monitor-item">
            <div class="monitor-icon light">
              <el-icon :size="24"><Sunny /></el-icon>
            </div>
            <div class="monitor-value">{{ monitorData.light }} lux</div>
            <div class="monitor-label">光照强度</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="monitor-item">
            <div class="monitor-icon co2">
              <el-icon :size="24"><WindPower /></el-icon>
            </div>
            <div class="monitor-value">{{ monitorData.co2 }} ppm</div>
            <div class="monitor-label">CO2浓度</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="monitor-item">
            <div class="monitor-icon rain">
              <el-icon :size="24"><Cloudy /></el-icon>
            </div>
            <div class="monitor-value">{{ monitorData.rainfall }} mm</div>
            <div class="monitor-label">降雨量</div>
          </div>
        </el-col>
      </el-row>
      
      <!-- 土壤数据 -->
      <el-divider>土壤监测</el-divider>
      <div class="soil-data">
        <el-card v-for="soil in soilData" :key="soil.location" class="soil-card">
          <h4>{{ soil.location }}</h4>
          <div class="soil-info">
            <span>🌡️ 温度: {{ soil.temperature }}°C</span>
            <span>💧 湿度: {{ soil.humidity }}%</span>
            <span>⚗️ pH值: {{ soil.ph }}</span>
            <span>🧪 含氮量: {{ soil.nitrogen }}mg/kg</span>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 地块对话框 -->
    <el-dialog v-model="landDialogVisible" :title="isEditLand ? '编辑地块' : '添加地块'" width="90%">
      <el-form :model="landForm" label-width="70px" size="small">
        <el-form-item label="所属农场">
          <el-select v-model="landForm.farm_id" placeholder="选择农场" style="width: 100%">
            <el-option v-for="f in farms" :key="f.id" :label="f.name" :value="f.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="名称">
          <el-input v-model="landForm.name" placeholder="地块名称" />
        </el-form-item>
        <el-form-item label="面积">
          <el-input-number v-model="landForm.area" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="作物">
          <el-input v-model="landForm.crop" placeholder="种植作物" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="landForm.status" style="width: 100%">
            <el-option label="正常" value="normal" />
            <el-option label="预警" value="warning" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="landDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveLand" size="small">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 作物对话框 -->
    <el-dialog v-model="cropDialogVisible" :title="isEditCrop ? '编辑作物' : '添加作物'" width="90%">
      <el-form :model="cropForm" label-width="70px" size="small">
        <el-form-item label="作物名称" required>
          <el-input v-model="cropForm.name" placeholder="如: 水稻、小麦、西红柿" />
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="分类" style="margin-bottom: 10px;">
              <el-select v-model="cropForm.category" style="width: 100%">
                <el-option label="粮食" value="粮食" />
                <el-option label="蔬菜" value="蔬菜" />
                <el-option label="水果" value="水果" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="种植季节" style="margin-bottom: 10px;">
              <el-select v-model="cropForm.planting_season" style="width: 100%">
                <el-option label="春季" value="春季" />
                <el-option label="夏季" value="夏季" />
                <el-option label="秋季" value="秋季" />
                <el-option label="冬季" value="冬季" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="生长周期" style="margin-bottom: 10px;">
              <el-input-number v-model="cropForm.growth_days" :min="1" :max="365" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="亩产量(斤)" style="margin-bottom: 10px;">
              <el-input-number v-model="cropForm.yield_per_mu" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="cropDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveCrop" size="small">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 设备对话框 -->
    <el-dialog v-model="deviceDialogVisible" title="添加设备" width="90%">
      <el-form :model="deviceForm" label-width="70px" size="small">
        <el-form-item label="设备名">
          <el-input v-model="deviceForm.name" placeholder="设备名称" />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="deviceForm.type" style="width: 100%">
            <el-option label="温度传感器" value="temp" />
            <el-option label="湿度传感器" value="humidity" />
            <el-option label="土壤传感器" value="soil" />
            <el-option label="气象站" value="weather" />
            <el-option label="摄像头" value="camera" />
            <el-option label="杀虫灯" value="pest_lamp" />
            <el-option label="叶片传感器" value="leaf_sensor" />
            <el-option label="水肥设备" value="water_fertilizer" />
            <el-option label="控制阀" value="control_valve" />
          </el-select>
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="deviceForm.location" placeholder="安装位置" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deviceDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveDevice" size="small">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 农场信息编辑对话框 -->
    <el-dialog v-model="farmDialogVisible" :title="isEditFarm ? '编辑农场' : '添加农场'" width="95%" top="5vh">
      <div class="farm-dialog-content">
        <el-form :model="farmForm" label-width="70px" size="small">
          <el-form-item label="农场名称" required>
            <el-input v-model="farmForm.name" placeholder="农场名称" />
          </el-form-item>
          <el-form-item label="农场地址">
            <el-input v-model="farmForm.address" placeholder="农场地址" />
          </el-form-item>
          <el-row :gutter="10">
            <el-col :span="12">
              <el-form-item label="经度" style="margin-bottom: 10px;">
                <el-input-number v-model="farmForm.lng" :step="0.01" :precision="6" style="width: 100%" placeholder="经度" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="纬度" style="margin-bottom: 10px;">
                <el-input-number v-model="farmForm.lat" :step="0.01" :precision="6" style="width: 100%" placeholder="纬度" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 地图选择器 -->
          <el-form-item label="地图选点">
            <div class="map-picker">
              <div class="map-tip">点击地图选择位置</div>
              <div id="farmMapContainer" style="width: 100%; height: 280px; border-radius: 4px;"></div>
              <div class="coord-display">
                <span v-if="farmForm.lat && farmForm.lng">
                  📍 已选坐标: {{ farmForm.lat.toFixed(4) }}, {{ farmForm.lng.toFixed(4) }}
                </span>
                <span v-else class="no-coord">
                  请在地图上点击选择位置
                </span>
              </div>
            </div>
          </el-form-item>
          
          <el-form-item label="负责人">
            <el-input v-model="farmForm.manager" placeholder="负责人姓名" />
          </el-form-item>
          <el-form-item label="联系电话">
            <el-input v-model="farmForm.phone" placeholder="联系电话" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="farmForm.status" style="width: 100%">
              <el-option label="正常" value="normal" />
              <el-option label="预警" value="warning" />
            </el-select>
          </el-form-item>
          <el-form-item label="农场描述">
            <el-input v-model="farmForm.description" type="textarea" placeholder="农场描述" :rows="2" />
          </el-form-item>
          <el-form-item label="成立日期">
            <el-date-picker v-model="farmForm.established_date" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <el-button @click="farmDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveFarm" size="small">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MapLocation, OfficeBuilding, Cpu, DataAnalysis, Sunny, Cloudy, Grid, WindPower, VideoCamera, Grape } from '@element-plus/icons-vue'
import axios from 'axios'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

const API_BASE = '/api/smart-agriculture'

const activeTab = ref('land')

// 农场数据
const farms = ref<any[]>([])
const currentFarmId = ref<number | undefined>(undefined)
const currentFarm = computed(() => farms.value.find(f => f.id === currentFarmId.value))

const fetchFarms = async () => {
  try {
    const res = await axios.get(`${API_BASE}/farms`)
    farms.value = res.data
    if (farms.value.length > 0 && !currentFarmId.value) {
      currentFarmId.value = farms.value[0].id
    }
  } catch (e) {
    console.error('获取农场失败', e)
  }
}

const onFarmChange = () => {
  // 切换农场后刷新地块数据
  fetchLands()
}

// 地块数据
const lands = ref<any[]>([])
const fetchLands = async () => {
  try {
    const params = currentFarmId.value ? { farm_id: currentFarmId.value } : {}
    const res = await axios.get(`${API_BASE}/lands`, { params })
    lands.value = res.data
  } catch (e) {
    console.error('获取地块失败', e)
  }
}

const totalLandArea = computed(() => lands.value.reduce((sum, l) => sum + (l.area || 0), 0))

// 作物数据 - 从API加载
const crops = ref<any[]>([])

// 加载作物数据
const loadCrops = async () => {
  try {
    const res = await axios.get('/api/smart-agriculture/crops')
    crops.value = res.data
  } catch (e) {
    console.error('加载作物失败', e)
  }
}

const cropDialogVisible = ref(false)
const isEditCrop = ref(false)
const editingCropId = ref<number>()
const cropForm = reactive({
  name: '', category: '蔬菜', planting_season: '春季', growth_days: 90, yield_per_mu: 1000
})

const showCropDialog = () => {
  isEditCrop.value = false
  Object.assign(cropForm, { name: '', category: '蔬菜', planting_season: '春季', growth_days: 90, yield_per_mu: 1000 })
  cropDialogVisible.value = true
}

const editCrop = (crop: any) => {
  isEditCrop.value = true
  editingCropId.value = crop.id
  Object.assign(cropForm, crop)
  cropDialogVisible.value = true
}

const saveCrop = async () => {
  try {
    if (isEditCrop.value) {
      await axios.put(`/api/smart-agriculture/crops/${editingCropId.value}`, cropForm)
    } else {
      await axios.post('/api/smart-agriculture/crops', cropForm)
    }
    ElMessage.success(isEditCrop.value ? '更新成功' : '添加成功')
    cropDialogVisible.value = false
    loadCrops()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const deleteCrop = async (crop: any) => {
  try {
    await ElMessageBox.confirm(`确定删除作物"${crop.name}"吗?`, '提示', { type: 'warning' })
    await axios.delete(`/api/smart-agriculture/crops/${crop.id}`)
    ElMessage.success('删除成功')
    loadCrops()
  } catch (e) {
    // 用户取消
  }
}

// 设备数据
const devices = ref<any[]>([])
const deviceStats = reactive({ online: 0, offline: 0, warning: 0, total: 0 })

const fetchDevices = async () => {
  try {
    const res = await axios.get(`${API_BASE}/devices`)
    devices.value = res.data
    deviceStats.total = devices.value.length
    deviceStats.online = devices.value.filter(d => d.status === 'online').length
    deviceStats.offline = devices.value.filter(d => d.status === 'offline').length
    deviceStats.warning = devices.value.filter(d => d.status === 'warning').length
  } catch (e) { console.error('获取设备失败', e) }
}

// 监测数据
const monitorData = reactive({
  temperature: 25, humidity: 65, soilMoisture: 72, light: 8500, co2: 420, rainfall: 0
})

// 土壤数据
const soilData = ref([
  { location: '东区1号田', temperature: 22.5, humidity: 68, ph: 6.8, nitrogen: 135 },
  { location: '西区1号田', temperature: 21.8, humidity: 72, ph: 6.5, nitrogen: 128 },
  { location: '东区2号田', temperature: 23.1, humidity: 65, ph: 7.0, nitrogen: 142 },
  { location: '西区2号田', temperature: 22.0, humidity: 70, ph: 6.6, nitrogen: 130 }
])

onMounted(() => {
  fetchFarms()
  fetchLands()
  fetchDevices()
})

// 对话框
const landDialogVisible = ref(false)
const isEditLand = ref(false)
const editingLandId = ref<number>()
const landForm = reactive({ name: '', area: 0, crop: '', status: 'normal', farm_id: undefined as number | undefined })

const showLandDialog = () => {
  isEditLand.value = false
  Object.assign(landForm, { name: '', area: 0, crop: '', status: 'normal', farm_id: currentFarmId.value })
  landDialogVisible.value = true
}

const editLand = (land: any) => {
  isEditLand.value = true
  editingLandId.value = land.id
  Object.assign(landForm, land)
  landDialogVisible.value = true
}

const saveLand = async () => {
  if (!landForm.name || landForm.area <= 0) {
    ElMessage.warning('请填写地块名称和面积')
    return
  }
  try {
    if (isEditLand.value && editingLandId.value) {
      await axios.put(`${API_BASE}/lands/${editingLandId.value}`, landForm)
      ElMessage.success('地块更新成功')
    } else {
      await axios.post(`${API_BASE}/lands`, landForm)
      ElMessage.success('地块添加成功')
    }
    landDialogVisible.value = false
    fetchLands()
    fetchFarms()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const deleteLand = async (land: any) => {
  try {
    await axios.delete(`${API_BASE}/lands/${land.id}`)
    ElMessage.success('删除成功')
    fetchLands()
    fetchFarms()
  } catch (e: any) { ElMessage.error('删除失败') }
}

// 农场信息表单
const farmDialogVisible = ref(false)
const isEditFarm = ref(false)
const editingFarmId = ref<number>()
const farmForm = reactive({
  name: '', address: '', manager: '', phone: '', coords: '', status: 'normal', description: '', established_date: '',
  lat: undefined as number | undefined, lng: undefined as number | undefined
})

// Leaflet地图实例
let farmMap: L.Map | null = null
let farmMarker: L.Marker | null = null

// 初始化地图选点
const initMapPicker = () => {
  nextTick(() => {
    const container = document.getElementById('farmMapContainer')
    if (!container) return
    
    // 如果地图已存在，先移除
    if (farmMap) {
      farmMap.remove()
      farmMap = null
    }
    
    const lat = farmForm.lat || 36.65
    const lng = farmForm.lng || 117.12
    
    // 创建地图
    farmMap = L.map('farmMapContainer').setView([lat, lng], 10)
    
    // 添加OpenStreetMap图层
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(farmMap)
    
    // 添加点击事件
    farmMap.on('click', (e: L.LeafletMouseEvent) => {
      farmForm.lat = e.latlng.lat
      farmForm.lng = e.latlng.lng
      
      // 更新标记位置
      if (farmMarker) {
        farmMarker.setLatLng(e.latlng)
      } else {
        farmMarker = L.marker(e.latlng).addTo(farmMap!)
      }
    })
    
    // 如果已有坐标，添加标记
    if (farmForm.lat && farmForm.lng) {
      farmMarker = L.marker([farmForm.lat, farmForm.lng]).addTo(farmMap)
    }
  })
}

// 当地图对话框打开时初始化
watch(() => farmDialogVisible, (val) => {
  if (val) {
    setTimeout(initMapPicker, 100)
  }
})

// 切换标签页时加载对应数据
watch(() => activeTab.value, (tab) => {
  if (tab === 'crop' && crops.value.length === 0) {
    loadCrops()
  }
})

// 保存时更新coords字段
const updateCoords = () => {
  if (farmForm.lat && farmForm.lng) {
    farmForm.coords = `${farmForm.lat.toFixed(4)}°N, ${farmForm.lng.toFixed(4)}°E`
  }
}

const showFarmDialog = (farm?: any) => {
  if (farm) {
    isEditFarm.value = true
    editingFarmId.value = farm.id
    // 解析坐标
    let lat: number | undefined, lng: number | undefined
    if (farm.coords) {
      const match = farm.coords.match(/([\d.]+).*?([\d.]+)/)
      if (match) {
        lat = parseFloat(match[1])
        lng = parseFloat(match[2])
      }
    }
    Object.assign(farmForm, farm, { lat, lng })
  } else {
    isEditFarm.value = false
    Object.assign(farmForm, { 
      name: '', address: '', manager: '', phone: '', 
      coords: '', status: 'normal', description: '', established_date: '',
      lat: 36.65, lng: 117.12 
    })
  }
  farmDialogVisible.value = true
}

const editFarm = (farm: any) => {
  showFarmDialog(farm)
}

const saveFarm = async () => {
  if (!farmForm.name) {
    ElMessage.warning('请填写农场名称')
    return
  }
  // 将经纬度转换为坐标字符串
  if (farmForm.lat && farmForm.lng) {
    farmForm.coords = `${farmForm.lat.toFixed(4)}°N, ${farmForm.lng.toFixed(4)}°E`
  }
  try {
    if (isEditFarm.value && editingFarmId.value) {
      await axios.put(`${API_BASE}/farm`, farmForm)
      ElMessage.success('农场更新成功')
    } else {
      await axios.post(`${API_BASE}/farms`, farmForm)
      ElMessage.success('农场添加成功')
    }
    farmDialogVisible.value = false
    fetchFarms()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '操作失败')
  }
}

const deleteFarm = async (farm: any) => {
  try {
    await ElMessageBox.confirm(`确定删除农场 "${farm.name}" 吗？\n注意：农场下的所有地块也会被删除！`, '警告', { type: 'warning' })
    await axios.delete(`${API_BASE}/farms/${farm.id}`)
    ElMessage.success('删除成功')
    if (currentFarmId.value === farm.id) {
      currentFarmId.value = undefined
    }
    fetchFarms()
    fetchLands()
  } catch (e: any) {
    ElMessage.error('删除失败')
  }
}

const deviceDialogVisible = ref(false)
const deviceForm = reactive({ name: '', type: '', location: '' })

const showDeviceDialog = () => {
  Object.assign(deviceForm, { name: '', type: '', location: '' })
  deviceDialogVisible.value = true
}

const saveDevice = async () => {
  try {
    await axios.post(`${API_BASE}/devices`, deviceForm)
    ElMessage.success('设备添加成功')
    deviceDialogVisible.value = false
    fetchDevices()
  } catch (e: any) { ElMessage.error('添加失败') }
}

const icons: any = { temp: Sunny, humidity: Cloudy, soil: Grid, weather: Sunny, camera: VideoCamera }
</script>

<style scoped>
.smart-agri-container { padding: 10px; }
.header-mobile h2 { font-size: 16px; margin: 0 0 10px 0; }

.quick-nav { margin-bottom: 10px; }
.nav-card { text-align: center; padding: 10px 5px; cursor: pointer; }
.nav-card :deep(.el-card__body) { padding: 10px; }
.nav-card .el-icon { font-size: 24px; color: #67c23a; display: block; margin-bottom: 4px; }
.nav-card span { font-size: 11px; color: #606266; }

.section-card { margin-bottom: 10px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header span { font-size: 14px; font-weight: 500; }

.stats-row { margin-bottom: 15px; }
.stat-box { text-align: center; padding: 10px; background: #f5f7fa; border-radius: 8px; }
.stat-box .num { display: block; font-size: 20px; font-weight: bold; color: #409eff; }
.stat-box .label { font-size: 11px; color: #909399; }

.land-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.land-card { padding: 10px; }
.land-card h4 { margin: 0 0 5px 0; font-size: 14px; }
.land-card p { margin: 2px 0; font-size: 12px; color: #909399; }
.land-actions { display: flex; gap: 5px; margin-top: 8px; }

.crop-list { display: flex; flex-direction: column; gap: 10px; }
.crop-card { padding: 10px; }
.crop-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.crop-info h4 { margin: 0; font-size: 14px; }
.crop-info p { margin: 2px 0 0; font-size: 12px; color: #909399; }
.crop-details { display: flex; flex-wrap: wrap; gap: 8px; font-size: 11px; color: #606266; margin-bottom: 8px; }
.crop-actions { display: flex; gap: 5px; }

.device-stats { margin-bottom: 15px; }
.stat-item { text-align: center; padding: 10px; border-radius: 8px; }
.stat-item.online { background: #67c23a20; }
.stat-item.offline { background: #90939920; }
.stat-item.warning { background: #e6a23c20; }
.stat-item.total { background: #409eff20; }
.stat-item .num { display: block; font-size: 20px; font-weight: bold; }
.stat-item .label { font-size: 11px; color: #909399; }

.device-list { display: flex; flex-direction: column; gap: 8px; }
.device-card { display: flex; align-items: center; padding: 10px; }
.device-icon .el-icon { font-size: 28px; }
.device-icon .online { color: #67c23a; }
.device-icon .warning { color: #e6a23c; }
.device-icon .offline { color: #909399; }
.device-info { flex: 1; margin-left: 10px; }
.device-info h4 { margin: 0; font-size: 14px; }
.device-info p { margin: 2px 0; font-size: 11px; color: #909399; }

.monitor-stats { display: flex; flex-wrap: wrap; }
.monitor-item { text-align: center; padding: 10px; background: #f5f7fa; border-radius: 8px; margin-bottom: 8px; width: 33.33%; }
.monitor-icon { margin-bottom: 5px; }
.monitor-icon.temp { color: #e6a23c; }
.monitor-icon.humidity { color: #409eff; }
.monitor-icon.soil { color: #67c23a; }
.monitor-icon.light { color: #f56c6c; }
.monitor-icon.co2 { color: #909399; }
.monitor-icon.rain { color: #409eff; }
.monitor-value { font-size: 18px; font-weight: bold; color: #303133; }
.monitor-label { font-size: 11px; color: #909399; }

.soil-data { display: flex; flex-direction: column; gap: 8px; }
.soil-card { padding: 10px; }
.soil-card h4 { margin: 0 0 8px 0; font-size: 13px; }
.soil-info { display: flex; flex-wrap: wrap; gap: 8px; font-size: 11px; color: #606266; }

.farm-map, .device-map { margin-top: 10px; }
.coords { text-align: center; font-size: 12px; color: #909399; margin-top: 5px; }

@media (min-width: 769px) {
  .land-grid { grid-template-columns: repeat(4, 1fr); }
  .crop-list { flex-direction: row; flex-wrap: wrap; }
  .crop-card { width: calc(50% - 5px); }
}
</style>

.farm-lands { min-height: 40px; }
.empty-tip { color: #909399; font-size: 12px; text-align: center; padding: 10px; }
.farm-selector { margin-bottom: 10px; }
.farm-actions { display: flex; gap: 10px; }
.farm-detail { }


.map-picker { border: 1px solid #dcdfe6; border-radius: 4px; overflow: hidden; }
.map-tip { padding: 8px; background: #f5f7fa; font-size: 12px; color: #909399; text-align: center; }
.coord-display { padding: 8px; background: #f0f9ff; font-size: 12px; text-align: center; }
.coord-display .no-coord { color: #909399; }
.farm-dialog-content { max-height: 60vh; overflow-y: auto; }

