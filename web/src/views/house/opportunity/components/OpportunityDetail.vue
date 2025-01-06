<template>
  <n-modal
    :show="show"
    :mask-closable="false"
    preset="card"
    class="opportunity-detail-modal"
    @update:show="handleUpdateShow"
  >
    <template #header>
      商机详情
    </template>
    
    <div class="modal-content">
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
                <n-divider>同小区房源统计</n-divider>
                
                <div class="flex gap-8">
                  <!-- 左侧统计表格 -->
                  <div class="w-1/2">
                    <!-- 户型统计表格 -->
                    <div class="mb-6">
                      <div class="text-lg font-bold mb-2">户型分布</div>
                      <n-data-table
                        :columns="layoutColumns"
                        :data="layoutStats"
                        :bordered="false"
                        :single-line="false"
                        size="small"
                      />
                    </div>

                    <!-- 楼层统计表格 -->
                    <div class="mb-6">
                      <div class="text-lg font-bold mb-2">楼层分布</div>
                      <n-data-table
                        :columns="floorColumns"
                        :data="floorStats"
                        :bordered="false"
                        :single-line="false"
                        size="small"
                      />
                    </div>
                  </div>

                  <!-- 右侧成交统计 -->
                  <div class="w-1/2">
                    <div class="text-lg font-bold mb-2">成交统计</div>
                    <!-- TODO: 添加成交统计表格 -->
                  </div>
                </div>

                <n-divider>同小区房源信息</n-divider>
                
                <div class="flex gap-4">
                  <!-- 左侧在售房源列表 -->
                  <div class="w-[48%]">
                    <div class="mb-2 font-bold text-lg flex items-center">
                      <span class="mr-2">在售房源</span>
                      <n-tag type="success" size="small">
                        {{ ershoufangList?.length || 0 }}套
                      </n-tag>
                    </div>
                    
                    <n-spin :show="ershoufangLoading">
                      <div class="h-[calc(100vh-500px)] overflow-y-auto pr-2">
                        <n-card
                          v-for="item in ershoufangList"
                          :key="item.id"
                          class="mb-4 cursor-pointer hover:shadow-md transition-shadow"
                          size="small"
                          @click="handleViewErshoufang(item)"
                        >
                          <div class="flex justify-between items-start">
                            <div>
                              <div class="text-16 font-medium mb-2">{{ item.layout }}</div>
                              <div class="text-gray-500 text-14">
                                {{ item.floor_info }} | {{ item.size }}㎡ | {{ item.orientation }}
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
                        <n-empty v-if="ershoufangList.length === 0" description="暂无在售房源" />
                      </div>
                    </n-spin>
                  </div>

                  <!-- 右侧成交房源列表 -->
                  <div class="w-[48%]">
                    <div class="mb-2 font-bold text-lg flex items-center">
                      <span class="mr-2">成交记录</span>
                      <n-tag type="info" size="small">
                        {{ dealRecordList?.length || 0 }}套
                      </n-tag>
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
                              <div class="text-16 font-medium mb-2">{{ item.layout }}</div>
                              <div class="text-gray-500 text-14">
                                {{ item.floor_info || item.floor }} | {{ item.area }}㎡ | {{ formatDate(item.deal_date) }}
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
          </div>
        </div>
      </n-spin>
    </div>
  </n-modal>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { opportunityApi, ershoufangApi, dealRecordApi } from '@/api/house'
import { OPPORTUNITY_STATUS_TAG_TYPE } from '../constants'
import { useMessage } from 'naive-ui'
import { formatDate } from '@/utils'

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
        city: 'shanghai'
      }
    }
  } catch (error) {
    message.error('加载商机详情失败')
  } finally {
    loading.value = false
  }
}

// 加载同小区房源
const loadCommunityErshoufang = async (communityId) => {
  ershoufangLoading.value = true
  try {
    const city = opportunityData.value?.city?.toLowerCase()
    if (!city || !communityId) {
      console.warn('Missing required params:', { city, communityId })
      return
    }

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
      console.log('Ershoufang data:', res.data.items)
      ershoufangList.value = res.data.items
    }
  } catch (error) {
    console.error('Load community ershoufang error:', error)
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
    const city = opportunityData.value?.city?.toLowerCase()
    if (!city || !communityId) {
      console.warn('Missing required params:', { city, communityId })
      return
    }

    const params = {
      community_id: Number(communityId),
      city,
      page: 1,
      page_size: 1000,
      sort_by: 'deal_date',
      sort_direction: 'desc'
    }

    const res = await dealRecordApi.list(params)
    
    if (res.code === 200 && res.data?.items) {
      dealRecordList.value = res.data.items
    } else {
      console.warn('Failed to load deal records:', res)
      dealRecordList.value = []
    }
  } catch (error) {
    console.error('Load community deal records error:', error)
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
    console.error('Load all data error:', error)
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
  return OPPORTUNITY_STATUS_TAG_TYPE[status] || 'default'
}

