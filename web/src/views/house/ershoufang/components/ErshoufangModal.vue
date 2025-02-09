<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="title"
    :loading="loading"
    preset="dialog"
    class="ershoufang-modal"
    style="width: 600px"
    :show-icon="false"
  >
    <n-form
      ref="formRef"
      :model="localFormValue"
      :rules="rules"
      label-placement="left"
      label-width="100"
      require-mark-placement="right-hanging"
      class="ershoufang-form"
    >
      <!-- 基本信息区域 -->
      <div class="form-section">
        <div class="section-title">基本信息</div>
        
        <!-- 小区选择 -->
        <n-form-item label="小区" path="community_id" required>
          <div class="community-select">
            <n-select
              v-model:value="localFormValue.community_id"
              :options="filteredCommunityOptions"
              placeholder="请选择小区"
              :loading="communityLoading"
              clearable
              filterable
              :consistent-menu-width="false"
              @update:value="handleCommunityChange"
            />
          </div>
        </n-form-item>

        <!-- 户型输入 -->
        <n-form-item label="户型" path="layout">
          <div class="layout-input">
            <n-input-number
              v-model:value="roomCount"
              :min="1"
              :max="9"
              placeholder="室"
              @update:value="handleLayoutChange"
              class="number-input"
            />
            <span class="separator">室</span>
            <n-input-number
              v-model:value="hallCount"
              :min="0"
              :max="9"
              placeholder="厅"
              @update:value="handleLayoutChange"
              class="number-input"
            />
            <span class="separator">厅</span>
          </div>
        </n-form-item>

        <!-- 楼层信息 -->
        <n-form-item label="楼层" path="floor_number">
          <div class="floor-input">
            <n-input-number
              v-model:value="localFormValue.floor_number"
              :min="1"
              placeholder="所在楼层"
              @update:value="handleFloorChange"
              class="number-input"
            />
            <span class="separator">/</span>
            <n-input-number
              v-model:value="localFormValue.total_floors"
              :min="1"
              placeholder="总层高"
              @update:value="handleFloorChange"
              class="number-input"
            />
            <span class="floor-label">层</span>
          </div>
        </n-form-item>

        <!-- 其他基本信息 -->
        <n-form-item label="朝向" path="orientation">
          <n-select
            v-model:value="localFormValue.orientation"
            :options="ORIENTATION_OPTIONS"
            placeholder="请选择朝向"
            class="full-width"
          />
        </n-form-item>

        <n-form-item label="面积" path="size">
          <n-input-number
            v-model:value="localFormValue.size"
            placeholder="请输入建筑面积"
            :min="0"
            :precision="2"
            clearable
            @update:value="handleSizeChange"
            class="full-width"
          >
            <template #suffix>
              <span class="unit">㎡</span>
            </template>
          </n-input-number>
        </n-form-item>

        <n-form-item label="总价" path="total_price">
          <n-input-number
            v-model:value="localFormValue.total_price"
            placeholder="请输入总价"
            :min="0"
            :precision="2"
            clearable
            @update:value="handleTotalPriceChange"
            class="full-width"
          >
            <template #suffix>
              <span class="unit">万元</span>
            </template>
          </n-input-number>
        </n-form-item>
      </div>

      <!-- 更多信息折叠面板 -->
      <n-collapse class="more-info">
        <n-collapse-item title="更多信息" name="more">
          <div class="form-section">
            <n-form-item label="梯户比" path="ladder_ratio">
              <n-input 
                v-model:value="localFormValue.ladder_ratio" 
                placeholder="请输入梯户比"
                class="full-width"
              />
            </n-form-item>

            <n-form-item label="抵押信息" path="mortgage_info">
              <n-input 
                v-model:value="localFormValue.mortgage_info" 
                placeholder="请输入抵押信息"
                class="full-width"
              />
            </n-form-item>

            <n-form-item label="房源编号" path="house_id">
              <n-input 
                v-model:value="localFormValue.house_id" 
                placeholder="请输入房源编号"
                class="full-width"
              />
            </n-form-item>

            <n-form-item label="贝壳编号" path="ke_code">
              <n-input 
                v-model:value="localFormValue.ke_code" 
                placeholder="请输入贝壳编号"
                class="full-width"
              />
            </n-form-item>

            <n-form-item label="房源链接" path="house_link">
              <n-input 
                v-model:value="localFormValue.house_link" 
                placeholder="请输入房源链接"
                class="full-width"
              />
            </n-form-item>

            <n-form-item label="信息来源" path="data_source">
              <n-select
                v-model:value="localFormValue.data_source"
                :options="DATA_SOURCE_OPTIONS"
                placeholder="请选择信息来源"
                class="full-width"
              />
            </n-form-item>

            <n-form-item label="城市" path="city">
              <n-select
                v-model:value="localFormValue.city"
                :options="departmentStore.departments"
                :render-label="renderLabel"
                :disabled="!userStore.isSuperUser"
                placeholder="请选择城市"
                class="full-width"
              />
            </n-form-item>
          </div>
        </n-collapse-item>
      </n-collapse>
    </n-form>

    <template #action>
      <div class="modal-footer">
        <n-button class="cancel-btn" @click="handleCancel">取消</n-button>
        <n-button type="primary" :loading="loading" @click="handleSubmit">
          确定
        </n-button>
      </div>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, reactive, onMounted, watch, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { useCityStore } from '@/stores/city'
