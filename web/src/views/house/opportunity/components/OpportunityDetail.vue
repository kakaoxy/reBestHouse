<template>
  <n-modal
    :show="show"
    @update:show="handleUpdateShow"
    style="width: 100vw; height: 100vh;"
    :mask-closable="false"
    class="opportunity-detail-modal"
    transform-origin="center"
  >
    <div class="modal-content">
      <div class="modal-header">
        <div class="flex justify-between items-center">
          <h3 class="modal-title">商机详情</h3>
          <n-button circle text @click="handleClose">
            <template #icon>
              <n-icon>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41z"/>
                </svg>
              </n-icon>
            </template>
          </n-button>
        </div>
      </div>

      <n-spin :show="loading">
        <div v-if="opportunityData" class="opportunity-detail">
          <div class="detail-layout">
            <!-- 左侧区域 -->
            <div class="left-section">
              <!-- 图片轮播 -->
              <div class="carousel-section">
                <n-carousel
                  show-arrow
                  dot-type="line"
                  effect="fade"
                  class="carousel"
                >
                  <n-carousel-item v-if="opportunityData.layout_image">
                    <n-image
                      :src="opportunityData.layout_image"
                      class="carousel-image"
                      preview-disabled
                    />
                    <div class="image-title">户型图</div>
                  </n-carousel-item>
                  <n-carousel-item v-if="opportunityData.interior_image">
                    <n-image
                      :src="opportunityData.interior_image"
                      class="carousel-image"
                      preview-disabled
                    />
                    <div class="image-title">室内图</div>
                  </n-carousel-item>
                  <n-carousel-item v-if="!opportunityData.layout_image && !opportunityData.interior_image">
                    <n-image
                      src="/layout.jpeg"
                      class="carousel-image"
                      preview-disabled
                    />
                    <div class="image-title">暂无图片</div>
                  </n-carousel-item>
                </n-carousel>
              </div>

              <!-- 基础信息卡片 -->
              <n-card class="info-card" :bordered="false">
                <div class="info-header">
                  <div class="community-title">
                    <h3 class="community-name">{{ opportunityData.community_name }}</h3>
                    <n-tooltip trigger="click">
                      <template #trigger>
                        <n-button text class="location-icon">
                          <n-icon>
                            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                              <path fill="currentColor" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5a2.5 2.5 0 0 1 0-5a2.5 2.5 0 0 1 0 5z"/>
                            </svg>
                          </n-icon>
                        </n-button>
                      </template>
                      {{ opportunityData.address }}
                    </n-tooltip>
                  </div>
                  <n-tag :type="getStatusType(opportunityData.status)">
                    {{ opportunityData.status }}
                  </n-tag>
                </div>
                
                <div class="info-grid">
                  <div class="info-item">
                    <div class="label">户型</div>
                    <div class="value">{{ opportunityData.layout }}</div>
                  </div>
                  <div class="info-item">
                    <div class="label">楼层</div>
                    <div class="value">{{ opportunityData.floor }}</div>
                  </div>
                  <div class="info-item">
                    <div class="label">面积</div>
                    <div class="value">{{ opportunityData.area }}㎡</div>
                  </div>
                  <div class="info-item">
                    <div class="label">总价</div>
                    <div class="value price">{{ opportunityData.total_price }}万</div>
                  </div>
                  <div class="info-item">
                    <div class="label">单价</div>
                    <div class="value">{{ opportunityData.unit_price }}元/㎡</div>
                  </div>
                </div>
              </n-card>

              <!-- 交易标签 -->
              <div class="tags-section">
                <n-space>
                  <n-tag v-if="opportunityData.is_full_five" type="success">满五</n-tag>
                  <n-tag v-if="opportunityData.is_full_two" type="success">满二</n-tag>
                  <n-tag v-if="opportunityData.is_unique" type="success">唯一</n-tag>
                </n-space>
              </div>

              <!-- 业务信息 -->
              <n-card class="business-card" :bordered="false">
                <n-descriptions :column="1" label-placement="left">
                  <n-descriptions-item label="商机方">
                    {{ opportunityData.opportunity_owner }}
                  </n-descriptions-item>
                  <n-descriptions-item label="归属方">
                    {{ opportunityData.belonging_owner }}
                  </n-descriptions-item>
                  <n-descriptions-item label="创建时间">
                    {{ formatDate(opportunityData.created_at) }}
                  </n-descriptions-item>
                  <n-descriptions-item label="更新时间">
                    {{ formatDate(opportunityData.updated_at) }}
                  </n-descriptions-item>
                </n-descriptions>
              </n-card>
            </div>

            <!-- 右侧信息区域 -->
            <div class="right-section">
              <!-- 右上部分 -->
              <div class="right-top">
                <div class="flex justify-between items-center mb-4">
                  <h2 class="text-2xl font-bold">{{ opportunityData.community_name }}</h2>
                  <n-tag :type="getStatusType(opportunityData.status)" size="large">
                    {{ opportunityData.status }}
                  </n-tag>
                </div>

                <n-descriptions bordered>
                  <n-descriptions-item label="户型">
                    {{ opportunityData.layout }}
                  </n-descriptions-item>
                  <n-descriptions-item label="楼层">
                    {{ opportunityData.floor }}
                  </n-descriptions-item>
                  <n-descriptions-item label="面积">
                    {{ opportunityData.area }}㎡
                  </n-descriptions-item>
                  <n-descriptions-item label="总价">
                    {{ opportunityData.total_price }}万
                  </n-descriptions-item>
                  <n-descriptions-item label="单价">
                    {{ opportunityData.unit_price }}元/㎡
                  </n-descriptions-item>
                  <n-descriptions-item label="具体地址">
                    {{ opportunityData.address }}{{ opportunityData.building_number ? ` ${opportunityData.building_number}栋` : '' }}{{ opportunityData.room_number ? ` ${opportunityData.room_number}室` : '' }}
                  </n-descriptions-item>
                </n-descriptions>
              </div>

              <!-- 右下部分 -->
              <div class="right-bottom">
                <n-divider>交易信息</n-divider>
                <n-descriptions bordered>
                  <n-descriptions-item label="满五年">
                    {{ opportunityData.is_full_five ? '是' : '否' }}
                  </n-descriptions-item>
                  <n-descriptions-item label="满二年">
                    {{ opportunityData.is_full_two ? '是' : '否' }}
                  </n-descriptions-item>
                  <n-descriptions-item label="唯一住房">
                    {{ opportunityData.is_unique ? '是' : '否' }}
                  </n-descriptions-item>
                  <n-descriptions-item label="交易来源">
                    {{ opportunityData.transaction_source }}
                  </n-descriptions-item>
                </n-descriptions>

                <n-divider>业务信息</n-divider>
                <n-descriptions bordered>
                  <n-descriptions-item label="商机方">
                    {{ opportunityData.opportunity_owner }}
                  </n-descriptions-item>
                  <n-descriptions-item label="归属方">
                    {{ opportunityData.belonging_owner }}
                  </n-descriptions-item>
                  <n-descriptions-item label="创建时间">
                    {{ formatDate(opportunityData.created_at) }}
                  </n-descriptions-item>
                  <n-descriptions-item label="更新时间">
                    {{ formatDate(opportunityData.updated_at) }}
                  </n-descriptions-item>
                </n-descriptions>

                <template v-if="opportunityData.remarks">
                  <n-divider>备注</n-divider>
                  <div class="remarks">
                    {{ opportunityData.remarks }}
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </n-spin>
    </div>
  </n-modal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { opportunityApi } from '@/api/house'
