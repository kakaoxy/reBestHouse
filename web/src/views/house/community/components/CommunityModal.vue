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
          :options="departmentStore.departments"
          :render-label="renderLabel"
          :disabled="!userStore.isSuperUser"
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
import { ref, reactive, watch, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useUserStore } from '@/store/modules/user'
import { useDepartmentStore } from '@/stores/department'

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
const userStore = useUserStore()
const departmentStore = useDepartmentStore()

// 本地表单数据
const localFormValue = reactive({
  name: '',
  city: '',  
  region: '',
  area: '',
  address: '',
  building_type: '',
  property_rights: [],
  total_houses: null,
  building_year: null
})

// 初始化部门信息
onMounted(async () => {
  await departmentStore.initCurrentDepartment()
  // 设置默认城市
  if (!localFormValue.city) {
    localFormValue.city = departmentStore.currentDepartment
  }
})

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
    // 只在城市为空时才使用部门作为默认值
    if (!formData.city) {
      formData.city = departmentStore.currentDepartment
    }
    Object.assign(localFormValue, formData)
  }
}, { deep: true })

// 监听 show 的变化，当 Modal 关闭时重置表单
watch(() => props.show, (newVal) => {
  if (newVal) {
    // 打开弹窗时，使用当前部门作为默认城市
    if (!props.formValue?.id) {
      localFormValue.city = departmentStore.currentDepartment
    }
  } else {
    formRef.value?.restoreValidation()
    Object.assign(localFormValue, {
      name: '',
      city: departmentStore.currentDepartment,  // 重置时使用当前部门
      region: '',
      area: '',
      address: '',
      building_type: '',
      property_rights: [],
      total_houses: null,
      building_year: null
    })
  }
}, { immediate: true })

const renderLabel = (option) => {
  return option.label || option.name || '未知'
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    const formData = { 
      ...localFormValue,
      property_rights: (localFormValue.property_rights || []).join(',')
    }
    emit('submit', formData)
  } catch (error) {
    message.error('表单验证失败')
  }
}

const handleCancel = () => {
  formRef.value?.restoreValidation()
  Object.assign(localFormValue, {
    name: '',
    city: departmentStore.currentDepartment,  // 重置时使用当前部门
    region: '',
    area: '',
    address: '',
    building_type: '',
    property_rights: [],
    total_houses: null,
    building_year: null
  })
  emit('cancel')
}

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

defineExpose({ formRef })
</script> 