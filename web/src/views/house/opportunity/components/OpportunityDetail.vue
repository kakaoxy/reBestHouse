<template>
  <n-modal
    :show="show"
    @update:show="emit('update:show', $event)"
    class="opportunity-detail-modal"
    preset="card"
    :style="{ width: '100%' }"
    :mask-closable="false"
  >
    <template #header>
      <div class="flex justify-between items-center">
        <div class="text-xxxl font-bold">商机详情</div>
      </div>
    </template>

    <div class="modal-content">
      <n-spin :show="loading">
        <div v-if="opportunityData" class="opportunity-detail">
          <n-layout has-sider class="detail-layout">
            <!-- 左侧区域改为可折叠侧边栏 -->
            <n-layout-sider
              collapse-mode="width"
              :collapsed-width="80"
              :width="360"
              :show-collapsed-content="false"
              show-trigger="arrow-circle"
              bordered
              :collapsed="collapsed"
              @update:collapsed="handleCollapse"
            >
            <div class="left-section">
                <!-- 原有的左侧内容保持不变 -->
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
                  <n-carousel-item v-if="opportunityData.location_image">
                    <n-image
                      :src="opportunityData.location_image"
                      class="carousel-image"
                      preview-disabled
                    />
                    <div class="image-title">位置图</div>
                  </n-carousel-item>
                  <n-carousel-item v-if="!opportunityData.layout_image && !opportunityData.interior_image && !opportunityData.location_image">
                    <n-image
                      src="/layout.jpeg"
                      class="carousel-image"
                      preview-disabled
                    />
                    <div class="image-title">暂无图片</div>
                  </n-carousel-item>
                </n-carousel>
              </div>

              <n-card class="info-card" :bordered="false">
                <div class="info-header">
                  <div class="community-title">
                    <div class="title-left">
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
                    <div class="status-tag">
                      <n-tag
                        :style="{
                          backgroundColor: getStatusType(opportunityData.status).color,
                          color: getStatusType(opportunityData.status).textColor,
                          border: `1px solid ${getStatusType(opportunityData.status).borderColor}`,
                          padding: '4px 12px',
                          fontSize: '12px',
                          fontWeight: '500'
                        }"
                        size="small"
                      >
                        {{ opportunityData.status }}
                      </n-tag>
                    </div>
                  </div>
                </div>
                
                <div class="info-grid">
                  <div class="info-item">
                    <div class="label">户型</div>
                    <div class="value">{{ getStandardLayout(opportunityData.layout) }}</div>
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
                    <div class="value">{{ opportunityData.total_price }}万</div>
                  </div>
                  <div class="info-item">
                    <div class="label">单价</div>
                    <div class="value">{{ opportunityData.unit_price }}元/㎡</div>
                  </div>
                </div>
              </n-card>

              <div class="tags-section">
                <n-space>
                  <n-tag v-if="opportunityData.is_full_five" type="success">满五</n-tag>
                  <n-tag v-if="opportunityData.is_full_two" type="success">满二</n-tag>
                  <n-tag v-if="opportunityData.is_unique" type="success">唯一</n-tag>
                </n-space>
              </div>

              <n-card class="business-card" :bordered="false">
                <template #header>
                  <span>商机信息</span>
                </template>
                <template #header-extra>
                  <n-button
                    type="primary"
                    size="small"
                    @click="handleFollowUp"
                  >
                    跟进/授权
                  </n-button>
                </template>
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
            </n-layout-sider>

            <!-- 右侧内容区域 -->
            <div :class="rightSectionClass">
              <!-- 原有的右侧内容保持不变 -->
              <div class="right-top">
                <!-- 添加图表容器 -->
                <div class="charts-container mt-4">
                  <div class="chart-wrapper">
                    <div ref="scatterChartRef" class="chart"></div>
                    <p class="chart-desc">
                      在售房源分布图：点的大小表示建筑面积，颜色深浅表示单价高低，
                      悬停可查看详细信息
                    </p>
                </div>
                  <div class="chart-wrapper">
                    <div ref="lineChartRef" class="chart"></div>
                    <p class="chart-desc">
                      成交单价走势：展示不同户型的成交单价变化，
                      红点表示最高价，绿点表示最低价
                    </p>
                  </div>
                </div>
              </div>
              <div class="right-bottom">
                <n-divider>同小区房源统计</n-divider>
                
                <!-- 使用外层表格包裹四个统计表 -->
                <n-card :bordered="false" class="stats-wrapper">
                  <div class="stats-section">
                    <div class="stats-section-title">在售房源统计</div>
                    <div class="stats-tables">
                      <div class="stats-table w-full">
                        <n-data-table
                          :columns="listingLayoutColumns"
                          :data="layoutStats"
                          :bordered="false"
                          :single-line="false"
                          size="small"
                          v-bind="tableProps.layout"
                        />
                      </div>
                    </div>
                  </div>
                  <div class="stats-section">
                    <div class="stats-section-title">成交房源统计</div>
                    <div class="stats-tables">
                      <div class="stats-table">
                        <n-data-table
                          :columns="dealLayoutColumns"
                          :data="dealLayoutStats"
                          :bordered="false"
                          :single-line="false"
                          size="small"
                          v-bind="tableProps.floor"
                        />
                      </div>
                    </div>
                  </div>
                </n-card>

                <n-divider>同小区房源信息</n-divider>
                
                <div class="flex gap-4">
                  <!-- 左侧在售房源列表 -->
                  <div class="w-[48%]">
                    <div class="mb-2 font-bold text-lg flex items-center">
                      <span class="mr-2 text-12 text-gray-400">在售房源{{ ershoufangList?.length || 0 }}套</span>
                  </div>
                    
                    <n-spin :show="ershoufangLoading">
                      <div class="h-[calc(100vh-500px)] overflow-y-auto pr-2">
                        <n-card
                          v-for="item in sortedErshoufangList"
                          :key="item.id"
                          class="mb-4 cursor-pointer hover:shadow-md transition-shadow"
                          size="small"
                          @click="handleViewErshoufang(item)"
                        >
                          <div class="flex justify-between items-start">
                            <div>
                              <div class="text-16 font-medium mb-2">{{ getStandardLayout(item.layout) }}</div>
                              <div class="text-gray-500 text-14">
                                {{ item.floor_info }} | {{ item.size }}㎡ | {{ formatDate(item.listing_date) }}
              </div>
            </div>
                            <div class="text-right">
                              <div class="text-18 font-bold text-primary mb-1">
                                {{ item.total_price }}万
          </div>
                              <div class="text-gray-400 text-12">
                                {{ Math.round(item.unit_price) }}元/㎡
                              </div>
                            </div>
                          </div>
                        </n-card>
                        <n-empty v-if="sortedErshoufangList.length === 0" description="暂无在售房源" />
                      </div>
                    </n-spin>
                  </div>

                  <!-- 右侧成交房源列表 -->
                  <div class="w-[48%]">
                    <div class="mb-2 font-bold text-lg flex items-center">
                      <span class="mr-2 text-12 text-gray-400">成交记录{{ dealRecordList?.length || 0 }}套</span>
                    </div>
                    
                    <n-spin :show="dealRecordLoading">
                      <div class="h-[calc(100vh-500px)] overflow-y-auto pr-2">
                        <n-card
                          v-for="item in dealRecordList"
                          :key="item.id"
                          class="mb-4 cursor-pointer hover:shadow-md transition-shadow"
                          size="small"
                          @click="handleViewDealRecord(item)"
                        >
                          <div class="flex justify-between items-start">
                            <div>
                              <div class="text-16 font-medium mb-2">{{ getStandardLayout(item.layout) }}</div>
                              <div class="text-gray-500 text-14">
                                {{ item.floor_info || item.floor }} | {{ item.size }}㎡ | {{ formatDate(item.deal_date) }}
                              </div>
                            </div>
                            <div class="text-right">
                              <div class="text-18 font-bold text-success mb-1">
                                {{ item.total_price }}万
                              </div>
                              <div class="text-gray-400 text-12">
                                {{ Math.round(item.unit_price) }}元/㎡
                              </div>
                            </div>
                          </div>
                        </n-card>
                        <n-empty v-if="dealRecordList.length === 0" description="暂无成交记录" />
                      </div>
                    </n-spin>
                  </div>
                </div>
              </div>
            </div>
          </n-layout>
        </div>
      </n-spin>
    </div>

    <FollowUpDrawer
      :show="showFollowUpDrawer"
      @update:show="showFollowUpDrawer = $event"
      :opportunity-id="id"
      :opportunity-data="opportunityData"
      @success="handleFollowUpSuccess"
    />
  </n-modal>
