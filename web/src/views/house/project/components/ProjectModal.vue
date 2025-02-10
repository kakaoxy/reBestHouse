<template>
  <n-modal
    :show="show"
    :title="title"
    preset="card"
    :style="{ width: '600px' }"
    @update:show="$emit('update:show', $event)"
  >
    <n-form
      ref="formRef"
      :model="localFormValue"
      :rules="rules"
      label-placement="left"
      label-width="100"
      require-mark-placement="right-hanging"
    >
      <!-- 选择商机 -->
      <n-form-item label="关联商机" path="opportunity_id">
        <n-select
          v-model:value="localFormValue.opportunity_id"
          :options="opportunityOptions"
          placeholder="请选择商机"
          :loading="loadingOpportunities"
          clearable
          filterable
          @focus="handleOpportunityFocus"
          @update:value="handleOpportunityChange"
        >
          <template #option="{ option }">
            <div class="opportunity-option">
              <div class="opportunity-info">
                <span class="community-name">{{ option.label }}</span>
                <span class="house-info">
                  {{ option.layout }} | {{ option.size }}㎡ | {{ option.floor }}
                </span>
              </div>
              <span class="owner-name">{{ option.owner }}</span>
            </div>
          </template>
        </n-select>
      </n-form-item>

      <!-- 房屋地址 -->
      <n-form-item label="房屋地址" path="address">
        <n-input
          v-model:value="localFormValue.address"
          placeholder="请输入具体房屋地址"
        />
      </n-form-item>

      <!-- 签约价格 -->
      <n-form-item label="签约价格" path="contract_price">
        <n-input-number
          v-model:value="localFormValue.contract_price"
          placeholder="请输入签约价格"
          :min="0"
          :precision="2"
          style="width: 100%"
        >
          <template #suffix>万元</template>
        </n-input-number>
      </n-form-item>

      <!-- 签约周期 -->
      <n-form-item label="签约周期" path="contract_period">
        <n-input-number
          v-model:value="localFormValue.contract_period"
          placeholder="请输入签约周期"
          :min="1"
          :precision="0"
          style="width: 100%"
        >
          <template #suffix>天</template>
        </n-input-number>
      </n-form-item>

      <!-- 签约人 -->
      <n-form-item label="签约人" path="signer">
        <n-select
          v-model:value="localFormValue.signer"
          :options="userOptions"
          placeholder="请选择签约人"
          :loading="loadingUsers"
          clearable
          @focus="loadUserOptions"
        />
      </n-form-item>

      <!-- 交房日期 -->
      <n-form-item label="交房日期" path="delivery_date">
        <n-date-picker
          v-model:value="localFormValue.delivery_date"
          type="date"
          clearable
          style="width: 100%"
        />
      </n-form-item>

      <!-- 当前阶段 -->
      <n-form-item label="当前阶段" path="current_phase">
        <n-select
          v-model:value="localFormValue.current_phase"
          :options="PHASE_OPTIONS"
          placeholder="请选择当前阶段"
        />
      </n-form-item>

      <!-- 装修公司 -->
      <n-form-item label="装修公司" path="decoration_company">
        <n-input
          v-model:value="localFormValue.decoration_company"
          placeholder="请输入装修公司名称"
        />
      </n-form-item>
    </n-form>

    <!-- 操作按钮 -->
    <template #footer>
      <n-space justify="end">
        <n-button @click="handleCancel">取消</n-button>
        <n-button
          type="primary"
          :loading="submitting"
          @click="handleSubmit"
        >
          确定
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useDepartmentStore } from '@/stores/department'
import { opportunityApi } from '@/api/house'
import { request } from '@/utils'

