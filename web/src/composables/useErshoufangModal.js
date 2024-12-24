import { ref, reactive, nextTick } from 'vue'
import { useMessage } from 'naive-ui'

export function useErshoufangModal(api) {
  const message = useMessage()
  const modalVisible = ref(false)
  const modalTitle = ref('')
  const modalLoading = ref(false)
  const formRef = ref(null)

  const formParams = reactive({
    community_id: null,
    community_name: '',
    region: '',
    area: '',
    layout: '',
    floor_number: null,
    total_floors: null,
    orientation: null,
    size: null,
    total_price: null,
    unit_price: null,
    listing_date: null,
    data_source: null
  })

  const rules = {
    community_name: {
      required: true,
      message: '请选择或输入小区名称',
      trigger: ['blur', 'input', 'change']
    },
    layout: {
      required: true,
      message: '请输入户型',
      trigger: ['blur', 'input']
    },
    floor_number: {
      required: true,
      type: 'number',
      message: '请输入楼层',
      trigger: ['blur', 'change']
    },
    total_floors: {
      required: true,
      type: 'number',
      message: '请输入总楼层',
      trigger: ['blur', 'change']
    },
    orientation: {
      required: true,
      message: '请选择朝向',
      trigger: ['blur', 'change']
    },
    size: {
      required: true,
      type: 'number',
      message: '请输入面积',
      trigger: ['blur', 'change']
    },
    total_price: {
      required: true,
      type: 'number',
      message: '请输入总价',
      trigger: ['blur', 'change']
    },
    data_source: {
      required: true,
      message: '请选择信息来源',
      trigger: ['blur', 'change']
    }
  }

  const resetForm = () => {
    Object.assign(formParams, {
      community_id: null,
      community_name: '',
      region: '',
      area: '',
      layout: '',
      floor_number: null,
      total_floors: null,
      orientation: null,
      size: null,
      total_price: null,
      unit_price: null,
      listing_date: null,
      data_source: null
    })
    formRef.value?.restoreValidation()
  }

  const handleAdd = () => {
    modalTitle.value = '新增房源'
    resetForm()
    modalVisible.value = true
  }

  const handleEdit = (row) => {
    modalTitle.value = '编辑房源'
    Object.assign(formParams, row)
    modalVisible.value = true
  }

  const handleSubmit = async () => {
    try {
      modalLoading.value = true
      const res = modalTitle.value.includes('新增')
        ? await api.create(formParams)
        : await api.update(formParams.id, formParams)

      if (res.code === 200) {
        message.success(res.msg || '操作成功')
        return true
      } else {
        message.error(res.msg || '操作失败')
        return false
      }
    } catch (error) {
      console.error('Submit error:', error)
      message.error(error.message || '操作失败')
      return false
    } finally {
      modalLoading.value = false
    }
  }

  const handleDelete = async (row) => {
    try {
      const res = await api.delete(row.id)
      if (res.code === 200) {
        message.success(res.msg || '删除成功')
        return true
      } else {
        message.error(res.msg || '删除失败')
        return false
      }
    } catch (error) {
      console.error('Delete error:', error)
      message.error('删除失败')
      return false
    }
  }

  return {
    modalVisible,
    modalTitle,
    modalLoading,
    formRef,
    formParams,
    rules,
    handleAdd,
    handleEdit,
    handleDelete,
    handleSubmit,
    resetForm
  }
} 