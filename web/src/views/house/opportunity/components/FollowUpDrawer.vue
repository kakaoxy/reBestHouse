<template>
  <n-drawer
    :show="show"
    @update:show="emit('update:show', $event)"
    :width="640"
    placement="right"
  >
    <n-drawer-content 
      title="商机跟进"
      :native-scrollbar="false"
    >
      <!-- 跟进表单 -->
      <n-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        :size="'small'"
        label-placement="left"
        label-width="100"
      >
        <n-form-item label="跟进时间" path="follow_up_time">
          <n-date-picker
            v-model:value="formData.follow_up_time"
            type="datetime"
            clearable
            :is-date-disabled="disableFutureDate"
            style="width: 100%"
            @update:value="handleDateUpdate"
          />
        </n-form-item>

        <n-form-item label="跟进方式" path="follow_up_method">
          <n-select
            v-model:value="formData.follow_up_method"
            :options="methodOptions"
            clearable
          />
        </n-form-item>

        <n-form-item label="跟进内容" path="follow_up_content">
          <n-input
            v-model:value="formData.follow_up_content"
            type="textarea"
            placeholder="请输入跟进内容"
          />
        </n-form-item>

        <n-form-item
          v-if="isAdmin"
          label="授权价格"
          path="authorized_price"
        >
          <n-input-number
            v-model:value="formData.authorized_price"
            clearable
            :min="0"
            :precision="2"
            style="width: 100%"
          >
            <template #suffix>
              万元
            </template>
          </n-input-number>
        </n-form-item>

        <n-form-item
          v-if="formData.adjust_reason !== null"
          label="调价原因"
          path="adjust_reason"
        >
          <n-input
            v-model:value="formData.adjust_reason"
            type="textarea"
            placeholder="请输入调价原因"
          />
        </n-form-item>
      </n-form>

      <!-- 分隔线 -->
      <n-divider>跟进历史</n-divider>

      <!-- 跟进历史 -->
      <n-timeline>
        <!-- 新增线索节点 -->
        <n-timeline-item
          type="success"
          title="新增商机"
          :time="formatDate(opportunityData?.created_at)"
        />

        <!-- 已评估节点 -->
        <n-timeline-item
          :type="lastEvaluatedRecord ? 'success' : 'default'"
          title="已评估"
          :time="lastEvaluatedRecord ? formatDate(lastEvaluatedRecord.created_at) : ''"
          :content="lastEvaluatedRecord ? `授权价格: ${lastEvaluatedRecord.authorized_price}万` : ''"
        />

        <!-- 持续跟进节点 -->
        <n-timeline-item
          :type="lastFollowUpRecord ? 'success' : 'default'"
          title="持续跟进"
          :time="lastFollowUpRecord ? formatDate(lastFollowUpRecord.created_at) : ''"
          :content="lastFollowUpRecord ? lastFollowUpRecord.follow_up_content : ''"
        />

        <!-- 已签约/已放弃节点 -->
        <n-timeline-item
          :type="finalStatusRecord ? 'success' : 'default'"
          :title="finalStatus"
          :time="finalStatusRecord ? formatDate(finalStatusRecord.created_at) : ''"
        />
      </n-timeline>

      <template #footer>
        <n-space justify="end">
          <n-button @click="handleCancel">取消</n-button>
          <n-button
            type="primary"
            :loading="loading"
            @click="handleSubmit"
          >
            保存
          </n-button>
        </n-space>
      </template>
    </n-drawer-content>
  </n-drawer>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { opportunityApi } from '@/api/house'
import { formatDate, formatDateTime } from '@/utils'
import { useUserStore } from '@/store/modules/user'
import { useMessage } from 'naive-ui'

const $message = useMessage()
const userStore = useUserStore()

// 判断用户角色
const isAdmin = computed(() => {
  const roles = userStore.role
  return roles?.includes('admin') || roles?.includes('manager') || userStore.isSuperUser
})