import { useErshoufangModal } from '@/composables/useErshoufangModal'
import { useUserStore } from '@/store/modules/user'
import { useDepartmentStore } from '@/stores/department'

const props = defineProps({
  show: Boolean,
  title: String,
  loading: Boolean,
  formValue: {
    type: Object,
    required: true
  },
  rules: Object
})

const emit = defineEmits(['update:show', 'submit', 'cancel'])

const formRef = ref(null)
const message = useMessage()
const cityStore = useCityStore()
const userStore = useUserStore()
const departmentStore = useDepartmentStore()
const { communityOptions, loading: communityLoading, loadCommunityOptions } = useErshoufangModal()

// 本地表单数据
const localFormValue = reactive({
  name: '',
  city: '',  // 初始为空，等待 onMounted 后设置
  community_id: null,
  community_name: '',
  building: '',
  unit: '',
  room: '',
  floor: null,
  total_floor: null,
  area: null,
  total_price: null,
  unit_price: null,
  data_source: 'store',
  ladder_ratio: '',
  mortgage_info: '',
  house_id: '',
  house_type: '',
  decoration: '',
  face: '',
  elevator: '',
  property_rights: [],
  property_year: null,
  remark: ''
})

const ORIENTATION_OPTIONS = [
  { label: '朝南', value: '朝南' },
  { label: '朝东', value: '朝东' },
  { label: '朝西', value: '朝西' },
  { label: '朝北', value: '朝北' },
  { label: '南北', value: '南北' }
]

const DATA_SOURCE_OPTIONS = [
  { label: '门店', value: 'store' },
  { label: '网络', value: 'web' },
  { label: 'API', value: 'api' }
]

// 监听部门变化
watch(() => departmentStore.currentDepartment, (newValue) => {
  if (!localFormValue.city) {
    localFormValue.city = newValue
  }
})

// 监听城市变化
watch(() => localFormValue.city, (newValue) => {
})

// 监听表单值变化
watch(() => props.formValue, (newVal) => {
  if (newVal) {
    const formData = { ...newVal }
    if (!formData.city) {
      formData.city = departmentStore.currentDepartment
    }
    Object.assign(localFormValue, formData)
  }
}, { deep: true })

// 初始化部门信息
onMounted(async () => {
  await departmentStore.initCurrentDepartment()
  if (!localFormValue.city) {
    localFormValue.city = departmentStore.currentDepartment
  }
  loadCommunityOptions()
})

// 渲染城市选择器的标签
const renderLabel = (option) => {
  return option.label || option.name || '未知'
}

// 添加日期格式
const dateFormat = 'yyyy-MM-dd'

// 根据当前城市过滤小区选项
const filteredCommunityOptions = computed(() => {
  return communityOptions.value
    .filter(option => option.city === cityStore.currentCity)
})