</template>

<script setup>
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue'
import { opportunityApi, ershoufangApi, dealRecordApi } from '@/api/house'
import { 
  NModal, 
  NButton, 
  NSpin, 
  NCarousel, 
  NCarouselItem,
  NImage, 
  NCard, 
  NDataTable,
  NIcon, 
  NLayout, 
  NLayoutSider, 
  NLayoutContent,
  NGrid,
  NGridItem,
  NStatistic,
  NDivider,
  NCollapse,
  NCollapseItem,
  NSkeleton,
  NEmpty,
  NTooltip,
  NTag,
  NTime,
  NSpace
} from 'naive-ui'
import { OPPORTUNITY_STATUS_TAG_TYPE } from '../constants'
import { useMessage } from 'naive-ui'
import { formatDate } from '@/utils'
import FollowUpDrawer from './FollowUpDrawer.vue'
import { useDepartmentStore } from '@/stores/department'

const departmentStore = useDepartmentStore()

const message = useMessage()
const loading = ref(false)
const opportunityData = ref(null)
const ershoufangList = ref([])
const dealRecordList = ref([])
const ershoufangLoading = ref(false)
const dealRecordLoading = ref(false)

// Props 定义
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  id: {
    type: [Number, String],
    default: ''
  }
})

// 添加 emit 定义
const emit = defineEmits(['update:show'])

// 处理模态框显示状态
const handleUpdateShow = (value) => {
  emit('update:show', value)
}

// 处理关闭按钮点击
const handleClose = () => {
  handleUpdateShow(false)
}

// 加载商机详情
const loadOpportunityDetail = async (id) => {
  if (!id) return
  
  loading.value = true
  try {
    const res = await opportunityApi.getDetail(id)
    
    if (res.code === 200) {
      opportunityData.value = {
        ...res.data,
        city: departmentStore.currentDepartment
      }
    }
  } catch (error) {
    message.error('加载机会详情失败')
  } finally {
    loading.value = false
  }
}

// 加载同小区房源
const loadCommunityErshoufang = async (communityId) => {
  ershoufangLoading.value = true
  try {
    const city = opportunityData.value?.city?.toLowerCase()
    if (!city || !communityId) return

    const params = {
      community_id: Number(communityId),
      city,
      page: 1,
      page_size: 1000,
      sort_by: 'listing_date',
      sort_direction: 'desc'
    }

    const res = await ershoufangApi.list(params)
    
    if (res.code === 200 && res.data?.items) {
      ershoufangList.value = res.data.items
    }
  } catch (error) {
    message.error('加载同小区在售房源失败')
    ershoufangList.value = []
  } finally {
    ershoufangLoading.value = false
  }
}

// 加载同小区成交记录
const loadCommunityDealRecords = async (communityId) => {
  dealRecordLoading.value = true
  try {
    const params = {
      community_id: communityId,
      page: 1,
      page_size: 1000
    }

    const res = await dealRecordApi.list(params)
    
    if (res.code === 200 && res.data?.items) {
      dealRecordList.value = res.data.items
    } else {
      dealRecordList.value = []
    }
  } catch (error) {
    message.error('加载同小区成交记录失败')
    dealRecordList.value = []
  } finally {
    dealRecordLoading.value = false
  }
}

// 加载所有数据
const loadAllData = async (id) => {
  if (!id) return
  
  try {
    await loadOpportunityDetail(id)
    
    if (opportunityData.value?.community_id) {
      await Promise.all([
        loadCommunityErshoufang(opportunityData.value.community_id),
        loadCommunityDealRecords(opportunityData.value.community_id)
      ])
    }
  } catch (error) {
    message.error('加载数据失败')
  }
}

// 监听 show 和 id 的变化
watch(
  () => [props.show, props.id],
  ([newShow, newId]) => {
    if (newShow && newId) {
      loadAllData(newId)
    }
  },
  { immediate: true }
)

// 查看在售房源详情
const handleViewErshoufang = (item) => {
  message.info('查看在售房源详情功能开发中')
}

// 查看成交记录详情  
const handleViewDealRecord = (item) => {
  message.info('查看成交记录详情功能开发中')
}

// 获取状态类型
const getStatusType = (status) => {
  switch (status) {
    case '待评估':
      return {
        type: 'warning',
        color: '#FF9800',
        textColor: '#FFF',
        borderColor: '#FF9800'
      }
    case '已评估':
      return {
        type: 'info',
        color: '#2196F3',
        textColor: '#FFF',
        borderColor: '#2196F3'
      }
    case '已签约':
      return {
        type: 'success',
        color: '#4CAF50',
        textColor: '#FFF',
        borderColor: '#4CAF50'
      }
    case '已放弃':
      return {
        type: 'error',
        color: '#F44336',
        textColor: '#FFF',
        borderColor: '#F44336'
      }
    default:
      return {
        type: 'default',
        color: '#9E9E9E',
        textColor: '#FFF',
        borderColor: '#9E9E9E'
      }
  }
}

