<template>
  <CommonPage>
    <n-card :bordered="false" class="project-dashboard">
      <!-- 顶部操作栏 -->
      <n-space vertical :size="24">
        <n-space justify="space-between" align="center">
          <n-space align="center" :size="12">
            <!-- 城市选择器 -->
            <n-select
              v-model:value="selectedCity"
              :options="departmentStore.departments"
              :render-label="renderLabel"
              style="width: 120px"
              :disabled="!userStore.isSuperUser"
              @update:value="handleCityChange"
            />
            <!-- 小区搜索框 -->
            <n-input
              v-model:value="searchParams.community_name"
              type="text"
              placeholder="输入小区名称搜索"
              style="width: 240px"
              clearable
              @keyup.enter="handleSearch"
            />
            <n-button 
              type="primary" 
              @click="handleSearch"
              :theme-overrides="buttonThemeOverrides"
            >
              <template #icon>
                <TheIcon icon="material-symbols:search" />
              </template>
              搜索
            </n-button>
            <n-button 
              quaternary 
              @click="handleReset"
              :theme-overrides="buttonThemeOverrides"
            >
              <template #icon>
                <TheIcon icon="material-symbols:refresh" />
              </template>
              重置
            </n-button>
          </n-space>
          <!-- 新增按钮 -->
          <n-button 
            type="primary" 
            @click="handleAdd"
            :theme-overrides="buttonThemeOverrides"
          >
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
                <span class="project-count">{{ getProjectCountByPhase(phase.value) }}</span>
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
                  <div class="card-content">
                    <div class="location-info">
                      <div class="community-name">
                        {{ project.community_name || '未找到' }}
                        <n-dropdown
                          trigger="hover"
                          :options="[
                            {
                              label: '删除项目',
                              key: 'delete',
                              props: {
                                style: 'color: #d03050;'
                              }
                            }
                          ]"
                          @select="handleProjectAction($event, project)"
                          placement="bottom-end"
                        >
                          <n-button
                            quaternary
                            circle
                            size="tiny"
                            style="position: absolute; right: 8px; top: 8px;"
                          >
                            <template #icon>
                              <TheIcon icon="material-symbols:more-vert" />
                            </template>
                          </n-button>
                        </n-dropdown>
                      </div>
                      <div class="address-text">{{ project.address }}</div>
                    </div>
                    <div class="main-info">
                      <span class="decoration-company">{{ project.decoration_company || '未指定' }}</span>
                      <span class="days-tag">{{ getDaysSinceDelivery(project.delivery_date) }}天</span>
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

    <!-- 项目详情弹窗 -->
    <ProjectDetail
      v-model:show="showDetail"
      :project-id="selectedProjectId"
      @project-updated="handleProjectUpdated"
    />
  </CommonPage>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { useDepartmentStore } from '@/stores/department'
import { useUserStore } from '@/store/modules/user'
import { projectApi } from '@/api/house'
import ProjectModal from './components/ProjectModal.vue'
import ProjectDetail from './components/ProjectDetail.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

const message = useMessage()
const dialog = useDialog()
const departmentStore = useDepartmentStore()
const userStore = useUserStore()

// 选中的城市
const selectedCity = ref(null)

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
  city: departmentStore.currentDepartment || 'shanghai'
})

// 渲染城市选择器的标签
const renderLabel = (option) => {
  return option.label
}

// 处理城市变化
const handleCityChange = (value) => {
  selectedCity.value = value
  searchParams.value.city = value
  departmentStore.setDepartment(value)
  loadProjects() // 刷新项目列表
}

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

// 详情弹窗相关
const showDetail = ref(false)
const selectedProjectId = ref(null)

// 添加按钮主题覆盖
const buttonThemeOverrides = {
  borderRadius: '6px',
  heightMedium: '34px',
  paddingMedium: '0 16px',
  fontSizeMedium: '14px'
}

