<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="title"
    :loading="loading"
    preset="dialog"
    :show-icon="false"
  >
    <n-form
      ref="formRef"
      :model="localFormValue"
      :rules="rules"
      label-placement="left"
      label-width="100"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="小区名称" path="name">
        <n-input v-model:value="localFormValue.name" placeholder="请输入小区名称" />
      </n-form-item>
      
      <n-form-item label="城市" path="city">
        <n-select
          v-model:value="localFormValue.city"
          :options="communityStore.CITY_OPTIONS"
          placeholder="请选择城市"
        />
      </n-form-item>

      <n-form-item label="所在区域" path="region">
        <n-input v-model:value="localFormValue.region" placeholder="请输入所在区域" />
      </n-form-item>
      <n-form-item label="所在商圈" path="area">
        <n-input v-model:value="localFormValue.area" placeholder="请输入所在商圈" />
      </n-form-item>
      <n-form-item label="详细地址" path="address">
        <n-input v-model:value="localFormValue.address" placeholder="请输入详细地址" />
      </n-form-item>
      <n-form-item label="建筑类型" path="building_type">
        <n-select
          v-model:value="localFormValue.building_type"
          :options="BUILDING_TYPE_OPTIONS"
          placeholder="请选择建筑类型"
        />
      </n-form-item>
      <n-form-item label="交易权属" path="property_rights">
        <n-checkbox-group v-model:value="localFormValue.property_rights">
          <n-space>
            <n-checkbox
              v-for="option in PROPERTY_RIGHTS_OPTIONS"
              :key="option.value"
              :value="option.value"
            >
              {{ option.label }}
            </n-checkbox>
          </n-space>
        </n-checkbox-group>
      </n-form-item>
      <n-form-item label="房屋总数" path="total_houses">
        <n-input-number
          v-model:value="localFormValue.total_houses"
          placeholder="请输入房屋总数"
          :min="0"
          :precision="0"
          clearable
        />
      </n-form-item>
      <n-form-item label="建筑年代" path="building_year">
        <n-input-number
          v-model:value="localFormValue.building_year"
          placeholder="请输入建筑年代"
          :min="1900"
          :max="new Date().getFullYear()"
          :precision="0"
          clearable
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
import { ref, reactive, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { useCommunityStore } from '@/stores/community'

const props = defineProps({
  show: Boolean,
  title: String,
  loading: Boolean,
  formValue: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:show', 'submit', 'cancel'])

const message = useMessage()
const formRef = ref(null)
const communityStore = useCommunityStore()

// 本地表单数据
const localFormValue = reactive({
  name: '',
  city: communityStore.currentCity,
  region: '',
  area: '',
  address: '',
  building_type: null,
  property_rights: [],
  total_houses: null,
  building_year: null
})

// 监听外部表单值变化
watch(() => props.formValue, (newVal) => {
  if (newVal) {
    const formData = { ...newVal }
    // 确保城市字段存在
    formData.city = formData.city || communityStore.currentCity
    // 如果 property_rights 是字符串，转换为数组
    if (typeof formData.property_rights === 'string') {
      formData.property_rights = formData.property_rights.split(',').filter(Boolean)
    }
    Object.assign(localFormValue, formData)
  }
}, { deep: true })

// 表单验证规则
const rules = {
  name: {
    required: true,
    message: '请输入小区名称',
    trigger: ['blur', 'input']
  },
  city: {
    required: true,
    message: '请选择城市',
    trigger: ['blur', 'change']
  },
  region: {
    required: true,
    message: '请输入所在区域',
    trigger: ['blur', 'input']
  },
  area: {
    required: true,
    message: '请输入所在商圈',
    trigger: ['blur', 'input']
  }
}

const BUILDING_TYPE_OPTIONS = [
  { label: '板楼', value: '板楼' },
  { label: '塔楼', value: '塔楼' },
  { label: '板塔结合', value: '板塔结合' }
]

const PROPERTY_RIGHTS_OPTIONS = [
  { label: '商品房', value: '商品房' },
  { label: '动迁房', value: '动迁房' },
  { label: '商住', value: '商住' },
  { label: '其他', value: '其他' }
]

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    // 检查必填字段
    const { name, city, region, area } = localFormValue
    if (!name || !city || !region || !area) {
      message.error('请填写完整的小区信息')
      return
    }
    
    // 处理 property_rights 数组为字符串
    const formData = { 
      ...localFormValue,
      property_rights: localFormValue.property_rights.join(',')  // 转换为逗号分隔的字符串
    }
    
    emit('submit', formData)
  } catch (error) {
    console.error('Form validation error:', error)
    message.error('表单验证失败')
  }
}

const handleCancel = () => {
  formRef.value?.restoreValidation()
  Object.assign(localFormValue, {
    name: '',
    city: '',
    region: '',
    area: '',
    address: '',
    building_type: null,
    property_rights: [],  // 保持为数组以便于表单操作
    total_houses: null,
    building_year: null
  })
  emit('cancel')
}

defineExpose({ formRef })
</script> 