// 计算天数差异
const getDaysDiff = (dateStr) => {
  if (!dateStr) return 0
  const today = new Date()
  const listingDate = new Date(dateStr)
  
  const diffTime = Math.abs(today - listingDate)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

// 户型标准化函数
const getStandardLayout = (layout) => {
  if (!layout || typeof layout !== 'string') return '其他'
  
  // 从户型描述中提取房间数（例如从"2室1厅"中提取"2"）
  const match = layout.match(/^(\d+)室/)
  if (!match) return '其他'
  
  const rooms = parseInt(match[1])
  switch (rooms) {
    case 1:
      return '一房'
    case 2:
      return '两房'
    case 3:
      return '三房'
    case 4:
      return '四房'
    default:
      return '其他'
  }
}

// 获取楼层范围
const getFloorRange = (floorInfo) => {
  if (!floorInfo) return '其他'
  
  if (floorInfo.includes('低楼层')) return '低楼层'
  if (floorInfo.includes('中楼层')) return '中楼层'
  if (floorInfo.includes('高楼层')) return '高楼层'
  return '其他'
}

// 计算挂牌天数
const getListingDays = (listingTime) => {
  if (!listingTime) return 0
  const listingDate = new Date(listingTime)
  const now = new Date()
  const diffTime = now - listingDate
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

// 公共表格列配置
const commonColumns = {
  layout: {
    title: '户型',
    key: 'layout',
    width: 100,
    fixed: 'left',
    className: 'layout-cell',
    render: (row) => row.layout
  },
  floor: {
    key: 'floor',
    width: 100,
    fixed: 'left',
    className: 'floor-cell',
    render: (row) => row.floor
  },
  count: {
    title: '套数',
    key: 'count',
    width: 80,
    align: 'right',
    render: (row) => row.count || '-'
  },
  avgSize: {
    title: '平均面积',
    key: 'avgSize',
    width: 100,
    align: 'right',
    render: (row) => row.avgSize ? `${Math.round(row.avgSize)}㎡` : '-'
  },
  avgUnitPrice: {
    title: '平均单价',
    key: 'avgUnitPrice',
    width: 120,
    align: 'right',
    render: (row) => row.avgUnitPrice ? `${Math.round(row.avgUnitPrice)}元/㎡` : '-'
  },
  avgTotalPrice: {
    title: '平均总价',
    key: 'avgTotalPrice',
    width: 100,
    align: 'right',
    render: (row) => row.avgTotalPrice ? `${Math.round(row.avgTotalPrice)}万` : '-'
  },
  maxTotalPrice: {
    title: '最高总价',
    key: 'maxTotalPrice',
    width: 100,
    align: 'right',
    render: (row) => row.maxTotalPrice ? `${Math.round(row.maxTotalPrice)}万` : '-'
  },
  minTotalPrice: {
    title: '最低总价',
    key: 'minTotalPrice',
    width: 100,
    align: 'right',
    render: (row) => row.minTotalPrice ? `${Math.round(row.minTotalPrice)}万` : '-'
  },
  avgListingDays: {
    title: '平均挂牌周期',
    key: 'avgListingDays',
    width: 120,
    align: 'right',
    render: (row) => row.avgListingDays ? `${Math.round(row.avgListingDays)}天` : '-'
  },
  avgDealCycle: {
    title: '平均成交周期',
    key: 'avgDealCycle',
    width: 120,
    align: 'right',
    render: (row) => row.avgDealCycle ? `${Math.round(row.avgDealCycle)}天` : '-'
  }
}

// 子表格列配置（不带标题）
const floorColumns = {
  ...commonColumns,
  floor: {
    ...commonColumns.floor,
    title: ''
  },
  count: {
    ...commonColumns.count,
    title: ''
  },
  avgSize: {
    ...commonColumns.avgSize,
    title: ''
  },
  avgUnitPrice: {
    ...commonColumns.avgUnitPrice,
    title: ''
  },
  avgTotalPrice: {
    ...commonColumns.avgTotalPrice,
    title: ''
  },
  maxTotalPrice: {
    ...commonColumns.maxTotalPrice,
    title: ''
  },
  minTotalPrice: {
    ...commonColumns.minTotalPrice,
    title: ''
  },
  avgListingDays: {
    ...commonColumns.avgListingDays,
    title: '',
    className: 'last-column'  // 为最后一列添加特殊类名
  },
  avgDealCycle: {
    ...commonColumns.avgDealCycle,
    title: '',
    className: 'last-column'  // 为最后一列添加特殊类名
  }
}

// 在售房源主表格列定义
const listingLayoutColumns = [
  { 
    type: 'expand',
    width: 24,
    fixed: 'left',
    expandable: (row) => row.layout !== '合计' && row.floorStats?.length > 0,
    renderExpand: (row) => {
      return h(NDataTable, {
        columns: listingFloorColumns,
        data: row.floorStats,
        size: 'small',
        bordered: false,
        class: 'floor-table',
        hideHeader: true,
        scrollX: true,
        style: {
          marginLeft: '24px',
          marginTop: '4px'
        }
      })
    }
  },
  commonColumns.layout,
  commonColumns.count,
  commonColumns.avgSize,
  commonColumns.avgUnitPrice,
  commonColumns.avgTotalPrice,
  commonColumns.maxTotalPrice,
  commonColumns.minTotalPrice,
  commonColumns.avgListingDays
]

// 在售房源子表格列定义
const listingFloorColumns = [
  floorColumns.floor,
  floorColumns.count,
  floorColumns.avgSize,
  floorColumns.avgUnitPrice,
  floorColumns.avgTotalPrice,
  floorColumns.maxTotalPrice,
  floorColumns.minTotalPrice,
  floorColumns.avgListingDays
]

// 成交房源主表格列定义
const dealLayoutColumns = [
  { 
    type: 'expand',
    width: 24,
    fixed: 'left',
    expandable: (row) => row.layout !== '合计' && row.floorStats?.length > 0,
    renderExpand: (row) => {
      return h(NDataTable, {
        columns: dealFloorColumns,
        data: row.floorStats,
        size: 'small',
        bordered: false,
        class: 'floor-table',
        hideHeader: true,
        scrollX: true,
        style: {
          marginLeft: '24px',
          marginTop: '4px'
        }
      })
    }
  },
  commonColumns.layout,
  commonColumns.count,
  commonColumns.avgSize,
  commonColumns.avgUnitPrice,
  commonColumns.avgTotalPrice,
  commonColumns.maxTotalPrice,
  commonColumns.minTotalPrice,
  commonColumns.avgDealCycle
]

// 成交房源子表格列定义
const dealFloorColumns = [
  floorColumns.floor,
  floorColumns.count,
  floorColumns.avgSize,
  floorColumns.avgUnitPrice,
  floorColumns.avgTotalPrice,
  floorColumns.maxTotalPrice,
  floorColumns.minTotalPrice,
  floorColumns.avgDealCycle
]

// 表格行样式配置
const tableProps = {
  layout: {
    rowClassName: (row) => getRowClass(row, 'layout')
  },
  floor: {
    rowClassName: (row) => getRowClass(row, 'floor')
  }
}

// 在售房源统计
const layoutStats = computed(() => {
  if (!ershoufangList.value?.length) {
    return []
  }
  
  
  const stats = {}
  let totalCount = 0
  let totalSize = 0
  let totalUnitPrice = 0
  let totalPrice = 0
  let totalListingDays = 0
  let maxTotalPrice = 0
  let minTotalPrice = Infinity
  
  // 按户型分组统计
  ershoufangList.value.forEach(item => {
    const layout = getStandardLayout(item.layout)
    if (!stats[layout]) {
      stats[layout] = {
        layout,
        count: 0,
        totalSize: 0,
        totalUnitPrice: 0,
        totalPrice: 0,
        totalListingDays: 0,
        maxTotalPrice: 0,
        minTotalPrice: Infinity,
        floorStats: {}
      }
    }
    
    const stat = stats[layout]
    stat.count++
    stat.totalSize += Number(item.size || 0)
    stat.totalUnitPrice += Number(item.unit_price || 0)
    stat.totalPrice += Number(item.total_price || 0)
    stat.totalListingDays += getListingDays(item.listing_date)
    stat.maxTotalPrice = Math.max(stat.maxTotalPrice, Number(item.total_price || 0))
    stat.minTotalPrice = Math.min(stat.minTotalPrice, Number(item.total_price || 0))
    
    
    // 按楼层分组统计
    const floor = getFloorRange(item.floor)
    if (!stat.floorStats[floor]) {
      stat.floorStats[floor] = {
        floor,
        count: 0,
        totalSize: 0,
        totalUnitPrice: 0,
        totalPrice: 0,
        totalListingDays: 0,
        maxTotalPrice: 0,
        minTotalPrice: Infinity
      }
    }
    
    const floorStat = stat.floorStats[floor]
    floorStat.count++
    floorStat.totalSize += Number(item.size || 0)
    floorStat.totalUnitPrice += Number(item.unit_price || 0)
    floorStat.totalPrice += Number(item.total_price || 0)
    floorStat.totalListingDays += getListingDays(item.listing_date)
    floorStat.maxTotalPrice = Math.max(floorStat.maxTotalPrice, Number(item.total_price || 0))
    floorStat.minTotalPrice = Math.min(floorStat.minTotalPrice, Number(item.total_price || 0))
    
    
    // 总计
    totalCount++
    totalSize += Number(item.size || 0)
    totalUnitPrice += Number(item.unit_price || 0)
    totalPrice += Number(item.total_price || 0)
    totalListingDays += getListingDays(item.listing_date)
    maxTotalPrice = Math.max(maxTotalPrice, Number(item.total_price || 0))
    minTotalPrice = Math.min(minTotalPrice, Number(item.total_price || 0))
  })
  
  // 转换为数组并计算平均值
  const result = Object.values(stats).map(stat => {
    const floorStatsArray = Object.values(stat.floorStats).map(floor => ({
      ...floor,
      avgSize: floor.count > 0 ? floor.totalSize / floor.count : 0,
      avgUnitPrice: floor.count > 0 ? floor.totalUnitPrice / floor.count : 0,
      avgTotalPrice: floor.count > 0 ? floor.totalPrice / floor.count : 0,
      avgListingDays: floor.count > 0 ? floor.totalListingDays / floor.count : 0
    }))
    
    return {
      ...stat,
      avgSize: stat.totalSize / stat.count,
      avgUnitPrice: stat.totalUnitPrice / stat.count,
      avgTotalPrice: stat.totalPrice / stat.count,
      avgListingDays: stat.totalListingDays / stat.count,
      floorStats: floorStatsArray
    }
  })
  
  // 添加合计行
  if (totalCount > 0) {
    result.push({
      layout: '合计',
      count: totalCount,
      avgSize: totalSize / totalCount,
      avgUnitPrice: totalUnitPrice / totalCount,
      avgTotalPrice: totalPrice / totalCount,
      avgListingDays: totalListingDays / totalCount,
      maxTotalPrice,
      minTotalPrice: minTotalPrice === Infinity ? 0 : minTotalPrice
    })
  }
  
  // 按户型排序
  return result.sort((a, b) => getLayoutWeight(a.layout) - getLayoutWeight(b.layout))
})

// 楼层统计数据
const floorStats = computed(() => {
  const stats = {}
  const total = {
    floor: '合计',
    count: 0,
    totalSize: 0,
    totalPrice: 0,
    totalUnitPrice: 0,
    maxTotalPrice: 0,
    minTotalPrice: Infinity,
    totalListingDays: 0
  }

  // 预定义楼层顺序
  const floorOrder = ['低楼层', '中楼层', '高楼层']
  
  floorOrder.forEach(floor => {
    stats[floor] = {
      floor,
      count: 0,
      totalSize: 0,
      totalPrice: 0,
      totalUnitPrice: 0,
      maxTotalPrice: 0,
      minTotalPrice: Infinity,
      totalListingDays: 0
    }
  })

  // 统计数据

  ershoufangList.value?.forEach((item, index) => {
    let floor = '其他'
    const floorInfo = item.floor_info?.toLowerCase() || ''
    
    if (floorInfo.includes('低楼层')) {
      floor = '低楼层'
    } else if (floorInfo.includes('中楼层')) {
      floor = '中楼层'
    } else if (floorInfo.includes('高楼层')) {
      floor = '高楼层'
    }

    const size = Number(item.size) || 0
    const totalPrice = Number(item.total_price) || 0
    const unitPrice = Number(item.unit_price) || 0
    const listingDays = getListingDays(item.listing_date || item.created_at)

    if (!stats[floor]) {
      stats[floor] = {
        floor,
        count: 0,
        totalSize: 0,
        totalPrice: 0,
        totalUnitPrice: 0,
        maxTotalPrice: 0,
        minTotalPrice: Infinity,
        totalListingDays: 0
      }
    }

    stats[floor].count++
    stats[floor].totalSize += size
    stats[floor].totalPrice += totalPrice
    stats[floor].totalUnitPrice += unitPrice
    stats[floor].maxTotalPrice = Math.max(stats[floor].maxTotalPrice, totalPrice)
    stats[floor].minTotalPrice = Math.min(stats[floor].minTotalPrice, totalPrice)
    stats[floor].totalListingDays += listingDays

    total.count++
    total.totalSize += size
    total.totalPrice += totalPrice
    total.totalUnitPrice += unitPrice
    total.maxTotalPrice = Math.max(total.maxTotalPrice, totalPrice)
    total.minTotalPrice = Math.min(total.minTotalPrice, totalPrice)
    total.totalListingDays += listingDays
  })

  // 按预定义顺序返回结果
  const result = floorOrder.map(floor => {
    if (!stats[floor]) {
      return {
        floor,
        count: 0,
        avgSize: '0.0',
        avgPrice: '0.0',
        avgUnitPrice: 0,
        maxTotalPrice: 0,
        minTotalPrice: 0,
        avgListingDays: 0
      }
    }

    const floorStats = {
      ...stats[floor],
      avgSize: stats[floor].count ? (stats[floor].totalSize / stats[floor].count).toFixed(1) : '0.0',
      avgPrice: stats[floor].count ? (stats[floor].totalPrice / stats[floor].count).toFixed(1) : '0.0',
      avgUnitPrice: stats[floor].count ? Math.round(stats[floor].totalUnitPrice / stats[floor].count) : 0,
      maxTotalPrice: stats[floor].maxTotalPrice === 0 ? 0 : stats[floor].maxTotalPrice,
      minTotalPrice: stats[floor].minTotalPrice === Infinity ? 0 : stats[floor].minTotalPrice,
      avgListingDays: stats[floor].count ? Math.round(stats[floor].totalListingDays / stats[floor].count) : 0
    }

    return floorStats
  })

  // 添加总计行
  if (total.count > 0) {
    const totalStats = {
      ...total,
      avgSize: (total.totalSize / total.count).toFixed(1),
      avgPrice: (total.totalPrice / total.count).toFixed(1),
      avgUnitPrice: Math.round(total.totalUnitPrice / total.count),
      maxTotalPrice: total.maxTotalPrice === 0 ? 0 : total.maxTotalPrice,
      minTotalPrice: total.minTotalPrice === Infinity ? 0 : total.minTotalPrice,
      avgListingDays: Math.round(total.totalListingDays / total.count)
    }

    result.push(totalStats)
  }
  return result
})

// 计算统计时间范围
const dealDateRange = computed(() => {
  if (!dealRecordList.value || dealRecordList.value.length === 0) {
    return {
      startDate: new Date(0),
      endDate: new Date()
    }
  }

  // 按成交时间排序，找到最新的成交记录
  const sortedRecords = [...dealRecordList.value].sort((a, b) => {
    return new Date(b.deal_date) - new Date(a.deal_date)
  })
  
  const endDate = new Date(sortedRecords[0].deal_date)
  const startDate = new Date(endDate)
  startDate.setMonth(startDate.getMonth() - 6)
  
  return {
    startDate,
    endDate
  }
})

// 户型成交统计数据
const dealLayoutStats = computed(() => {
  const stats = {}
  const total = { 
    layout: '合计', 
    count: 0, 
    totalPrice: 0,
    totalSize: 0,
    maxTotalPrice: 0,
    minTotalPrice: Infinity,
    totalDealCycle: 0,
    floorStats: []
  }

  // 按户型分组统计
  dealRecordList.value.forEach(item => {
    const layout = getStandardLayout(item.layout)
    const floor = getFloorRange(item.floor_info)
    
    // 初始化户型统计
    if (!stats[layout]) {
      stats[layout] = {
        layout,
        count: 0,
        totalPrice: 0,
        totalSize: 0,
        maxTotalPrice: 0,
        minTotalPrice: Infinity,
        totalDealCycle: 0,
        floorStats: {}
      }
    }
    
    // 初始化楼层统计
    if (!stats[layout].floorStats[floor]) {
      stats[layout].floorStats[floor] = {
        floor,
        count: 0,
        totalPrice: 0,
        totalSize: 0,
        totalUnitPrice: 0,
        maxTotalPrice: 0,
        minTotalPrice: Infinity,
        totalDealCycle: 0
      }
    }
    
    const price = Number(item.total_price || 0)
    const dealCycle = Number(item.deal_cycle || 0)
    
    // 更新户型统计
    stats[layout].count++
    stats[layout].totalPrice += price
    stats[layout].totalSize += item.size || 0
    stats[layout].maxTotalPrice = Math.max(stats[layout].maxTotalPrice, price)
    stats[layout].minTotalPrice = price > 0 ? Math.min(stats[layout].minTotalPrice, price) : stats[layout].minTotalPrice
    stats[layout].totalDealCycle += dealCycle
    
    // 更新楼层统计
    const floorStat = stats[layout].floorStats[floor]
    floorStat.count++
    floorStat.totalPrice += price
    floorStat.totalSize += item.size || 0
    floorStat.totalUnitPrice += (price && item.size) ? (price * 10000 / item.size) : 0
    floorStat.maxTotalPrice = Math.max(floorStat.maxTotalPrice, price)
    floorStat.minTotalPrice = price > 0 ? Math.min(floorStat.minTotalPrice, price) : floorStat.minTotalPrice
    floorStat.totalDealCycle += dealCycle
    
    // 更新总计
    total.count++
    total.totalPrice += price
    total.totalSize += item.size || 0
    total.maxTotalPrice = Math.max(total.maxTotalPrice, price)
    total.minTotalPrice = price > 0 ? Math.min(total.minTotalPrice, price) : total.minTotalPrice
    total.totalDealCycle += dealCycle
  })

  // 计算均价并转换为数组
  const result = Object.values(stats).map(item => {
    // 计算户型均价
    const avgSize = item.count > 0 ? item.totalSize / item.count : 0
    const avgTotalPrice = item.count > 0 ? item.totalPrice / item.count : 0
    const avgUnitPrice = item.totalSize > 0 ? (item.totalPrice * 10000) / item.totalSize : 0
    const avgDealCycle = item.count > 0 ? Math.round(item.totalDealCycle / item.count) : 0
    
    // 转换楼层统计为数组并计算均价
    const floorStats = Object.values(item.floorStats).map(floor => ({
      ...floor,
      avgSize: floor.count > 0 ? floor.totalSize / floor.count : 0,
      avgTotalPrice: floor.count > 0 ? floor.totalPrice / floor.count : 0,
      avgUnitPrice: floor.count > 0 ? floor.totalUnitPrice / floor.count : 0,
      avgDealCycle: floor.count > 0 ? Math.round(floor.totalDealCycle / floor.count) : 0,
      maxTotalPrice: floor.maxTotalPrice || 0,
      minTotalPrice: floor.minTotalPrice === Infinity ? 0 : floor.minTotalPrice
    }))
    
    // 按楼层排序：高楼层 > 中楼层 > 低楼层 > 其他
    floorStats.sort((a, b) => {
      const floorOrder = {
        '高楼层': 1,
        '中楼层': 2,
        '低楼层': 3,
        '其他': 4
      }
      return floorOrder[a.floor] - floorOrder[b.floor]
    })
    
    return {
      layout: item.layout,
      count: item.count,
      avgSize,
      avgTotalPrice,
      avgUnitPrice,
      avgDealCycle,
      maxTotalPrice: item.maxTotalPrice || 0,
      minTotalPrice: item.minTotalPrice === Infinity ? 0 : item.minTotalPrice,
      floorStats
    }
  })
  
  // 计算总计的均价
  if (total.count > 0) {
    total.avgSize = total.totalSize / total.count
    total.avgTotalPrice = total.totalPrice / total.count
    total.avgUnitPrice = total.totalSize > 0 ? (total.totalPrice * 10000) / total.totalSize : 0
    total.avgDealCycle = Math.round(total.totalDealCycle / total.count)
    total.maxTotalPrice = total.maxTotalPrice || 0
    total.minTotalPrice = total.minTotalPrice === Infinity ? 0 : total.minTotalPrice
  }
  
  // 按户型权重排序
  result.sort((a, b) => getLayoutWeight(a.layout) - getLayoutWeight(b.layout))
  
  // 添加合计行
  result.push(total)
  
  return result
})

// 处理在售房源数据 - 散点图
const processScatterData = (data) => {
  // 按户型分组
  const groupedData = {}
  const layoutOrder = ['一房', '两房', '三房', '四房', '其他']
  const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']

  layoutOrder.forEach((layout, index) => {
    groupedData[layout] = {
      name: layout,
      type: 'scatter',
      itemStyle: {
        color: colors[index]
      },
      data: []
    }
  })

  // 处理每个房源数据
  data.forEach(item => {
    if (!item.size || !item.unit_price) return

    // 确定户型
    let layout = '其他'
    const match = item.layout?.match(/^(\d+)室/)
    if (match) {
      layout = getStandardLayout(item.layout)
    }

    // 添加数据点
    groupedData[layout].data.push({
      value: [item.size, item.unit_price],
      ...item // 保存原始数据用于tooltip
    })
  })

  return Object.values(groupedData)
}

// 处理成交记录数据 - 折线图
const processLineChartData = (data) => {
  // 按月份和户型分组
  const groupedData = {}
  
  data.forEach(item => {
    if (!item.deal_date || !item.unit_price) return
    
    const month = item.deal_date.substring(0, 7)
    const layout = getStandardLayout(item.layout)

    if (!groupedData[layout]) {
      groupedData[layout] = new Map()
    }
    
    if (!groupedData[layout].has(month)) {
      groupedData[layout].set(month, {
        prices: [],
        count: 0,
        sum: 0
      })
    }
    
    const monthData = groupedData[layout].get(month)
    monthData.prices.push(item.unit_price)
    monthData.count++
    monthData.sum += item.unit_price
  })

  // 转换为echarts系列数据
  const series = []
  const layoutOrder = ['一房', '两房', '三房', '四房', '其他']
  const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']
  
  // 获取所有月份并排序
  const allMonths = new Set()
  Object.values(groupedData).forEach(layoutData => {
    layoutData.forEach((_, month) => allMonths.add(month))
  })
  const sortedMonths = Array.from(allMonths).sort()
  
  layoutOrder.forEach((layout, index) => {
    if (!groupedData[layout]) {
      series.push({
        name: layout,
        type: 'line',
        smooth: true,
        color: colors[index],
        data: []
      })
      return
    }

    // 处理每个月的数据，确保连续性
    const monthlyData = sortedMonths.map(month => {
      const data = groupedData[layout].get(month)
      if (!data) return [month, null]
      return [month, Math.round(data.sum / data.count)]
    })

    // 主折线 - 平均单价
    series.push({
      name: layout,
      type: 'line',
      smooth: true,
      color: colors[index],
      symbol: 'circle',
      symbolSize: 6,
      emphasis: {
        scale: 1.5
      },
      data: monthlyData,
      connectNulls: true // 连接空值点
    })
  })

  return series
}

// 初始化散点图
const initScatterChart = async (echarts) => {
  if (!scatterChartRef.value) return
  
  // 设置设备像素比
  scatterChart = echarts.init(scatterChartRef.value, null, {
    devicePixelRatio: window.devicePixelRatio
  })
  
  const option = {
    title: {
      text: '在售房源分布',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 500
      }
    },
    tooltip: {
      formatter: (params) => {
        const data = params.data
        return `
          小区：${data.community_name}<br/>
          户型：${data.layout}<br/>
          楼层：${data.floor}<br/>
          面积：${data.size}㎡<br/>
          单价：${data.unit_price}元/㎡<br/>
          总价：${data.total_price}万
        `
      }
    },
    legend: {
      data: ['一房', '两房', '三房', '四房', '其他'],
      bottom: '0%',
      textStyle: {
        fontSize: 13
      }
    },
    grid: {
      left: '12%',
      right: '8%',
      top: '15%',
      bottom: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: '建筑面积(㎡)',
      nameGap: 20,
      min: 30,
      axisLabel: {
        fontSize: 12
      },
      nameTextStyle: {
        fontSize: 13,
        padding: [0, 0, 0, 10]
      }
    },
    yAxis: {
      type: 'value',
      name: '单价(元/㎡)',
      axisLabel: {
        fontSize: 12,
        formatter: (value) => {
          return value >= 1000 ? (value/1000 + 'k') : value
        }
      },
      nameTextStyle: {
        fontSize: 13,
        padding: [0, 20, 0, 0]
      }
    },
    series: processScatterData(ershoufangList.value || [])
  }
  
  scatterChart.setOption(option)
}

// 初始化折线图
const initLineChart = async (echarts) => {
  if (!lineChartRef.value) return
  
  // 设置设备像素比
  lineChart = echarts.init(lineChartRef.value, null, {
    devicePixelRatio: window.devicePixelRatio
  })
  
  const option = {
    title: {
      text: '成交单价走势',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 500
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        return params
          .filter(param => param.data[1] !== null)
          .map(param => 
            `${param.seriesName}<br/>
            时间：${param.data[0]}<br/>
            均价：${param.data[1] >= 1000 ? (param.data[1]/1000).toFixed(1) + 'k' : param.data[1]}元/㎡`
          ).join('<br/><br/>')
      }
    },
    legend: {
      data: ['一房', '两房', '三房', '四房', '其他'],
      bottom: '0%',
      textStyle: {
        fontSize: 13
      }
    },
    grid: {
      left: '12%',
      right: '8%',
      top: '15%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      axisLabel: {
        fontSize: 12,
        interval: 'auto',
        hideOverlap: true
      }
    },
    yAxis: {
      type: 'value',
      name: '单价(元/㎡)',
      nameTextStyle: {
        fontSize: 13,
        padding: [0, 20, 0, 0]
      },
      axisLabel: {
        fontSize: 12,
        formatter: (value) => {
          return value >= 1000 ? (value/1000 + 'k') : value
        }
      }
    },
    series: processLineChartData(dealRecordList.value || [])
  }
  
  lineChart.setOption(option)
}

