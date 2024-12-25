<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="title"
    preset="dialog"
    :style="{ width: screenWidth < 768 ? '95vw' : '800px' }"
  >
    <n-form
      ref="formRef"
      :model="localFormValue"
      :rules="rules"
      label-placement="left"
      :label-width="screenWidth < 768 ? 80 : 120"
      require-mark-placement="right-hanging"
      :size="screenWidth < 768 ? 'small' : 'medium'"
    >
      <n-grid :cols="screenWidth < 768 ? 1 : 2" :x-gap="24" responsive="screen">
        <n-grid-item>
          <n-form-item label="小区" path="community_id">
            <n-select
              v-model:value="localFormValue.community_id"
              :options="communityOptions"
              placeholder="请选择小区"
              :loading="loadingCommunities"
              filterable
              clearable
              @focus="handleCommunityFocus"
              @search="handleCommunitySearch"
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="成交日期" path="deal_date">
            <n-date-picker
              v-model:value="localFormValue.deal_date"
              type="date"
              clearable
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <n-grid :cols="screenWidth < 768 ? 1 : 2" :x-gap="24" responsive="screen">
        <n-grid-item>
          <n-form-item label="总价(万)" path="total_price">
            <n-input-number
              v-model:value="localFormValue.total_price"
              :min="0"
              :precision="2"
              clearable
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="建筑面积(㎡)" path="size">
            <n-input-number
              v-model:value="localFormValue.size"
              :min="0"
              :precision="2"
              clearable
              style="width: 100%"
              @update:value="handleSizeChange"
            />
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <n-grid :cols="screenWidth < 768 ? 1 : 2" :x-gap="24" responsive="screen">
        <n-grid-item>
          <n-form-item label="单价(元/㎡)" path="unit_price">
            <n-input-number
              v-model:value="localFormValue.unit_price"
              :min="0"
              :precision="2"
              clearable
              style="width: 100%"
              readonly
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="户型" path="layout">
            <n-input
              v-model:value="localFormValue.layout"
              placeholder="例如: 2室1厅"
              clearable
            />
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <n-grid :cols="screenWidth < 768 ? 1 : 2" :x-gap="24" responsive="screen">
        <n-grid-item>
          <n-form-item label="楼层" path="floor_info">
            <n-input
              v-model:value="localFormValue.floor_info"
              placeholder="例如: 中楼层/共33层"
              clearable
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="朝向" path="orientation">
            <n-select
              v-model:value="localFormValue.orientation"
              :options="ORIENTATION_OPTIONS"
              placeholder="请选择朝向"
              clearable
            />
          </n-form-item>
        </n-grid-item>
      </n-grid>

      <n-grid :cols="screenWidth < 768 ? 1 : 2" :x-gap="24" responsive="screen">
        <n-grid-item>
          <n-form-item label="中介公司" path="agency">
            <n-input
              v-model:value="localFormValue.agency"
              placeholder="请输入中介公司"
              clearable
            />
          </n-form-item>
        </n-grid-item>
        <n-grid-item>
          <n-form-item label="成交周期(天)" path="deal_cycle">
            <n-input-number
              v-model:value="localFormValue.deal_cycle"
              :min="0"
              clearable
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>
      </n-grid>
    </n-form>

    <template #action>
      <n-space justify="end">
        <n-button @click="handleCancel">取消</n-button>
        <n-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          确定
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onBeforeMount } from 'vue'
import { useMessage } from 'naive-ui'
import { communityApi } from '@/api/house'
import { useCityStore } from '@/stores/city'

const props = defineProps({
  show: Boolean,
  title: String,
  loading: Boolean,
  formValue: Object
})

const emit = defineEmits(['update:show', 'submit', 'cancel'])
const message = useMessage()
const cityStore = useCityStore()
const formRef = ref(null)

// 本地表单数据
const localFormValue = reactive({})

// 监听外部表单数据变化
watch(() => props.formValue, (val) => {
  Object.assign(localFormValue, val)
}, { deep: true })

