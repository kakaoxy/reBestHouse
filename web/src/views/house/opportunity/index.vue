<template>
  <n-card class="page-container">
    <div class="operation-area">
      <div class="flex justify-between mb-4">
        <div class="n-space n-space-horizontal">
          <n-select
            v-model:value="searchParams.city"
            class="n-base-selection n-base-selection--active"
            style="width: 120px"
            :options="cityOptions"
            placeholder="选择城市"
            size="medium"
          />
          <n-input
            v-model:value="searchParams.communityName"
            placeholder="搜索小区"
            class="n-input n-input--medium"
            style="width: 240px; margin-left: 12px"
            @keydown.enter="handleSearch"
          >
            <template #prefix>
              <n-icon><Search /></n-icon>
            </template>
          </n-input>
        </div>
        <n-button type="primary" @click="handleAdd">
          <template #icon>
            <n-icon color="#fff"><Add /></n-icon>
          </template>
          添加商机
        </n-button>
      </div>

      <n-tabs
        v-model:value="currentTab"
        type="segment"
        class="mb-4 mt-4"
        @update:value="handleTabChange"
      >
        <n-tab-pane name="all" tab="全部" />
        <n-tab-pane name="pending" tab="待评估" />
        <n-tab-pane name="evaluated" tab="已评估" />
        <n-tab-pane name="signed" tab="已签约" />
        <n-tab-pane name="abandoned" tab="已放弃" />
      </n-tabs>
    </div>

    <div class="content-area">
      <div 
        class="grid grid-cols-3 gap-4 overflow-auto" 
        style="max-height: calc(100vh - 200px);"
        @scroll="handleScroll"
      >
        <n-card
          v-for="item in opportunityList"
          :key="item.id"
          class="opportunity-card"
          :bordered="false"
          style="min-width: 225px; max-width: 300px; margin: 0 auto;"
        >
          <div class="card-content" @click.stop="handleCardClick(item)">
            <div class="relative">
              <div class="absolute right-2 top-2 z-10">
                <n-dropdown
                  :options="actionOptions"
                  @select="handleSelect($event, item)"
                  placement="bottom-end"
                  trigger="hover"
                >
                  <n-button text class="action-button" style="padding: 4px;">
                    <template #icon>
                      <n-icon size="18">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                          <path fill="currentColor" d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2s-2 .9-2 2s.9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2s2-.9 2-2s-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2s2-.9 2-2s-.9-2-2-2z"/>
                        </svg>
                      </n-icon>
                    </template>
                  </n-button>
                </n-dropdown>
              </div>

              <n-image
                :src="item.layout_image || '/layout.jpeg'"
                class="w-full aspect-[1.36/1] object-cover rounded"
                preview-disabled
              />
              <div class="absolute left-4 bottom-4 right-4 flex justify-between items-center">
                <span class="text-5xl font-bold text-white">{{ item.community_name }}</span>
                <n-tag :type="getStatusType(item.status)" size="small">
                  {{ item.status }}
                </n-tag>
              </div>
            </div>

            <div class="house-details">
              <div class="house-info">
                <div class="house-layout">
                  <n-icon class="mr-1 text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M10 20v-6h4v6h5v-8h3L12 3L2 12h3v8z"/>
                    </svg>
                  </n-icon>
                  <span>{{ item.layout }}</span>
                </div>
                <div class="house-floor">
                  <n-icon class="mr-1 text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M2 22h20V2z"/>
                    </svg>
                  </n-icon>
                  <span>{{ formatFloor(item.floor) }}</span>
                </div>
                <div class="house-area">
                  <n-icon class="mr-1 text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M15 15H5v-4h10m5 4v-4h-3v4M2 20h20V4H2z"/>
                    </svg>
                  </n-icon>
                  <span>{{ item.area }}㎡</span>
                </div>
                <div class="house-price">
                  <n-icon class="mr-1 text-gray-400">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10s10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87c1.96 0 2.4-.98 2.4-1.59c0-.83-.44-1.61-2.67-2.14c-2.48-.6-4.18-1.62-4.18-3.67c0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87c-1.5 0-2.4.68-2.4 1.64c0 .84.65 1.39 2.67 1.91s4.18 1.39 4.18 3.91c-.01 1.83-1.38 2.83-3.12 3.16z"/>
                    </svg>
                  </n-icon>
                  <span>{{ item.total_price }}万</span>
                </div>
              </div>
            </div>
          </div>
        </n-card>
        <n-empty v-if="opportunityList.length === 0" description="暂无数据" />
      </div>
    </div>

    <OpportunityDetail
      v-model:show="showDetail"
      :id="selectedOpportunityId"
    />

    <n-modal
      v-model:show="showModal"
      :title="modalTitle"
      preset="card"
      style="width: 800px"
      :mask-closable="false"
    >
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-placement="left"
        label-width="100"
        require-mark-placement="right-hanging"
      >
        <n-divider>基础信息</n-divider>
        <n-grid :cols="2" :x-gap="24">
          <n-grid-item>
            <n-form-item label="小区" path="community_name">
              <n-select
                v-model:value="formData.community_id"
                :options="communityOptions"
                placeholder="请选择小区"
                :loading="loadingCommunities"
                remote
                filterable
                @update:value="handleCommunityChange"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="户型" path="layout">
              <n-input-group>
                <n-input-number
                  v-model:value="formData.rooms"
                  placeholder="室"
                  :min="1"
                  :max="9"
                />
                <n-input-number
                  v-model:value="formData.halls"
                  placeholder="厅"
                  :min="0"
                  :max="9"
                />
              </n-input-group>
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="楼层" path="floor">
              <n-input-group>
                <n-input-number
                  v-model:value="formData.floor_number"
                  placeholder="所在楼层"
                  :min="1"
                  :precision="0"
                  @update:value="updateFloor"
                />
                <n-input-number
                  v-model:value="formData.total_floors"
                  placeholder="总层高"
                  :min="1"
                  :precision="0"
                  @update:value="updateFloor"
                />
              </n-input-group>
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="面积" path="area">
              <n-input-number
                v-model:value="formData.area"
                placeholder="请输入面积"
                :min="1"
                :precision="2"
                @update:value="handleAreaChange"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="总价" path="total_price">
              <n-input-number
                v-model:value="formData.total_price"
                placeholder="请输入总价"
                :min="1"
                :precision="2"
                @update:value="calculateUnitPrice"
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="单价" path="unit_price">
              <n-input-number
                v-model:value="formData.unit_price"
                placeholder="请输入单价"
                :min="1"
                :precision="2"
                disabled
                style="width: 100%"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="备注" path="remarks">
              <n-input
                v-model:value="formData.remarks"
                type="textarea"
                placeholder="请输入备注"
              />
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="户型图" path="layout_image">
              <n-upload
                list-type="image-card"
                :max="1"
                :custom-request="customRequest('layout')"
                @update:file-list="handleLayoutImageUpdate"
              >
                点击上传
              </n-upload>
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="室内图" path="interior_image">
              <n-upload
                list-type="image-card"
                :max="1"
                :custom-request="customRequest('interior')"
                @update:file-list="handleInteriorImageUpdate"
              >
                点击上传
              </n-upload>
            </n-form-item>
          </n-grid-item>
          <n-grid-item>
            <n-form-item label="位置图" path="location_image">
              <n-upload
                list-type="image-card"
                :max="1"
                :custom-request="customRequest('location')"
                @update:file-list="handleLocationImageUpdate"
              >
                点击上传
              </n-upload>
            </n-form-item>
          </n-grid-item>
        </n-grid>
        <n-divider>交易信息</n-divider>
        <n-form-item>
          <div style="display: flex; justify-content: center; width: 100%;">
            <n-space>
              <n-checkbox v-model:checked="formData.is_full_five">满五</n-checkbox>
              <n-checkbox v-model:checked="formData.is_full_two">满二</n-checkbox>
              <n-checkbox v-model:checked="formData.is_unique">唯一</n-checkbox>
            </n-space>
          </div>
        </n-form-item>
        <n-form-item label="交易来源" path="transaction_source">
          <n-select
            v-model:value="formData.transaction_source"
            :options="[
              { label: '动迁', value: '动迁' },
              { label: '买卖', value: '买卖' },
              { label: '继承', value: '继承' }
            ]"
            placeholder="请选择交易来源"
          />
        </n-form-item>
        <n-divider>业务信息</n-divider>
        <n-form-item label="商机方" path="opportunity_owner">
          <n-input v-model:value="formData.opportunity_owner" placeholder="请输入商机方" />
        </n-form-item>
        <n-form-item label="归属方" path="belonging_owner">
          <n-select
            v-model:value="formData.belonging_owner"
            :options="userOptions"
            placeholder="请选择归属方"
            filterable
            :default-value="currentUser?.username"
          />
        </n-form-item>
        <n-form-item label="商机状态" path="status">
          <n-select
            v-model:value="formData.status"
            :options="statusOptions"
            placeholder="请选择状态"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="handleCancel">取消</n-button>
          <n-button type="primary" @click="handleSubmit">
            确定
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </n-card>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { Add20Regular as Add, Search20Regular as Search } from '@vicons/fluent'
import { opportunityApi } from '@/api/house'
import { communityApi } from '@/api/house'
import { OPPORTUNITY_STATUS, OPPORTUNITY_STATUS_TAG_TYPE } from './constants'
import { useMessage } from 'naive-ui'
import { NPopconfirm, NIcon, NUpload } from 'naive-ui'
import { h } from 'vue'
import OpportunityDetail from './components/OpportunityDetail.vue'
import { request } from '@/utils'