// 监听数据变化，更新图表
watch([ershoufangList, dealRecordList], async () => {
  const echarts = await loadEcharts()
  await initScatterChart(echarts)
  await initLineChart(echarts)
})

// 监听窗口大小变化，调整图表大小
onMounted(async () => {
  const echarts = await loadEcharts()
  await initScatterChart(echarts)
  await initLineChart(echarts)
  
  window.addEventListener('resize', () => {
    scatterChart?.resize()
    lineChart?.resize()
  })
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', () => {
    scatterChart?.resize()
    lineChart?.resize()
  })
  scatterChart?.dispose()
  lineChart?.dispose()
})

defineOptions({
  name: 'OpportunityDetail'
})

// 添加计算属性控制右侧区域样式
const rightSectionClass = computed(() => ({
  'right-section': true,
  'collapsed': collapsed.value
}))

// 排序函数 - 获取户型数字
const getLayoutNumber = (layout) => {
  if (!layout || typeof layout !== 'string') return 0
  const match = layout.match(/^(\d+)室/)
  return match ? parseInt(match[1]) : 0
}

// 排序后的在售房源列表
const sortedErshoufangList = computed(() => {
  if (!ershoufangList.value) return []
  
  return [...ershoufangList.value].sort((a, b) => {
    // 确定户型
    let layoutA = '其他'
    let layoutB = '其他'
    
    if (a.layout && typeof a.layout === 'string') {
      const matchA = a.layout.match(/^(\d+)室/)
      if (matchA) {
        layoutA = getStandardLayout(a.layout)
      }
    }
    
    if (b.layout && typeof b.layout === 'string') {
      const matchB = b.layout.match(/^(\d+)室/)
      if (matchB) {
        layoutB = getStandardLayout(b.layout)
      }
    }
    
    // 按户型排序
    if (layoutA !== layoutB) {
      return getLayoutWeight(layoutA) - getLayoutWeight(layoutB)
    }
    
    // 按总价排序
    return (b.total_price || 0) - (a.total_price || 0)
  })
})