// 计算天数差异
const getDaysDiff = (dateStr) => {
  if (!dateStr) return 0
  const today = new Date()
  const listingDate = new Date(dateStr)
  
  // 检查日期是否有效
  if (isNaN(listingDate.getTime())) {
    console.warn('Invalid date:', dateStr)
    return 0
  }
  
  const diffTime = Math.abs(today - listingDate)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
}

// 统计列定义 - 添加宽度配置
const commonColumns = [
  { title: '套数', key: 'count', width: 80 },
  { title: '平均面积', key: 'avgSize', width: 100, render: (row) => `${row.avgSize.toFixed(1)}㎡` },
  { title: '平均单价', key: 'avgUnitPrice', width: 120, render: (row) => `${Math.round(row.avgUnitPrice)}元/㎡` },
  { title: '平均总价', key: 'avgTotalPrice', width: 100, render: (row) => `${row.avgTotalPrice.toFixed(1)}万` },
  { title: '最高总价', key: 'maxTotalPrice', width: 100, render: (row) => `${row.maxTotalPrice}万` },
  { title: '最低总价', key: 'minTotalPrice', width: 100, render: (row) => `${row.minTotalPrice}万` },
  { title: '平均挂牌', key: 'avgListingDays', width: 100, render: (row) => `${Math.round(row.avgListingDays)}天` }
]

const layoutColumns = [
  { title: '户型', key: 'layout', width: 100 },
  ...commonColumns
]

const floorColumns = [
  { title: '楼层', key: 'floor', width: 100 },
  ...commonColumns
]

// 修改户型统计逻辑
const layoutStats = computed(() => {
  const stats = {}
  const total = { 
    layout: '合计', 
    count: 0, 
    totalSize: 0, 
    totalUnitPrice: 0, 
    totalPrice: 0, 
    maxTotalPrice: 0, 
    minTotalPrice: Infinity,
    totalListingDays: 0
  }
  
  ershoufangList.value.forEach(item => {
    const match = item.layout?.match(/^(\d)/)
    const layout = match ? `${match[1]}室` : '其他'
    if (!stats[layout]) {
      stats[layout] = {
        layout,
        count: 0,
        totalSize: 0,
        totalUnitPrice: 0,
        totalPrice: 0,
        maxTotalPrice: 0,
        minTotalPrice: Infinity,
        totalListingDays: 0
      }
    }
    
    const listingDays = getDaysDiff(item.listing_date || item.created_at)
    
    stats[layout].count++
    stats[layout].totalSize += item.size
    stats[layout].totalUnitPrice += item.unit_price
    stats[layout].totalPrice += item.total_price
    stats[layout].maxTotalPrice = Math.max(stats[layout].maxTotalPrice, item.total_price)
    stats[layout].minTotalPrice = Math.min(stats[layout].minTotalPrice, item.total_price)
    stats[layout].totalListingDays += listingDays
    
    // 更新总计
    total.count++
    total.totalSize += item.size
    total.totalUnitPrice += item.unit_price
    total.totalPrice += item.total_price
    total.maxTotalPrice = Math.max(total.maxTotalPrice, item.total_price)
    total.minTotalPrice = Math.min(total.minTotalPrice, item.total_price)
    total.totalListingDays += listingDays
  })
  
  // 计算平均值并按户型排序
  const result = Object.values(stats)
    .map(stat => ({
      ...stat,
      avgSize: stat.totalSize / stat.count,
      avgUnitPrice: stat.totalUnitPrice / stat.count,
      avgTotalPrice: stat.totalPrice / stat.count,
      avgListingDays: stat.totalListingDays / stat.count,
      minTotalPrice: stat.minTotalPrice === Infinity ? 0 : stat.minTotalPrice
    }))
    .sort((a, b) => {
      const numA = parseInt(a.layout) || Infinity
      const numB = parseInt(b.layout) || Infinity
      return numA - numB
    })
  
  // 添加总计行
  if (total.count > 0) {
    result.push({
      layout: '合计',
      count: total.count,
      avgSize: total.totalSize / total.count,
      avgUnitPrice: total.totalUnitPrice / total.count,
      avgTotalPrice: total.totalPrice / total.count,
      avgListingDays: total.totalListingDays / total.count,
      maxTotalPrice: total.maxTotalPrice,
      minTotalPrice: total.minTotalPrice === Infinity ? 0 : total.minTotalPrice
    })
  }
  
  return result
})