const props = defineProps({
  show: Boolean,
  opportunityId: [String, Number],
  opportunityData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:show', 'success'])

// 禁用未来日期
const disableFutureDate = (ts) => {
  return ts > Date.now()
}

// 处理日期更新
const handleDateUpdate = (value) => {
  formData.value.follow_up_time = value
}

// 表单数据
const formRef = ref(null)
const formData = ref({
  opportunity_id: null,
  follow_up_time: new Date(),
  follow_up_method: '电话',
  follow_up_content: '',
  authorized_price: null,
  adjust_reason: null,
  follow_up_result: '继续跟进'
})

// 监听授权价格变化
watch(() => formData.value.authorized_price, async (newPrice) => {
  if (!newPrice || !isAdmin.value) return
  
  // 获取最新的跟进记录
  const res = await opportunityApi.getFollowUps(props.opportunityId)
  if (res.code === 200 && res.data.length > 0) {
    const lastRecord = res.data[0]
    // 比较价格是否调整
    if (lastRecord.authorized_price && newPrice !== lastRecord.authorized_price) {
      // 自动设置调价原因输入框
      formData.value.adjust_reason = ''
    }
  }
})

// 选项数据
const methodOptions = [
  { label: '电话', value: '电话' },
  { label: '微信', value: '微信' },
  { label: '面谈', value: '面谈' }
]

const resultOptions = [
  { label: '继续跟进', value: '继续跟进' },
  { label: '已评估', value: '已评估' },
  { label: '已签约', value: '已签约' },
  { label: '已放弃', value: '已放弃' }
]

// 表单验证规则
const rules = {
  follow_up_time: {
    required: true,
    message: '请选择跟进时间',
    trigger: ['blur', 'change'],
    validator: (rule, value) => {
      if (!value) {
        return new Error('请选择跟进时间')
      }
      return true
    }
  },
  follow_up_method: {
    required: true,
    message: '请选择跟进方式',
    trigger: ['blur', 'change']
  },
  follow_up_content: {
    required: true,
    message: '请输入跟进内容',
    trigger: ['blur', 'input']
  },
  adjust_reason: {
    required: true,
    message: '请输入调价原因',
    trigger: ['blur', 'input'],
    validator: (rule, value) => {
      // 只在需要调价原因时验证
      if (formData.value.adjust_reason !== null && !value) {
        return new Error('请输入调价原因')
      }
      return true
    }
  }
}

// 跟进记录列表
const followUps = ref([])
const loading = ref(false)

// 获取跟进记录
const loadFollowUps = async () => {
  if (!props.opportunityId) return
  try {
    const res = await opportunityApi.getFollowUps(props.opportunityId)
    if (res.code === 200) {
      followUps.value = res.data
    }
  } catch (error) {
    console.error('加载跟进记录失败:', error)
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    loading.value = true
    
    const submitData = { ...formData.value }
    submitData.opportunity_id = props.opportunityId
    
    // 格式化日期
    if (submitData.follow_up_time instanceof Date) {
      submitData.follow_up_time = formatDateTime(submitData.follow_up_time)
    }
    
    // 如果是管理员且填写了授权价格,更新商机状态
    if (isAdmin.value && submitData.authorized_price) {
      if (submitData.follow_up_result === '继续跟进') {
        submitData.follow_up_result = '已评估'
      }
    }
    
    const res = await opportunityApi.createFollowUp(submitData)
    if (res.code === 200) {
      $message.success('创建成功')
      emit('success')
      handleCancel()
    }
  } catch (error) {
    console.error('创建跟进记录失败:', error)
  } finally {
    loading.value = false
  }
}

// 取消
const handleCancel = () => {
  formRef.value?.restoreValidation()
  formData.value = {
    opportunity_id: null,
    follow_up_time: new Date(),
    follow_up_method: '电话',
    follow_up_content: '',
    authorized_price: null,
    adjust_reason: null,
    follow_up_result: '继续跟进'
  }
  emit('update:show', false)
}

// 获取时间轴类型
const getTimelineType = (result) => {
  switch (result) {
    case '已签约':
      return 'success'
    case '已放弃':
      return 'error'
    case '已评估':
      return 'info'
    default:
      return 'default'
  }
}

// 处理时间轴显示顺序
const sortedFollowUps = computed(() => {
  if (!followUps.value.length) return []
  
  // 按时间倒序排序
  return [...followUps.value].sort((a, b) => {
    return new Date(b.follow_up_time) - new Date(a.follow_up_time)
  })
})

// 监听显示状态
watch(
  () => props.show,
  (newVal) => {
    if (newVal && props.opportunityId) {
      loadFollowUps()
    }
  }
)

onMounted(() => {
  if (props.show && props.opportunityId) {
    loadFollowUps()
  }
})

// 获取最后一次评估记录
const lastEvaluatedRecord = computed(() => {
  return sortedFollowUps.value.find(item => item.follow_up_result === '已评估')
})

// 获取最后一次跟进记录
const lastFollowUpRecord = computed(() => {
  return sortedFollowUps.value.find(item => item.follow_up_result === '继续跟进')
})

// 获取最终状态记录
const finalStatusRecord = computed(() => {
  return sortedFollowUps.value.find(item => 
    item.follow_up_result === '已签约' || item.follow_up_result === '已放弃'
  )
})

// 最终状态
const finalStatus = computed(() => {
  return finalStatusRecord.value?.follow_up_result || '未完成'
})

// 最终状态类型
const finalStatusType = computed(() => {
  if (!finalStatusRecord.value) return 'default'
  return finalStatusRecord.value.follow_up_result === '已签约' ? 'success' : 'error'
})
</script>

<style scoped>
.follow-up-item {
  padding: 12px 0;
  border-radius: 4px;
}

.follow-up-header {
  display: flex;
  gap: 12px;
  color: #666;
  font-size: 12px;
  margin-bottom: 8px;
  align-items: center;
}

.follow-up-header span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.follow-up-content {
  margin: 8px 0;
  white-space: pre-wrap;
  line-height: 1.6;
  color: #333;
}

.follow-up-price {
  font-size: 12px;
  margin-top: 8px;
  display: flex;
  align-items: center;
}

/* 分隔线样式 */
:deep(.n-divider) {
  margin: 24px 0;
}
</style> 