// 跟进抽屉控制
const showFollowUpDrawer = ref(false)

// 处理跟进按钮点击
const handleFollowUp = () => {
  showFollowUpDrawer.value = true
}

// 处理跟进成功
const handleFollowUpSuccess = () => {
  // 重新加载商机详情
  loadOpportunityDetail(props.id)
}

// 添加之前被误删的成交房源统计相关的列定义
// const dealFloorColumns = [
//   commonColumns.floor,
//   commonColumns.count,
//   commonColumns.avgSize,
//   commonColumns.avgUnitPrice,
//   commonColumns.avgTotalPrice,
//   commonColumns.maxTotalPrice,
//   commonColumns.minTotalPrice,
//   commonColumns.avgDealCycle
// ]

// 成交房源主表格列定义
// const dealLayoutColumns = [
//   { 
//     type: 'expand',
//     width: 24,
//     fixed: 'left',
//     expandable: (row) => row.layout !== '合计' && row.floorStats?.length > 0,
//     renderExpand: (row) => {
//       return h(NDataTable, {
//         columns: dealFloorColumns,
//         data: row.floorStats,
//         size: 'small',
//         bordered: false,
//         class: 'floor-table',
//         hideHeader: true,
//         scrollX: true,
//         style: {
//           marginLeft: '24px',
//           marginTop: '4px'
//         }
//       })
//     }
//   },
//   commonColumns.layout,
//   commonColumns.count,
//   commonColumns.avgSize,
//   commonColumns.avgUnitPrice,
//   commonColumns.avgTotalPrice,
//   commonColumns.maxTotalPrice,
//   commonColumns.minTotalPrice,
//   commonColumns.avgDealCycle
// ]

