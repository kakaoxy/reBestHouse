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
                <span class="value">{{ project?.layout || '-' }}</span>
              </div>
              <div class="info-item">
                <span class="label">面积</span>
                <span class="value">{{ project?.area ? `${project.area}m²` : '-' }}</span>
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
              <div class="value-with-edit">
                <template v-if="!isEditingDeliveryDate">
                  <span class="value">{{ formatDate(project?.delivery_date) }}</span>
                  <n-button text type="primary" size="tiny" @click="startEditDeliveryDate">
                    <template #icon>
                      <TheIcon icon="material-symbols:edit" />
                    </template>
                  </n-button>
                </template>
                <template v-else>
                  <n-date-picker
                    v-model:value="editingDeliveryDate"
                    type="date"
                    size="small"
                    :disabled="updating"
                    style="width: 150px"
                  />
                  <n-button text type="primary" size="tiny" :loading="updating" @click="saveDeliveryDate">
                    <template #icon>
                      <TheIcon icon="material-symbols:check" />
                    </template>
                  </n-button>
                  <n-button text type="error" size="tiny" :disabled="updating" @click="cancelEditDeliveryDate">
                    <template #icon>
                      <TheIcon icon="material-symbols:close" />
                    </template>
                  </n-button>
                </template>
              </div>
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
                <div class="value-with-edit">
                  <template v-if="!isEditingDecorationCompany">
                    <span class="value">{{ project?.decoration_company || '-' }}</span>
                    <n-button text type="primary" size="tiny" @click="startEditDecorationCompany">
                      <template #icon>
                        <TheIcon icon="material-symbols:edit" />
                      </template>
                    </n-button>
                  </template>
                  <template v-else>
                    <n-input
                      v-model:value="editingDecorationCompany"
                      type="text"
                      size="small"
                      :disabled="updating"
                      style="width: 150px"
                    />
                    <n-button text type="primary" size="tiny" :loading="updating" @click="saveDecorationCompany">
                      <template #icon>
                        <TheIcon icon="material-symbols:check" />
                      </template>
                    </n-button>
                    <n-button text type="error" size="tiny" :disabled="updating" @click="cancelEditDecorationCompany">
                      <template #icon>
                        <TheIcon icon="material-symbols:close" />
                      </template>
                    </n-button>
                  </template>
                </div>
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
                v-for="option in PHASE_OPTIONS"
                :key="option.value"
                :name="option.value"
                :tab="option.label"
              >
                <div class="phase-materials">
                  <!-- 上传按钮区 -->
                  <div class="upload-section">
                    <div v-if="option.value === 'delivery'" class="upload-buttons">
                      <n-upload
                        accept="image/*"
                        :custom-request="file => handleUpload(file, 'image', '交房材料')"
                        :show-file-list="false"
                      >
                        <n-button type="primary">上传交房材料</n-button>
                      </n-upload>
                    </div>
                    
                    <div v-else-if="option.value === 'design'" class="upload-buttons">
                      <n-upload
                        accept="image/*"
                        :custom-request="file => handleUpload(file, 'image', '设计图')"
                        :show-file-list="false"
                        class="upload-button"
                      >
                        <n-button type="primary">上传设计图</n-button>
                      </n-upload>
                      
                      <n-upload
                        accept=".dwg,.dxf"
                        :custom-request="file => handleUpload(file, 'cad', 'CAD文件')"
                        :show-file-list="false"
                        class="upload-button"
                      >
                        <n-button type="primary">上传CAD</n-button>
                      </n-upload>
                      
                      <n-upload
                        accept=".pdf,.doc,.docx,.xls,.xlsx"
                        :custom-request="file => handleUpload(file, 'document', '报价单')"
                        :show-file-list="false"
                        class="upload-button"
                      >
                        <n-button type="primary">上传报价单</n-button>
                      </n-upload>
                    </div>
                    
                    <div v-else class="upload-buttons">
                      <n-upload
                        accept="image/*"
                        :custom-request="file => handleUpload(file, 'image', '现场照片')"
                        :show-file-list="false"
                      >
                        <n-button type="primary">上传照片</n-button>
                      </n-upload>
                    </div>
                  </div>
                  
                  <!-- 材料列表 -->
                  <div class="materials-list">
                    <n-empty v-if="!phaseMaterials.length" description="暂无材料" />
                    <n-grid v-else :cols="3" :x-gap="12" :y-gap="12">
                      <n-grid-item v-for="material in phaseMaterials" :key="material.id">
                        <n-card :title="material.material_type" size="small">
                          <template #cover>
                            <div class="material-preview">
                              <img
                                v-if="material.file_type === 'image'"
                                :src="material.file_url"
                                :alt="material.material_type"
                                class="preview-image"
                              />
                              <div v-else class="file-icon">
                                <TheIcon icon="material-symbols:description" size="48" />
                              </div>
                            </div>
                          </template>
                          <n-space justify="end">
                            <n-button text type="primary" @click="handleDownload(material)">
                              下载
                            </n-button>
                            <n-button text type="error" @click="handleDelete(material)">
                              删除
                            </n-button>
                          </n-space>
                        </n-card>
                      </n-grid-item>
                    </n-grid>
                  </div>
                </div>
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
import { useMessage, useDialog } from 'naive-ui'
import { projectApi } from '@/api/house'
import TheIcon from '@/components/icon/TheIcon.vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  projectId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:show', 'project-updated'])
const message = useMessage()
const dialog = useDialog()

