<template>
  <n-modal
    :show="show"
    @update:show="$emit('update:show', $event)"
    :title="title"
    preset="dialog"
    :style="{ width: screenWidth < 768 ? '95vw' : '600px' }"
    :icon="null"
  >
    <n-form
      ref="formRef"
      :model="localFormValue"
      :rules="rules"
      label-placement="left"
      :label-width="screenWidth < 768 ? 100 : 140"
      require-mark-placement="right-hanging"
      :size="screenWidth < 768 ? 'small' : 'medium'"
    >
      <!-- 按照列表顺序排列字段 -->
      <n-form-item label="城市" path="city">
        <n-select
          v-model:value="localFormValue.city"
          :options="cityStore.CITY_OPTIONS"
          placeholder="请选择城市"
          :disabled="true"
        />
      </n-form-item>

      <n-form-item label="小区名称" path="community_id" required>
        <n-select
          v-model:value="localFormValue.community_id"
          :options="formattedCommunityOptions"
          placeholder="请选择或输入小区名称"
          :loading="loadingCommunities"
          filterable
          clearable
          remote
          :show-create-option="true"
          :create-option-label="(value) => `添加小区：${value}`"
          @create="handleCreateOption"
          :consistent-menu-width="false"
          @focus="handleCommunityFocus"
          @search="handleCommunitySearch"
          @update:value="handleCommunityChange"
        />
      </n-form-item>

      <n-form-item label="户型" path="layout">
        <div class="layout-inputs">
          <n-input-number
            v-model:value="layoutInfo.rooms"
            :min="1"
            :max="9"
            class="layout-input"
            placeholder="室"
            @update:value="handleLayoutChange"
          >
            <template #suffix>室</template>
          </n-input-number>
          <n-input-number
            v-model:value="layoutInfo.halls"
            :min="0"
            :max="9"
            class="layout-input"
            placeholder="厅"
            @update:value="handleLayoutChange"
          >
            <template #suffix>厅</template>
          </n-input-number>
        </div>
      </n-form-item>

      <n-form-item label="楼层" path="floor_info">
        <n-input
          v-model:value="localFormValue.floor_info"
          placeholder="例如: 中楼层/共33层"
          clearable
        />
      </n-form-item>

      <n-form-item label="面积" path="size" required>
        <n-input-number
          v-model:value="localFormValue.size"
          :min="0"
          :precision="2"
          placeholder="请输入面积"
          clearable
          style="width: 100%"
          @update:value="handleSizeChange"
        >
          <template #suffix>㎡</template>
        </n-input-number>
      </n-form-item>

      <n-form-item label="总价" path="total_price" required>
        <n-input-number
          v-model:value="localFormValue.total_price"
          :min="0"
          :precision="2"
          placeholder="请输入总价"
          clearable
          style="width: 100%"
          @update:value="handleSizeChange"
        >
          <template #suffix>万元</template>
        </n-input-number>
      </n-form-item>

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

      <n-form-item label="成交时间" path="deal_date" required>
        <n-date-picker
          v-model:value="localFormValue.deal_date"
          type="date"
          clearable
          style="width: 100%"
        />
      </n-form-item>
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
import { ref, reactive, watch, onMounted, onBeforeMount, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { communityApi } from '@/api/house'
import { useCityStore } from '@/stores/city'
import { debounce } from 'lodash-es'

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

// 添加户型信息状态
const layoutInfo = reactive({
  rooms: null,
  halls: null
})

// 监听外部表单数据变化
watch(() => props.formValue, (val) => {
  Object.assign(localFormValue, val)
  
  // 解析户型
  if (val.layout) {
    const matches = val.layout.match(/(\d+)室(\d+)厅/)
    if (matches) {
      layoutInfo.rooms = parseInt(matches[1])
      layoutInfo.halls = parseInt(matches[2])
    }
  }
}, { deep: true })

// 小区选择相关
const communityOptions = ref([])
const loadingCommunities = ref(false)
const selectedCommunity = ref(null)

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

// 格式化小区选项，添加区域信息到名称中
const formattedCommunityOptions = computed(() => {
  return communityOptions.value.map(item => ({
    label: `${item.label}（${item.region}）`,  // 名称中包含区域
    value: item.value,
    raw: item.raw
  }))
})

// 加载小区列表
const loadCommunities = async (keyword = '') => {
  loadingCommunities.value = true
  try {
    const res = await communityApi.list({
      name: keyword,
      city: localFormValue.city,
      page_size: 100
    })
    if (res.code === 200) {
      // 先过滤当前城市的小区
      const filteredItems = res.data.items.filter(item => 
        item.city === localFormValue.city
      )
      
      // 如果有关键词，进行本地过滤
      const items = keyword 
        ? filteredItems.filter(item => 
            item.name.toLowerCase().includes(keyword.toLowerCase()) ||
            item.region.toLowerCase().includes(keyword.toLowerCase())
          )
        : filteredItems

      communityOptions.value = items.map(item => ({
        label: item.name,
        value: item.id,
        region: item.region,
        area: item.area,
        raw: item
      }))
    }
  } catch (error) {
    console.error('Load community options error:', error)
    message.error('加载小区列表失败')
  } finally {
    loadingCommunities.value = false
  }
}

// 处理小区选择
const handleCommunityChange = (value, option) => {
  if (option?.raw) {
    // 选择已有小区
    selectedCommunity.value = option.raw
    localFormValue.community_id = option.value
  } else if (typeof value === 'string') {
    // 手动输入的情况
    selectedCommunity.value = null
    localFormValue.community_id = value
  } else {
    // 清空选择
    selectedCommunity.value = null
    localFormValue.community_id = null
  }
}

// 处理小区搜索
const handleCommunitySearch = debounce((query) => {
  loadCommunities(query)
}, 300)

// 处理小区选择框获得焦点
const handleCommunityFocus = () => {
  if (communityOptions.value.length === 0) {
    loadCommunities()
  }
}

// 监听城市变化
watch(() => localFormValue.city, (newCity) => {
  if (newCity) {
    localFormValue.community_id = null
    selectedCommunity.value = null
    communityOptions.value = []
    loadCommunities()  // 自动加载新城市的小区列表
  }
})

// 处理新增小区
const handleCreateCommunity = () => {
  message.info('请先在小区管理中添加小区信息')
  return false
}

// 处理面积变化，自动计算单价
const handleSizeChange = () => {
  if (localFormValue.total_price && localFormValue.size) {
    localFormValue.unit_price = Math.round((localFormValue.total_price * 10000) / localFormValue.size)
  }
}

// 处理户型变化
const handleLayoutChange = () => {
  if (layoutInfo.rooms) {
    const layout = `${layoutInfo.rooms}室${layoutInfo.halls || 0}厅`
    localFormValue.layout = layout
  } else {
    localFormValue.layout = null
  }
}

// 处理创建选项
const handleCreateOption = (value) => {
  // 手动输入的小区名称作为 community_id
  localFormValue.community_id = value
  // 清空选中的小区数据
  selectedCommunity.value = null
  return value
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
  // 清空户型信息
  Object.assign(layoutInfo, {
    rooms: null,
    halls: null
  })
  emit('cancel')
}

// 修改初始化逻辑
onMounted(() => {
  // 确保表单中有城市字段
  if (!localFormValue.city) {
    localFormValue.city = cityStore.currentCity
  }
})
</script>

<style scoped>
.n-form {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 16px;
}

.n-form-item {
  margin-bottom: 16px;
}

.n-input-number {
  width: 100% !important;
}

.layout-inputs {
  display: flex;
  gap: 12px;
  width: 100%;
}

.layout-input {
  flex: 1;
}

@media (max-width: 768px) {
  .layout-inputs {
    gap: 12px;
  }
  
  .layout-input {
    flex: 1;
  }
}

/* 添加全局样式来隐藏图标 */
:global(.n-dialog__icon) {
  display: none !important;
}
</style>

<style>
/* 如果 scoped 样式不生效，可以使用全局样式 */
.n-dialog__icon {
  display: none !important;
}
</style> 