// 表格响应式配置
// const layoutTableProps = {
//   rowClassName: (row) => getRowClass(row, 'layout')
// }

// const floorTableProps = {
//   rowClassName: (row) => getRowClass(row, 'floor')
// }

// 添加侧边栏折叠状态控制
const collapsed = ref(false)

// 处理侧边栏折叠状态变化
const handleCollapse = (value) => {
  collapsed.value = value
}

// 导入 echarts
const echartsUrl = 'https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js'
const loadEcharts = () => {
  return new Promise((resolve) => {
    if (window.echarts) {
      resolve(window.echarts)
    } else {
      const script = document.createElement('script')
      script.src = echartsUrl
      script.onload = () => resolve(window.echarts)
      document.head.appendChild(script)
    }
  })
}

// 图表相关
const scatterChartRef = ref(null)
const lineChartRef = ref(null)
let scatterChart = null
let lineChart = null

// 行样式计算函数
const getRowClass = (row, type) => {
  if (!opportunityData.value) return ''
  
  // 户型匹配
  if (type === 'layout') {
    const match = opportunityData.value.layout?.match(/^(\d+)室/)
    if (match) {
      const roomCount = match[1]
      const layoutMap = {
        '1': '一房',
        '2': '两房',
        '3': '三房',
        '4': '四房'
      }
      if (row.layout === layoutMap[roomCount]) {
        return 'highlight-row'
      }
    }
  }
  
  // 楼层匹配
  if (type === 'floor') {
    // 获取商机房源的楼层信息
    const floorInfo = opportunityData.value.floor_info || opportunityData.value.floor || ''
    
    // 从楼层信息中提取楼层位置
    let targetFloor = ''
    
    // 尝试从数字格式解析（如 6/17）
    const floorMatch = floorInfo.match(/(\d+)\/(\d+)/)
    if (floorMatch) {
      const [, current, total] = floorMatch
      const ratio = current / total
      if (ratio <= 0.33) targetFloor = '低楼层'
      else if (ratio <= 0.66) targetFloor = '中楼层'
      else targetFloor = '高楼层'
    } 
    // 尝试从文字描述解析
    else {
      if (floorInfo.includes('低')) targetFloor = '低楼层'
      else if (floorInfo.includes('中')) targetFloor = '中楼层'
      else if (floorInfo.includes('高')) targetFloor = '高楼层'
    }

    // 匹配当前行是否为目标楼层
    if (targetFloor && row.floor === targetFloor) {
      return 'highlight-row'
    }
  }
  
  return ''
}