// 处理小区选择变化
const handleCommunityChange = (communityId) => {
  if (communityId) {
    const selectedCommunity = communityOptions.value.find(
      option => option.value === communityId
    )
    if (selectedCommunity) {
      localFormValue.community_id = parseInt(communityId)
      localFormValue.community_name = selectedCommunity.label
      localFormValue.region = selectedCommunity.region
      localFormValue.area = selectedCommunity.area
      localFormValue.city = selectedCommunity.city
    }
  } else {
    localFormValue.community_id = null
    localFormValue.community_name = ''
    localFormValue.region = ''
    localFormValue.area = ''
  }
}

// 修改总价变化处理函数，只计算单价但不显示
const handleTotalPriceChange = (value) => {
  if (value && localFormValue.size) {
    localFormValue.unit_price = (value * 10000 / localFormValue.size).toFixed(2)
  }
}

// 修改面积变化处理函数，只计算单价但不显示
const handleSizeChange = (value) => {
  if (value && localFormValue.total_price) {
    localFormValue.unit_price = (localFormValue.total_price * 10000 / value).toFixed(2)
  }
}

// 添加楼层计算函数
const calculateFloorInfo = (floorNumber, totalFloors) => {
  if (!floorNumber || !totalFloors) return null
  
  const ratio = floorNumber / totalFloors
  if (ratio < 1/3) {
    return `低楼层/共${totalFloors}层`
  } else if (ratio < 2/3) {
    return `中楼层/共${totalFloors}层`
  } else {
    return `高楼层/共${totalFloors}层`
  }
}

// 处理楼层变化
const handleFloorChange = () => {
  if (localFormValue.floor_number && localFormValue.total_floors) {
    if (localFormValue.floor_number > localFormValue.total_floors) {
      message.warning('所在楼层不能大于总层高')
      localFormValue.floor_number = localFormValue.total_floors
    }
  }
}

// 修改提交处理函数
const handleSubmit = async () => {
  try {
    if (!formRef.value) {
      return
    }

    // 表单验证
    await formRef.value.validate()

    // 准备提交数据
    const submitData = { ...localFormValue }

    // 确保楼层信息是数字类型并计算楼层描述
    if (submitData.floor_number && submitData.total_floors) {
      submitData.floor_number = Number(submitData.floor_number)
      submitData.total_floors = Number(submitData.total_floors)
      submitData.floor = calculateFloorInfo(submitData.floor_number, submitData.total_floors)
    }

    // 计算单价
    if (submitData.total_price && submitData.size) {
      submitData.unit_price = Number((submitData.total_price * 10000 / submitData.size).toFixed(2))
    }

    emit('submit', submitData)
  } catch (error) {
    message.error('表单验证失败')
  }
}

const handleCancel = () => {
  formRef.value?.restoreValidation()
  emit('update:show', false)
  emit('cancel')
}

// 户型数字输入 - 移除默认值
const roomCount = ref(null)
const hallCount = ref(null)

// 解析户型字符串
const parseLayout = (layout) => {
  if (!layout) return { rooms: null, halls: null }
  const match = layout.match(/(\d+)室(\d+)厅/)
  if (match) {
    return {
      rooms: parseInt(match[1]),
      halls: parseInt(match[2])
    }
  }
  return { rooms: null, halls: null }
}

// 处理户型变化
const handleLayoutChange = () => {
  if (roomCount.value !== null && hallCount.value !== null) {
    localFormValue.layout = `${roomCount.value}室${hallCount.value}厅`
  } else {
    localFormValue.layout = ''
  }
}

// 监听表单显示状态
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadCommunityOptions()
  }
})

// 监听 show 的变化，当 Modal 关闭时重置表单
watch(
  () => props.show,
  (newVal) => {
    if (!newVal) {
      // Modal 关闭时重置表单
      formRef.value?.restoreValidation()
      roomCount.value = null
      hallCount.value = null
      if (!props.formValue.id) {
        // 只在新建时重置表单数据
        Object.assign(localFormValue, {
          name: '',
          city: departmentStore.currentDepartment,  // 重置时使用当前部门
          community_id: null,
          community_name: '',
          building: '',
          unit: '',
          room: '',
          floor: null,
          total_floor: null,
          area: null,
          total_price: null,
          unit_price: null,
          data_source: 'store',
          ladder_ratio: '',
          mortgage_info: '',
          house_id: '',
          house_type: '',
          decoration: '',
          face: '',
          elevator: '',
          property_rights: [],
          property_year: null,
          remark: ''
        })
      }
    } else {
      // Modal 打开时，使用当前部门作为默认城市
      if (!props.formValue?.id) {
        localFormValue.city = departmentStore.currentDepartment
      }
    }
  },
  { immediate: true }
)