const props = defineProps({
  show: Boolean,
  title: String,
  formParams: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:show', 'submit', 'cancel'])
const departmentStore = useDepartmentStore() // 使用部门store

// 表单相关
const formRef = ref(null)
const submitting = ref(false)
const localFormValue = ref({ ...props.formParams })

// 商机选项相关
const opportunityOptions = ref([])
const loadingOpportunities = ref(false)

// 用户选项相关
const userOptions = ref([])
const loadingUsers = ref(false)

// 阶段选项
const PHASE_OPTIONS = [
  { label: '交房', value: 'delivery' },
  { label: '设计', value: 'design' },
  { label: '拆除', value: 'demolition' },
  { label: '水电', value: 'plumbing' },
  { label: '木瓦', value: 'carpentry' },
  { label: '油漆', value: 'painting' },
  { label: '安装', value: 'installation' },
  { label: '交付', value: 'completion' }
]

// 搜索参数
const searchParams = ref({
  city: departmentStore.currentDepartment || '',
  status: ['已评估', '已签约'],
  page_size: 100
})

// 监听部门变化
watch(
  () => departmentStore.currentDepartment,
  (newCity) => {
    if (newCity) {
      searchParams.value.city = newCity
      // 清空并重新加载商机列表
      opportunityOptions.value = []
      handleOpportunityFocus()
    }
  },
  { immediate: true } // 立即执行一次
)

// 加载商机列表
const handleOpportunityFocus = async () => {
  if (opportunityOptions.value.length > 0) return
  
  loadingOpportunities.value = true
  try {
    const res = await opportunityApi.list(searchParams.value)
    if (res.code === 200) {
      opportunityOptions.value = res.data.items.map(item => ({
        label: `${item.community_name}-${item.area}m²-${item.layout}-${item.floor}层-${item.total_price}万-${item.belonging_owner}`,
        value: item.id,
        raw: item
      }))
    }
  } finally {
    loadingOpportunities.value = false
  }
}

// 加载用户选项
const loadUserOptions = async () => {
  if (userOptions.value.length > 0) return
  
  loadingUsers.value = true
  try {
    const res = await request.get('/user/list', {
      params: {
        page: 1,
        page_size: 100,
        dept_id: undefined
      }
    })
    
    if (res.code === 200 && res.data) {
      userOptions.value = res.data.map(user => ({
        label: `${user.username}${user.dept?.name ? ` (${user.dept.name})` : ''}`,
        value: user.username
      }))
    }
  } catch (error) {
    window.$message.error('加载用户列表失败')
  } finally {
    loadingUsers.value = false
  }
}

// 表单验证规则
const rules = {
  opportunity_id: {
    required: true,
    type: 'number',
    message: '请选择关联商机',
    trigger: ['blur', 'change']
  },
  address: {
    required: true,
    message: '请输入房屋地址',
    trigger: 'blur'
  },
  contract_price: {
    required: true,
    type: 'number',
    message: '请输入签约价格',
    trigger: ['blur', 'change']
  },
  contract_period: {
    required: true,
    type: 'number',
    message: '请输入签约周期',
    trigger: ['blur', 'change']
  },
  signer: {
    required: true,
    message: '请选择签约人',
    trigger: 'change'
  },
  delivery_date: {
    required: false,
    type: 'number',
    trigger: ['blur', 'change'],
    validator: (rule, value) => {
      if (!value) return true
      return true
    }
  },
  current_phase: {
    required: true,
    message: '请选择当前阶段',
    trigger: 'change'
  },
  decoration_company: {
    required: false,
    message: '请输入装修公司名称',
    trigger: 'blur'
  }
}

// 处理商机选择变化
const handleOpportunityChange = (opportunityId) => {
  const selectedOpportunity = opportunityOptions.value.find(opt => opt.value === opportunityId)
  
  if (selectedOpportunity?.raw) {
    // 从选中的商机中获取小区名称等信息
    localFormValue.value = {
      ...localFormValue.value,
      opportunity_id: opportunityId,
      community_name: selectedOpportunity.raw.community_name, // 设置小区名称
      community_id: selectedOpportunity.raw.community_id,     // 设置小区ID
      // 可以添加其他需要的字段
    }
  }
}

// 修改提交处理
const handleSubmit = () => {
  formRef.value?.validate(async (errors) => {
    if (errors) {
      return
    }
    
    const selectedOpportunity = opportunityOptions.value.find(
      opt => opt.value === localFormValue.value.opportunity_id
    )
    
    if (!selectedOpportunity?.raw) {
      window.$message.error('商机信息获取失败')
      return
    }
    
    // 增加社区名称必填校验
    const submitData = {
      opportunity_id: localFormValue.value.opportunity_id,
      community_name: selectedOpportunity.raw.community_name || "", // 确保不为空
      address: localFormValue.value.address,
      contract_price: Number(localFormValue.value.contract_price), // 转换为数字
      contract_period: Number(localFormValue.value.contract_period),
      signer: localFormValue.value.signer,
      current_phase: localFormValue.value.current_phase,
      delivery_date: localFormValue.value.delivery_date 
        ? new Date(localFormValue.value.delivery_date).getTime() // 转换为时间戳
        : null,
      decoration_company: localFormValue.value.decoration_company
    }
    
    submitting.value = true
    try {
      emit('submit', submitData)
    } catch (error) {
      console.error('Submit error:', error)
    } finally {
      submitting.value = false
    }
  })
}

// 修改初始化表单值
const initFormValue = () => {
  localFormValue.value = {
    opportunity_id: null,
    community_id: null,
    community_name: '',
    address: '',
    contract_price: null,
    contract_period: null,
    signer: '',
    delivery_date: undefined,
    current_phase: 'delivery',
    decoration_company: ''  // 新增字段
  }
}

// 在组件挂载时初始化表单
onMounted(() => {
  initFormValue()
})

// 修改表单参数监听
watch(() => props.formParams, (newVal) => {
  if (Object.keys(newVal).length > 0) {
    localFormValue.value = { ...newVal }
  } else {
    initFormValue()
  }
}, { deep: true })

// 处理取消
const handleCancel = () => {
  emit('cancel')
  emit('update:show', false)
}
</script>

<style scoped>
.opportunity-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
}

.opportunity-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.community-name {
  font-weight: 500;
  color: #333;
}

.house-info {
  font-size: 12px;
  color: #666;
}

.owner-name {
  color: #1890ff;
  font-size: 13px;
}

:deep(.n-input-number-suffix) {
  color: #666;
  margin-left: 4px;
}
</style>