// 修改楼层统计逻辑，添加挂牌时长
const floorStats = computed(() => {
  const stats = {
    '低楼层': {
      floor: '低楼层',
      count: 0,
      totalSize: 0,
      totalUnitPrice: 0,
      totalPrice: 0,
      maxTotalPrice: 0,
      minTotalPrice: Infinity,
      totalListingDays: 0
    },
    '中楼层': {
      floor: '中楼层',
      count: 0,
      totalSize: 0,
      totalUnitPrice: 0,
      totalPrice: 0,
      maxTotalPrice: 0,
      minTotalPrice: Infinity,
      totalListingDays: 0
    },
    '高楼层': {
      floor: '高楼层',
      count: 0,
      totalSize: 0,
      totalUnitPrice: 0,
      totalPrice: 0,
      maxTotalPrice: 0,
      minTotalPrice: Infinity,
      totalListingDays: 0
    },
    '其他': {
      floor: '其他',
      count: 0,
      totalSize: 0,
      totalUnitPrice: 0,
      totalPrice: 0,
      maxTotalPrice: 0,
      minTotalPrice: Infinity,
      totalListingDays: 0
    }
  }
  
  const total = { 
    floor: '合计', 
    count: 0, 
    totalSize: 0, 
    totalUnitPrice: 0, 
    totalPrice: 0, 
    maxTotalPrice: 0, 
    minTotalPrice: Infinity,
    totalListingDays: 0
  }
  
  ershoufangList.value.forEach(item => {
    let floor = '其他'
    if (item.floor_info) {
      if (item.floor_info.includes('低楼层')) {
        floor = '低楼层'
      } else if (item.floor_info.includes('中楼层')) {
        floor = '中楼层'
      } else if (item.floor_info.includes('高楼层')) {
        floor = '高楼层'
      }
    } else if (item.floor) {
      if (item.floor.includes('低')) {
        floor = '低楼层'
      } else if (item.floor.includes('中')) {
        floor = '中楼层'
      } else if (item.floor.includes('高')) {
        floor = '高楼层'
      }
    }
    
    const listingDays = getDaysDiff(item.listing_date || item.created_at)
    
    stats[floor].count++
    stats[floor].totalSize += item.size
    stats[floor].totalUnitPrice += item.unit_price
    stats[floor].totalPrice += item.total_price
    stats[floor].maxTotalPrice = Math.max(stats[floor].maxTotalPrice, item.total_price)
    stats[floor].minTotalPrice = Math.min(stats[floor].minTotalPrice, item.total_price)
    stats[floor].totalListingDays += listingDays
    
    // 更新总计
    total.count++
    total.totalSize += item.size
    total.totalUnitPrice += item.unit_price
    total.totalPrice += item.total_price
    total.maxTotalPrice = Math.max(total.maxTotalPrice, item.total_price)
    total.minTotalPrice = Math.min(total.minTotalPrice, item.total_price)
    total.totalListingDays += listingDays
  })
  
  // 计算平均值并按楼层排序
  const result = Object.values(stats)
    .filter(stat => stat.count > 0)  // 只显示有数据的楼层
    .map(stat => ({
      ...stat,
      avgSize: stat.totalSize / stat.count,
      avgUnitPrice: stat.totalUnitPrice / stat.count,
      avgTotalPrice: stat.totalPrice / stat.count,
      avgListingDays: stat.totalListingDays / stat.count,
      minTotalPrice: stat.minTotalPrice === Infinity ? 0 : stat.minTotalPrice
    }))
    .sort((a, b) => {
      const order = { '低楼层': 1, '中楼层': 2, '高楼层': 3, '其他': 4 }
      return order[a.floor] - order[b.floor]
    })
  
  // 添加总计行
  if (total.count > 0) {
    result.push({
      floor: '合计',
      count: total.count,
      avgSize: total.totalSize / total.count,
      avgUnitPrice: total.totalUnitPrice / total.count,
      avgTotalPrice: total.totalPrice / total.count,
      avgListingDays: total.totalListingDays / total.count,
      maxTotalPrice: total.maxTotalPrice,
      minTotalPrice: total.minTotalPrice === Infinity ? 0 : total.minTotalPrice
    })
  }
  
  return result
})

defineOptions({
  name: 'OpportunityDetail'
})
</script>

<style scoped>
.opportunity-detail-modal {
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

  :deep(.n-card) {
    height: 100vh;
  }

  :deep(.n-card-header) {
    padding: 16px 24px;
    border-bottom: 1px solid #eee;
  }

  :deep(.n-card-content) {
    padding: 0;
    height: calc(100vh - 60px); /* 减去header高度 */
  }
}

.modal-content {
  height: 100%;
  display: flex;
  flex-direction: column;
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
  height: calc(100vh - 120px); /* 减去header和padding的高度 */
  min-height: 0;
  padding: 24px;
}

.left-section {
  flex: 0 0 25%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-right: 16px;
  border-right: 1px solid #eee;
  height: 100%;
}

.right-section {
  flex: 0 0 75%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  height: 100%;
  overflow: hidden;
}

.right-top {
  flex: 0 0 auto;
  padding: 0 24px;
}

.right-bottom {
  flex: 1;
  overflow: hidden;
  padding: 0 24px;
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

.right-bottom {
  padding: 16px;
}

/* 自定义滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background-color: #f5f5f5;
}

/* 主色调 */
.text-primary {
  color: #2080f0;
}

.text-success {
  color: #18a058;
}

/* 添加表格样式 */
:deep(.n-data-table) {
  --n-merged-th-color: #f5f7fa;
  --n-merged-td-color: transparent;
  --n-th-color: #f5f7fa;
  --n-td-color: transparent;
}

:deep(.n-data-table-wrapper) {
  border-radius: 8px;
  border: 1px solid #eee;
}
</style> 