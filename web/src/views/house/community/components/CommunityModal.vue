<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="title"
    :mask-closable="false"
    preset="dialog"
    :show-icon="false"
  >
    <n-form
      ref="formRef"
      :model="formValue"
      :rules="rules"
      label-placement="left"
      label-width="100"
      require-mark-placement="right-hanging"
    >
      <n-form-item label="小区名称" path="name">
        <n-input v-model:value="formValue.name" placeholder="请输入小区名称" />
      </n-form-item>
      <n-form-item label="所在区域" path="region">
        <n-input v-model:value="formValue.region" placeholder="请输入所在区域" />
      </n-form-item>
      <n-form-item label="所在商圈" path="area">
        <n-input v-model:value="formValue.area" placeholder="请输入所在商圈" />
      </n-form-item>
      <n-form-item label="详细地址" path="address">
        <n-input v-model:value="formValue.address" placeholder="请输入详细地址" />
      </n-form-item>
      <n-form-item label="建筑类型" path="building_type">
        <n-select
          v-model:value="formValue.building_type"
          :options="BUILDING_TYPE_OPTIONS"
          placeholder="请选择建筑类型"
        />
      </n-form-item>
      <n-form-item label="交易权属" path="property_rights">
        <n-checkbox-group v-model:value="formValue.property_rights">
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
          v-model:value="formValue.total_houses"
          placeholder="请输入房屋总数"
          :min="0"
          :precision="0"
          clearable
        />
      </n-form-item>
      <n-form-item label="建筑年代" path="building_year">
        <n-input-number
          v-model:value="formValue.building_year"
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
import { ref, reactive } from 'vue'
import { useMessage, NModal, NForm, NFormItem, NInput, NSelect, NCheckbox, NCheckboxGroup, NInputNumber, NSpace, NButton } from 'naive-ui'

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
  console.log('Modal handleSubmit called')
  try {
    await formRef.value?.validate()
    console.log('Form validation passed')
    console.log('Form data:', props.formValue)
    emit('submit')
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

defineExpose({ formRef })
</script> 