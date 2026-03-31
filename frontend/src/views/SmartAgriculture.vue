<template>
  <div class="smart-agri-container">
    <!-- 页面头部 -->
    <header class="page-header">
      <div class="header-left">
        <h1 class="page-title">🌱 智慧农业</h1>
        <p class="page-subtitle">智能监测 · 科学管理 · 精准决策</p>
      </div>
    </header>

    <!-- 快捷入口 -->
    <div class="quick-nav-grid">
      <div
        v-for="(item, index) in navItems"
        :key="item.key"
        class="nav-card"
        :style="{ '--accent': item.color, '--delay': `${index * 0.05}s` }"
        @click="setActiveTab(item.key)"
      >
        <div class="nav-card-glow"></div>
        <div class="nav-card-content">
          <div class="nav-icon-wrapper">
            <el-icon :size="28" :color="item.color">
              <component :is="item.icon" />
            </el-icon>
          </div>
          <span class="nav-label">{{ item.label }}</span>
        </div>
      </div>
    </div>
    
    <!-- 地块管理 -->
    <el-card v-show="activeTab === 'land'" class="section-card">
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
    <el-card v-show="activeTab === 'crop'" class="section-card">
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
    <el-card v-show="activeTab === 'farm'" class="section-card">
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
          <div id="farmOverviewMap" style="width: 100%; height: 200px; border-radius: 8px;"></div>
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
    <el-card v-show="activeTab === 'device'" class="section-card">
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
        <div id="deviceMap" style="width: 100%; height: 200px; border-radius: 8px;"></div>
        <p class="coords">共 {{ devices.length }} 个设备</p>
      </div>
    </el-card>
    
    <!-- 环境监测 -->
    <el-card v-show="activeTab === 'monitor'" class="section-card">
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

    <!-- 智能决策系统 -->
    <el-card v-show="activeTab === 'decision'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>🤖 智能决策系统</span>
          <el-button type="primary" size="small" @click="showDecisionDialog()">生成决策</el-button>
        </div>
      </template>
      
      <el-alert title="基于农作物生长模型的智能决策系统" type="info" :closable="false" style="margin-bottom: 15px" />
      
      <el-row :gutter="10" class="stats-row">
        <el-col :span="8">
          <div class="stat-box">
            <span class="num">{{ cropModels.length }}</span>
            <span class="label">作物模型</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-box">
            <span class="num">{{ decisionRecords.length }}</span>
            <span class="label">决策记录</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-box">
            <span class="num">{{ decisionRecords.filter(r => r.executed).length }}</span>
            <span class="label">已执行</span>
          </div>
        </el-col>
      </el-row>
      
      <el-divider>作物生长模型</el-divider>
      <div class="model-grid">
        <el-card v-for="model in cropModels" :key="model.id" class="model-card">
          <div class="model-info">
            <h4>{{ model.cropName }}</h4>
            <p>类型: {{ model.cropType }}</p>
            <p>预期产量: {{ model.expectedYield }}斤/亩</p>
            <p>预测准确率: {{ model.predictionAccuracy }}%</p>
            <el-tag size="small">{{ model.modelVersion }}</el-tag>
          </div>
        </el-card>
      </div>
      
      <el-divider>决策记录</el-divider>
      <el-timeline>
        <el-timeline-item v-for="record in decisionRecords" :key="record.id" :timestamp="record.createdAt" placement="top">
          <el-card>
            <div class="decision-info">
              <h4>
                <el-tag :type="record.decisionType === '灌溉' ? 'primary' : record.decisionType === '施肥' ? 'success' : 'warning'">
                  {{ record.decisionType }}
                </el-tag>
                决策建议
              </h4>
              <p>{{ record.recommendation }}</p>
              <p>置信度: {{ (record.confidence * 100).toFixed(0) }}%</p>
              <el-button v-if="!record.executed" type="primary" size="small" @click="executeDecision(record.id)">执行</el-button>
              <el-tag v-else type="success" size="small">已执行</el-tag>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <!-- 全产业链追溯系统 -->
    <el-card v-show="activeTab === 'traceability'" class="section-card">
      <template #header>
        <div class="card-header">
          <span>📋 全</span>
         产业链追溯系统 <el-button type="primary" size="small" @click="showTraceabilityDialog()">添加产品</el-button>
        </div>
      </template>
      
      <el-alert title="农产品从田间到餐桌的全程追溯" type="info" :closable="false" style="margin-bottom: 15px" />
      
      <el-row :gutter="10" class="stats-row">
        <el-col :span="8">
          <div class="stat-box">
            <span class="num">{{ traceabilityRecords.length }}</span>
            <span class="label">追溯记录</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-box">
            <span class="num">{{ traceabilityRecords.filter(r => r.status === 'active').length }}</span>
            <span class="label">在售</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="stat-box">
            <span class="num">{{ traceabilityRecords.filter(r => r.status === 'sold').length }}</span>
            <span class="label">已售</span>
          </div>
        </el-col>
      </el-row>
      
      <el-divider>追溯记录列表</el-divider>
      <div class="trace-grid">
        <el-card v-for="record in traceabilityRecords" :key="record.id" class="trace-card">
          <div class="trace-info">
            <h4>{{ record.productName }}</h4>
            <p>批次: {{ record.productBatch }}</p>
            <p>产地: {{ record.originFarm }}</p>
            <p>追溯码: <el-tag size="small">{{ record.traceCode }}</el-tag></p>
            <p>种植: {{ record.plantingDate }} | 收获: {{ record.harvestDate }}</p>
            <el-tag :type="record.status === 'active' ? 'success' : 'info'" size="small">{{ record.status === 'active' ? '在售' : record.status }}</el-tag>
          </div>
        </el-card>
      </div>
    </el-card>
    
    <!-- 地块对话框 -->
    <el-dialog v-model="landDialogVisible" :title="isEditLand ? '编辑地块' : '添加地块'" width="90%">
      <el-form :model="landForm" label-width="80px" size="small">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="所属农场">
              <el-select v-model="landForm.farm_id" placeholder="选择农场" style="width: 100%">
                <el-option v-for="f in farms" :key="f.id" :label="f.name" :value="f.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名称">
              <el-input v-model="landForm.name" placeholder="地块名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="面积(亩)">
              <el-input-number v-model="landForm.area" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="作物">
              <el-input v-model="landForm.crop" placeholder="种植作物" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">土地属性</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="土壤类型">
              <el-select v-model="landForm.soilType" style="width: 100%">
                <el-option label="沙土" value="沙土" />
                <el-option label="壤土" value="壤土" />
                <el-option label="粘土" value="粘土" />
                <el-option label="沙壤土" value="沙壤土" />
                <el-option label="粘壤土" value="粘壤土" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="灌溉方式">
              <el-select v-model="landForm.irrigationType" style="width: 100%">
                <el-option label="滴灌" value="滴灌" />
                <el-option label="喷灌" value="喷灌" />
                <el-option label="漫灌" value="漫灌" />
                <el-option label="沟灌" value="沟灌" />
                <el-option label="微喷" value="微喷" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="海拔(米)">
              <el-input-number v-model="landForm.altitude" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="landForm.status" style="width: 100%">
                <el-option label="正常" value="normal" />
                <el-option label="预警" value="warning" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="landDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveLand" size="small">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 作物对话框 -->
    <el-dialog v-model="cropDialogVisible" :title="isEditCrop ? '编辑作物' : '添加作物'" width="90%">
      <el-form :model="cropForm" label-width="80px" size="small">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="作物名称" required>
              <el-input v-model="cropForm.name" placeholder="如: 水稻、小麦、西红柿" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品种">
              <el-input v-model="cropForm.variety" placeholder="如: 优系一号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="分类">
              <el-select v-model="cropForm.category" style="width: 100%">
                <el-option label="粮食" value="粮食" />
                <el-option label="蔬菜" value="蔬菜" />
                <el-option label="水果" value="水果" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="种植季节">
              <el-select v-model="cropForm.planting_season" style="width: 100%">
                <el-option label="春季" value="春季" />
                <el-option label="夏季" value="夏季" />
                <el-option label="秋季" value="秋季" />
                <el-option label="冬季" value="冬季" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">种植信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="种植日期">
              <el-date-picker v-model="cropForm.plantingDate" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计收获">
              <el-date-picker v-model="cropForm.expectedHarvest" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="生长周期">
              <el-input-number v-model="cropForm.growth_days" :min="1" :max="365" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="亩产量(斤)">
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
      <el-form :model="deviceForm" label-width="80px" size="small">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="设备名" required>
              <el-input v-model="deviceForm.name" placeholder="设备名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="序列号">
              <el-input v-model="deviceForm.serialNumber" placeholder="设备序列号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
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
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备状态">
              <el-select v-model="deviceForm.status" style="width: 100%">
                <el-option label="在线" value="online" />
                <el-option label="离线" value="offline" />
                <el-option label="维护中" value="maintenance" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">安装信息</div>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="所属地块">
              <el-select v-model="deviceForm.landId" style="width: 100%" placeholder="选择地块">
                <el-option v-for="l in lands" :key="l.id" :label="l.name" :value="l.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安装位置">
              <el-input v-model="deviceForm.location" placeholder="安装位置" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="安装日期">
              <el-date-picker v-model="deviceForm.installDate" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最后维护">
              <el-date-picker v-model="deviceForm.lastMaintenance" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
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

    <!-- 智能决策生成对话框 -->
    <el-dialog v-model="decisionDialogVisible" title="生成智能决策" width="90%">
      <el-form :model="decisionForm" label-width="80px" size="small">
        <el-form-item label="决策类型">
          <el-select v-model="decisionForm.decisionType" style="width: 100%">
            <el-option label="灌溉" value="灌溉" />
            <el-option label="施肥" value="施肥" />
            <el-option label="喷药" value="喷药" />
            <el-option label="收获预警" value="收获预警" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="decisionDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="generateDecision" size="small">生成</el-button>
      </template>
    </el-dialog>

    <!-- 追溯记录添加对话框 -->
    <el-dialog v-model="traceabilityDialogVisible" title="添加追溯记录" width="90%">
      <el-form :model="traceabilityForm" label-width="80px" size="small">
        <el-form-item label="产品名称">
          <el-input v-model="traceabilityForm.productName" placeholder="如：有机大米" />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="traceabilityForm.productBatch" placeholder="如：RICE20260219" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="traceabilityForm.category" style="width: 100%">
            <el-option label="粮食" value="粮食" />
            <el-option label="水果" value="水果" />
            <el-option label="蔬菜" value="蔬菜" />
            <el-option label="茶叶" value="茶叶" />
          </el-select>
        </el-form-item>
        <el-form-item label="产地农场">
          <el-input v-model="traceabilityForm.originFarm" placeholder="如：智慧生态农场" />
        </el-form-item>
        <el-form-item label="种植日期">
          <el-date-picker v-model="traceabilityForm.plantingDate" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="收获日期">
          <el-date-picker v-model="traceabilityForm.harvestDate" type="date" placeholder="选择日期" style="width: 100%" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="traceabilityDialogVisible = false" size="small">取消</el-button>
        <el-button type="primary" @click="saveTraceability" size="small">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MapLocation, OfficeBuilding, Cpu, DataAnalysis, Sunny, Cloudy, Grid, WindPower, VideoCamera, Grape, TrendCharts, Link } from '@element-plus/icons-vue'