// 监听 formValue 的变化
watch(
  () => props.formValue,
  async (newVal) => {
    if (newVal.community_id) {
      await loadCommunityOptions()
    }

    // 处理数据转换
    const processedData = {
      name: newVal.name,
      city: newVal.city,
      community_id: newVal.community_id ? parseInt(newVal.community_id) : undefined,
      community_name: newVal.community_name || '',
      building: newVal.building || '',
      unit: newVal.unit || '',
      room: newVal.room || '',
      floor: newVal.floor || '',
      total_floor: newVal.total_floor || null,
      area: newVal.area || null,
      total_price: newVal.total_price || null,
      unit_price: newVal.unit_price || null,
      data_source: newVal.data_source || 'store',
      ladder_ratio: newVal.ladder_ratio || '',
      mortgage_info: newVal.mortgage_info || '',
      house_id: newVal.house_id || '',
      house_type: newVal.house_type || '',
      decoration: newVal.decoration || '',
      face: newVal.face || '',
      elevator: newVal.elevator || '',
      property_rights: newVal.property_rights || [],
      property_year: newVal.property_year || null,
      remark: newVal.remark || ''
    }

    // 更新本地表单数据
    Object.assign(localFormValue, processedData)
    
    // 解析并设置户型数据
    if (processedData.layout) {
      const { rooms, halls } = parseLayout(processedData.layout)
      roomCount.value = rooms
      hallCount.value = halls
    }

    // 确保小区选项已加载完成后再设置小区ID
    if (processedData.community_id) {
      await new Promise(resolve => {
        const timer = setInterval(() => {
          if (communityOptions.value.length > 0) {
            clearInterval(timer)
            localFormValue.community_id = processedData.community_id
            resolve()
          }
        }, 100)
        
        // 5秒后超时
        setTimeout(() => {
          clearInterval(timer)
          resolve()
        }, 5000)
      })
    }
  },
  { deep: true, immediate: true }
)

// 修改表单验证规则
const rules = {
  community_id: {
    required: true,
    message: '请选择小区',
    trigger: ['blur', 'change'],
    type: 'number'
  },
  layout: {
    required: true,
    message: '请输入户型',
    trigger: ['blur', 'change']
  },
  // ... 其他验证规则
}
</script>

<style scoped>
.ershoufang-modal {
  --primary-color: #18a058;
  --border-radius: 4px;
  --input-height: 34px;
}

.ershoufang-form {
  padding: 0 16px;
}

.form-section {
  background: #f9f9f9;
  border-radius: var(--border-radius);
  padding: 16px;
  margin-bottom: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 16px;
  padding-left: 8px;
  border-left: 3px solid var(--primary-color);
}

.layout-input,
.floor-input {
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

.unit {
  color: #666;
  margin-left: 4px;
}

.full-width {
  width: 100%;
}

.select-with-input :deep(.n-base-selection) {
  margin-bottom: 8px;
}

.manual-input {
  margin-top: 8px;
  width: 100%;
}

.more-info {
  margin-top: 24px;
  border: 1px solid #eee;
  border-radius: var(--border-radius);
}

.more-info :deep(.n-collapse-item__header) {
  font-size: 14px;
  color: #666;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
}

.cancel-btn {
  background: #f5f5f5;
}

:deep(.n-form-item) {
  margin-bottom: 20px;
}

:deep(.n-form-item-label) {
  font-weight: 500;
  color: #333;
}

:deep(.n-input),
:deep(.n-input-number),
:deep(.n-select) {
  height: var(--input-height);
}

:deep(.n-base-selection) {
  height: var(--input-height);
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
</style>