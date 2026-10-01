<template>
  <div class="page-container">
    <PageHeader title="智慧农业" subtitle="智能监测 · 科学管理 · 精准决策" />

    <ModuleNav v-model="activeTab" :groups="navGroups" aria-label="智慧农业功能导航" />

    <!-- 地块管理 -->
    <div v-show="activeTab === 'land'">
      <div class="stat-grid stat-grid--3">
        <StatCard :value="lands.length" title="地块数" :icon="MapLocation" />
        <StatCard :value="totalLandArea" unit="亩" title="总面积" :icon="Crop" />
        <StatCard :value="lands.filter(l => l.status === 'normal').length" title="正常" type="success" :icon="CircleCheck" />
      </div>

      <SectionCard title="地块管理" :icon="MapLocation">
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showLandDialog()">添加地块</el-button>
        </template>
        <div class="tile-grid">
          <div v-for="land in lands" :key="land.id" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ land.name }}</span>
              <el-tag :type="land.status === 'normal' ? 'success' : 'warning'">
                {{ land.status === 'normal' ? '正常' : '预警' }}
              </el-tag>
            </div>
            <div class="tile-meta">
              <span>农场：{{ land.farm_name || '未分配' }}</span>
              <span>面积：{{ land.area }} 亩</span>
              <span>作物：{{ land.crops && land.crops.length ? land.crops.join('、') : (land.crop || '未设置') }}</span>
            </div>
            <div class="tile-actions">
              <el-button type="primary" link @click="editLand(land)">编辑</el-button>
              <el-button type="danger" link @click="deleteLand(land)">删除</el-button>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 作物管理 -->
    <div v-show="activeTab === 'crop'">
      <SectionCard title="作物管理" :icon="Grape">
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showCropDialog()">添加作物</el-button>
        </template>
        <div class="tile-grid">
          <div v-for="crop in crops" :key="crop.id" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ crop.name }}</span>
              <el-tag :type="crop.status === 'active' ? 'success' : 'info'">
                {{ crop.status === 'active' ? '活跃' : '停用' }}
              </el-tag>
            </div>
            <div class="tile-meta">
              <span>分类：{{ crop.category }} · 种植季节：{{ crop.planting_season }}</span>
              <span>生长周期：{{ crop.growth_days }} 天</span>
              <span>亩产量：{{ crop.yield_per_mu }} 斤</span>
            </div>
            <div class="tile-actions">
              <el-button type="primary" link @click="editCrop(crop)">编辑</el-button>
              <el-button type="danger" link @click="deleteCrop(crop)">删除</el-button>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 农场信息 -->
    <div v-show="activeTab === 'farm'">
      <SectionCard title="农场信息" :icon="OfficeBuilding">
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showFarmDialog()">添加农场</el-button>
        </template>

        <el-select v-if="farms.length > 1" v-model="currentFarmId" placeholder="选择农场" class="w-full farm-select" @change="onFarmChange">
          <el-option v-for="f in farms" :key="f.id" :label="f.name" :value="f.id" />
        </el-select>

        <div v-if="currentFarm">
          <el-descriptions :column="2" border class="farm-descriptions">
            <el-descriptions-item label="农场名称">{{ currentFarm.name }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :type="currentFarm.status === 'normal' ? 'success' : 'warning'">
                {{ currentFarm.status === 'normal' ? '正常' : '预警' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="农场地址" :span="2">{{ currentFarm.address }}</el-descriptions-item>
            <el-descriptions-item label="总面积">{{ currentFarm.totalArea }} 亩</el-descriptions-item>
            <el-descriptions-item label="地块数量">{{ currentFarm.landCount }} 块</el-descriptions-item>
            <el-descriptions-item label="负责人">{{ currentFarm.manager }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ currentFarm.phone }}</el-descriptions-item>
          </el-descriptions>

          <div class="farm-actions">
            <el-button @click="editFarm(currentFarm)">编辑</el-button>
            <el-button type="danger" plain @click="deleteFarm(currentFarm)">删除农场</el-button>
          </div>

          <h4 class="subsection-title">地图概览</h4>
          <div id="farmOverviewMap" class="map-box"></div>
          <p class="map-caption">{{ currentFarm.coords }}</p>

          <h4 class="subsection-title">所属地块（{{ lands.filter(l => l.farm_id === currentFarm.id).length }}）</h4>
          <div class="farm-lands">
            <el-tag v-for="land in lands.filter(l => l.farm_id === currentFarm.id)" :key="land.id">
              {{ land.name }}（{{ land.area }} 亩）
            </el-tag>
            <span v-if="lands.filter(l => l.farm_id === currentFarm.id).length === 0" class="empty-tip">
              暂无地块，请添加
            </span>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 物联网设备 -->
    <div v-show="activeTab === 'device'">
      <div class="stat-grid">
        <StatCard :value="deviceStats.online" title="在线" type="success" :icon="CircleCheck" />
        <StatCard :value="deviceStats.offline" title="离线" type="danger" :icon="CircleClose" />
        <StatCard :value="deviceStats.warning" title="预警" type="warning" :icon="Warning" />
        <StatCard :value="deviceStats.total" title="总计" :icon="Cpu" />
      </div>

      <SectionCard title="物联网设备" :icon="Cpu">
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showDeviceDialog()">添加设备</el-button>
        </template>
        <div class="tile-grid">
          <div v-for="device in devices" :key="device.id" class="tile device-tile">
            <span class="device-icon" :class="`is-${device.status}`">
              <el-icon :size="22"><component :is="device.icon" /></el-icon>
            </span>
            <div class="device-body">
              <div class="tile-header">
                <span class="tile-title">{{ device.name }}</span>
                <el-tag :type="device.status === 'online' ? 'success' : device.status === 'warning' ? 'warning' : 'info'">
                  {{ device.status === 'online' ? '在线' : device.status === 'warning' ? '预警' : '离线' }}
                </el-tag>
              </div>
              <div class="tile-meta">
                <span>位置：{{ device.location }}</span>
                <span>最后更新：{{ device.lastUpdate }}</span>
              </div>
            </div>
          </div>
        </div>

        <h4 class="subsection-title">设备分布</h4>
        <div id="deviceMap" class="map-box"></div>
        <p class="map-caption">共 {{ devices.length }} 个设备</p>
      </SectionCard>
    </div>

    <!-- 环境监测 -->
    <div v-show="activeTab === 'monitor'">
      <div class="stat-grid stat-grid--3">
        <StatCard :value="monitorData.temperature" unit="°C" title="空气温度" :icon="Sunny" />
        <StatCard :value="monitorData.humidity" unit="%" title="空气湿度" :icon="Cloudy" />
        <StatCard :value="monitorData.soilMoisture" unit="%" title="土壤湿度" :icon="Grid" />
        <StatCard :value="monitorData.light" unit="lux" title="光照强度" :icon="Sunny" />
        <StatCard :value="monitorData.co2" unit="ppm" title="CO₂ 浓度" :icon="WindPower" />
        <StatCard :value="monitorData.rainfall" unit="mm" title="降雨量" :icon="Cloudy" />
      </div>

      <SectionCard title="土壤监测" :icon="DataAnalysis">
        <div class="tile-grid">
          <div v-for="soil in soilData" :key="soil.location" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ soil.location }}</span>
            </div>
            <div class="tile-meta soil-meta">
              <span>温度：{{ soil.temperature }}°C</span>
              <span>湿度：{{ soil.humidity }}%</span>
              <span>pH 值：{{ soil.ph }}</span>
              <span>含氮量：{{ soil.nitrogen }} mg/kg</span>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 智能决策 -->
    <div v-show="activeTab === 'decision'">
      <div class="stat-grid stat-grid--3">
        <StatCard :value="cropModels.length" title="作物模型" :icon="Histogram" />
        <StatCard :value="decisionRecords.length" title="决策记录" :icon="Document" />
        <StatCard :value="decisionRecords.filter(r => r.executed).length" title="已执行" type="success" :icon="CircleCheck" />
      </div>

      <SectionCard title="智能决策" :icon="TrendCharts">
        <template #extra>
          <el-button type="primary" @click="showDecisionDialog()">生成决策</el-button>
        </template>
        <el-alert title="基于农作物生长模型的智能决策系统" type="info" :closable="false" class="section-alert" />

        <h4 class="subsection-title">作物生长模型</h4>
        <div class="tile-grid">
          <div v-for="model in cropModels" :key="model.id" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ model.cropName }}</span>
              <el-tag>{{ model.modelVersion }}</el-tag>
            </div>
            <div class="tile-meta">
              <span>类型：{{ model.cropType }}</span>
              <span>预期产量：{{ model.expectedYield }} 斤/亩</span>
              <span>预测准确率：{{ model.predictionAccuracy }}%</span>
            </div>
          </div>
        </div>

        <h4 class="subsection-title">决策记录</h4>
        <el-timeline class="decision-timeline">
          <el-timeline-item v-for="record in decisionRecords" :key="record.id" :timestamp="record.createdAt" placement="top">
            <div class="tile">
              <div class="tile-header">
                <span class="decision-head">
                  <el-tag :type="record.decisionType === '灌溉' ? 'primary' : record.decisionType === '施肥' ? 'success' : 'warning'">
                    {{ record.decisionType }}
                  </el-tag>
                  <span class="tile-title">决策建议</span>
                </span>
                <el-button v-if="!record.executed" type="primary" @click="executeDecision(record.id)">执行</el-button>
                <el-tag v-else type="success">已执行</el-tag>
              </div>
              <p class="decision-text">{{ record.recommendation }}</p>
              <div class="tile-meta">置信度：{{ (record.confidence * 100).toFixed(0) }}%</div>
            </div>
          </el-timeline-item>
        </el-timeline>
      </SectionCard>
    </div>

    <!-- 全产业链追溯 -->
    <div v-show="activeTab === 'traceability'">
      <div class="stat-grid stat-grid--3">
        <StatCard :value="traceabilityRecords.length" title="追溯记录" :icon="Link" />
        <StatCard :value="traceabilityRecords.filter(r => r.status === 'active').length" title="在售" type="success" :icon="Sell" />
        <StatCard :value="traceabilityRecords.filter(r => r.status === 'sold').length" title="已售" :icon="ShoppingBag" />
      </div>

      <SectionCard title="全产业链追溯" :icon="Link">
        <template #extra>
          <el-button type="primary" :icon="Plus" @click="showTraceabilityDialog()">添加产品</el-button>
        </template>
        <el-alert title="农产品从田间到餐桌的全程追溯" type="info" :closable="false" class="section-alert" />
        <div class="tile-grid">
          <div v-for="record in traceabilityRecords" :key="record.id" class="tile">
            <div class="tile-header">
              <span class="tile-title">{{ record.productName }}</span>
              <el-tag :type="record.status === 'active' ? 'success' : 'info'">{{ record.status === 'active' ? '在售' : record.status }}</el-tag>
            </div>
            <div class="tile-meta">
              <span>批次：{{ record.productBatch }}</span>
              <span>产地：{{ record.originFarm }}</span>
              <span>追溯码：<el-tag class="inline-tag">{{ record.traceCode }}</el-tag></span>
              <span>种植：{{ record.plantingDate }} · 收获：{{ record.harvestDate }}</span>
            </div>
          </div>
        </div>
      </SectionCard>
    </div>

    <!-- 地块对话框 -->
    <el-dialog v-model="landDialogVisible" :title="isEditLand ? '编辑地块' : '添加地块'" class="dialog-md">
      <el-form :model="landForm" label-width="90px">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="所属农场">
              <el-select v-model="landForm.farm_id" placeholder="选择农场" class="w-full">
                <el-option v-for="f in farms" :key="f.id" :label="f.name" :value="f.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="名称">
              <el-input v-model="landForm.name" placeholder="地块名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="面积(亩)">
              <el-input-number v-model="landForm.area" :min="1" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="作物">
              <el-input v-model="landForm.crop" placeholder="种植作物" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">土地属性</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="土壤类型">
              <el-select v-model="landForm.soilType" class="w-full">
                <el-option label="沙土" value="沙土" />
                <el-option label="壤土" value="壤土" />
                <el-option label="粘土" value="粘土" />
                <el-option label="沙壤土" value="沙壤土" />
                <el-option label="粘壤土" value="粘壤土" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="灌溉方式">
              <el-select v-model="landForm.irrigationType" class="w-full">
                <el-option label="滴灌" value="滴灌" />
                <el-option label="喷灌" value="喷灌" />
                <el-option label="漫灌" value="漫灌" />
                <el-option label="沟灌" value="沟灌" />
                <el-option label="微喷" value="微喷" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="海拔(米)">
              <el-input-number v-model="landForm.altitude" :min="0" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="状态">
              <el-select v-model="landForm.status" class="w-full">
                <el-option label="正常" value="normal" />
                <el-option label="预警" value="warning" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="landDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLand">保存</el-button>
      </template>
    </el-dialog>

    <!-- 作物对话框 -->
    <el-dialog v-model="cropDialogVisible" :title="isEditCrop ? '编辑作物' : '添加作物'" class="dialog-md">
      <el-form :model="cropForm" label-width="90px">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="作物名称" required>
              <el-input v-model="cropForm.name" placeholder="如：水稻、小麦、西红柿" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="品种">
              <el-input v-model="cropForm.variety" placeholder="如：优系一号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="分类">
              <el-select v-model="cropForm.category" class="w-full">
                <el-option label="粮食" value="粮食" />
                <el-option label="蔬菜" value="蔬菜" />
                <el-option label="水果" value="水果" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="种植季节">
              <el-select v-model="cropForm.planting_season" class="w-full">
                <el-option label="春季" value="春季" />
                <el-option label="夏季" value="夏季" />
                <el-option label="秋季" value="秋季" />
                <el-option label="冬季" value="冬季" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">种植信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="种植日期">
              <el-date-picker v-model="cropForm.plantingDate" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="预计收获">
              <el-date-picker v-model="cropForm.expectedHarvest" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="生长周期">
              <el-input-number v-model="cropForm.growth_days" :min="1" :max="365" class="w-full" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="亩产量(斤)">
              <el-input-number v-model="cropForm.yield_per_mu" :min="1" class="w-full" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="cropDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCrop">保存</el-button>
      </template>
    </el-dialog>

    <!-- 设备对话框 -->
    <el-dialog v-model="deviceDialogVisible" title="添加设备" class="dialog-md">
      <el-form :model="deviceForm" label-width="90px">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="设备名" required>
              <el-input v-model="deviceForm.name" placeholder="设备名称" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="序列号">
              <el-input v-model="deviceForm.serialNumber" placeholder="设备序列号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="设备类型">
              <el-select v-model="deviceForm.type" class="w-full">
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
          <el-col :xs="24" :sm="12">
            <el-form-item label="设备状态">
              <el-select v-model="deviceForm.status" class="w-full">
                <el-option label="在线" value="online" />
                <el-option label="离线" value="offline" />
                <el-option label="维护中" value="maintenance" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">安装信息</div>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="所属地块">
              <el-select v-model="deviceForm.landId" class="w-full" placeholder="选择地块">
                <el-option v-for="l in lands" :key="l.id" :label="l.name" :value="l.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="安装位置">
              <el-input v-model="deviceForm.location" placeholder="安装位置" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="安装日期">
              <el-date-picker v-model="deviceForm.installDate" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="最后维护">
              <el-date-picker v-model="deviceForm.lastMaintenance" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="deviceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveDevice">保存</el-button>
      </template>
    </el-dialog>

    <!-- 农场信息编辑对话框 -->
    <el-dialog v-model="farmDialogVisible" :title="isEditFarm ? '编辑农场' : '添加农场'" class="dialog-lg" top="5vh">
      <el-form :model="farmForm" label-width="90px">
        <el-form-item label="农场名称" required>
          <el-input v-model="farmForm.name" placeholder="农场名称" />
        </el-form-item>
        <el-form-item label="农场地址">
          <el-input v-model="farmForm.address" placeholder="农场地址" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :xs="24" :sm="12">
            <el-form-item label="经度">
              <el-input-number v-model="farmForm.lng" :step="0.01" :precision="6" class="w-full" placeholder="经度" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12">
            <el-form-item label="纬度">
              <el-input-number v-model="farmForm.lat" :step="0.01" :precision="6" class="w-full" placeholder="纬度" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="地图选点">
          <div class="map-picker">
            <div id="farmMapContainer" class="map-box map-box--picker"></div>
            <div class="map-caption">
              <span v-if="farmForm.lat && farmForm.lng">
                已选坐标：{{ farmForm.lat.toFixed(4) }}, {{ farmForm.lng.toFixed(4) }}
              </span>
              <span v-else>点击地图选择位置</span>
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
          <el-select v-model="farmForm.status" class="w-full">
            <el-option label="正常" value="normal" />
            <el-option label="预警" value="warning" />
          </el-select>
        </el-form-item>
        <el-form-item label="农场描述">
          <el-input v-model="farmForm.description" type="textarea" placeholder="农场描述" :rows="2" />
        </el-form-item>
        <el-form-item label="成立日期">
          <el-date-picker v-model="farmForm.established_date" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="farmDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveFarm">保存</el-button>
      </template>
    </el-dialog>

    <!-- 智能决策生成对话框 -->
    <el-dialog v-model="decisionDialogVisible" title="生成智能决策" class="dialog-sm">
      <el-form :model="decisionForm" label-width="80px">
        <el-form-item label="决策类型">
          <el-select v-model="decisionForm.decisionType" class="w-full">
            <el-option label="灌溉" value="灌溉" />
            <el-option label="施肥" value="施肥" />
            <el-option label="喷药" value="喷药" />
            <el-option label="收获预警" value="收获预警" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="decisionDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="generateDecision">生成</el-button>
      </template>
    </el-dialog>

    <!-- 追溯记录添加对话框 -->
    <el-dialog v-model="traceabilityDialogVisible" title="添加追溯记录" class="dialog-sm">
      <el-form :model="traceabilityForm" label-width="80px">
        <el-form-item label="产品名称">
          <el-input v-model="traceabilityForm.productName" placeholder="如：有机大米" />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input v-model="traceabilityForm.productBatch" placeholder="如：RICE20260219" />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="traceabilityForm.category" class="w-full">
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
          <el-date-picker v-model="traceabilityForm.plantingDate" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
        <el-form-item label="收获日期">
          <el-date-picker v-model="traceabilityForm.harvestDate" type="date" placeholder="选择日期" class="w-full" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="traceabilityDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTraceability">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  CircleCheck, CircleClose, Cloudy, Cpu, Crop, DataAnalysis, Document, Grape, Grid, Histogram, Link, MapLocation,
  OfficeBuilding, Plus, Sell, ShoppingBag, Sunny, TrendCharts, Warning, WindPower
} from '@element-plus/icons-vue'
import type { ModuleNavGroup } from '../components/ui/ModuleNav.vue'
import { createLatestGuard } from '../utils/latest'
import axios from 'axios'