// 获取户型排序权重
const getLayoutWeight = (layout) => {
  switch (layout) {
    case '一房':
      return 1
    case '两房':
      return 2
    case '三房':
      return 3
    case '四房':
      return 4
    default:
      return 5
  }
}
</script>

<style scoped>
.opportunity-detail-modal {
  :deep(.n-modal) {
    max-width: 90vw;
    border-radius: 12px;
    background-color: #f5f5f7;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  :deep(.layout-cell) {
    padding-left: 24px !important;
  }

  :deep(.floor-cell) {
    padding-left: 48px !important;
  }

  :deep(.floor-table) {
    .n-data-table-th {
      background-color: transparent;
    }

    .n-data-table-td {
      background-color: var(--n-merged-td-color);
    }

    .n-data-table-tr:hover .n-data-table-td {
      background-color: var(--n-merged-td-color-hover);
    }
  }

  :deep(.n-data-table-expand-trigger) {
    width: 24px;
    height: 24px;
    margin-right: 8px;
  }

  :deep(.n-data-table-expand-trigger--expanded) {
    transform: rotate(90deg);
  }
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .opportunity-detail-modal {
    :deep(.n-data-table) {
      overflow-x: auto;
    }
  }
}

@media (max-width: 768px) {
  .opportunity-detail-modal {
    :deep(.n-modal) {
      max-width: 100vw;
      margin: 0;
    }
  }
}

