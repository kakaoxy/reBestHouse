<template>
  <n-modal
    :show="show"
    preset="card"
    style="width: 900px; max-width: 90%"
    :title="project?.community_name || '项目详情'"
    :bordered="false"
    size="huge"
    @update:show="handleUpdateShow"
  >
    <n-spin :show="loading">
      <div class="project-detail">
        <!-- 基础信息区 -->
        <n-card title="基础信息" class="detail-card">
          <div class="info-grid">
            <div class="layout-image">
              <n-image
                :src="project?.layout_image || '/layout.jpeg'"
                object-fit="cover"
                :preview-disabled="!project?.layout_image"
                class="layout-img"
              />
            </div>
            <div class="info-list">
              <div class="info-item">
                <span class="label">小区名称</span>
                <span class="value">{{ project?.community_name || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">楼房号</span>
                <span class="value">{{ formatAddress(project?.address) || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">户型</span>
                <span class="value">{{ opportunity?.layout || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">面积</span>
                <span class="value">{{ opportunity?.area ? `${opportunity.area}m²` : '-' }}</span>
              </div>
            </div>
          </div>
        </n-card>

        <!-- 签约信息区 -->
        <n-card title="签约信息" class="detail-card">
          <div class="info-grid">
            <div class="info-item">
              <span class="label">签约价格</span>
              <span class="value">{{ project?.contract_price ? `${project.contract_price}万` : '-' }}</span>
            </div>
            <div class="info-item">
              <span class="label">签约周期</span>
              <span class="value">{{ formatContractPeriod(project?.contract_period) }}</span>
            </div>
            <div class="info-item">
              <span class="label">交房日期</span>
              <span class="value">{{ formatDate(project?.delivery_date) }}</span>
            </div>
            <div class="info-item">
              <span class="label">销售截止日</span>
              <span class="value">{{ calculateEndDate(project?.delivery_date, project?.contract_period) }}</span>
            </div>
            <div class="info-item">
              <span class="label">签约人</span>
              <span class="value">{{ project?.signer || '-' }}</span>
            </div>
          </div>
        </n-card>

        <!-- 项目进度区 -->
        <n-card title="项目进度" class="detail-card">
          <div class="progress-info">
            <div class="info-grid">
              <div class="info-item">
                <span class="label">装修公司</span>
                <span class="value">{{ project?.decoration_company || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">进场时间</span>
                <span class="value">{{ formatDate(project?.delivery_date) }}</span>
              </div>
              <div class="info-item">
                <span class="label">当前阶段</span>
                <span class="value">{{ getPhaseLabel(project?.current_phase) }}</span>
              </div>
            </div>

            <n-tabs
              v-model:value="currentPhase"
              type="line"
              class="phase-tabs"
              @update:value="handlePhaseChange"
            >
              <n-tab-pane
                v-for="phase in PHASE_OPTIONS"
                :key="phase.value"
                :name="phase.value"
                :tab="phase.label"
              >
                <div class="phase-content" v-if="currentPhaseData">
                  <div class="info-grid">
                    <div class="info-item">
                      <span class="label">阶段负责人</span>
                      <span class="value">{{ currentPhaseData.responsible || '-' }}</span>
                    </div>
                    <div class="info-item">
                      <span class="label">完成时间</span>
                      <span class="value">{{ formatDate(currentPhaseData.complete_time) }}</span>
                    </div>
                  </div>

                  <!-- 附件列表 -->
                  <div class="materials-list">
                    <n-space vertical>
                      <div class="material-item" v-for="material in phaseMaterials" :key="material.id">
                        <n-button text @click="handleDownload(material)">
                          <template #icon>
                            <TheIcon icon="material-symbols:description" />
                          </template>
                          {{ material.material_type }}
                        </n-button>
                      </div>
                      <n-empty v-if="!phaseMaterials.length" description="暂无附件" />
                    </n-space>
                  </div>
                </div>
                <n-empty v-else description="暂无数据" />
              </n-tab-pane>
            </n-tabs>
          </div>
        </n-card>
      </div>
    </n-spin>
  </n-modal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { projectApi } from '@/api/project'
import { opportunityApi } from '@/api/house'
import TheIcon from '@/components/icon/TheIcon.vue'

const props = defineProps({
  show: Boolean,
  projectId: [String, Number]
})

const emit = defineEmits(['update:show'])

const message = useMessage()
const loading = ref(false)
const project = ref(null)
const opportunity = ref(null)
const currentPhase = ref('delivery')
const phases = ref([])
const phaseMaterials = ref([])

// 阶段选项
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

// 获取当前阶段数据
const currentPhaseData = computed(() => {
  return phases.value.find(phase => phase.phase_type === currentPhase.value)
})

// 监听显示状态变化
watch(() => props.show, async (newVal) => {
  if (newVal && props.projectId) {
    await loadProjectDetail()
  }
})

// 加载项目详情
const loadProjectDetail = async () => {
  loading.value = true
  try {
    // 加载项目信息
    const projectRes = await projectApi.getDetail(props.projectId)
    if (projectRes.code === 200) {
      project.value = projectRes.data
    
      // 加载关联的商机信息
      if (project.value?.opportunity_id) {
        const opportunityRes = await opportunityApi.getDetail(project.value.opportunity_id)
        if (opportunityRes.code === 200) {
          opportunity.value = opportunityRes.data
        }
      }
    
      // 加载施工阶段信息
      await loadPhases()
    
      // 设置当前阶段
      currentPhase.value = project.value.current_phase || 'delivery'
    }
  } catch (error) {
    message.error(error.response?.data?.detail || '加载项目详情失败')
    console.error('加载项目详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载施工阶段信息
const loadPhases = async () => {
  try {
    const res = await projectApi.getPhases(props.projectId)
    if (res.code === 200) {
      phases.value = res.data
    }
    await loadPhaseMaterials()
  } catch (error) {
    message.error(error.response?.data?.detail || '加载施工阶段失败')
    console.error('加载施工阶段失败:', error)
  }
}

// 加载阶段材料
const loadPhaseMaterials = async () => {
  const currentPhase = phases.value.find(p => p.phase_type === currentPhase.value)
  if (currentPhase) {
    try {
      const res = await projectApi.getPhaseMaterials(currentPhase.id)
      if (res.code === 200) {
        phaseMaterials.value = res.data
      }
    } catch (error) {
      message.error(error.response?.data?.detail || '加载阶段材料失败')
      console.error('加载阶段材料失败:', error)
    }
  }
}

// 处理阶段切换
const handlePhaseChange = async (phase) => {
  currentPhase.value = phase
  await loadPhaseMaterials()
}

// 格式化地址
const formatAddress = (address) => {
  if (!address) return '-'
  // 这里可以添加地址解析逻辑，提取楼号信息
  return address
}

// 格式化合同周期
const formatContractPeriod = (days) => {
  if (!days) return '-'
  const months = Math.ceil(days / 30)
  return `${months}个月`
}

// 格式化日期
const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).replace(/\//g, '-')
}

// 计算截止日期
const calculateEndDate = (startDate, days) => {
  if (!startDate || !days) return '-'
  const date = new Date(startDate)
  date.setDate(date.getDate() + days)
  return formatDate(date)
}

// 获取阶段标签
const getPhaseLabel = (phase) => {
  const option = PHASE_OPTIONS.find(opt => opt.value === phase)
  return option ? option.label : '-'
}

// 处理下载
const handleDownload = (material) => {
  window.open(material.file_path)
}

// 处理显示状态更新
const handleUpdateShow = (value) => {
  emit('update:show', value)
  if (!value) {
    project.value = null
    opportunity.value = null
    phases.value = []
    phaseMaterials.value = []
  }
}
</script>

<style lang="scss" scoped>
.project-detail {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-card {
  background: #fff;
  border-radius: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.layout-image {
  grid-row: span 2;
  
  .layout-img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 4px;
  }
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  
  .label {
    color: #8c8c8c;
    font-size: 13px;
  }
  
  .value {
    color: #262626;
    font-size: 14px;
    font-weight: 500;
  }
}

.phase-tabs {
  margin-top: 16px;
}

.phase-content {
  padding: 16px 0;
}

.materials-list {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.material-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1890ff;
  cursor: pointer;
  
  &:hover {
    color: #40a9ff;
  }
}
</style> 