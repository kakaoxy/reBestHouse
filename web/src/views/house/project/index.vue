<template>
  <CommonPage>
    <n-card :bordered="false" class="proCard">
      <!-- 顶部操作栏 -->
      <n-space vertical :size="16">
        <n-space justify="space-between" align="center">
          <n-space align="center" :size="8">
            <!-- 城市选择器 -->
            <n-select
              v-model:value="cityStore.currentCity"
              :options="cityStore.CITY_OPTIONS"
              style="width: 120px"
              @update:value="handleCityChange"
            />
            <!-- 小区搜索框 -->
            <n-input
              v-model:value="searchParams.community_name"
              type="text"
              placeholder="输入小区名称搜索"
              style="width: 200px"
              clearable
              @keyup.enter="handleSearch"
            />
            <n-button type="primary" @click="handleSearch">
              <template #icon>
                <TheIcon icon="material-symbols:search" />
              </template>
              搜索
            </n-button>
            <n-button @click="handleReset">
              <template #icon>
                <TheIcon icon="material-symbols:refresh" />
              </template>
              重置
            </n-button>
          </n-space>
          <!-- 新增按钮 -->
          <n-button type="primary" @click="handleAdd">
            <template #icon>
              <TheIcon icon="material-symbols:add" />
            </template>
            新增项目
          </n-button>
        </n-space>

        <!-- 项目阶段展示区域 -->
        <div class="project-phases">
          <div class="phase-row" v-for="(row, rowIndex) in phaseRows" :key="rowIndex">
            <div
              v-for="phase in row"
              :key="phase.value"
              class="phase-container"
              :class="{ 'drop-active': isDraggingOver === phase.value }"
              @dragover.prevent="handleDragOver(phase.value)"
              @drop="handleDrop($event, phase.value)"
            >
              <div class="phase-header">
                <span class="phase-name">{{ phase.label }}</span>
                <span class="project-count">({{ getProjectCountByPhase(phase.value) }})</span>
              </div>
              <div class="project-cards">
                <n-card
                  v-for="project in getProjectsByPhase(phase.value)"
                  :key="project.id"
                  class="project-card"
                  :class="{ 'dragging': isDragging === project.id }"
                  draggable="true"
                  @dragstart="handleDragStart($event, project)"
                  @dragend="handleDragEnd"
                  @click="handleProjectClick(project)"
                >
                  <template #header>
                    <div class="card-header">
                      <span class="community-name">{{ project.community_name }}</span>
                      <n-tag :type="getStatusType(project.status)">
                        {{ project.status }}
                      </n-tag>
                    </div>
                  </template>
                  <div class="card-content">
                    <p class="address">{{ project.address }}</p>
                    <p class="company">装修公司: {{ project.company_name }}</p>
                    <p class="days">
                      进场天数: {{ getDaysSinceDelivery(project.delivery_date) }}天
                    </p>
                    <div v-if="project.decoration_company" class="decoration-company">
                      装修公司：{{ project.decoration_company }}
                    </div>
                  </div>
                </n-card>
              </div>
            </div>
          </div>
        </div>
      </n-space>
    </n-card>

    <!-- 新增/编辑项目弹窗 -->
    <ProjectModal
      v-model:show="showModal"
      :title="modalTitle"
      :form-params="formParams"
      @submit="handleModalSubmit"
      @cancel="handleModalCancel"
    />
  </CommonPage>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useCityStore } from '@/store/modules/city'
import { projectApi } from '@/api/house'
import ProjectModal from './components/ProjectModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

const message = useMessage()
const cityStore = useCityStore()

// 项目阶段定义
const PHASE_OPTIONS = [
  { label: '交房', value: 'delivery' },
  { label: '设计', value: 'design' },
  { label: '拆除', value: 'demolition' },
  { label: '水电', value: 'plumbing' },
  { label: '木瓦', value: 'carpentry' },
  { label: '油漆', value: 'painting' },
  { label: '安装', value: 'installation' },
  { label: '交付', value: 'completion' }
]

// 将阶段分成两行
const phaseRows = computed(() => {
  const halfLength = Math.ceil(PHASE_OPTIONS.length / 2)
  return [
    PHASE_OPTIONS.slice(0, halfLength),
    PHASE_OPTIONS.slice(halfLength)
  ]
})

// 搜索参数
const searchParams = ref({
  community_name: '',
  city: cityStore.currentCity
})

// 项目列表数据
const projectList = ref([])
const loading = ref(false)

// 拖拽相关状态
const isDragging = ref(null)
const isDraggingOver = ref(null)

// 模态框相关
const showModal = ref(false)
const modalTitle = ref('')
const formParams = ref({})