import { OPPORTUNITY_STATUS_TAG_TYPE } from '../constants'
import { useMessage } from 'naive-ui'

defineOptions({
  name: 'OpportunityDetail'
})

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  id: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['update:show'])

const message = useMessage()
const loading = ref(false)
const opportunityData = ref(null)

const handleUpdateShow = (value) => {
  emit('update:show', value)
}

const handleClose = () => {
  handleUpdateShow(false)
}

const getStatusType = (status) => OPPORTUNITY_STATUS_TAG_TYPE[status] || 'default'

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const loadOpportunityDetail = async () => {
  if (!props.id) return
  
  loading.value = true
  try {
    const res = await opportunityApi.getDetail(props.id)
    if (res.code === 200) {
      opportunityData.value = res.data
    } else {
      message.error('加载商机详情失败')
    }
  } catch (error) {
    console.error('加载商机详情失败:', error)
    message.error('加载商机详情失败')
  } finally {
    loading.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    loadOpportunityDetail()
  }
})
</script>

<style scoped>
.opportunity-detail-modal {
  display: flex;
  flex-direction: column;
  max-width: 100vw !important;
  max-height: 100vh !important;
}

.modal-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.opportunity-detail {
  padding: 16px;
  height: calc(100vh - 80px);
  overflow-y: auto;
  flex: 1;
}

.detail-layout {
  display: flex;
  gap: 24px;
  height: 100%;
  min-height: 0;
}

.left-section {
  flex: 0 0 25%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-right: 16px;
  border-right: 1px solid #eee;
}

.right-section {
  flex: 0 0 75%;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.right-top {
  flex: 0 0 25%;
  overflow-y: auto;
}

.right-bottom {
  flex: 0 0 75%;
  overflow-y: auto;
}

.remarks {
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
  white-space: pre-wrap;
}

/* 美化滚动条 */
.right-top::-webkit-scrollbar,
.right-bottom::-webkit-scrollbar {
  width: 6px;
}

.right-top::-webkit-scrollbar-thumb,
.right-bottom::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 3px;
}

.right-top::-webkit-scrollbar-track,
.right-bottom::-webkit-scrollbar-track {
  background-color: #f5f5f5;
}

/* 覆盖 naive-ui 的默认样式 */
:deep(.n-modal-mask) {
  backdrop-filter: blur(2px);
}

:deep(.n-modal) {
  max-width: 100vw !important;
  max-height: 100vh !important;
  width: 100vw !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
}

:deep(.n-modal-body) {
  padding: 0 !important;
  height: 100vh !important;
}

.carousel-section {
  aspect-ratio: 4/3;
  border-radius: 8px;
  overflow: hidden;
}

.carousel {
  height: 100%;
}

.carousel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-title {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 8px;
  background: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 14px;
  text-align: center;
}

.info-card {
  background: #f9f9f9;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.community-name {
  font-size: 18px;
  font-weight: bold;
  color: #1f2937;
  line-height: 1.2;
  margin-right: 8px;
}

.community-title {
  display: flex;
  align-items: center;
}

.location-icon {
  padding: 4px;
  margin-left: 4px;
  color: #666;
}

.location-icon:hover {
  color: #2080f0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 12px;
  color: #666;
}

.info-item .value {
  font-size: 14px;
  font-weight: 500;
}

.info-item .value.price {
  color: #f5222d;
  font-size: 16px;
}

.tags-section {
  padding: 8px 0;
}

.business-card {
  background: #f9f9f9;
}

.business-card :deep(.n-descriptions-item-label) {
  color: #666;
  width: 80px;
}

.modal-title {
  font-size: 3.5rem;
  font-weight: bold;
}
</style> 