// 项目数据
const project = ref(null)
const opportunity = ref(null)
const loading = ref(false)

// 施工阶段相关
const phases = ref([])
const currentPhase = ref('delivery')
const phaseMaterials = ref([])

// 阶段选项
const PHASE_OPTIONS = [
  { label: '交房', value: 'delivery' },
  { label: '设计', value: 'design' },
  { label: '水电', value: 'plumbing' },
  { label: '木瓦', value: 'carpentry' },
  { label: '油漆', value: 'painting' },
  { label: '安装', value: 'installation' },
  { label: '交付', value: 'completion' }
]

// 监听显示状态变化
watch(() => props.show, async (newVal) => {
  if (newVal && props.projectId) {
    await loadProjectDetail()
  }
})

// 加载项目详情
const loadProjectDetail = async () => {
  if (!props.projectId) return
  
  loading.value = true
  try {
    const res = await projectApi.getDetail(props.projectId)
    if (res.code === 200) {
      project.value = res.data
      await loadPhases()
    }
  } catch (error) {
    message.error('加载项目详情失败：' + error.message)
  } finally {
    loading.value = false
  }
}

// 加载施工阶段信息
const loadPhases = async () => {
  if (!props.projectId) return
  
  try {
    const res = await projectApi.getProjectPhases(props.projectId)
    if (res.code === 200) {
      phases.value = res.data.items
      await loadPhaseMaterials()
    }
  } catch (error) {
    message.error('加载施工阶段失败：' + error.message)
  }
}

// 加载阶段材料
const loadPhaseMaterials = async () => {
  if (!currentPhase.value) return

  try {
    const res = await projectApi.getMaterials({
      project_id: props.projectId,
      phase: currentPhase.value
    })
    phaseMaterials.value = res.data || []
  } catch (error) {
    message.error('加载阶段材料失败：' + error.message)
  }
}

// 处理阶段切换
const handlePhaseChange = async (phase) => {
  if (!project.value) return
  try {
    const res = await projectApi.getMaterials({
      project_id: props.projectId,
      phase
    })
    phaseMaterials.value = res.data || []
  } catch (error) {
    message.error('获取材料失败')
  }
}

// 处理上传
const handleUpload = async ({ file }, fileType, materialType) => {
  if (!project.value) {
    message.error('请先选择项目')
    return
  }

  const formData = new FormData()
  formData.append('file', file.file)
  formData.append('project_id', project.value.id)
  formData.append('phase', currentPhase.value)
  formData.append('file_type', fileType)
  formData.append('material_type', materialType)

  try {
    await projectApi.uploadMaterial(formData)
    message.success('上传成功')
    // 刷新当前阶段的材料列表
    handlePhaseChange(currentPhase.value)
  } catch (error) {
    message.error('上传失败')
  }
}

// 初始化时加载第一个阶段的材料
watch(project, (newProject) => {
  if (newProject) {
    handlePhaseChange(currentPhase.value)
  }
})