const message = useMessage()

const communityOptions = ref([])

const searchParams = reactive({
  city: 'shanghai',
  communityName: '',
  status: '',
  page: 1,
  page_size: 30
})

const currentTab = ref('all')
const opportunityList = ref([])
const total = ref(0)
const loading = ref(false)
const showModal = ref(false)
const modalTitle = ref('添加商机')
const formRef = ref(null)
const loadingCommunities = ref(false)

const formData = reactive({
  community_id: null,
  community_name: '',
  rooms: null,
  halls: null,
  layout: '',
  floor_number: null,
  total_floors: null,
  floor: '',
  area: null,
  total_price: null,
  unit_price: null,
  is_full_five: false,
  is_full_two: false,
  is_unique: false,
  transaction_source: null,
  status: OPPORTUNITY_STATUS.PENDING,
  remarks: '',
  layout_image: null,
  interior_image: null,
  location_image: null,
  opportunity_owner: '',
  belonging_owner: ''
})

const cityOptions = [
  { label: '上海', value: 'shanghai' },
  { label: '北京', value: 'beijing' },
  { label: '广州', value: 'guangzhou' },
  { label: '深圳', value: 'shenzhen' }
].map(item => ({
  ...item,
  label: item.label + '市'
}))

const statusOptions = [
  { label: '待评估', value: '待评估' },
  { label: '已评估', value: '已评估' },
  { label: '已签约', value: '已签约' },
  { label: '已放弃', value: '已放弃' }
]