// 小区选项相关
const communityOptions = ref([])
const loadingCommunities = ref(false)

// 添加屏幕宽度响应
const screenWidth = ref(window.innerWidth)

const handleResize = () => {
  screenWidth.value = window.innerWidth
}

onBeforeMount(() => {
  window.addEventListener('resize', handleResize)
})

onMounted(() => {
  handleResize()
})

// 修改小区选择相关逻辑
const handleCommunityFocus = () => {
  if (communityOptions.value.length === 0) {
    loadCommunities()
  }
}

const loadCommunities = async () => {
  loadingCommunities.value = true
  try {
    const res = await communityApi.list({
      city: cityStore.currentCity,
      page_size: 100  // 加载更多选项
    })
    if (res.code === 200) {
      communityOptions.value = res.data.items.map(item => ({
        label: item.name,
        value: item.id
      }))
    }
  } catch (error) {
    console.error('Load community options error:', error)
  } finally {
    loadingCommunities.value = false
  }
}

// 搜索小区
const handleCommunitySearch = async (query) => {
  loadingCommunities.value = true
  try {
    const res = await communityApi.list({
      name: query,
      city: cityStore.currentCity,
      page_size: 100
    })
    if (res.code === 200) {
      communityOptions.value = res.data.items.map(item => ({
        label: item.name,
        value: item.id
      }))
    }
  } catch (error) {
    console.error('Load community options error:', error)
  } finally {
    loadingCommunities.value = false
  }
}

// 处理面积变化，自动计算单价
const handleSizeChange = () => {
  if (localFormValue.total_price && localFormValue.size) {
    localFormValue.unit_price = Math.round((localFormValue.total_price * 10000) / localFormValue.size)
  }
}

const ORIENTATION_OPTIONS = [
  { label: '南', value: '南' },
  { label: '北', value: '北' },
  { label: '东', value: '东' },
  { label: '西', value: '西' },
  { label: '东南', value: '东南' },
  { label: '西南', value: '西南' },
  { label: '东北', value: '东北' },
  { label: '西北', value: '西北' }
]

const rules = {
  community_id: {
    required: true,
    message: '请选择小区',
    trigger: 'submit',
    validator: (rule, value) => {
      return !!value
    }
  },
  deal_date: {
    required: true,
    message: '请选择成交日期',
    trigger: 'submit',
    validator: (rule, value) => {
      return !!value
    }
  },
  total_price: {
    required: true,
    message: '请输入成交总价',
    trigger: 'submit',
    validator: (rule, value) => {
      return value > 0
    }
  },
  size: {
    required: true,
    message: '请输入建筑面积',
    trigger: 'submit',
    validator: (rule, value) => {
      return value > 0
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    
    // 转换日期格式
    const submitData = {
      ...localFormValue,
      source: 'manual',
      deal_date: localFormValue.deal_date ? new Date(localFormValue.deal_date).toISOString().split('T')[0] : null,
      unit_price: localFormValue.unit_price || Math.round((localFormValue.total_price * 10000) / localFormValue.size)
    }
    
    emit('submit', submitData)
  } catch (err) {
    // 如果有验证错误，显示第一个错误消息
    if (Array.isArray(err) && err.length > 0 && err[0].length > 0) {
      message.error(err[0][0].message)
    } else {
      message.error('表单验证失败，请检查必填项')
    }
  }
}

const handleCancel = () => {
  formRef.value?.restoreValidation()
  Object.assign(localFormValue, {
    community_id: null,
    deal_date: null,
    total_price: null,
    unit_price: null,
    size: null,
    layout: null,
    floor_info: null,
    orientation: null,
    agency: null,
    deal_cycle: null
  })
  emit('cancel')
}

// 修改初始化逻辑
onMounted(() => {
  loadCommunities()
})
</script>

<style scoped>
.n-form {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 16px;
}

@media (max-width: 768px) {
  .n-form-item {
    margin-bottom: 12px;
  }
  
  .n-input-number,
  .n-input,
  .n-select,
  .n-date-picker {
    width: 100% !important;
  }
}
</style> 