// 处理文件下载
const handleDownload = (material) => {
  if (material.file_url) {
    window.open(material.file_url, '_blank')
  }
}

// 处理删除
const handleDelete = (material) => {
  const d = dialog.create({
    type: 'warning',
    title: '确认删除',
    content: `确定要删除材料 "${material.file_name}" 吗？`,
    positiveText: '确定',
    negativeText: '取消',
    async onPositiveClick() {
      try {
        await projectApi.deleteMaterial(material.id)
        message.success('删除成功')
        // 刷新当前阶段的材料列表
        handlePhaseChange(currentPhase.value)
      } catch (error) {
        message.error('删除失败：' + error.message)
      }
    }
  })
}

// 编辑交房时间相关
const isEditingDeliveryDate = ref(false)
const editingDeliveryDate = ref(null)
const updating = ref(false)

const startEditDeliveryDate = () => {
  editingDeliveryDate.value = project.value?.delivery_date ? new Date(project.value.delivery_date) : null
  isEditingDeliveryDate.value = true
}

const cancelEditDeliveryDate = () => {
  isEditingDeliveryDate.value = false
  editingDeliveryDate.value = null
}

const saveDeliveryDate = async () => {
  if (!project.value?.id) return
  
  updating.value = true
  try {
    // 只发送必要的字段
    const updateData = {
      delivery_date: editingDeliveryDate.value,
      community_name: project.value.community_name,
      address: project.value.address,
      contract_price: project.value.contract_price,
      contract_period: project.value.contract_period,
      signer: project.value.signer,
      current_phase: project.value.current_phase,
      decoration_company: project.value.decoration_company
    }
    
    await projectApi.update(project.value.id, updateData)
    
    // 更新本地数据
    project.value = {
      ...project.value,
      delivery_date: editingDeliveryDate.value
    }
    
    message.success('更新成功')
    isEditingDeliveryDate.value = false
  } catch (error) {
    message.error('更新失败：' + error.message)
  } finally {
    updating.value = false
  }
}

// 编辑装修公司相关
const isEditingDecorationCompany = ref(false)
const editingDecorationCompany = ref(null)

const startEditDecorationCompany = () => {
  editingDecorationCompany.value = project.value?.decoration_company || ''
  isEditingDecorationCompany.value = true
}

const cancelEditDecorationCompany = () => {
  isEditingDecorationCompany.value = false
  editingDecorationCompany.value = null
}

const saveDecorationCompany = async () => {
  if (!project.value?.id) return
  
  updating.value = true
  try {
    // 只发送必要的字段
    const updateData = {
      community_name: project.value.community_name,
      address: project.value.address,
      contract_price: project.value.contract_price,
      contract_period: project.value.contract_period,
      signer: project.value.signer,
      current_phase: project.value.current_phase,
      delivery_date: project.value.delivery_date,
      decoration_company: editingDecorationCompany.value
    }
    
    await projectApi.update(project.value.id, updateData)
    
    // 更新本地数据
    project.value = {
      ...project.value,
      decoration_company: editingDecorationCompany.value
    }
    
    message.success('更新成功')
    isEditingDecorationCompany.value = false
    
    // 发出更新事件
    emit('project-updated', project.value)
  } catch (error) {
    message.error('更新失败：' + error.message)
  } finally {
    updating.value = false
  }
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

.value-with-edit {
  display: flex;
  align-items: center;
  gap: 4px;
}

.upload-section {
  margin-bottom: 16px;
  
  .upload-buttons {
    display: flex;
    gap: 12px;
    
    .upload-button {
      flex: 1;
    }
  }
}

.materials-list {
  .material-preview {
    width: 100%;
    height: 160px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f5f5;
    
    .preview-image {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
    
    .file-icon {
      color: #999;
    }
  }
}

.phase-materials {
  padding: 16px 0;

  .upload-section {
    margin-bottom: 16px;
    
    .upload-buttons {
      display: flex;
      gap: 12px;
      
      .upload-button {
        flex: 1;
      }
    }
  }

  .materials-list {
    .material-preview {
      width: 100%;
      height: 160px;
      display: flex;
      align-items: center;
      justify-content: center;
      background-color: #f5f5f5;
      
      .preview-image {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
      }
      
      .file-icon {
        color: #999;
      }
    }
  }
}
</style>