declare global {
  interface Window {
    AMap: any
  }
}

const API_BASE = '/api/smart-agriculture'

const activeTab = ref('land')
const navGroups: ModuleNavGroup[] = [
  {
    label: '生产管理',
    items: [
      { key: 'farm', label: '农场信息', icon: OfficeBuilding },
      { key: 'land', label: '地块管理', icon: MapLocation },
      { key: 'crop', label: '作物管理', icon: Grape }
    ]
  },
  {
    label: '物联监测',
    items: [
      { key: 'device', label: '物联网设备', icon: Cpu },
      { key: 'monitor', label: '环境监测', icon: DataAnalysis }
    ]
  },
  {
    label: '决策与追溯',
    items: [
      { key: 'decision', label: '智能决策', icon: TrendCharts },
      { key: 'traceability', label: '追溯系统', icon: Link }
    ]
  }
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

// 监测数据（来自 /monitor：各监测站最新读数均值，降雨量为近 24 小时累计）
type MonitorKey = 'temperature' | 'humidity' | 'soilMoisture' | 'light' | 'co2' | 'rainfall'
const monitorKeys: MonitorKey[] = ['temperature', 'humidity', 'soilMoisture', 'light', 'co2', 'rainfall']
const monitorData = reactive<Record<MonitorKey, number | string>>({
  temperature: '--', humidity: '--', soilMoisture: '--', light: '--', co2: '--', rainfall: '--'
})
const loadMonitorData = async () => {
  try {
    const res = await axios.get(`${API_BASE}/monitor`)
    monitorKeys.forEach((k) => {
      const v = res.data?.[k]
      monitorData[k] = v === null || v === undefined ? '--' : v
    })
  } catch (e) {
    console.error('加载环境监测数据失败', e)
  }
}

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
const overviewGuard = createLatestGuard()

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
  // 农场切换/面板切换可能连续触发，只认最新一次；卸载后放弃
  const isCurrent = overviewGuard.begin()
  nextTick(async () => {
    await waitForAMap()
    if (!isCurrent() || !window.AMap) return

    // 农场概览地图
    // 面板为 v-show 常驻：地图只建一次（resizeEnable 让隐藏时创建的地图在显示后恢复尺寸），之后清空覆盖物重画
    const farmContainer = document.getElementById('farmOverviewMap')
    if (farmContainer && currentFarm.value) {

      let lat = 36.65
      let lng = 117.12
      if (currentFarm.value.coords) {
        const match = currentFarm.value.coords.match(/([\d.]+).*?([\d.]+)/)
        if (match) {
          lat = parseFloat(match[1])
          lng = parseFloat(match[2])
        }
      }

      if (farmOverviewMap) {
        farmOverviewMap.clearMap()
        farmOverviewMap.setZoomAndCenter(12, [lng, lat])
      } else {
        farmOverviewMap = new window.AMap.Map('farmOverviewMap', {
          zoom: 12,
          center: [lng, lat],
          viewMode: '2D',
          resizeEnable: true
        })
      }

      const farmMarker = new window.AMap.Marker({
        position: [lng, lat]
      })
      farmOverviewMap.add(farmMarker)
    }

    // 设备分布地图
    const deviceContainer = document.getElementById('deviceMap')
    if (deviceContainer && devices.value.length > 0) {
      if (deviceMap) {
        deviceMap.clearMap()
      } else {
        deviceMap = new window.AMap.Map('deviceMap', {
          zoom: 10,
          center: [117.12, 36.65],
          viewMode: '2D',
          resizeEnable: true
        })
      }

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
  // 农场概览图与设备分布图分别在 farm / device 面板；进入时（容器已可见）重画
  if (tab === 'device' || tab === 'farm') {
    initFarmOverviewMap()
  }
})

onBeforeUnmount(() => {
  overviewGuard.invalidate()
  farmMap?.destroy()
  farmOverviewMap?.destroy()
  deviceMap?.destroy()
  farmMap = null
  farmOverviewMap = null
  deviceMap = null
})

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
    await axios.post(`${API_BASE}/decision/generate`, decisionForm)
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
  loadMonitorData()
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
.farm-select {
  margin-bottom: 16px;
}

.farm-actions {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.map-box {
  width: 100%;
  height: 240px;
  overflow: hidden;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.map-box--picker {
  height: 280px;
}

.map-picker {
  width: 100%;
}

.map-caption {
  margin: 8px 0 0;
  font-size: var(--font-xs);
  color: var(--text-tertiary);
}

.farm-lands {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.empty-tip {
  font-size: var(--font-sm);
  color: var(--text-tertiary);
}

.device-tile {
  display: flex;
  gap: 12px;
}

.device-body {
  flex: 1;
  min-width: 0;
}

.device-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  color: var(--text-tertiary);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
}

.device-icon.is-online { color: var(--color-success); }
.device-icon.is-warning { color: var(--color-warning); }

.soil-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.section-alert {
  margin-bottom: 16px;
}

.decision-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.decision-text {
  margin: 0 0 6px;
  font-size: var(--font-sm);
  color: var(--text-primary);
}

.inline-tag {
  margin-left: 2px;
}
</style>
