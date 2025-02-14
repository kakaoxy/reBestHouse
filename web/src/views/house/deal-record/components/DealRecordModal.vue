<template>
    <n-modal
      :show="show"
      :title="title"
      :loading="loading"
      preset="dialog"
      class="deal-record-modal"
      :style="{ width: screenWidth < 768 ? '95vw' : '800px' }"
      :show-icon="false"
      @update:show="$emit('update:show', $event)"
    >
      <div class="deal-record-container">
        <n-form
          ref="formRef"
          :model="localFormValue"
          :rules="rules"
          label-placement="left"
          :label-width="screenWidth < 768 ? 80 : 100"
          require-mark-placement="right-hanging"
          class="deal-record-form"
        >
          <n-tabs type="line" animated>
            <!-- 基础信息 -->
            <n-tab-pane name="basic" tab="基础信息">
              <n-grid :cols="screenWidth < 768 ? 1 : 2" :x-gap="24" :y-gap="16">
                <!-- 小区名称 -->
                <n-grid-item>
                  <n-form-item label="小区" path="community_id" required>
                    <div class="community-select">
                      <n-select
                        v-model:value="localFormValue.community_id"
                        :options="filteredCommunityOptions"
                        placeholder="请选择小区"
                        :loading="loadingCommunities"
                        clearable
                        filterable
                        remote
                        :consistent-menu-width="false"
                        @search="handleCommunitySearch"
                        @update:value="handleCommunityChange"
                        @focus="handleCommunityFocus"
                      >
                        <template #option="{ option }">
                          <div class="community-option">
                            <span class="community-name">{{ option.label }}</span>
                            <span class="community-region">{{ option.region }}</span>
                          </div>
                        </template>
                      </n-select>
                    </div>
                  </n-form-item>
                </n-grid-item>
  
                <!-- 户型 -->
                <n-grid-item>
                  <n-form-item label="户型" path="layout">
                    <div class="layout-input">
                      <n-input-number
                        v-model:value="layoutInfo.rooms"
                        :min="1"
                        :max="9"
                        placeholder="室"
                        @update:value="handleLayoutChange"
                        class="number-input"
                      />
                      <span class="separator">室</span>
                      <n-input-number
                        v-model:value="layoutInfo.halls"
                        :min="0"
                        :max="9"
                        placeholder="厅"
                        @update:value="handleLayoutChange"
                        class="number-input"
                      />
                      <span class="separator">厅</span>
                    </div>
                  </n-form-item>
                </n-grid-item>
  
                <!-- 建筑面积 -->
                <n-grid-item>
                  <n-form-item label="建筑面积" path="size" required>
                    <n-input-number
                      v-model:value="localFormValue.size"
                      :min="0"
                      :precision="2"
                      placeholder="请输入面积"
                      style="width: 100%"
                      @update:value="handleSizeChange"
                    >
                      <template #suffix>㎡</template>
                    </n-input-number>
                  </n-form-item>
                </n-grid-item>
  
                <!-- 楼层信息 -->
                <n-grid-item>
                  <n-form-item label="楼层信息">
                    <n-input-group>
                      <n-input-number
                        v-model:value="localFormValue.floor_number"
                        :min="1"
                        placeholder="所在楼层"
                        @update:value="handleFloorChange"
                      />
                      <n-input-number
                        v-model:value="localFormValue.total_floors"
                        :min="1"
                        placeholder="总楼层"
                        @update:value="handleFloorChange"
                      />
                    </n-input-group>
                  </n-form-item>
                </n-grid-item>
  
                <!-- 挂牌价 -->
                <n-grid-item>
                  <n-form-item label="挂牌价" path="listing_price">
                    <n-input-number
                      v-model:value="localFormValue.listing_price"
                      :min="0"
                      :precision="2"
                      placeholder="请输入挂牌价"
                      style="width: 100%"
                    >
                      <template #suffix>万元</template>
                    </n-input-number>
                  </n-form-item>
                </n-grid-item>
  
                <!-- 成交价 -->
                <n-grid-item>
                  <n-form-item label="成交价" path="total_price" required>
                    <n-input-number
                      v-model:value="localFormValue.total_price"
                      :min="0"
                      :precision="2"
                      placeholder="请输入成交价"
                      style="width: 100%"
                      @update:value="handleTotalPriceChange"
                    >
                      <template #suffix>万元</template>
                    </n-input-number>
                  </n-form-item>
                </n-grid-item>
  
                <!-- 单价 -->
                <n-grid-item>
                  <n-form-item label="单价" path="unit_price">
                    <n-input-number
                      v-model:value="localFormValue.unit_price"
                      :min="0"
                      :precision="2"
                      placeholder="自动计算"
                      readonly
                      style="width: 100%"
                    >
                      <template #suffix>元/㎡</template>
                    </n-input-number>
                  </n-form-item>
                </n-grid-item>
  
                <!-- 成交时间 -->
                <n-grid-item>
                  <n-form-item label="成交时间" path="deal_date" required>
                    <n-date-picker
                      v-model:value="localFormValue.deal_date"
                      type="date"
                      clearable
                      :is-date-disabled="disableFutureDates"
                      v-bind="datePickerProps"
                      style="width: 100%"
                    />
                  </n-form-item>
                </n-grid-item>
              </n-grid>
            </n-tab-pane>
  
            <!-- 更多信息 -->
            <n-tab-pane name="more" tab="更多信息">
              <n-grid :cols="screenWidth < 768 ? 1 : 2" :x-gap="24" :y-gap="16">
                <!-- 房屋朝向 -->
                <n-grid-item>
                  <n-form-item label="房屋朝向" path="orientation">
                    <n-select
                      v-model:value="localFormValue.orientation"
                      :options="ORIENTATION_OPTIONS"
                      placeholder="请选择朝向"
                    />
                  </n-form-item>
                </n-grid-item>
  
                <!-- 成交周期 -->
                <n-grid-item>
                  <n-form-item label="成交周期" path="deal_cycle">
                    <n-input-number
                      v-model:value="localFormValue.deal_cycle"
                      :min="0"
                      placeholder="请输入成交周期"
                    >
                      <template #suffix>天</template>
                    </n-input-number>
                  </n-form-item>
                </n-grid-item>
  
                <!-- 户型图链接 -->
                <n-grid-item>
                  <n-form-item label="户型图链接" path="layout_image">
                    <n-input
                      v-model:value="localFormValue.layout_image"
                      placeholder="请输入户型图链接"
                      type="text"
                    />
                  </n-form-item>
                </n-grid-item>
  
                <!-- 房源链接 -->
                <n-grid-item>
                  <n-form-item label="房源链接" path="house_link">
                    <n-input
                      v-model:value="localFormValue.house_link"
                      placeholder="请输入房源链接"
                      type="text"
                    />
                  </n-form-item>
                </n-grid-item>
  
                <!-- 所在城市 -->
                <n-grid-item>
                  <n-form-item label="所在城市" path="city">
                    <n-select
                      v-model:value="localFormValue.city"
                      :options="departmentStore.departments"
                      disabled
                    />
                  </n-form-item>
                </n-grid-item>
  
                <!-- 建筑年代 -->
                <n-grid-item>
                  <n-form-item label="建筑年代" path="building_year">
                    <n-input-number
                      v-model:value="localFormValue.building_year"
                      :min="1900"
                      :max="new Date().getFullYear()"
                      placeholder="请输入建筑年代"
                    />
                  </n-form-item>
                </n-grid-item>
  
                <!-- 建筑结构 -->
                <n-grid-item>
                  <n-form-item label="建筑结构" path="building_structure">
                    <n-select
                      v-model:value="localFormValue.building_structure"
                      :options="STRUCTURE_OPTIONS"
                      placeholder="请选择建筑结构"
                    />
                  </n-form-item>
                </n-grid-item>
  
                <!-- 装修 -->
                <n-grid-item>
                  <n-form-item label="装修" path="decoration">
                    <n-select
                      v-model:value="localFormValue.decoration"
                      :options="DECORATION_OPTIONS"
                      placeholder="请选择装修情况"
                    />
                  </n-form-item>
                </n-grid-item>
  
                <!-- 中介公司 -->
                <n-grid-item>
                  <n-form-item label="中介公司" path="agency">
                    <n-input
                      v-model:value="localFormValue.agency"
                      placeholder="请输入中介公司"
                    />
                  </n-form-item>
                </n-grid-item>
  
                <!-- 数据来源 -->
                <n-grid-item>
                  <n-form-item label="数据来源" path="source">
                    <n-select
                      v-model:value="localFormValue.source"
                      :options="SOURCE_OPTIONS"
                      placeholder="请选择数据来源"
                    />
                  </n-form-item>
                </n-grid-item>
  
                <!-- 平台房源ID -->
                <n-grid-item>
                  <n-form-item label="平台房源ID" path="platform_house_id">
                    <n-input
                      v-model:value="localFormValue.platform_house_id"
                      placeholder="请输入平台房源ID"
                    />
                  </n-form-item>
                </n-grid-item>
              </n-grid>
            </n-tab-pane>
          </n-tabs>
        </n-form>
  
        <!-- 添加底部按钮区域 -->
        <div class="form-actions">
          <n-space justify="end">
            <n-button @click="handleCancel" class="action-btn">
              取消
            </n-button>
            <n-button 
              type="primary" 
              :loading="loading" 
              @click="handleSubmit"
              class="action-btn"
            >
              确定
            </n-button>
          </n-space>
        </div>
      </div>
    </n-modal>
  </template>
  
  <script setup>
  import { ref, computed, watch, nextTick } from 'vue'
  import { useMessage } from 'naive-ui'
  import { useDepartmentStore } from '@/stores/department'
  import { communityApi } from '@/api/house'
  import { debounce } from 'lodash-es'
  import { useWindowSize } from '@vueuse/core'
  import { useAppStore } from '@/store'
  
  // 响应式窗口宽度
  const { width: screenWidth } = useWindowSize()
  
  const message = useMessage()
  const departmentStore = useDepartmentStore()
  const appStore = useAppStore()
  const currentDepartment = computed(() => departmentStore.currentDepartment)
  const formRef = ref(null)
  
  // 本地状态
  const communityOptions = ref([])
  const loadingCommunities = ref(false)
  const layoutInfo = ref({
    rooms: null,
    halls: null
  })
  
  const localFormValue = ref({
    id: undefined,
    community_id: undefined,
    community_name: '',
    region: '',
    area: '',
    layout: '',
    size: null,
    floor_number: null,
    total_floors: null,
    floor_info: '',
    orientation: null,
    total_price: null,
    unit_price: null,
    deal_date: null,
    deal_cycle: null,
    agency: '',
    source: 'store',
    tags: [],
    layout_image: '',
    house_link: '',
    building_year: null,
    decoration: '',
    building_structure: '',
    platform_house_id: '',
    city: departmentStore.currentDepartment  // 使用当前部门作为默认值
  })

  // Props 定义
  const props = defineProps({
    show: Boolean,
    title: String,
    loading: Boolean,
    formValue: Object,
    ORIENTATION_OPTIONS: {
      type: Array,
      default: () => []
    },
    DECORATION_OPTIONS: {
      type: Array,
      default: () => []
    },
    STRUCTURE_OPTIONS: {
      type: Array,
      default: () => []
    },
    SOURCE_OPTIONS: {
      type: Array,
      default: () => []
    }
  })
  
  // Emits 定义
  const emit = defineEmits([
    'update:show',
    'submit',
    'cancel'
  ])
  
  // 根据当前部门过滤小区选项
  const filteredCommunityOptions = computed(() => {
    return communityOptions.value.filter(option => option.city === departmentStore.currentDepartment)
  })
  
  // 修改处理小区选择变化的函数
  const handleCommunityChange = async (communityId) => {
    if (communityId) {
      const selectedCommunity = filteredCommunityOptions.value.find(
        (item) => item.value === communityId
      )
      if (selectedCommunity) {
        // 自动填充小区相关信息
        localFormValue.value = {
          ...localFormValue.value,
          community_id: communityId,
          community_name: selectedCommunity.label,  // 添加小区名称
          region: selectedCommunity.region,         // 添加区域
          area: selectedCommunity.area,            // 添加商圈
          building_year: selectedCommunity.raw?.building_year,
          city: currentDepartment.value
        }
      }
    } else {
      // 当清空选择时，重置相关字段
      localFormValue.value = {
        ...localFormValue.value,
        community_id: undefined,
        community_name: '',
        region: '',
        area: '',
        building_year: null
      }
    }
  }
  
  // 修改小区搜索处理函数
  const handleCommunitySearch = debounce(async (query) => {
    if (!query) {
      communityOptions.value = []
      return
    }
  
    loadingCommunities.value = true
    try {
      const res = await communityApi.list({
        name: query,
        city: departmentStore.currentDepartment,
        page_size: 100
      })
      if (res.code === 200) {
        communityOptions.value = res.data.items.map(item => ({
          label: item.name,
          value: item.id,
          region: item.region,
          area: item.area,
          city: item.city,
          raw: item
        }))
      }
    } catch (error) {
      console.error('Search community error:', error)
      message.error('搜索小区失败')
    } finally {
      loadingCommunities.value = false
    }
  }, 300)
  
  // 添加小区选择器获得焦点时的处理
  const handleCommunityFocus = async () => {
    if (communityOptions.value.length === 0) {
      // 当获得焦点且没有选项时，加载数据
      loadingCommunities.value = true
      try {
        const res = await communityApi.list({
          city: departmentStore.currentDepartment,
          page_size: 100
        })
        if (res.code === 200) {
          communityOptions.value = res.data.items.map(item => ({
            label: item.name,
            value: item.id,
            region: item.region,
            area: item.area,
            city: item.city,
            raw: item
          }))
        }
      } catch (error) {
        console.error('Load communities error:', error)
        message.error('加载小区列表失败')
      } finally {
        loadingCommunities.value = false
      }
    }
  }
  
  // 监听部门变化
  watch(() => departmentStore.currentDepartment, (newDepartment) => {
    if (newDepartment) {
      communityOptions.value = []
      // 清空小区相关信息并更新部门
      Object.assign(localFormValue.value, {
        community_id: null,
        community_name: '',
        region: '',
        area: '',
        city: newDepartment
      })
    }
  })

  // 监听 show 的变化，当 Modal 打开或关闭时处理表单
  watch(
    () => props.show,
    async (newVal) => {
      if (newVal) {
        // 打开弹窗时，先初始化部门列表和当前部门
        if (!props.formValue?.id) {
          await departmentStore.getDepartmentOptions()
          await departmentStore.initCurrentDepartment()
          localFormValue.value.city = departmentStore.currentDepartment
        }
      } else {
        formRef.value?.restoreValidation()
        if (!props.formValue?.id) {
          // 只在新建时重置表单数据
          Object.assign(localFormValue.value, {
            id: undefined,
            community_id: undefined,
            community_name: '',
            region: '',
            area: '',
            layout: '',
            size: null,
            floor_number: null,
            total_floors: null,
            floor_info: '',
            orientation: null,
            total_price: null,
            unit_price: null,
            deal_date: null,
            deal_cycle: null,
            agency: '',
            source: 'store',
            tags: [],
            layout_image: '',
            house_link: '',
            building_year: null,
            decoration: '',
            building_structure: '',
            platform_house_id: '',
            city: departmentStore.currentDepartment  // 重置时使用当前部门
          })
        }
      }
    }
  )

  // 监听表单值变化
  watch(() => props.formValue, (newVal) => {
    if (newVal) {
      const formData = { ...newVal }
      // 只在部门为空时才使用当前部门作为默认值
      if (!formData.city) {
        formData.city = departmentStore.currentDepartment
      }

      // 处理日期格式
      formData.deal_date = formData.deal_date ? new Date(formData.deal_date).getTime() : null
      formData.tags = formData.tags ? formData.tags.split(',') : []

      // 更新本地表单数据
      Object.assign(localFormValue.value, formData)

      // 解析并设置户型数据
      if (formData.layout) {
        const { rooms, halls } = parseLayout(formData.layout)
        layoutInfo.value.rooms = rooms
        layoutInfo.value.halls = halls
      }
    }
  }, { deep: true })

  // 禁用未来日期
  const disableFutureDates = (timestamp) => {
    return timestamp > Date.now()
  }
  
  // 处理面积变化
  const handleSizeChange = (value) => {
    if (value && localFormValue.value.total_price) {
      // 计算单价并保留两位小数
      localFormValue.value.unit_price = Number((localFormValue.value.total_price * 10000 / value).toFixed(2))
    } else {
      localFormValue.value.unit_price = null
    }
  }
  
  // 处理总价变化
  const handleTotalPriceChange = (value) => {
    if (value && localFormValue.value.size) {
      // 计算单价并保留两位小数
      localFormValue.value.unit_price = Number((value * 10000 / localFormValue.value.size).toFixed(2))
    } else {
      localFormValue.value.unit_price = null
    }
  }
  
  // 处理提交
  const handleSubmit = async () => {
    try {
      await formRef.value?.validate()
      
      // 创建提交数据的副本
      const formData = { ...localFormValue.value }
      
      // 添加当前部门
      formData.city = currentDepartment.value
      
      // 确保数值字段为数字类型
      if (formData.community_id) {
        formData.community_id = parseInt(formData.community_id)
      }
      if (formData.size) {
        formData.size = parseFloat(formData.size)
      }
      if (formData.total_price) {
        formData.total_price = parseFloat(formData.total_price)
      }
      if (formData.unit_price) {
        formData.unit_price = parseFloat(formData.unit_price)
      }
      if (formData.floor_number) {
        formData.floor_number = parseInt(formData.floor_number)
      }
      if (formData.total_floors) {
        formData.total_floors = parseInt(formData.total_floors)
      }
      
      // 处理标签
      if (formData.tags && Array.isArray(formData.tags)) {
        formData.tags = formData.tags.join(',')
      }
      
      // 设置数据来源
      formData.source = 'store'
      
      emit('submit', formData)
    } catch (error) {
      console.error('Form validation failed:', error)
    }
  }
  
  // 处理取消
  const handleCancel = () => {
    formRef.value?.restoreValidation()
    emit('cancel')
  }
  
  // 重置表单
  const resetForm = () => {
    Object.assign(localFormValue.value, {
      city: departmentStore.currentDepartment,
      community_id: null,
      community_name: '',
      region: '',
      area: '',
      layout: null,
      size: null,
      floor_number: null,
      total_floors: null,
      floor_info: null,
      orientation: null,
      total_price: null,
      unit_price: null,
      deal_date: null,
      deal_cycle: null,
      agency: null,
      source: 'store',
      tags: [],
      layout_image: '',
      house_link: '',
      building_year: null,
      decoration: null,
      building_structure: null,
      platform_house_id: ''
    })
    
    // 重置户型信息
    Object.assign(layoutInfo.value, {
      rooms: null,
      halls: null
    })
    
    formRef.value?.restoreValidation()
  }
  
  // 处理户型变化
  const handleLayoutChange = () => {
    const { rooms, halls } = layoutInfo.value
    if (rooms !== null && halls !== null) {
      localFormValue.value.layout = `${rooms}室${halls}厅`
    } else {
      localFormValue.value.layout = null
    }
  }
  
  // 处理楼层变化
  const handleFloorChange = () => {
    const { floor_number, total_floors } = localFormValue.value
    if (floor_number && total_floors) {
      const floorRatio = floor_number / total_floors
      let floorDesc = ''
      if (floorRatio <= 0.33) {
        floorDesc = '低楼层'
      } else if (floorRatio <= 0.66) {
        floorDesc = '中楼层'
      } else {
        floorDesc = '高楼层'
      }
      localFormValue.value.floor_info = `${floorDesc}/共${total_floors}层`
    } else {
      localFormValue.value.floor_info = null
    }
  }
  
  // 处理日期变化
  const handleDateChange = (value) => {
    localFormValue.value.deal_date = value
  }
  
  // 表单验证规则
  const rules = {
    community_id: {
      required: true,
      type: 'number',
      message: '请选择小区',
      trigger: ['blur', 'change']
    },
    total_price: {
      required: true,
      type: 'number',
      message: '请输入成交价',
      trigger: ['blur', 'change']
    },
    deal_date: {
      required: true,
      type: 'number',
      message: '请选择成交日期',
      trigger: ['blur', 'change']
    },
    size: {
      required: true,
      type: 'number',
      message: '请输入建筑面积',
      trigger: ['blur', 'change']
    }
  }
  
  // 日期选择器配置
  const datePickerProps = {
    valueFormat: 'yyyy-MM-dd',  // 直接使用 YYYY-MM-DD 格式
    format: 'yyyy-MM-dd'
  }
  
  // 修改户型解析函数
  const parseLayout = (layout) => {
    if (!layout) return { rooms: null, halls: null }
    const match = layout.match(/(\d+)\s*[室房]\s*(\d+)\s*[厅]?/)
    if (match) {
      return {
        rooms: parseInt(match[1]),
        halls: parseInt(match[2])
      }
    }
    return { rooms: null, halls: null }
  }
  </script>
  
  <style scoped>
  .deal-record-container {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  .deal-record-form {
    flex: 1;
    max-height: calc(90vh - 180px);
    overflow-y: auto;
    padding: 0 12px;
  }
  
  .form-actions {
    padding: 16px 12px;
    border-top: 1px solid #eee;
    background-color: #fff;
  }
  
  .action-btn {
    min-width: 90px;
  }
  
  .community-select {
    width: 100%;
  }
  
  .community-option {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 0;
  }
  
  .community-name {
    font-weight: 500;
  }
  
  .community-region {
    color: #999;
    font-size: 12px;
  }
  
  /* 响应式样式 */
  @media (max-width: 768px) {
    .deal-record-form {
      padding: 0 8px;
    }
    
    .form-actions {
      padding: 12px 8px;
    }
    
    :deep(.n-form-item) {
      margin-bottom: 12px;
    }
  }
  
  .layout-input {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .number-input {
    width: 100px;
  }
  
  .separator {
    color: #666;
    padding: 0 4px;
  }
  
  :deep(.n-input-number-suffix) {
    color: #666;
    margin-left: 4px;
  }
  </style>