import axios from 'axios'

declare global {
  interface Window {
    AMap: any
  }
}

const API_BASE = '/api/smart-agriculture'

const activeTab = ref('land')
const setActiveTab = (tab: string) => { activeTab.value = tab }

const navItems = [
  { key: 'land', label: '地块管理', icon: MapLocation, color: '#10B981' },
  { key: 'farm', label: '农场信息', icon: OfficeBuilding, color: '#3B82F6' },
  { key: 'crop', label: '作物管理', icon: Grape, color: '#F59E0B' },
  { key: 'device', label: '物联网设备', icon: Cpu, color: '#8B5CF6' },
  { key: 'monitor', label: '环境监测', icon: DataAnalysis, color: '#EC4899' },
  { key: 'decision', label: '智能决策', icon: TrendCharts, color: '#06B6D4' },
  { key: 'traceability', label: '追溯系统', icon: Link, color: '#EF4444' }
]

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

// 土壤数据
const soilData = ref<any[]>([])
const loadSoilData = async () => {
  try {
    const res = await axios.get('/api/smart-agriculture/soil')
    soilData.value = res.data
  } catch (e) {
    console.error('加载土壤数据失败', e)
  }
}

// 气象数据
const weatherData = ref<any[]>([])
const loadWeatherData = async () => {
  try {
    const res = await axios.get('/api/smart-agriculture/weather')
    weatherData.value = res.data
  } catch (e) {
    console.error('加载气象数据失败', e)
  }
}