// 获取项目列表
const loadProjects = async () => {
  loading.value = true
  try {
    const res = await projectApi.list(searchParams.value)
    if (res.code === 200) {
      projectList.value = res.data.items
    }
  } catch (error) {
    message.error('获取项目列表失败')
  } finally {
    loading.value = false
  }
}

// 按阶段获取项目
const getProjectsByPhase = (phase) => {
  return projectList.value.filter(p => p.current_phase === phase)
}

// 获取各阶段项目数量
const getProjectCountByPhase = (phase) => {
  return getProjectsByPhase(phase).length
}

// 计算进场天数
const getDaysSinceDelivery = (deliveryDate) => {
  if (!deliveryDate) return 0
  const delivery = new Date(deliveryDate)
  const today = new Date()
  return Math.floor((today - delivery) / (1000 * 60 * 60 * 24))
}

// 获取状态样式
const getStatusType = (status) => {
  const types = {
    'delivery': 'default',
    'design': 'info',
    'demolition': 'warning',
    'plumbing': 'warning',
    'carpentry': 'warning',
    'painting': 'warning',
    'installation': 'success',
    'completion': 'success'
  }
  return types[status] || 'default'
}

// 处理拖拽
const handleDragStart = (e, project) => {
  e.dataTransfer.setData('projectId', project.id)
}

const handleDragEnd = () => {
  isDragging.value = null
  isDraggingOver.value = null
}

const handleDragOver = (phase) => {
  isDraggingOver.value = phase
}

const handleDrop = async (e, phase) => {
  const projectId = e.dataTransfer.getData('projectId')
  const project = projectList.value.find(p => p.id === Number(projectId))
  
  if (!project) return
  
  try {
    const res = await projectApi.update(projectId, {
      current_phase: phase
    })
    
    if (res.code === 200) {
      // 更新本地数据，避免刷新
      project.current_phase = phase
      message.success('更新项目阶段成功')
    } else {
      message.error(res.message || '更新项目阶段失败')
      // 如果失败，刷新列表
      loadProjects()
    }
  } catch (error) {
    console.error('Update project phase error:', error)
    message.error('更新项目阶段失败')
    // 如果出错，刷新列表
    loadProjects()
  }
}

// 处理搜索和重置
const handleSearch = () => {
  loadProjects()
}

const handleReset = () => {
  searchParams.value = {
    community_name: '',
    city: cityStore.currentCity
  }
  loadProjects()
}

// 处理城市变化
const handleCityChange = (city) => {
  cityStore.setCurrentCity(city)
  searchParams.value.city = city
  loadProjects()
}

// 处理新增项目
const handleAdd = () => {
  modalTitle.value = '新增项目'
  formParams.value = {
    community_id: null,
    address: '',
    contract_price: null,
    contract_period: null,
    signer: '',
    delivery_date: null,
    current_phase: 'delivery'
  }
  showModal.value = true
}

// 处理项目点击
const handleProjectClick = (project) => {
  modalTitle.value = '编辑项目'
  formParams.value = { ...project }
  showModal.value = true
}

// 处理模态框提交
const handleModalSubmit = async (data) => {
  try {
    if (data.id) {
      await projectApi.update(data.id, data)
      message.success('更新项目成功')
    } else {
      await projectApi.create(data)
      message.success('创建项目成功')
    }
    showModal.value = false
    loadProjects()
  } catch (error) {
    message.error(error.response?.data?.detail || '操作失败')
  }
}

const handleModalCancel = () => {
  showModal.value = false
}

onMounted(() => {
  loadProjects()
})
</script>

<style lang="scss" scoped>
.project-phases {
  margin-top: 16px;
  
  .phase-row {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    
    &:last-child {
      margin-bottom: 0;
    }
  }

  .phase-container {
    flex: 1;
    min-height: 300px;
    background: #f5f5f5;
    border-radius: 8px;
    padding: 12px;
    
    &.drop-active {
      background: #e6f4ff;
      border: 2px dashed #1890ff;
    }
  }

  .phase-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    .phase-name {
      font-weight: bold;
      font-size: 16px;
    }
    
    .project-count {
      color: #999;
    }
  }

  .project-cards {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .project-card {
    cursor: move;
    
    &.dragging {
      opacity: 0.5;
    }
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .community-name {
        font-weight: bold;
      }
    }
    
    .card-content {
      font-size: 14px;
      
      p {
        margin: 4px 0;
      }
      
      .address {
        color: #666;
      }
      
      .company {
        color: #1890ff;
      }
      
      .days {
        color: #f5222d;
      }
    }
  }
}

.decoration-company {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}
</style> 