.opportunity-detail-modal {
  :deep(.n-modal) {
    max-width: 90vw;
    border-radius: 12px;
    background-color: #f5f5f7;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  }

  :deep(.layout-cell) {
    padding-left: 24px !important;
  }

  :deep(.floor-cell) {
    padding-left: 48px !important;
  }

  :deep(.floor-table) {
    .n-data-table-th {
      background-color: transparent;
    }

    .n-data-table-td {
      background-color: var(--n-merged-td-color);
    }

    .n-data-table-tr:hover .n-data-table-td {
      background-color: var(--n-merged-td-color-hover);
    }
  }

  :deep(.n-data-table-expand-trigger) {
    width: 24px;
    height: 24px;
    margin-right: 8px;
  }

  :deep(.n-data-table-expand-trigger--expanded) {
    transform: rotate(90deg);
  }
}

/* 响应式布局 */
@media (max-width: 1200px) {
  .opportunity-detail-modal {
    :deep(.n-data-table) {
      overflow-x: auto;
    }
  }
}

@media (max-width: 768px) {
  .opportunity-detail-modal {
    :deep(.n-modal) {
      max-width: 100vw;
      margin: 0;
    }
  }
}

.modal-content {
  padding: 0;
  background-color: #f5f5f7;
}

.opportunity-detail {
  min-height: 600px;
}

.detail-layout {
  background-color: #f5f5f7;
  border-radius: 12px;
}

.left-section {
  padding: 16px;
  background-color: #ffffff;
  border-radius: 12px;
  height: 100%;
  width: 360px;
}

.carousel-section {
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  
  .carousel {
    height: 240px;
    border-radius: 12px;
    
    :deep(.n-carousel-arrow) {
      background-color: rgba(0, 0, 0, 0.2);
      backdrop-filter: blur(4px);
      width: 32px;
      height: 32px;
      border-radius: 16px;
      color: #ffffff;
      font-size: 18px;
      transition: all 0.3s;
      
      &:hover {
        background-color: rgba(0, 0, 0, 0.5);
        transform: scale(1.1);
      }
    }
    
    :deep(.n-carousel-dots) {
      padding: 8px;
      background: linear-gradient(to top, rgba(0, 0, 0, 0.3), transparent);
      
      .n-carousel-dot {
        width: 24px;
        height: 3px;
        border-radius: 1.5px;
        background-color: rgba(255, 255, 255, 0.4);
        transition: all 0.3s;
        
        &.n-carousel-dot--active {
          background-color: #ffffff;
          width: 32px;
        }
      }
    }
    
    .carousel-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      border-radius: 12px;
    }
    
    .image-title {
      position: absolute;
      bottom: 16px;
      left: 16px;
      color: #ffffff;
      font-size: 14px;
      font-weight: 500;
      text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
      padding: 4px 8px;
      border-radius: 4px;
      background: rgba(0, 0, 0, 0.2);
      backdrop-filter: blur(4px);
    }
  }
}

.info-card {
  margin-bottom: 24px;
  border-radius: 12px;
  background-color: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  }
  
  .info-header {
    margin-bottom: 16px;
    padding: 16px 20px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    
    .community-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      
      .title-left {
        display: flex;
        align-items: center;
        gap: 8px;
      }
      
      .community-name {
        font-size: 20px;
        font-weight: 600;
        color: #1d1d1f;
        margin: 0;
      }
      
      .location-icon {
        color: #06c;
      }

      .status-tag {
        margin-left: auto;
      }
    }
  }
  
  .info-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    padding: 0 20px 20px;
    
    .info-item {
      .label {
        font-size: 13px;
        color: #86868b;
        margin-bottom: 4px;
      }
      
      .value {
        font-size: 15px;
        color: #1d1d1f;
        font-weight: 500;
        
        &.price {
          color: #06c;
          font-weight: 600;
        }
      }
    }
  }
}

.business-card {
  border-radius: 12px;
  background-color: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  transition: box-shadow 0.3s ease;
  
  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  }
  
  :deep(.n-card-header) {
    font-size: 16px;
    font-weight: 600;
    color: #1d1d1f;
  }
  
  :deep(.n-descriptions-item-label) {
    color: #86868b;
    font-size: 13px;
  }
  
  :deep(.n-descriptions-item-content) {
    color: #1d1d1f;
    font-size: 14px;
  }
  
  :deep(.n-button) {
    border-radius: 6px;
    font-weight: 500;
  }
}

.right-section {
  padding: 24px;
  background-color: #ffffff;
  /* border-radius: 0px; */
  margin-left: 24px;
  flex: 1;
  
  .charts-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 32px;
    
    .chart-wrapper {
      background-color: #ffffff;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      transition: box-shadow 0.3s ease;
      
      &:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
      }
      
      .chart {
        height: 300px;
      }
      
      .chart-desc {
        margin: 12px 0 0;
        font-size: 13px;
        color: #86868b;
        text-align: center;
      }
    }
  }
}

.stats-wrapper {
  background-color: #ffffff;
  border-radius: 12px;
  
  .stats-section {
    margin-bottom: 24px;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .stats-section-title {
      font-size: 16px;
      font-weight: 600;
      color: #1d1d1f;
      margin-bottom: 16px;
    }
  }
  
  :deep(.n-data-table) {
    .n-data-table-th {
      background-color: #f5f5f7;
      font-size: 13px;
      color: #86868b;
      padding: 12px 16px;
    }
    
    .n-data-table-td {
      font-size: 14px;
      color: #1d1d1f;
      padding: 12px 16px;
    }
    
    .highlight-row {
      background-color: #f5f5f7;
      font-weight: 600;
    }
  }
}

.time-range-tip {
  margin-top: 12px;
  text-align: right;
  font-size: 12px;
  color: #86868b;
}

.tags-section {
  margin: 24px 0;
  padding: 0 20px;
  
  :deep(.n-tag) {
    border-radius: 6px;
    padding: 4px 8px;
    font-size: 13px;
    margin-right: 8px;
    margin-bottom: 8px;
  }
}

/* 响应式布局优化 */
@media (max-width: 1200px) {
  .right-section {
    .charts-container {
      grid-template-columns: 1fr;
    }
  }
}

@media (max-width: 768px) {
  .detail-layout {
    flex-direction: column;
  }
  
  .left-section {
    width: 100%;
  }
  
  .right-section {
    margin-left: 0;
    margin-top: 24px;
    padding: 16px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}

:deep(.last-column) {
  padding-right: 16px !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}
</style>