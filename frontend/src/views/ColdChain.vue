<template>
  <div class="cold-chain-container">
    <div class="header-mobile">
      <h2>❄️ 数字冷链</h2>
    </div>
    
    <!-- 快捷入口 -->
    <el-row :gutter="10" class="quick-nav">
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'monitor'">
          <el-icon><DataAnalysis /></el-icon>
          <span>实时监控</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'warehouse'">
          <el-icon><OfficeBuilding /></el-icon>
          <span>仓库管理</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'vehicle'">
          <el-icon><Van /></el-icon>
          <span>车辆管理</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'transport'">
          <el-icon><Location /></el-icon>
          <span>运输追踪</span>
        </el-card>
      </el-col>
    </el-row>
    <el-row :gutter="10" class="quick-nav">
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'inventory'">
          <el-icon><Box /></el-icon>
          <span>库存管理</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'analytics'">
          <el-icon><TrendCharts /></el-icon>
          <span>数据分析</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'quality'">
          <el-icon><CircleCheck /></el-icon>
          <span>品控管理</span>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="nav-card" @click="activeTab = 'alert'">
          <el-icon><Warning /></el-icon>
          <span>库存预警</span>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 实时监控 -->
    <div v-if="activeTab === 'monitor'">
      <el-row :gutter="10" class="monitor-cards">
        <el-col :span="12" v-for="item in monitorData" :key="item.title">
          <el-card class="monitor-card" :style="{ borderLeft: `4px solid ${item.color}` }">
            <div class="monitor-info">
              <h3>{{ item.value }}</h3>
              <p>{{ item.title }}</p>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card class="section-card">
        <template #header>
          <span>🌡️ 温度监控</span>
        </template>
        
        <div class="temp-list">
          <el-card v-for="item in temperatureData" :key="item.warehouse" class="temp-card">
            <div class="temp-header">
              <span class="warehouse-name">{{ item.warehouse }}</span>
              <el-tag :type="item.status === '正常' ? 'success' : 'danger'" size="small">
                {{ item.status }}
              </el-tag>
            </div>
            <div class="temp-info">
              <span>位置: {{ item.location }}</span>
              <span>温度: <b :style="{ color: getTempColor(item.currentTemp) }">{{ item.currentTemp }}°C</b></span>
              <span>湿度: {{ item.humidity }}</span>
            </div>
          </el-card>
        </div>
      </el-card>
    </div>
    
    <!-- 仓库管理 -->
    <el-card v-if="activeTab === 'warehouse'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🏭 仓库管理</span>
          <el-button type="primary" size="small" @click="showWarehouseDialog()">+ 添加仓库</el-button>
        </div>
      </template>
      
      <!-- 仓库统计 -->
      <el-row :gutter="10" class="warehouse-stats">
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ warehouses.length }}</span>
            <span class="label">仓库数</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ warehouses.filter(w => w.status === '正常').length }}</span>
            <span class="label">正常</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ totalCapacity }}m³</span>
            <span class="label">总容量</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 仓库列表 -->
      <div class="warehouse-list">
        <el-card v-for="wh in warehouses" :key="wh.id" class="warehouse-card">
          <div class="warehouse-header">
            <div class="warehouse-title">
              <el-icon :size="24"><OfficeBuilding /></el-icon>
              <span>{{ wh.name }}</span>
            </div>
            <el-tag :type="wh.status === '正常' ? 'success' : 'warning'" size="small">
              {{ wh.status }}
            </el-tag>
          </div>
          <div class="warehouse-info">
            <p>📍 {{ wh.address }}</p>
            <p>📐 容量: {{ wh.capacity }}m³ | 面积: {{ wh.area }}㎡</p>
            <p>🌡️ 温度: {{ wh.temperature }}°C | 湿度: {{ wh.humidity }}%</p>
            <p>📦 库存: {{ wh.inventory }}件</p>
          </div>
          <div class="warehouse-actions">
            <el-button type="primary" link size="small" @click="editWarehouse(wh)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteWarehouse(wh)">删除</el-button>
          </div>
        </el-card>
      </div>
      
      <el-divider>仓库分布</el-divider>
      <div class="warehouse-map">
        <iframe 
          width="100%" 
          height="200" 
          frameborder="0" 
          scrolling="no" 
          src="https://www.openstreetmap.org/export/embed.html?bbox=117.0%2C36.5%2C117.3%2C36.8&amp;layer=mapnik&amp;marker=36.65%2C117.12"
          style="border-radius: 8px;">
        </iframe>
      </div>
    </el-card>
    
    <!-- 车辆管理 -->
    <el-card v-if="activeTab === 'vehicle'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🚛 车辆管理</span>
          <el-button type="primary" size="small" @click="showVehicleDialog()">+ 添加车辆</el-button>
        </div>
      </template>
      
      <!-- 车辆统计 -->
      <el-row :gutter="10" class="vehicle-stats">
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ vehicles.length }}</span>
            <span class="label">车辆数</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ vehicles.filter(v => v.status === '运输中').length }}</span>
            <span class="label">运输中</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ vehicles.filter(v => v.status === '空闲').length }}</span>
            <span class="label">空闲</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 车辆列表 -->
      <div class="vehicle-list">
        <el-card v-for="v in vehicles" :key="v.id" class="vehicle-card">
          <div class="vehicle-header">
            <el-icon :size="28" color="#409eff"><Van /></el-icon>
            <div class="vehicle-info">
              <h4>{{ v.plate }}</h4>
              <p>司机: {{ v.driver }} | 电话: {{ v.phone }}</p>
            </div>
            <el-tag :type="v.status === '运输中' ? 'success' : v.status === '维修中' ? 'danger' : 'info'" size="small">
              {{ v.status }}
            </el-tag>
          </div>
          <div class="vehicle-detail">
            <span>📍 当前位置: {{ v.location }}</span>
            <span>🌡️ 车厢温度: {{ v.temperature }}°C</span>
            <span>🔋 电量: {{ v.battery }}%</span>
          </div>
          <div class="vehicle-actions">
            <el-button type="primary" link size="small" @click="trackVehicle(v)">追踪</el-button>
            <el-button type="warning" link size="small" @click="editVehicle(v)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteVehicle(v)">删除</el-button>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 运输追踪 -->
    <el-card v-if="activeTab === 'transport'" class="section-card">
      <template #header>
        <span>🗺️ 运输追踪</span>
      </template>
      
      <!-- 运输路线地图 -->
      <div class="transport-map">
        <iframe 
          width="100%" 
          height="250" 
          frameborder="0" 
          scrolling="no" 
          src="https://www.openstreetmap.org/export/embed.html?bbox=116.5%2C36.0%2C118.0%2C37.0&amp;layer=mapnik"
          style="border-radius: 8px; margin-bottom: 15px;">
        </iframe>
      </div>
      
      <!-- 运输轨迹 -->
      <el-timeline>
        <el-timeline-item
          v-for="(item, index) in transportData"
          :key="index"
          :timestamp="item.timestamp"
          :type="item.type"
          :hollow="item.hollow"
        >
          <h4>{{ item.title }}</h4>
          <p>{{ item.location }}</p>
          <p class="timeline-info">
            <span>🌡️ {{ item.temperature }}</span>
            <span>💧 {{ item.humidity }}</span>
          </p>
        </el-timeline-item>
      </el-timeline>
    </el-card>
    
    <!-- 库存管理 -->
    <el-card v-if="activeTab === 'inventory'" class="section-card">
      <template #header>
        <span>📦 库存管理</span>
      </template>
      
      <!-- 库存统计 -->
      <el-row :gutter="10" class="inventory-stats">
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ totalInventory }}</span>
            <span class="label">总库存</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ inventoryData.length }}</span>
            <span class="label">SKU数</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num">{{ expiringCount }}</span>
            <span class="label">临期</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 库存列表 -->
      <div class="inventory-list">
        <el-card v-for="item in inventoryData" :key="item.product" class="inventory-card">
          <div class="inventory-header">
            <span class="product-name">{{ item.product }}</span>
            <el-tag size="small">{{ item.storage }}</el-tag>
          </div>
          <div class="inventory-info">
            <span>数量: {{ item.quantity }}</span>
            <span>保质期: {{ item.expiry }}</span>
            <el-tag v-if="isExpiring(item.expiry)" type="warning" size="small">临期</el-tag>
          </div>
        </el-card>
      </div>
      
      <el-divider />
      
      <!-- 质量追溯 -->
      <h4>🔍 质量追溯</h4>
      <el-form :model="traceForm" label-width="80px" size="small">
        <el-form-item label="追溯码">
          <el-input v-model="traceForm.code" placeholder="请输入追溯码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="traceProduct" size="small">查询</el-button>
        </el-form-item>
      </el-form>
      
      <div v-if="traceResult" class="trace-result">
        <h4>追溯信息</h4>
        <p><strong>产品:</strong> {{ traceResult.product }}</p>
        <p><strong>产地:</strong> {{ traceResult.origin }}</p>
        <p><strong>加工日期:</strong> {{ traceResult.processDate }}</p>
        <p><strong>存储温度:</strong> {{ traceResult.storageTemp }}</p>
        <p><strong>运输路线:</strong> {{ traceResult.transportRoute }}</p>
      </div>
    </el-card>
    
    <!-- 数据分析 -->
    <el-card v-if="activeTab === 'analytics'" class="section-card">
      <template #header>
        <span>📊 数据分析</span>
      </template>
      
      <!-- 库存周转 -->
      <el-row :gutter="10" class="analytics-section">
        <el-col :span="12">
          <h4>📦 库存周转</h4>
          <div class="chart-placeholder">
            <el-progress type="circle" :percentage="72" :width="100" />
            <p>周转率 72%</p>
          </div>
        </el-col>
        <el-col :span="12">
          <h4>🚛 运输效率</h4>
          <div class="chart-placeholder">
            <el-progress type="circle" :percentage="85" :width="100" color="#67C23A" />
            <p>准点率 85%</p>
          </div>
        </el-col>
      </el-row>
      
      <!-- 温度合规率 -->
      <el-divider />
      <h4>🌡️ 温度合规率</h4>
      <el-progress :percentage="98" :stroke-width="20" />
      <p class="analytics-note">本月温度异常时间: 2.3小时 / 720小时</p>
      
      <!-- 损耗统计 -->
      <el-divider />
      <h4>📉 损耗统计</h4>
      <el-row :gutter="10">
        <el-col :span="8">
          <div class="loss-item">
            <span class="num">0.5%</span>
            <span class="label">运输损耗</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="loss-item">
            <span class="num">0.2%</span>
            <span class="label">仓储损耗</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="loss-item">
            <span class="num">0.7%</span>
            <span class="label">总损耗</span>
          </div>
        </el-col>
      </el-row>
    </el-card>
    
    <!-- 品控管理 -->
    <el-card v-if="activeTab === 'quality'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>✅ 品控管理</span>
          <el-button type="primary" size="small" @click="loadQualityData">🔄 刷新</el-button>
        </div>
      </template>
      
      <!-- 品控统计 -->
      <el-row :gutter="10" class="quality-stats">
        <el-col :span="6">
          <div class="stat-item">
            <span class="num">{{ qualityInspections.length }}</span>
            <span class="label">检查总数</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="num">{{ qualityInspections.filter(i => i.result === '合格').length }}</span>
            <span class="label">合格</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="num">{{ qualityInspections.filter(i => i.result === '待复检').length }}</span>
            <span class="label">待复检</span>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <span class="num" style="color: #F56C6C;">{{ qualityInspections.filter(i => i.result === '不合格').length }}</span>
            <span class="label">不合格</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 品控标准 -->
      <el-divider>📋 品控标准</el-divider>
      <div class="quality-standards">
        <el-card v-for="std in qualityStandards" :key="std.id" class="standard-card">
          <div class="standard-header">
            <span class="standard-name">{{ std.name }}</span>
            <el-tag size="small">{{ std.category }}</el-tag>
          </div>
          <div class="standard-info">
            <span>🌡️ 温度: {{ std.temperature.min }}~{{ std.temperature.max }}{{ std.temperature.unit }}</span>
            <span>💧 湿度: {{ std.humidity.min }}~{{ std.humidity.max }}{{ std.humidity.unit }}</span>
            <span>📅 货架期: {{ std.shelf_days }}天</span>
          </div>
        </el-card>
      </div>
      
      <!-- 检查记录 -->
      <el-divider>📝 检查记录</el-divider>
      <el-table :data="qualityInspections" size="small" stripe>
        <el-table-column prop="id" label="编号" width="100" />
        <el-table-column prop="type" label="类型" width="80" />
        <el-table-column prop="product" label="产品" />
        <el-table-column prop="batch_no" label="批次" width="140" />
        <el-table-column prop="result" label="结果" width="70">
          <template #default="{ row }">
            <el-tag :type="row.result === '合格' ? 'success' : row.result === '不合格' ? 'danger' : 'warning'" size="small">
              {{ row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="评分" width="60" />
        <el-table-column prop="inspector" label="质检员" width="80" />
        <el-table-column prop="created_at" label="时间" width="130" />
      </el-table>
    </el-card>
    
    <!-- 库存预警 -->
    <el-card v-if="activeTab === 'alert'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🔔 库存预警</span>
          <el-button type="primary" size="small" @click="loadAlertData">🔄 刷新</el-button>
        </div>
      </template>
      
      <!-- 预警统计 -->
      <el-row :gutter="10" class="alert-stats">
        <el-col :span="8">
          <div class="stat-item">
            <span class="num" style="color: #F56C6C;">{{ inventoryStats.low_stock_count }}</span>
            <span class="label">库存不足</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num" style="color: #E6A23C;">{{ inventoryStats.overstock_count }}</span>
            <span class="label">库存过多</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-item">
            <span class="num" style="color: #909399;">{{ inventoryStats.expiring_soon_count }}</span>
            <span class="label">临期预警</span>
          </div>
        </el-col>
      </el-row>
      
      <!-- 预警规则 -->
      <el-divider>⚙️ 预警规则</el-divider>
      <div class="alert-rules">
        <el-card v-for="rule in alertRules" :key="rule.id" class="rule-card">
          <div class="rule-header">
            <span class="rule-name">{{ rule.name }}</span>
            <el-switch v-model="rule.enabled" size="small" />
          </div>
          <div class="rule-info">
            <span>类型: {{ rule.type }}</span>
            <span>阈值: {{ rule.threshold }}{{ rule.unit }}</span>
            <span>通知: {{ rule.notify_channels.join(', ') }}</span>
          </div>
        </el-card>
      </div>
      
      <!-- 预警列表 -->
      <el-divider>📋 预警列表</el-divider>
      <div class="alert-list">
        <el-card v-for="alert in inventoryAlerts" :key="alert.id" class="alert-card" 
          :class="'alert-' + alert.level">
          <div class="alert-header">
            <el-tag :type="alert.level === 'critical' ? 'danger' : alert.level === 'high' ? 'warning' : 'info'" size="small">
              {{ alert.level === 'critical' ? '紧急' : alert.level === 'high' ? '高' : alert.level === 'medium' ? '中' : '低' }}
            </el-tag>
            <span class="alert-type">{{ alert.type }}</span>
            <el-tag :type="alert.status === '待处理' ? 'danger' : alert.status === '处理中' ? 'warning' : 'success'" size="small">
              {{ alert.status }}
            </el-tag>
          </div>
          <div class="alert-content">
            <p>📦 产品: {{ alert.product }}</p>
            <p>🏭 仓库: {{ alert.warehouse }}</p>
            <p>📊 {{ alert.message }}</p>
          </div>
          <div class="alert-footer">
            <span class="alert-time">{{ alert.created_at }}</span>
            <el-button v-if="alert.status === '待处理'" type="primary" size="small" link @click="resolveAlert(alert.id)">
              标记处理
            </el-button>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 添加/编辑仓库对话框 -->
    <el-dialog v-model="warehouseDialogVisible" :title="isEditWarehouse ? '编辑仓库' : '添加仓库'" width="95%">
      <el-form :model="warehouseForm" label-width="70px" size="small">
        <el-form-item label="仓库名称" required>
          <el-input v-model="warehouseForm.name" placeholder="如: 北京冷库" />
        </el-form-item>
        <el-form-item label="地址" required>
          <el-input v-model="warehouseForm.address" placeholder="仓库地址" />
        </el-form-item>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="容量(m³)" style="margin-bottom: 10px;">
              <el-input-number v-model="warehouseForm.capacity" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="面积(㎡)" style="margin-bottom: 10px;">
              <el-input-number v-model="warehouseForm.area" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="温度(°C)" style="margin-bottom: 10px;">
              <el-input-number v-model="warehouseForm.temperature" :min="-30" :max="10" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="湿度(%)" style="margin-bottom: 10px;">
              <el-input-number v-model="warehouseForm.humidity" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-select v-model="warehouseForm.status" style="width: 100%">
            <el-option label="正常" value="正常" />
            <el-option label="维护中" value="维护中" />
            <el-option label="已满" value="已满" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="warehouseDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveWarehouse" size="small">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 添加/编辑车辆对话框 -->
    <el-dialog v-model="vehicleDialogVisible" :title="isEditVehicle ? '编辑车辆' : '添加车辆'" width="95%">
      <el-form :model="vehicleForm" label-width="70px" size="small">
        <el-form-item label="车牌号" required>
          <el-input v-model="vehicleForm.plate" placeholder="如: 京A12345" />
        </el-form-item>
        <el-form-item label="司机" required>
          <el-input v-model="vehicleForm.driver" placeholder="司机姓名" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="vehicleForm.phone" placeholder="联系电话" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="vehicleForm.status" style="width: 100%">
            <el-option label="空闲" value="空闲" />
            <el-option label="运输中" value="运输中" />
            <el-option label="维修中" value="维修中" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="vehicleDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveVehicle" size="small">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis, OfficeBuilding, Van, Box, Location, TrendCharts, CircleCheck, Warning } from '@element-plus/icons-vue'

const activeTab = ref('monitor')

// 页面加载时获取数据
onMounted(() => {
  loadMonitorData()
  loadWarehouseData()
  loadVehicleData()
  loadTransportData()
})

// 加载监控数据
const loadMonitorData = async () => {
  try {
    const res = await axios.get('/api/cold-chain/monitoring/temperature')
    temperatureData.value = res.data
  } catch (e) { console.error('加载监控数据失败', e) }
}

// 加载仓库数据
const loadWarehouseData = async () => {
  try {
    const res = await axios.get('/api/cold-chain/warehouse')
    warehouses.value = res.data.map((w: any) => ({
      id: w.id,
      name: w.name,
      address: w.address,
      capacity: w.capacity,
      area: Math.floor(w.capacity / 2),
      temperature: w.temperature,
      humidity: w.humidity,
      inventory: w.products_count * 10,
      status: w.alerts > 0 ? '预警' : '正常'
    }))
  } catch (e) { console.error('加载仓库数据失败', e) }
}

// 加载车辆数据
const loadVehicleData = async () => {
  try {
    const res = await axios.get('/api/cold-chain/transport')
    vehicles.value = res.data.slice(0, 6).map((v: any, i: number) => ({
      id: i + 1,
      plate: v.vehicle_no,
      driver: v.driver,
      phone: '138****' + Math.floor(Math.random() * 10000),
      location: v.location,
      temperature: v.temperature,
      status: v.status === '运输中' ? '运输中' : '空闲'
    }))
  } catch (e) { console.error('加载车辆数据失败', e) }
}

// 加载运输数据
const loadTransportData = async () => {
  try {
    const res = await axios.get('/api/cold-chain/transport')
    transports.value = res.data
  } catch (e) { console.error('加载运输数据失败', e) }
}

// 监听标签页切换，加载对应数据
watch(activeTab, (newTab) => {
  if (newTab === 'quality' && qualityInspections.value.length === 0) {
    loadQualityData()
  }
  if (newTab === 'alert' && inventoryAlerts.value.length === 0) {
    loadAlertData()
  }
})

// 监控数据
const monitorData = ref([
  { title: '在线车辆', value: '12', color: '#67C23A' },
  { title: '在线仓库', value: '5', color: '#409EFF' },
  { title: '温度异常', value: '0', color: '#F56C6C' },
  { title: '今日运输', value: '28', color: '#E6A23C' }
])

const temperatureData = ref([
  { warehouse: 'A冷库', location: '北京仓', currentTemp: -18, targetTemp: -18, humidity: '45%', status: '正常' },
  { warehouse: 'B冷库', location: '上海仓', currentTemp: -20, targetTemp: -18, humidity: '42%', status: '正常' },
  { warehouse: '京A12345', location: '运输中-京沪高速', currentTemp: -16, targetTemp: -18, humidity: '50%', status: '正常' },
  { warehouse: '京B67890', location: '运输中-京港澳', currentTemp: -17, targetTemp: -18, humidity: '48%', status: '正常' }
])

// 仓库数据
const warehouses = ref([
  { id: 1, name: '北京冷库', address: '北京市朝阳区', capacity: 5000, area: 2000, temperature: -18, humidity: 45, inventory: 3500, status: '正常' },
  { id: 2, name: '上海冷库', address: '上海市浦东新区', capacity: 8000, area: 3000, temperature: -20, humidity: 42, inventory: 6200, status: '正常' },
  { id: 3, name: '济南中心库', address: '山东省济南市', capacity: 12000, area: 5000, temperature: -18, humidity: 48, inventory: 9800, status: '正常' },
  { id: 4, name: '南京配送库', address: '江苏省南京市', capacity: 3000, area: 1500, temperature: -16, humidity: 50, inventory: 2100, status: '正常' }
])

const totalCapacity = computed(() => warehouses.value.reduce((sum, w) => sum + w.capacity, 0))

// 品控数据
const qualityInspections = ref<any[]>([])
const qualityStandards = ref<any[]>([])

// 库存预警数据
const inventoryAlerts = ref<any[]>([])
const inventoryStats = ref({
  total_products: 0,
  total_stock: 0,
  low_stock_count: 0,
  overstock_count: 0,
  expiring_soon_count: 0,
  temp_alert_count: 0,
  today_resolved: 0,
  this_week: { total_alerts: 0, resolved: 0, pending: 0 }
})
const alertRules = ref<any[]>([])

// 加载品控数据
const loadQualityData = async () => {
  try {
    const [inspRes, stdRes] = await Promise.all([
      axios.get('/api/cold-chain/quality/inspections'),
      axios.get('/api/cold-chain/quality/standards')
    ])
    qualityInspections.value = inspRes.data
    qualityStandards.value = stdRes.data.standards
  } catch (e) {
    console.error('加载品控数据失败', e)
  }
}

// 加载库存预警数据
const loadAlertData = async () => {
  try {
    const [alertsRes, rulesRes, statsRes] = await Promise.all([
      axios.get('/api/cold-chain/inventory/alerts'),
      axios.get('/api/cold-chain/inventory/rules'),
      axios.get('/api/cold-chain/inventory/stats')
    ])
    inventoryAlerts.value = alertsRes.data
    alertRules.value = rulesRes.data.rules
    inventoryStats.value = statsRes.data
  } catch (e) {
    console.error('加载库存预警数据失败', e)
  }
}

// 标记预警已处理
const resolveAlert = async (alertId: string) => {
  try {
    await axios.post(`/api/cold-chain/inventory/alerts/${alertId}/resolve`)
    ElMessage.success('已标记为已处理')
    loadAlertData()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const warehouseDialogVisible = ref(false)
const isEditWarehouse = ref(false)
const editingWarehouseId = ref<number>()
const warehouseForm = reactive({
  name: '', address: '', capacity: 1000, area: 500, temperature: -18, humidity: 45, status: '正常'
})

const showWarehouseDialog = () => {
  isEditWarehouse.value = false
  Object.assign(warehouseForm, { name: '', address: '', capacity: 1000, area: 500, temperature: -18, humidity: 45, status: '正常' })
  warehouseDialogVisible.value = true
}

const editWarehouse = (wh: any) => {
  isEditWarehouse.value = true
  editingWarehouseId.value = wh.id
  Object.assign(warehouseForm, wh)
  warehouseDialogVisible.value = true
}

const saveWarehouse = () => {
  if (!warehouseForm.name || !warehouseForm.address) {
    ElMessage.warning('请填写仓库名称和地址')
    return
  }
  if (isEditWarehouse.value && editingWarehouseId.value) {
    const index = warehouses.value.findIndex(w => w.id === editingWarehouseId.value)
    if (index !== -1) warehouses.value[index] = { ...warehouseForm, id: editingWarehouseId.value }
    ElMessage.success('仓库更新成功')
  } else {
    warehouses.value.push({ id: Date.now(), ...warehouseForm, inventory: 0 })
    ElMessage.success('仓库添加成功')
  }
  warehouseDialogVisible.value = false
}

const deleteWarehouse = async (wh: any) => {
  try {
    await ElMessageBox.confirm(`确定删除仓库 "${wh.name}" 吗？`, '提示', { type: 'warning' })
    warehouses.value = warehouses.value.filter(w => w.id !== wh.id)
    ElMessage.success('删除成功')
  } catch {}
}

// 车辆数据
const vehicles = ref([
  { id: 1, plate: '京A12345', driver: '张三', phone: '138****8888', status: '运输中', location: '京沪高速-南京段', temperature: -18, battery: 85 },
  { id: 2, plate: '京B67890', driver: '李四', phone: '139****9999', status: '空闲', location: '北京仓库', temperature: -18, battery: 100 },
  { id: 3, plate: '鲁A11111', driver: '王五', phone: '137****7777', status: '运输中', location: '京港澳高速-石家庄段', temperature: -17, battery: 72 },
  { id: 4, plate: '沪A22222', driver: '赵六', phone: '136****6666', status: '维修中', location: '维修厂', temperature: 0, battery: 45 }
])

// 运输数据
const transports = ref<any[]>([])

const vehicleDialogVisible = ref(false)
const isEditVehicle = ref(false)
const editingVehicleId = ref<number>()
const vehicleForm = reactive({
  plate: '', driver: '', phone: '', status: '空闲', location: '', temperature: -18, battery: 100
})

const showVehicleDialog = () => {
  isEditVehicle.value = false
  Object.assign(vehicleForm, { plate: '', driver: '', phone: '', status: '空闲', location: '', temperature: -18, battery: 100 })
  vehicleDialogVisible.value = true
}

const editVehicle = (v: any) => {
  isEditVehicle.value = true
  editingVehicleId.value = v.id
  Object.assign(vehicleForm, v)
  vehicleDialogVisible.value = true
}

const saveVehicle = () => {
  if (!vehicleForm.plate || !vehicleForm.driver) {
    ElMessage.warning('请填写车牌号和司机')
    return
  }
  if (isEditVehicle.value && editingVehicleId.value) {
    const index = vehicles.value.findIndex(v => v.id === editingVehicleId.value)
    if (index !== -1) vehicles.value[index] = { ...vehicleForm, id: editingVehicleId.value }
    ElMessage.success('车辆更新成功')
  } else {
    vehicles.value.push({ id: Date.now(), ...vehicleForm })
    ElMessage.success('车辆添加成功')
  }
  vehicleDialogVisible.value = false
}

const deleteVehicle = async (v: any) => {
  try {
    await ElMessageBox.confirm(`确定删除车辆 "${v.plate}" 吗？`, '提示', { type: 'warning' })
    vehicles.value = vehicles.value.filter(ve => ve.id !== v.id)
    ElMessage.success('删除成功')
  } catch {}
}

const trackVehicle = (v: any) => {
  ElMessage.success(`正在追踪 ${v.plate}，当前位置: ${v.location}`)
}

// 运输数据
const transportData = ref([
  { timestamp: '2026-02-17 14:30', title: '到达目的地', location: '北京仓储中心', temperature: '-18°C', humidity: '45%', type: 'success', hollow: false },
  { timestamp: '2026-02-17 08:15', title: '离开中转站', location: '济南分拨中心', temperature: '-17°C', humidity: '48%', type: 'primary', hollow: false },
  { timestamp: '2026-02-16 22:00', title: '运输中', location: '南京路段', temperature: '-16°C', humidity: '50%', type: 'warning', hollow: false },
  { timestamp: '2026-02-16 18:00', title: '装货完成', location: '上海仓库', temperature: '-18°C', humidity: '45%', type: 'info', hollow: false }
])

// 库存数据
const inventoryData = ref([
  { product: '有机草莓 2斤装', quantity: '500箱', storage: 'A冷库-01区', expiry: '2026-02-25' },
  { product: '新鲜三文鱼', quantity: '200盒', storage: 'B冷库-02区', expiry: '2026-02-20' },
  { product: '进口车厘子', quantity: '800箱', storage: 'A冷库-03区', expiry: '2026-03-01' },
  { product: '有机西兰花', quantity: '300箱', storage: 'C冷库-01区', expiry: '2026-02-22' }
])

const totalInventory = computed(() => {
  return inventoryData.value.reduce((sum, item) => {
    const num = parseInt(item.quantity)
    return sum + (isNaN(num) ? 0 : num)
  }, 0)
})

const expiringCount = computed(() => {
  const now = new Date()
  return inventoryData.value.filter(item => {
    const exp = new Date(item.expiry)
    const diff = (exp.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
    return diff <= 7 && diff > 0
  }).length
})

const isExpiring = (expiry: string) => {
  const now = new Date()
  const exp = new Date(expiry)
  const diff = (exp.getTime() - now.getTime()) / (1000 * 60 * 60 * 24)
  return diff <= 7 && diff > 0
}

const traceForm = reactive({ code: '' })
const traceResult = ref<any>(null)

const getTempColor = (temp: number) => {
  if (temp > -15) return '#F56C6C'
  if (temp < -20) return '#409EFF'
  return '#67C23A'
}

const traceProduct = () => {
  if (!traceForm.code) {
    ElMessage.warning('请输入追溯码')
    return
  }
  traceResult.value = {
    product: '有机草莓 2斤装',
    origin: '山东济南生态农场',
    processDate: '2026-02-15',
    storageTemp: '-18°C',
    transportRoute: '济南 → 南京 → 上海 → 北京'
  }
  ElMessage.success('追溯查询成功')
}
</script>

<style scoped>
.cold-chain-container { padding: 10px; }
.header-mobile h2 { font-size: 16px; margin: 0 0 10px 0; }

.quick-nav { margin-bottom: 10px; }
.nav-card { text-align: center; padding: 10px 5px; cursor: pointer; }
.nav-card :deep(.el-card__body) { padding: 10px; }
.nav-card .el-icon { font-size: 24px; color: #409eff; display: block; margin-bottom: 4px; }
.nav-card span { font-size: 11px; color: #606266; }

.monitor-cards { margin-bottom: 10px; }
.monitor-card { margin-bottom: 10px; }
.monitor-info h3 { font-size: 24px; margin: 0; }
.monitor-info p { margin: 5px 0 0; font-size: 12px; color: #909399; }

.section-card { margin-bottom: 10px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header span { font-size: 14px; font-weight: 500; }

.stat-item { text-align: center; padding: 10px; background: #f5f7fa; border-radius: 8px; }
.stat-item .num { display: block; font-size: 20px; font-weight: bold; color: #409eff; }
.stat-item .label { font-size: 11px; color: #909399; }

.warehouse-list, .vehicle-list, .inventory-list { display: flex; flex-direction: column; gap: 10px; }
.warehouse-card, .vehicle-card, .inventory-card { padding: 10px; }

.warehouse-header, .vehicle-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.warehouse-title { display: flex; align-items: center; gap: 8px; font-weight: 500; font-size: 14px; }
.warehouse-info p, .vehicle-detail { margin: 3px 0; font-size: 12px; color: #606266; }
.warehouse-actions, .vehicle-actions { display: flex; gap: 5px; margin-top: 8px; }

.vehicle-info h4 { margin: 0; font-size: 14px; }
.vehicle-info p { margin: 2px 0 0; font-size: 11px; color: #909399; }
.vehicle-detail { display: flex; flex-wrap: wrap; gap: 8px; }

.inventory-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px; }
.product-name { font-weight: 500; font-size: 14px; }
.inventory-info { display: flex; gap: 15px; font-size: 12px; color: #606266; align-items: center; }

.transport-map { margin-bottom: 15px; }
.timeline-info { margin: 5px 0 0; color: #909399; font-size: 12px; }
.timeline-info span { margin-right: 10px; }

.chart-placeholder { text-align: center; padding: 15px; }
.chart-placeholder p { margin: 10px 0 0; font-size: 12px; color: #909399; }
.analytics-note { font-size: 12px; color: #909399; text-align: center; margin-top: 5px; }

.loss-item { text-align: center; padding: 10px; background: #f5f7fa; border-radius: 8px; }
.loss-item .num { display: block; font-size: 18px; font-weight: bold; color: #67C23A; }
.loss-item .label { font-size: 11px; color: #909399; }

.trace-result { padding: 15px; background: #f5f7fa; border-radius: 8px; margin-top: 10px; }
.trace-result h4 { margin: 0 0 10px; }
.trace-result p { margin: 5px 0; font-size: 12px; }

.analytics-section { margin-bottom: 15px; }
.analytics-section h4 { font-size: 14px; margin: 0 0 10px 0; }

/* 品控管理 */
.quality-stats, .alert-stats { margin-bottom: 15px; }
.quality-standards, .alert-rules { display: flex; flex-direction: column; gap: 10px; margin-bottom: 15px; }
.standard-card, .rule-card { padding: 10px; }
.standard-header, .rule-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.standard-name, .rule-name { font-weight: 500; }
.standard-info, .rule-info { font-size: 12px; color: #606266; display: flex; flex-wrap: wrap; gap: 10px; }
.standard-info span, .rule-info span { display: block; }

/* 库存预警 */
.alert-list { display: flex; flex-direction: column; gap: 10px; }
.alert-card { padding: 10px; border-left: 4px solid #909399; }
.alert-card.alert-critical { border-left-color: #F56C6C; }
.alert-card.alert-high { border-left-color: #E6A23C; }
.alert-card.alert-medium { border-left-color: #409EFF; }
.alert-card.alert-low { border-left-color: #909399; }
.alert-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.alert-type { flex: 1; font-weight: 500; }
.alert-content { font-size: 12px; color: #606266; }
.alert-content p { margin: 3px 0; }
.alert-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.alert-time { font-size: 11px; color: #909399; }
</style>
