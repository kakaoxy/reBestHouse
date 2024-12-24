import { ref, reactive } from 'vue'
import { useMessage } from 'naive-ui'

export function useCommunityModal(api) {
  const message = useMessage()
  const modalVisible = ref(false)
  const modalTitle = ref('')
  const modalLoading = ref(false)
  const formRef = ref(null)

  const formParams = reactive({
    name: '',
    region: '',
    area: '',
    address: '',
    building_type: null,
    property_rights: [],
    total_houses: undefined,
    building_year: undefined
  })

  const rules = {
    name: {
      required: true,
      message: '请输入小区名称',
      trigger: ['blur', 'input']
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
    },
    address: {
      required: true,
      message: '请输入详细地址',
      trigger: ['blur', 'input']
    },
    building_type: {
      required: true,
      message: '请选择建筑类型',
      trigger: 'change'
    },
    property_rights: {
      type: 'array',
      required: true,
      message: '请选择交易权属',
      trigger: 'change'
    },
    total_houses: {
      type: 'number',
      required: true,
      message: '请输入房屋总数',
      trigger: 'change'
    },
    building_year: {
      type: 'number',
      required: true,
      message: '请输入建筑年代',
      trigger: 'change'
    }
  }

  const resetForm = () => {
    Object.assign(formParams, {
      name: '',
      region: '',
      area: '',
      address: '',
      building_type: null,
      property_rights: [],
      total_houses: undefined,
      building_year: undefined
    })
    formRef.value?.restoreValidation()
  }

  const handleAdd = () => {
    modalTitle.value = '新增小区'
    resetForm()
    modalVisible.value = true
  }

  const handleEdit = (row) => {
    modalTitle.value = '编辑小区'
    Object.assign(formParams, row)
    modalVisible.value = true
  }

  const handleSubmit = async () => {
    try {
      await formRef.value?.validate()
      modalLoading.value = true

      const submitData = { ...formParams }
      if (Array.isArray(submitData.property_rights)) {
        submitData.property_rights = submitData.property_rights.join(',')
      }

      const res = modalTitle.value.includes('新增')
        ? await api.create(submitData)
        : await api.update(submitData.id, submitData)

      if (res.code === 200) {
        message.success(res.msg || '操作成功')
        modalVisible.value = false
        return true
      } else {
        message.error(res.msg || '操作失败')
        return false
      }
    } catch (error) {
      console.error('Submit error:', error)
      message.error('表单验证失败')
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