// 获取项目列表
const loadProjects = async () => {
  loading.value = true
  try {
    const params = {
      ...searchParams.value,
      city: selectedCity.value
    }
    const res = await projectApi.list(params)
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
    city: selectedCity.value
  }
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
  selectedProjectId.value = project.id
  showDetail.value = true
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

// 处理项目更新
const handleProjectUpdated = (updatedProject) => {
  // 找到并更新项目列表中的项目
  const index = projectList.value.findIndex(p => p.id === updatedProject.id)
  if (index !== -1) {
    projectList.value[index] = {
      ...projectList.value[index],
      ...updatedProject
    }
  }
}

// 处理项目操作
const handleProjectAction = async (key, project) => {
  if (key === 'delete') {
    dialog.warning({
      title: '确认删除',
      content: `确定要删除项目"${project.community_name}"吗？此操作不可恢复。`,
      positiveText: '确定',
      negativeText: '取消',
      async onPositiveClick() {
        try {
          loading.value = true;
          await projectApi.delete(project.id);
          message.success('删除成功');
          await loadProjects();
        } catch (error) {
          if (error?.response?.data?.detail) {
            message.error(error.response.data.detail);
          }
        } finally {
          loading.value = false;
        }
      }
    });
  }
}

// 监听城市变化
watch(
  () => departmentStore.currentDepartment,
  (newValue, oldValue) => {
    if (newValue) {
      selectedCity.value = newValue
      searchParams.value.city = newValue
      loadProjects() // 刷新项目列表
    }
  },
  { immediate: true }
)

onMounted(async () => {
  await departmentStore.getDepartmentOptions()
  await departmentStore.initCurrentDepartment()
  selectedCity.value = departmentStore.currentDepartment
  searchParams.value.city = selectedCity.value
  loadProjects()
})
</script>

<style lang="scss" scoped>
.project-dashboard {
  .project-phases {
    margin-top: 24px;
    
    .phase-row {
      display: flex;
      gap: 24px;
      margin-bottom: 24px;
      
      &:last-child {
        margin-bottom: 0;
      }
    }

    .phase-container {
      flex: 1;
      min-height: 300px;
      background: #f9fafb;
      border-radius: 12px;
      padding: 20px;
      border: 1px solid #f0f0f0;
      transition: all 0.3s ease;

      &.drop-active {
        background: #f0f5ff;
        border: 2px dashed #4096ff;
      }

      .project-cards {
        display: flex;
        flex-direction: column;
        gap: 16px;
        
        .project-card {
          background: #ffffff;
          cursor: move;
          border-radius: 8px;
          padding: 14px 16px;
          border: 1px solid #f0f0f0;
          transition: all 0.2s ease;

          &.dragging {
            opacity: 0.7;
            transform: scale(0.97);
          }

          &:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-color: #e6e6e6;
          }

          .card-content {
            display: flex;
            flex-direction: column;
            gap: 8px;

            .location-info {
              margin-bottom: 4px;
              
              .community-name {
                font-weight: 600;
                font-size: 15px;
                color: #262626;
                margin-bottom: 4px;
                letter-spacing: 0.1px;
              }
              
              .address-text {
                color: #8c8c8c;
                font-size: 13px;
                line-height: 1.5;
              }
            }

            .main-info {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-top: 4px;

              .days-tag {
                color: #4096ff;
                font-size: 14px;
                font-weight: 500;
                transition: color 0.2s ease;
              }
              
              .decoration-company {
                color: #595959;
                font-size: 14px;
                font-weight: 500;
              }
            }
          }
        }
      }
    }

    .phase-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 1px solid #f0f0f0;

      .phase-name {
        font-weight: 600;
        font-size: 16px;
        color: #262626;
        letter-spacing: 0.2px;
      }

      .project-count {
        color: #8c8c8c;
        font-size: 14px;
        font-weight: 500;
      }
    }
  }
}

/* 添加全局系统字体，使界面更具苹果风格 */
* {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Helvetica, Arial, sans-serif;
}
</style>