const transactionSourceOptions = [
  { label: '个人', value: '个人' },
  { label: '中介', value: '中介' },
  { label: '开发商', value: '开发商' }
]

const userOptions = ref([])
const currentUser = ref(null)

// 获取当前用户信息
const getCurrentUser = async () => {
  try {
    const res = await request.get('/base/userinfo')
    if (res.code === 200) {
      currentUser.value = res.data
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 加载用户选项
const loadUserOptions = async () => {
  try {
    const res = await request.get('/user/list', {
      params: {
        page: 1,
        page_size: 100,
        dept_id: currentUser.value?.dept_id || undefined
      }
    })
    
    // console.log('用户列表请求参数:', {
    //   dept_id: currentUser.value?.dept_id,
    //   currentUser: currentUser.value
    // })
    // console.log('用户列表原始数据:', res)
    
    if (res.code === 200 && res.data) {
      // 打印过滤前的数据
      // console.log('过滤前的用户列表:', res.data)
      
      const filteredUsers = res.data.filter(user => {
        // 如果当前用户是超级管理员，显示所有用户
        if (currentUser.value?.is_superuser) {
          return true
        }
        
        // 如果当前用户有部门
        if (currentUser.value?.dept_id) {
          // 同部门
          if (user.dept_id === currentUser.value.dept_id) {
            return true
          }
          // 下级部门（当前用户部门是父部门）
          if (user.dept?.parent_id === currentUser.value.dept_id) {
            return true
          }
          // 上级部门（当前用户部门是子部门）
          if (currentUser.value.dept?.parent_id === user.dept_id) {
            return true
          }
        }
        
        // 如果没有部门，只显示自己
        return user.id === currentUser.value?.id
      })
      
      // console.log('过滤后的用户列表:', filteredUsers)
      
      userOptions.value = filteredUsers.map(user => ({
        label: `${user.username}${user.dept?.name ? ` (${user.dept.name})` : ''}`,
        value: user.username,
        dept_id: user.dept_id
      }))
      
      // console.log('最终的用户选项:', userOptions.value)
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
    message.error('加载用户列表失败')
  }
}

const rules = {
  community_name: {
    required: true,
    message: '请选择小区',
    trigger: 'change'
  },
  layout: {
    required: true,
    message: '请输入户型',
    trigger: 'blur'
  },
  floor: {
    required: true,
    message: '请输入楼层信息',
    trigger: ['input', 'change']
  },
  area: {
    required: true,
    message: '请输入面积',
    trigger: ['input', 'change'],
    validator: (rule, value) => {
      return value > 0
    }
  },
  total_price: {
    required: true,
    message: '请输入总价',
    trigger: ['input', 'change'],
    validator: (rule, value) => {
      return value > 0
    }
  },
  status: {
    required: true,
    message: '请选择状态',
    trigger: 'change'
  }
}

const getStatusType = (status) => OPPORTUNITY_STATUS_TAG_TYPE[status] || 'default'

const loadOpportunities = async () => {
  loading.value = true
  try {
    const params = { ...searchParams }
    if (params.communityName) {
      params.community_name_like = params.communityName
      delete params.communityName
    }

    if (currentTab.value !== 'all') {
      params.status = currentTab.value === 'pending' ? '待评估' :
                     currentTab.value === 'evaluated' ? '已评估' :
                     currentTab.value === 'signed' ? '已签约' :
                     currentTab.value === 'abandoned' ? '已放弃' : undefined
    }
    params.sort_by = 'updated_at'
    params.sort_direction = 'desc'
    params.page = params.page || 1
    params.page_size = params.page_size || 30

    const res = await opportunityApi.list(params)
    if (!res.data || !Array.isArray(res.data.items)) {
      console.error('响应数据格式错误:', res)
      return
    }
    if (params.page === 1) {
      const items = Array.isArray(res.data.items) ? res.data.items : []
      const filteredItems = params.community_name_like
        ? items.filter(item => item.community_name.toLowerCase().includes(params.community_name_like.toLowerCase()))
        : items

      opportunityList.value = filteredItems.sort((a, b) => {
        const statusOrder = {
          '待评估': 1,
          '已评估': 2,
          '已签约': 3,
          '已放弃': 4
        }
        if (statusOrder[a.status] !== statusOrder[b.status]) {
          return statusOrder[a.status] - statusOrder[b.status]
        }
        return new Date(b.updated_at) - new Date(a.updated_at)
      })
      total.value = opportunityList.value.length
    } else {
      const newItems = Array.isArray(res.data.items) ? res.data.items : []
      const filteredNewItems = params.community_name_like
        ? newItems.filter(item => item.community_name.toLowerCase().includes(params.community_name_like.toLowerCase()))
        : newItems
      opportunityList.value.push(...filteredNewItems)
    }
  } catch (error) {
    console.error('加载商机列表失败:', error)
    message.error('加载商机列表失败')
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  resetList()
}

const loadCommunities = async () => {
  loadingCommunities.value = true
  try {
    const res = await communityApi.list({
      city: searchParams.city,
      name: searchParams.communityName,
      page: 1,
      page_size: 100
    })
    communityOptions.value = res.data.items
      .filter(item => item.city === searchParams.city)
      .map(item => ({
        label: `${item.name} (${item.region}-${item.area})`,
        value: item.id,
        community: item
      }))
  } catch (error) {
    console.error('加载小区列表失败:', error)
    message.error('加载小区列表失败')
  } finally {
    loadingCommunities.value = false
  }
}

watch(
  () => searchParams.city,
  () => {
    searchParams.communityName = ''
    resetList()
  }
)

watch(
  () => searchParams.communityName,
  () => {
    loadCommunities()
  }
)

watch(
  [() => formData.rooms, () => formData.halls],
  ([rooms, halls]) => {
    if (rooms !== null && halls !== null) {
      formData.layout = `${rooms}室${halls}厅`
    }
  }
)

watch(
  () => formData.area,
  (value) => {
    handleAreaChange(value)
  }
)

watch(
  () => formData.total_price,
  (value) => {
    calculateUnitPrice(value)
  }
)

const handleAdd = () => {
  modalTitle.value = '添加商机'
  formData.id = undefined
  Object.assign(formData, {
    community_id: null,
    community_name: '',
    rooms: null,
    halls: null,
    layout: '',
    floor_number: null,
    total_floors: null,
    floor: '',
    area: null,
    total_price: null,
    unit_price: null,
    is_full_five: false,
    is_full_two: false,
    is_unique: false,
    transaction_source: null,
    status: OPPORTUNITY_STATUS.PENDING,
    remarks: '',
    belonging_owner: currentUser.value?.username || '',
  })
  formRef.value?.restoreValidation()
  showModal.value = true
  loadCommunities()
  loadUserOptions()
}

const handleEdit = (item) => {
  modalTitle.value = '编辑商机'
  const layoutMatch = item.layout?.match(/(\d+)室(\d+)厅/)
  const floorMatch = item.floor?.match(/(\d+)\/(\d+)/)
  showModal.value = true
  
  // 先重置表单
  resetForm()
  
  // 先设置基础数据
  Object.keys(formData).forEach(key => {
    if (key in item) {
      formData[key] = item[key]
    }
  })
  
  // 确保 id 被正确设置
  formData.id = item.id
  
  // 设置解析后的户型和楼层数据
  if (layoutMatch) {
    formData.rooms = parseInt(layoutMatch[1])
    formData.halls = parseInt(layoutMatch[2])
  }
  
  if (floorMatch) {
    formData.floor_number = parseInt(floorMatch[1])
    formData.total_floors = parseInt(floorMatch[2])
  }
  
  formRef.value?.restoreValidation()
  loadCommunities()
  loadUserOptions()
}

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatFloor = (floor) => {
  const match = floor?.match(/第(\d+)层\/共(\d+)层/)
  return match ? `${match[1]}/${match[2]}` : floor
}

const handleCommunityChange = (communityId) => {
  const selectedCommunity = communityOptions.value.find(
    option => option.value === communityId
  )
  if (selectedCommunity) {
    const { community } = selectedCommunity
    formData.community_name = community.name
    formData.community_id = community.id
    formData.address = community.address
  }
}

const handleDelete = async (item) => {
  try {
    await opportunityApi.delete(item.id)
    message.success('删除成功')
    resetList()
  } catch (error) {
    message.error('删除失败')
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    // 构建提交数据
    const submitData = {
      id: formData.id,
      ...formData,
      layout: `${formData.rooms}室${formData.halls}厅`,
      floor: `${formData.floor_number}/${formData.total_floors}`,
    }
    
    console.log('提交前的表单数据:', submitData)
    
    // 移除临时字段
    delete submitData.rooms
    delete submitData.halls
    delete submitData.floor_number
    delete submitData.total_floors
    
    console.log('处理后的提交数据:', submitData)

    if (!submitData.id) {
      delete submitData.id
      const res = await opportunityApi.create(submitData)
      console.log('创建响应:', res)
      message.success('创建成功')
    } else {
      const res = await opportunityApi.update(submitData.id, submitData)
      console.log('更新响应:', res)
      message.success('更新成功')
    }
    
    showModal.value = false
    resetList()
  } catch (error) {
    console.error('提交失败:', error)
    message.error(error.message || '提交失败')
  }
}

const updateFloor = () => {
  if (formData.floor_number && formData.total_floors) {
    formData.floor = `${formData.floor_number}/${formData.total_floors}`
  }
}

const handleAreaChange = (value) => {
  formData.area = value
  if (formData.total_price) {
    const unitPrice = (formData.total_price * 10000) / formData.area
    formData.unit_price = Number.isFinite(unitPrice) ? Math.round(unitPrice) : null
  }
}

const calculateUnitPrice = (value) => {
  formData.total_price = value
  if (value && formData.area) {
    const unitPrice = (value * 10000) / formData.area
    formData.unit_price = Number.isFinite(unitPrice) ? Math.round(unitPrice) : null
  }
}

const loadMore = async () => {
  searchParams.page++
  try {
    const params = { ...searchParams }
    if (currentTab.value !== 'all') {
      params.status = currentTab.value === 'pending' ? '待评估' :
                     currentTab.value === 'evaluated' ? '已评估' :
                     currentTab.value === 'signed' ? '已签约' :
                     currentTab.value === 'abandoned' ? '已放弃' : undefined
    }
    const res = await opportunityApi.list(params)
    if (Array.isArray(res.data.items)) {
      opportunityList.value.push(...res.data.items)
    }
  } catch (error) {
    message.error('加载更多失败')
  }
}

const handleScroll = (e) => {
  const { scrollHeight, scrollTop, clientHeight } = e.target
  if (!loading.value && scrollHeight - scrollTop - clientHeight < 100) {
    if (opportunityList.value.length < total.value) {
      loadMore()
    }
  }
}

const resetList = () => {
  searchParams.page = 1
  searchParams.page_size = 30
  loadOpportunities()
}

const actionOptions = [
  {
    label: '编辑',
    key: 'edit',
    icon: renderIcon('edit')
  },
  {
    label: '删除',
    key: 'delete',
    icon: renderIcon('delete')
  }
]

function renderIcon(type) {
  return () => h('svg', {
    xmlns: 'http://www.w3.org/2000/svg',
    width: '16',
    height: '16',
    viewBox: '0 0 24 24'
  }, [
    h('path', {
      fill: 'currentColor',
      d: type === 'edit' 
        ? 'M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z'
        : 'M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z'
    })
  ])
}

const handleSelect = (key, item) => {
  if (key === 'edit') {
    handleEdit(item)
  } else if (key === 'delete') {
    window.$dialog.warning({
      title: '确认删除',
      content: '确定要删除这条商机吗？',
      positiveText: '确定',
      negativeText: '取消',
      onPositiveClick: () => {
        handleDelete(item)
      }
    })
  }
}

const showDetail = ref(false)
const selectedOpportunityId = ref(null)

const handleCardClick = (item) => {
  selectedOpportunityId.value = item.id
  showDetail.value = true
}

const handleCancel = () => {
  showModal.value = false
}

const handleSearch = () => {
  resetList()
}

// 处理图片上传
const handleUpload = async ({ file }) => {
  const uploadFormData = new FormData()
  uploadFormData.append('file', file.file)
  
  try {
    const res = await opportunityApi.uploadImage(uploadFormData)
    if (res.code === 200) {
      const imageUrl = res.data.url
      const result = {
        status: 'finished',
        name: file.file.name,
        url: imageUrl
      }
      // 直接更新对应的图片字段
      if (file.type === 'layout') {
        formData.layout_image = imageUrl
      } else if (file.type === 'interior') {
        formData.interior_image = imageUrl
      } else if (file.type === 'location') {
        formData.location_image = imageUrl
      }
      return result
    }
    return {
      status: 'error',
      message: '上传失败'
    }
  } catch (error) {
    return {
      status: 'error',
      message: error.message || '上传失败'
    }
  }
}

// 修改上传组件，添加自定义参数
const customRequest = (type) => {
  return ({ file }) => handleUpload({ file: { ...file, type } })
}

// 处理图片更新
const handleLayoutImageUpdate = (files) => {
  const file = files[0]
  if (file?.status === 'finished') {
    formData.layout_image = file.url
  } else {
    formData.layout_image = null
  }
}

const handleInteriorImageUpdate = (files) => {
  const file = files[0]
  if (file?.status === 'finished') {
    formData.interior_image = file.url
  } else {
    formData.interior_image = null
  }
}

const handleLocationImageUpdate = (files) => {
  const file = files[0]
  if (file?.status === 'finished') {
    formData.location_image = file.url
  } else {
    formData.location_image = null
  }
}

const resetForm = () => {
  Object.keys(formData).forEach(key => {
    if (key === 'status') {
      formData[key] = OPPORTUNITY_STATUS.PENDING
    } else if (key === 'belonging_owner') {
      formData[key] = currentUser.value?.username || ''
    } else if (['is_full_five', 'is_full_two', 'is_unique'].includes(key)) {
      formData[key] = false
    } else {
      formData[key] = null
    }
  })
  formData.id = undefined
}

onMounted(async () => {
  await getCurrentUser() // 先获取当前用户信息
  loadOpportunities()
  loadCommunities()
  loadUserOptions()
})
</script>

<style scoped>
.action-button {
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 4px;
  opacity: 0.7;
  transition: all 0.2s ease;
}

.action-button:hover {
  background-color: #fff;
  opacity: 1;
}

.action-button :deep(.n-icon) {
  color: #666;
}

.operation-area {
  background-color: #fff;
  padding: 16px 16px 0;
  margin: -16px -16px 16px;
  border-radius: 8px 8px 0 0;
}

.content-area {
  background-color: #fff;
  padding: 16px;
  border-radius: 8px;
  min-height: calc(100vh - 250px);
}

.page-container {
  background-color: #f5f6fb;
  min-height: calc(100vh - 64px);
}

.page-container :deep(.n-card-header) {
  background-color: #fff;
}

.page-container :deep(.n-card__content) {
  background-color: #f5f6fb;
  padding: 16px;
}

.house-details {
  padding: 8px;
  background-color: transparent;
  border-radius: 0 0 8px 8px;
}

.house-info {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.house-area,
.house-layout,
.house-floor,
.house-price {
  display: flex;
  align-items: center;
  color: #1c1c1c;
  font-size: 14px;
  line-height: 20px;
}

:deep(.n-icon) {
  width: 16px;
  height: 16px;
  margin-right: 6px;
  flex-shrink: 0;
  color: #758599;
}

.opportunity-card {
  transition: all 0.3s ease;
  width: 100%;
  overflow: hidden;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  min-width: 225px;
  cursor: pointer;
}

.opportunity-card :deep(.n-card__content) {
  padding: 8px;
}

.opportunity-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.06);
}

.opportunity-card .relative::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: linear-gradient(to top, rgba(0,0,0,0.6) 0%, rgba(0,0,0,0) 100%);
  border-radius: 0 0 8px 8px;
  z-index: 1;
}

.opportunity-card .relative .absolute {
  z-index: 2;
}

.grid {
  grid-template-columns: repeat(auto-fill, minmax(225px, 1fr));
  gap: 1rem;
}

.n-button--primary-type :deep(.n-icon) {
  color: #fff;
}

.n-tabs {
  margin-top: 16px;
}

.card-content {
  position: relative;
  z-index: 1;
}

.action-button {
  position: relative;
  z-index: 2;
}
</style> 