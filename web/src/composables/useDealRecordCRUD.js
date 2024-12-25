import { ref, reactive } from 'vue'
import { useMessage } from 'naive-ui'
import { h } from 'vue'
import { NSpace, NButton, NPopconfirm, NTag } from 'naive-ui'
import { useCityStore } from '@/stores/city'

export function useDealRecordCRUD(api) {
  const message = useMessage()
  const loading = ref(false)
  const data = ref([])
  const cityStore = useCityStore()
  
  // 分页配置
  const pagination = reactive({
    page: 1,
    pageSize: 20,
    itemCount: 0,
    showSizePicker: true,
    pageSizes: [10, 20, 50, 100]
  })

  // 查询参数
  const queryParams = reactive({
    search_keyword: '',
    layout: undefined,
    floor_info: undefined,
    city: cityStore.currentCity,
    page: 1,
    page_size: 20,
    sort_by: 'deal_date',
    sort_direction: 'desc'
  })

  // 表格列定义
  const columns = [
    {
      title: '小区名称',
      key: 'community_name',
      width: 150
    },
    {
      title: '户型',
      key: 'layout',
      width: 100
    },
    {
      title: '楼层',
      key: 'floor_info',
      width: 120
    },
    {
      title: '面积(㎡)',
      key: 'size',
      width: 100
    },
    {
      title: '总价(万)',
      key: 'total_price',
      width: 100
    },
    {
      title: '单价(元/㎡)',
      key: 'unit_price',
      width: 120
    },
    {
      title: '成交时间',
      key: 'deal_date',
      width: 120
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (row) => {
        return h(
          NSpace,
          { justify: 'center', align: 'center' },
          {
            default: () => [
              h(
                NButton,
                {
                  size: 'small',
                  type: 'primary',
                  onClick: () => handleEdit(row)
                },
                { default: () => '编辑' }
              ),
              h(
                NPopconfirm,
                {
                  onPositiveClick: () => handleDelete(row)
                },
                {
                  default: () => '确认删除？',
                  trigger: () =>
                    h(
                      NButton,
                      {
                        size: 'small',
                        type: 'error'
                      },
                      { default: () => '删除' }
                    )
                }
              )
            ]
          }
        )
      }
    }
  ]

  // 加载数据
  const loadData = async () => {
    loading.value = true
    try {
      const res = await api.list({
        ...queryParams,
        page: pagination.page,
        page_size: pagination.pageSize,
        city: queryParams.city || cityStore.currentCity
      })
      if (res.code === 200) {
        data.value = res.data.items
        pagination.itemCount = res.data.total
        pagination.page = res.data.page
        pagination.pageSize = res.data.page_size
      } else {
        message.error(res.msg || '加载数据失败')
      }
    } catch (error) {
      console.error('Load data error:', error)
      message.error(error.response?.data?.detail || '加载数据失败')
    } finally {
      loading.value = false
    }
  }

  // 处理分页
  const handlePageChange = (page) => {
    pagination.page = page
    loadData()
  }

  const handlePageSizeChange = (pageSize) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadData()
  }

  // 处理排序
  const handleSorterChange = (sorter) => {
    if (sorter) {
      queryParams.sort_by = sorter.columnKey
      queryParams.sort_direction = sorter.order === 'ascend' ? 'asc' : 'desc'
    } else {
      queryParams.sort_by = 'deal_date'
      queryParams.sort_direction = 'desc'
    }
    loadData()
  }

  // 筛选条件
  const LAYOUT_OPTIONS = [
    { label: '一室', value: '1室' },
    { label: '二室', value: '2室' },
    { label: '三室', value: '3室' },
    { label: '四室及以上', value: '4室以上' }
  ]

  const FLOOR_OPTIONS = [
    { label: '低楼层', value: '低楼层' },
    { label: '中楼层', value: '中楼层' },
    { label: '高楼层', value: '高楼层' }
  ]

  const handleLayoutChange = (value) => {
    queryParams.layout = value
    loadData()
  }

  const handleFloorChange = (value) => {
    queryParams.floor_info = value
    loadData()
  }

  const handleReset = () => {
    Object.assign(queryParams, {
      search_keyword: '',
      layout: undefined,
      floor_info: undefined,
      city: cityStore.currentCity,
      sort_by: 'deal_date',
      sort_direction: 'desc'
    })
    pagination.page = 1
    loadData()
  }

  // 添加 Modal 相关状态
  const showModal = ref(false)
  const modalTitle = ref('')
  const modalLoading = ref(false)
  const formValue = ref({})

  // 删除处理
  const handleDelete = async (row) => {
    try {
      await api.delete(row.id)
      message.success('删除成功')
      loadData()
    } catch (error) {
      console.error('Delete error:', error)
      message.error('删除失败')
    }
  }

  // 添加编辑处理函数
  const handleEdit = (row) => {
    // 转换日期格式
    const formData = { ...row }
    if (formData.deal_date) {
      // 将日期字符串转换为时间戳
      formData.deal_date = new Date(formData.deal_date).getTime()
    }
    
    formValue.value = formData
    modalTitle.value = '编辑成交记录'
    showModal.value = true
  }

  // 修改提交处理函数
  const handleSubmit = async (data) => {
    try {
      modalLoading.value = true
      let res
      if (data.id) {
        // 编辑
        res = await api.update(data.id, data)
      } else {
        // 新增
        res = await api.create(data)
      }
      
      if (res.code === 200) {
        message.success(data.id ? '更新成功' : '创建成功')
        showModal.value = false
        loadData()
      } else {
        message.error(res.msg || '操作失败')
      }
    } catch (error) {
      console.error('Submit error:', error)
      message.error(error.response?.data?.detail || '操作失败')
    } finally {
      modalLoading.value = false
    }
  }

  return {
    loading,
    columns,
    data,
    pagination,
    queryParams,
    loadData,
    handlePageChange,
    handlePageSizeChange,
    handleSorterChange,
    handleLayoutChange,
    handleFloorChange,
    handleReset,
    LAYOUT_OPTIONS,
    FLOOR_OPTIONS,
    // 添加返回的 Modal 相关状态
    showModal,
    modalTitle,
    modalLoading,
    formValue,
    handleDelete,
    handleEdit,
    handleSubmit
  }
} 