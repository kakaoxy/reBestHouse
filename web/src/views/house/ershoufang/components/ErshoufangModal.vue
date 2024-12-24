<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="title"
    :loading="loading"
    preset="dialog"
  >
    <n-form
      ref="formRef"
      :model="localFormValue"
      :rules="rules"
      label-placement="left"
      label-width="100"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="小区" path="community_name">
        <n-select
          v-model:value="localFormValue.community_id"
          :options="communityOptions"
          placeholder="请选择小区"
          filterable
          clearable
          @update:value="handleCommunityChange"
        >
          <template #action>
            <n-input
              v-model:value="localFormValue.community_name"
              type="text"
              placeholder="或手动输入小区名称"
              @input="handleCommunityNameInput"
            />
          </template>
        </n-select>
      </n-form-item>
      <n-form-item label="户型" path="layout">
        <n-input v-model:value="localFormValue.layout" placeholder="请输入户型，如：2室1厅" />
      </n-form-item>
      <n-space :size="24">
        <n-form-item label="所在楼层" path="floor_number">
          <n-input-number
            v-model:value="localFormValue.floor_number"
            placeholder="请输入所在楼层"
            :min="1"
            @update:value="handleFloorChange"
          />
        </n-form-item>
        <n-form-item label="总层高" path="total_floors">
          <n-input-number
            v-model:value="localFormValue.total_floors"
            placeholder="请输入总层高"
            :min="1"
            @update:value="handleFloorChange"
          />
        </n-form-item>
      </n-space>
      <n-form-item label="朝向" path="orientation">
        <n-select
          v-model:value="localFormValue.orientation"
          :options="ORIENTATION_OPTIONS"
          placeholder="请选择朝向"
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
        />
      </n-form-item>
      <n-form-item label="总价" path="total_price">
        <n-input-number
          v-model:value="localFormValue.total_price"
          placeholder="请输入总价(万元)"
          :min="0"
          :precision="2"
          clearable
          @update:value="handleTotalPriceChange"
        />
      </n-form-item>
      <n-form-item label="梯户比" path="ladder_ratio">
        <n-input v-model:value="localFormValue.ladder_ratio" placeholder="请输入梯户比" />
      </n-form-item>
      <n-form-item label="抵押信息" path="mortgage_info">
        <n-input v-model:value="localFormValue.mortgage_info" placeholder="请输入抵押信息" />
      </n-form-item>
      <n-form-item label="房源编号" path="house_id">
        <n-input v-model:value="localFormValue.house_id" placeholder="请输入房源编号" />
      </n-form-item>
      <n-form-item label="贝壳编号" path="ke_code">
        <n-input v-model:value="localFormValue.ke_code" placeholder="请输入贝壳编号" />
      </n-form-item>
      <n-form-item label="房源链接" path="house_link">
        <n-input v-model:value="localFormValue.house_link" placeholder="请输入房源链接" />
      </n-form-item>
      <n-form-item label="信息来源" path="data_source">
        <n-select
          v-model:value="localFormValue.data_source"
          :options="DATA_SOURCE_OPTIONS"
          placeholder="请选择信息来源"
        />
      </n-form-item>
    </n-form>

    <template #action>
      <n-space>
        <n-button @click="handleCancel">取消</n-button>
        <n-button type="primary" :loading="loading" @click="handleSubmit">
          确定
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { request } from '@/utils'

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

const message = useMessage()
const formRef = ref(null)
const communityOptions = ref([])

// 本地表单数据
const localFormValue = reactive({ ...props.formValue })

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

// 添加日期格式
const dateFormat = 'yyyy-MM-dd'

// 加载小区选项
const loadCommunityOptions = async () => {
  try {
    const res = await request.get('/house/communities')
    if (res.code === 200 && res.data) {
      communityOptions.value = res.data.items.map(item => ({
        label: item.name,
        value: item.id,
        region: item.region,
        area: item.area
      }))
    }
  } catch (error) {
    console.error('Failed to load communities:', error)
  }
}

// 修改小区选择处理函数
const handleCommunityChange = async (communityId) => {
  if (!communityId) {
    // 清空相关字段
    localFormValue.community_name = ''
    localFormValue.region = ''
    localFormValue.area = ''
    return
  }
  const community = communityOptions.value.find(item => item.value === communityId)
  if (community) {
    localFormValue.community_name = community.label
    localFormValue.region = community.region
    localFormValue.area = community.area
  }
}

// 处理手动输入小区名
const handleCommunityNameInput = (value) => {
  if (value) {
    // 如果手动输入，清空小区ID
    localFormValue.community_id = null
    // 清空区和圈
    localFormValue.region = ''
    localFormValue.area = ''
  }
}

// 修改总价变化处理函数，只计算单价但不显示
const handleTotalPriceChange = (value) => {
  if (value && localFormValue.size) {
    // 计算单价但不显示在表单中
    localFormValue.unit_price = (value * 10000 / localFormValue.size).toFixed(2)
  }
}

// 修改面积变化处理函数，只计算单价但不显示
const handleSizeChange = (value) => {
  if (value && localFormValue.total_price) {
    // 计算单价但不显示在表单中
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
  const floorNumber = Number(localFormValue.floor_number)
  const totalFloors = Number(localFormValue.total_floors)
  
  if (floorNumber && totalFloors) {
    // 计算楼层描述
    localFormValue.floor = calculateFloorInfo(floorNumber, totalFloors)
    console.log('Floor info calculated:', localFormValue.floor)
  }
}

// 修改提交处理函数
const handleSubmit = async () => {
  console.log('Modal handleSubmit called')
  try {
    if (!formRef.value) {
      console.error('Modal formRef is null')
      return
    }

    // 表单验证
    await formRef.value.validate()
    console.log('Form validation passed')

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

    console.log('Submitting form data:', submitData)
    emit('submit', submitData)
  } catch (error) {
    console.error('Form validation error:', error)
    message.error('表单验证失败')
  }
}

const handleCancel = () => {
  formRef.value?.restoreValidation()
  emit('update:show', false)
  emit('cancel')
}

// 监听 formValue 的变化
watch(() => props.formValue, (newVal) => {
  // 更新本地表单数据
  Object.assign(localFormValue, newVal)
}, { deep: true })

onMounted(() => {
  loadCommunityOptions()
})

defineExpose({
  formRef,
  validate: () => formRef.value?.validate()
})
</script> 