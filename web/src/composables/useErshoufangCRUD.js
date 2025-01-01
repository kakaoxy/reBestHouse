import { ref, reactive, h } from 'vue'
import { useMessage, NSpace, NButton, NPopconfirm } from 'naive-ui'

export function useErshoufangCRUD(api) {
  const message = useMessage()
  const loading = ref(false)
  const showModal = ref(false)
  const modalTitle = ref('')
  const formParams = ref({})
  
  // 表格数据
  const data = ref([])
  const pagination = reactive({
    page: 1,
    pageSize: 10,
    total: 0,
    showSizePicker: true,
    pageSizes: [10, 20, 30, 40]
  })

  // 查询参数
  const queryParams = reactive({
    city: '',
    search_keyword: '',
    layout: undefined,
    orientation: undefined,
    floor: undefined,
    size_range: undefined,
    sort_by: 'created_at',
    sort_direction: 'desc'
  })

  // 表格列定义
  const columns = [
    { 
      title: '小区',
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
      key: 'floor',
      width: 100,
      render: (row) => {
        return row.floor || (row.floor_number && row.total_floors 
          ? `${row.floor_number}/${row.total_floors}层`
          : row.floor_number 
            ? `${row.floor_number}层` 
            : row.total_floors 
              ? `共${row.total_floors}层`
              : '暂无楼层信息')
      }
    },
    { 
      title: '朝向',
      key: 'orientation',
      width: 100
    },
    { 
      title: '面积(㎡)',
      key: 'size',
      width: 100,
      align: 'right',
      render: (row) => row.size?.toFixed(2) || '-'
    },
    { 
      title: '总价(万)',
      key: 'total_price',
      width: 100,
      align: 'right',
      sorter: true,
      render: (row) => row.total_price?.toFixed(2) || '-'
    },
    { 
      title: '单价(元/㎡)',
      key: 'unit_price',
      width: 120,
      align: 'right',
      sorter: true,
      render: (row) => row.unit_price?.toFixed(0) || '-'
    },
    { 
      title: '创建时间',
      key: 'created_at',
      width: 150,
      sorter: true,
      render: (row) => row.created_at?.split('T')[0] || '-'
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      fixed: 'right',
      render: (row) => {
        return h(NSpace, {}, {
          default: () => [
            h(NButton, {
              size: 'small',
              onClick: () => handleEdit(row)
            }, { default: () => '编辑' }),
            h(NPopconfirm, {
              onPositiveClick: () => handleDelete(row.id)
            }, {
              default: () => '确认删除？',
              trigger: () => h(NButton, {
                size: 'small',
                type: 'error'
              }, { default: () => '删除' })
            })
          ]
        })
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
        page_size: pagination.pageSize
      })
      if (res?.code === 200 && Array.isArray(res.data?.items)) {
        data.value = res.data.items.map(item => ({
          ...item,
          community_id: parseInt(item.community_id),
          floor_number: item.floor_number ? parseInt(item.floor_number) : null,
          total_floors: item.total_floors ? parseInt(item.total_floors) : null,
          created_at: item.created_at || null,
          total_price: Number(item.total_price),
          unit_price: Number(item.unit_price),
          size: Number(item.size)
        }))
        pagination.total = res.data.total
      } else {
        console.error('Invalid response format:', res)
        message.error(res?.msg || '数据格式错误')
      }
    } catch (error) {
      console.error('Load data error:', {
        response: error?.response?.data,
        error: error,
        message: error?.message
      })
      message.error('加载数据失败')
    } finally {
      loading.value = false
    }
  }

  // 统一的筛选条件处理函数
  const handleFilterChange = (type, value) => {
    queryParams[type] = value
    pagination.page = 1
    loadData()
  }

  // 处理新增
  const handleAdd = () => {
    modalTitle.value = '新增房源'
    formParams.value = {
      community_id: null,
      community_name: '',
      region: '',
      area: '',
      layout: null,
      floor_number: null,
      total_floors: null,
      orientation: null,
      size: null,
      total_price: null,
      data_source: 'store',
      city: queryParams.city
    }
    showModal.value = true
  }

  // 处理编辑
  const handleEdit = (row) => {
    if (!row) {
      console.error('No row data provided for edit')
      return
    }
    console.log('Original row data:', row)
    modalTitle.value = '编辑房源'
    formParams.value = {
      id: row.id,
      community_id: row.community_id ? parseInt(row.community_id) : null,
      community_name: row.community_name || '',
      region: row.region || '',
      area: row.area || '',
      city: row.city || '',
      layout: row.layout || null,
      floor_number: row.floor_number ? parseInt(row.floor_number) : null,
      total_floors: row.total_floors ? parseInt(row.total_floors) : null,
      floor: row.floor || '',
      orientation: row.orientation || null,
      size: row.size ? parseFloat(row.size) : null,
      total_price: row.total_price ? parseFloat(row.total_price) : null,
      unit_price: row.unit_price ? parseFloat(row.unit_price) : null,
      data_source: row.data_source || 'store',
      ladder_ratio: row.ladder_ratio || '',
      mortgage_info: row.mortgage_info || '',
      house_id: row.house_id || '',
      ke_code: row.ke_code || '',
      house_link: row.house_link || ''
    }
    console.log('Processed form data:', formParams.value)
    showModal.value = true
  }

  // 处理删除
  const handleDelete = async (id) => {
    try {
      const res = await api.delete(id)
      if (res.code === 200) {
        message.success('删除成功')
        loadData()
      }
    } catch (error) {
      message.error('删除失败')
    }
  }

  // Modal 提交处理
  const handleModalSubmit = async (formData) => {
    try {
      loading.value = true
      const res = modalTitle.value.includes('新增')
        ? await api.create(formData)
        : await api.update(formData.id, formData)

      if (res.code === 200) {
        message.success(res.msg || '操作成功')
        showModal.value = false
        loadData()
      } else {
        message.error(res.msg || '操作失败')
      }
    } catch (error) {
      console.error('Submit error:', error)
      message.error(error.message || '操作失败')
    } finally {
      loading.value = false
    }
  }

  // Modal 取消处理
  const handleModalCancel = () => {
    showModal.value = false
  }

  // 分页处理
  const handlePageChange = (page) => {
    pagination.page = page
    loadData()
  }

  const handlePageSizeChange = (pageSize) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadData()
  }

  // 排序处理
  const handleSorterChange = (sorter) => {
    if (sorter) {
      queryParams.sort_by = sorter.key
      queryParams.sort_direction = sorter.order === 'ascend' ? 'asc' : 'desc'
    } else {
      queryParams.sort_by = 'created_at'
      queryParams.sort_direction = 'desc'
    }
    loadData()
  }

  return {
    loading,
    columns,
    data,
    pagination,
    queryParams,
    showModal,
    modalTitle,
    formParams,
    loadData,
    handleFilterChange,
    handleAdd,
    handleEdit,
    handleDelete,
    handleModalSubmit,
    handleModalCancel,
    handlePageChange,
    handlePageSizeChange,
    handleSorterChange
  }
} 