// 灌溉数据
const irrigationData = ref<any[]>([])
const loadIrrigationData = async () => {
  try {
    const res = await axios.get('/api/smart-agriculture/irrigation')
    irrigationData.value = res.data
  } catch (e) {
    console.error('加载灌溉数据失败', e)
  }
}

// 分析数据
const analyticsData = ref<any>({})
const loadAnalytics = async () => {
  try {
    const res = await axios.get('/api/smart-agriculture/analytics')
    analyticsData.value = res.data
  } catch (e) {
    console.error('加载分析数据失败', e)
  }
}

const cropDialogVisible = ref(false)
const isEditCrop = ref(false)
const editingCropId = ref<number>()
const cropForm = reactive({
  name: '', category: '蔬菜', planting_season: '春季', growth_days: 90, yield_per_mu: 1000,
  variety: '', plantingDate: '', expectedHarvest: ''
})

const showCropDialog = () => {
  isEditCrop.value = false
  Object.assign(cropForm, {
    name: '', category: '蔬菜', planting_season: '春季', growth_days: 90, yield_per_mu: 1000,
    variety: '', plantingDate: '', expectedHarvest: ''
  })
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

onMounted(() => {
  window.scrollTo(0, 0)
  fetchFarms()
  fetchLands()
  fetchDevices()
})

// 对话框
const landDialogVisible = ref(false)
const isEditLand = ref(false)
const editingLandId = ref<number>()
const landForm = reactive({
  name: '', area: 0, crop: '', status: 'normal', farm_id: undefined as number | undefined,
  soilType: '壤土', irrigationType: '滴灌', altitude: 0
})

const showLandDialog = () => {
  isEditLand.value = false
  Object.assign(landForm, {
    name: '', area: 0, crop: '', status: 'normal', farm_id: currentFarmId.value,
    soilType: '壤土', irrigationType: '滴灌', altitude: 0
  })
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

// 高德地图实例
let farmMap: any = null
let farmMarker: any = null
let farmOverviewMap: any = null
let deviceMap: any = null

// 等待 AMap 加载完成
const waitForAMap = (): Promise<void> => {
  return new Promise((resolve) => {
    if (window.AMap) {
      resolve()
    } else {
      const check = setInterval(() => {
        if (window.AMap) {
          clearInterval(check)
          resolve()
        }
      }, 100)
      // 超时保护，5秒后强制结束
      setTimeout(() => {
        clearInterval(check)
        resolve()
      }, 5000)
    }
  })
}

// 初始化高德地图选点
const initMapPicker = async () => {
  await nextTick()
  const container = document.getElementById('farmMapContainer')
  if (!container) {
    console.log('[Map] 容器不存在，等待...')
    return
  }

  console.log('[Map] 容器尺寸:', container.offsetWidth, container.offsetHeight)

  await waitForAMap()
  if (!window.AMap) {
    console.error('[Map] 高德地图加载失败')
    return
  }

  console.log('[Map] 开始初始化')

  // 如果地图已存在，先移除
  if (farmMap) {
    farmMap.destroy()
    farmMap = null
  }

  const lat = farmForm.lat || 36.65
  const lng = farmForm.lng || 117.12

  // 创建高德地图
  farmMap = new window.AMap.Map('farmMapContainer', {
    zoom: 10,
    center: [lng, lat],
    viewMode: '2D'
  })

  console.log('[Map] 地图创建成功')

  // 添加点击事件
  farmMap.on('click', (e: any) => {
    const lng = e.lnglat.getLng()
    const lat = e.lnglat.getLat()
    farmForm.lat = lat
    farmForm.lng = lng

    console.log('[Map] 点击位置:', lng, lat)

    // 更新标记位置
    if (farmMarker) {
      farmMarker.setPosition([lng, lat])
    } else {
      farmMarker = new window.AMap.Marker({
        position: [lng, lat]
      })
      farmMap.add(farmMarker)
    }
  })

  // 如果已有坐标，添加标记
  if (farmForm.lat && farmForm.lng) {
    farmMarker = new window.AMap.Marker({
      position: [farmForm.lng, farmForm.lat]
    })
    farmMap.add(farmMarker)
    console.log('[Map] 显示已有标记:', farmForm.lng, farmForm.lat)
  }
}

// 初始化农场概览地图
const initFarmOverviewMap = () => {
  nextTick(async () => {
    await waitForAMap()
    if (!window.AMap) return

    // 农场概览地图
    const farmContainer = document.getElementById('farmOverviewMap')
    if (farmContainer && currentFarm.value) {
      if (farmOverviewMap) {
        farmOverviewMap.destroy()
        farmOverviewMap = null
      }

      let lat = 36.65
      let lng = 117.12
      if (currentFarm.value.coords) {
        const match = currentFarm.value.coords.match(/([\d.]+).*?([\d.]+)/)
        if (match) {
          lat = parseFloat(match[1])
          lng = parseFloat(match[2])
        }
      }

      farmOverviewMap = new window.AMap.Map('farmOverviewMap', {
        zoom: 12,
        center: [lng, lat],
        viewMode: '2D'
      })

      const farmMarker = new window.AMap.Marker({
        position: [lng, lat]
      })
      farmOverviewMap.add(farmMarker)
    }

    // 设备分布地图
    const deviceContainer = document.getElementById('deviceMap')
    if (deviceContainer && devices.value.length > 0) {
      if (deviceMap) {
        deviceMap.destroy()
        deviceMap = null
      }

      deviceMap = new window.AMap.Map('deviceMap', {
        zoom: 10,
        center: [117.12, 36.65],
        viewMode: '2D'
      })

      // 添加设备标记
      devices.value.forEach((device: any) => {
        if (device.lat && device.lng) {
          const marker = new window.AMap.Marker({
            position: [device.lng, device.lat],
            title: device.name
          })
          deviceMap.add(marker)
        }
      })
    }
  })
}

// 当地图对话框打开时初始化
watch(() => farmDialogVisible, (val) => {
  if (val) {
    console.log('[Map] 对话框打开，等待初始化...')
    setTimeout(initMapPicker, 500)
  }
})

// 监听当前农场变化，更新概览地图
watch(currentFarmId, () => {
  setTimeout(initFarmOverviewMap, 300)
}, { immediate: true })

// 切换标签页时加载对应数据
watch(() => activeTab.value, (tab) => {
  if (tab === 'crop' && crops.value.length === 0) {
    loadCrops()
  }
  if (tab === 'device') {
    setTimeout(initFarmOverviewMap, 300)
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
  // 直接在这里初始化地图
  setTimeout(() => {
    console.log('[Map] showFarmDialog 中初始化地图')
    initMapPicker()
  }, 300)
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
const deviceForm = reactive({
  name: '', type: '', location: '',
  serialNumber: '', status: 'online', landId: '', installDate: '', lastMaintenance: ''
})

const showDeviceDialog = () => {
  Object.assign(deviceForm, {
    name: '', type: '', location: '',
    serialNumber: '', status: 'online', landId: '', installDate: '', lastMaintenance: ''
  })
  deviceDialogVisible.value = true
}

const saveDevice = async () => {
  try {
    // 映射字段名到后端期望的格式
    const payload = {
      name: deviceForm.name,
      device_type: deviceForm.type,
      location: deviceForm.location,
      land_id: deviceForm.landId || null,
      status: deviceForm.status,
      serial_number: deviceForm.serialNumber,
      install_date: deviceForm.installDate,
      last_maintenance: deviceForm.lastMaintenance
    }
    await axios.post(`${API_BASE}/devices`, payload)
    ElMessage.success('设备添加成功')
    deviceDialogVisible.value = false
    fetchDevices()
  } catch (e: any) { ElMessage.error('添加失败') }
}

const icons: any = { temp: Sunny, humidity: Cloudy, soil: Grid, weather: Sunny, camera: VideoCamera }

// 智能决策系统数据
const cropModels = ref<any[]>([])
const decisionRecords = ref<any[]>([])
const decisionDialogVisible = ref(false)
const decisionForm = reactive({ landId: undefined as number | undefined, decisionType: '灌溉' })

const loadCropModels = async () => {
  try {
    const res = await axios.get(`${API_BASE}/decision/models`)
    cropModels.value = res.data
  } catch (e) { console.error('加载作物模型失败', e) }
}

const loadDecisionRecords = async () => {
  try {
    const res = await axios.get(`${API_BASE}/decision/records`)
    decisionRecords.value = res.data
  } catch (e) { console.error('加载决策记录失败', e) }
}

const showDecisionDialog = () => {
  Object.assign(decisionForm, { landId: undefined, decisionType: '灌溉' })
  decisionDialogVisible.value = true
}

const generateDecision = async () => {
  try {
    const res = await axios.post(`${API_BASE}/decision/generate`, decisionForm)
    ElMessage.success('决策生成成功')
    decisionDialogVisible.value = false
    loadDecisionRecords()
  } catch (e) { ElMessage.error('生成失败') }
}

const executeDecision = async (id: number) => {
  try {
    await axios.post(`${API_BASE}/decision/records/${id}/execute`)
    ElMessage.success('执行成功')
    loadDecisionRecords()
  } catch (e) { ElMessage.error('执行失败') }
}

// 追溯系统数据
const traceabilityRecords = ref<any[]>([])
const traceabilityDialogVisible = ref(false)
const traceabilityForm = reactive({ productName: '', productBatch: '', category: '', originFarm: '', originAddress: '', plantingDate: '', harvestDate: '' })

const loadTraceabilityRecords = async () => {
  try {
    const res = await axios.get(`${API_BASE}/traceability/records`)
    traceabilityRecords.value = res.data
  } catch (e) { console.error('加载追溯记录失败', e) }
}

const showTraceabilityDialog = () => {
  Object.assign(traceabilityForm, { productName: '', productBatch: '', category: '', originFarm: '', originAddress: '', plantingDate: '', harvestDate: '' })
  traceabilityDialogVisible.value = true
}

const saveTraceability = async () => {
  try {
    await axios.post(`${API_BASE}/traceability/records`, traceabilityForm)
    ElMessage.success('追溯记录添加成功')
    traceabilityDialogVisible.value = false
    loadTraceabilityRecords()
  } catch (e) { ElMessage.error('添加失败') }
}

// 加载新模块数据
onMounted(() => {
  fetchFarms()
  fetchLands()
  loadCrops()
  fetchDevices()
  loadSoilData()
  loadWeatherData()
  loadIrrigationData()
  loadAnalytics()
  loadCropModels()
  loadDecisionRecords()
  loadTraceabilityRecords()
})
</script>

<style scoped>
.smart-agri-container {
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  background: var(--bg-secondary, #F8FAFC);
  min-height: calc(100vh - 64px);
}

@media (max-width: 768px) {
  .smart-agri-container {
    padding: 20px;
  }
}

.section-card {
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 20px;
  transition: all 0.3s ease;
}

.section-card :deep(.el-card__header) {
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-color, #E2E8F0);
  background: var(--bg-secondary, #F8FAFC);
}

.section-card :deep(.el-card__body) {
  padding: 20px 24px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header span { font-size: 14px; font-weight: 500; }

.stats-row { margin-bottom: 15px; }
.stat-box { text-align: center; padding: 10px; background: #f5f7fa; border-radius: 8px; }
.stat-box .num { display: block; font-size: 20px; font-weight: bold; color: #409eff; }
.stat-box .label { font-size: 11px; color: #909399; }

.land-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.land-card { padding: 10px; transition: all 0.3s ease; }
.land-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.land-card h4 { margin: 0 0 5px 0; font-size: 14px; }
.land-card p { margin: 2px 0; font-size: 12px; color: #909399; }
.land-actions { display: flex; gap: 5px; margin-top: 8px; }

.crop-list { display: flex; flex-direction: column; gap: 10px; }
.crop-card { padding: 10px; transition: all 0.3s ease; }
.crop-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
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
.device-card { display: flex; align-items: center; padding: 10px; transition: all 0.3s ease; }
.device-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.device-icon .el-icon { font-size: 28px; }
.device-icon .online { color: #67c23a; }
.device-icon .warning { color: #e6a23c; }
.device-icon .offline { color: #909399; }
.device-info { flex: 1; margin-left: 10px; }
.device-info h4 { margin: 0; font-size: 14px; }
.device-info p { margin: 2px 0; font-size: 11px; color: #909399; }

.monitor-stats { display: flex; flex-wrap: wrap; }
.monitor-item { text-align: center; padding: 10px; background: #f5f7fa; border-radius: 8px; margin-bottom: 8px; width: 33.33%; transition: all 0.3s ease; }
.monitor-item:hover { transform: scale(1.02); }
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
.soil-card { padding: 10px; transition: all 0.3s ease; }
.soil-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.soil-card h4 { margin: 0 0 8px 0; font-size: 13px; }
.soil-info { display: flex; flex-wrap: wrap; gap: 8px; font-size: 11px; color: #606266; }

.farm-map, .device-map { margin-top: 10px; }
.coords { text-align: center; font-size: 12px; color: #909399; margin-top: 5px; }

@media (min-width: 769px) {
  .land-grid { grid-template-columns: repeat(4, 1fr); }
  .crop-list { flex-direction: row; flex-wrap: wrap; }
  .crop-card { width: calc(50% - 5px); }
}

/* ========== 页面头部 ========== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 28px;
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #0F172A);
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}

.page-subtitle {
  font-size: 15px;
  color: var(--text-secondary, #475569);
  margin: 0;
}

/* ========== 快捷入口导航 ========== */
.quick-nav-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.nav-card {
  position: relative;
  background: var(--bg-primary, #FFFFFF);
  border: 1px solid var(--border-color, #E2E8F0);
  border-radius: 14px;
  padding: 16px 12px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  animation: fadeInUp 0.4s ease forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.nav-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
  border-color: var(--accent);
}

.nav-card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.nav-card:hover .nav-card-glow {
  transform: scaleX(1);
}

.nav-card-content {
  position: relative;
}

.nav-icon-wrapper {
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary, #F8FAFC);
  border-radius: 12px;
  margin: 0 auto 12px;
  transition: all 0.3s ease;
}

.nav-card:hover .nav-icon-wrapper {
  background: color-mix(in srgb, var(--accent) 10%, transparent);
}

.nav-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary, #0F172A);
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .quick-nav-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .quick-nav-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .nav-card {
    padding: 12px 8px;
  }

  .nav-icon-wrapper {
    width: 40px;
    height: 40px;
  }

  .nav-label {
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .quick-nav-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

.farm-lands { min-height: 40px; }
.empty-tip { color: #909399; font-size: 12px; text-align: center; padding: 10px; }
.farm-selector { margin-bottom: 10px; }
.farm-actions { display: flex; gap: 10px; }
.farm-detail { }


.map-picker { border: 1px solid #dcdfe6; border-radius: 4px; overflow: hidden; min-height: 280px; }
.map-tip { padding: 8px; background: #f5f7fa; font-size: 12px; color: #909399; text-align: center; }
.coord-display { padding: 8px; background: #f0f9ff; font-size: 12px; text-align: center; }
.coord-display .no-coord { color: #909399; }
.farm-dialog-content { max-height: 60vh; overflow-y: auto; }

