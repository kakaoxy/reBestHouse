import { ref, reactive, h } from 'vue'
import { useMessage, NSpace, NButton, NPopconfirm } from 'naive-ui'
import { useCityStore } from '@/stores/city'

export function useErshoufangCRUD(api) {
  const message = useMessage()
  const loading = ref(false)
  const showModal = ref(false)
  const modalTitle = ref('')
  const formParams = ref({})
  const cityStore = useCityStore()
  
  // 表格数据
  const data = ref([])
  const pagination = ref({
    page: 1,
    pageSize: 10,
    total: 0,
    pageSizes: [10, 20, 50],
    showSizePicker: true,
    prefix({ itemCount }) {
      return `共 ${itemCount} 条`
    },
    pageCount: 0,
    itemCount: 0,
    onChange: (page) => {
      handlePageChange(page)
    },
    onUpdatePageSize: (pageSize) => {
      handlePageSizeChange(pageSize)
    }
  })

  // 查询参数
  const queryParams = reactive({
    search_keyword: '',
    city: '',
    layout: null,
    orientation: null,
    floor: null,
    size_min: null,
    size_max: null,
    sort_by: 'listing_date',
    sort_direction: 'desc'
  })

  // 添加预定义的选项
  const CITY_OPTIONS = [
    { label: '上海', value: 'shanghai' },
    { label: '北京', value: 'beijing' },
    { label: '深圳', value: 'shenzhen' },
    { label: '广州', value: 'guangzhou' }
  ]
  
  const ORIENTATION_OPTIONS = [
    { label: '南', value: '朝南' },
    { label: '北', value: '朝北' },
    { label: '东', value: '朝东' },
    { label: '西', value: '朝西' },
    { label: '南北', value: '南北' }
  ]
  
  const FLOOR_OPTIONS = [
    { label: '低楼层', value: '低楼层' },
    { label: '中楼层', value: '中楼层' },
    { label: '高楼层', value: '高楼层' }
  ]
  
  const AREA_OPTIONS = [
    { label: '50以下', value: [0, 50] },
    { label: '50-70', value: [50, 70] },
    { label: '70-90', value: [70, 90] },
    { label: '90-110', value: [90, 110] },
    { label: '110-130', value: [110, 130] },
    { label: '130-150', value: [130, 150] },
    { label: '150以上', value: [150, null] }
  ]

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
      width: 120,
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
      width: 60
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
      title: '挂牌时间',
      key: 'listing_date',
      width: 150,
      sorter: true,
      render: (row) => row.listing_date?.split('T')[0] || '-'
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
    try {
      loading.value = true
      const params = {
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        city: queryParams.city || cityStore.currentCity,
        search_keyword: queryParams.search_keyword,
        layout: queryParams.layout,
        orientation: queryParams.orientation,
        floor: queryParams.floor,
        size_min: queryParams.size_min,
        size_max: queryParams.size_max,
        sort_by: queryParams.sort_by || 'listing_date',
        sort_direction: queryParams.sort_direction || 'desc'
      }
      console.log('Loading data with params:', params)
      
      // 移除空值参数，但保留分页参数
      const cleanParams = Object.entries(params).reduce((acc, [key, value]) => {
        if (key === 'page' || key === 'page_size' || 
            (value !== undefined && value !== null && value !== '')) {
          acc[key] = value
        }
        return acc
      }, {})
      
      const res = await api.list(cleanParams)
      
      if (res?.code === 200 && res.data) {
        data.value = (res.data.items || []).map(item => ({
          ...item,
          community_id: parseInt(item.community_id),
          floor_number: parseInt(item.floor_number) || null,
          total_floors: parseInt(item.total_floors) || null,
          total_price: Number(item.total_price),
          unit_price: Number(item.unit_price),
          size: Number(item.size),
          listing_date: item.listing_date || item.created_at
        }))
        
        // 更新分页信息
        pagination.value = {
          ...pagination.value,
          page: parseInt(res.data.page) || 1,
          pageSize: parseInt(res.data.page_size) || 10,
          total: parseInt(res.data.total) || 0,
          itemCount: parseInt(res.data.total) || 0,
          pageCount: Math.ceil((parseInt(res.data.total) || 0) / (parseInt(res.data.page_size) || 10))
        }
        console.log('Response data:', res.data)
      }
    } catch (error) {
      console.error('Load data error:', error)
      message.error(error.message || '获取数据失败')
    } finally {
      loading.value = false
    }
  }

  // 根据楼层号和总楼层判断楼层类型
  const getFloorType = (floorNumber, totalFloors) => {
    if (!floorNumber || !totalFloors) return null
    
    const floor = parseInt(floorNumber)
    const total = parseInt(totalFloors)
    
    if (isNaN(floor) || isNaN(total)) return null
    
    // 将楼层分为三等分
    const lowLimit = Math.ceil(total / 3)
    const highLimit = Math.ceil(total * 2 / 3)
    
    if (floor <= lowLimit) return '低楼层'
    if (floor <= highLimit) return '中楼层'
    return '高楼层'
  }

  // 处理新增
  const handleAdd = () => {
    modalTitle.value = '新增房源'
    formParams.value = {
      id: null,
      community_id: null,
      community_name: '',
      region: '',
      area: '',
      city: cityStore.currentCity,
      layout: null,
      floor_number: null,
      total_floors: null,
      orientation: null,
      size: null,
      total_price: null,
      data_source: 'store',
      ladder_ratio: '',
      mortgage_info: '',
      house_id: '',
      ke_code: '',
      house_link: ''
    }
    showModal.value = true
  }

  // 处理编辑
  const handleEdit = (row) => {
    modalTitle.value = '编辑房源'
    formParams.value = {
      id: row.id,
      community_id: parseInt(row.community_id),
      community_name: row.community_name || '',
      region: row.region || '',
      area: row.area || '',
      city: row.city || cityStore.currentCity,
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
    console.log('Page changed to:', page)
    pagination.value.page = page
    loadData()
  }

  const handlePageSizeChange = (pageSize) => {
    console.log('Page size changed to:', pageSize)
    pagination.value.page = 1
    pagination.value.pageSize = pageSize
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

  // 处理筛选条件变化
  const handleLayoutChange = (value) => {
    queryParams.layout = queryParams.layout === value ? null : value
    pagination.value.page = 1
    loadData()
  }

  const handleOrientationChange = (value) => {
    queryParams.orientation = queryParams.orientation === value ? null : value
    pagination.value.page = 1
    loadData()
  }

  const handleFloorChange = (value) => {
    queryParams.floor = queryParams.floor === value ? null : value
    pagination.value.page = 1
    loadData()
  }

  const handleAreaChange = (value) => {
    if (Array.isArray(value)) {
      queryParams.size_min = value[0]
      queryParams.size_max = value[1]
    } else {
      queryParams.size_min = null
      queryParams.size_max = null
    }
    pagination.value.page = 1
    loadData()
  }

  // 重置函数
  const handleReset = () => {
    Object.assign(queryParams, {
      search_keyword: '',
      layout: null,
      orientation: null,
      floor: null,
      size_min: null,
      size_max: null,
      sort_by: 'listing_date',
      sort_direction: 'desc'
    })
    pagination.value.page = 1
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
    handleAdd,
    handleEdit,
    handleDelete,
    handleModalSubmit,
    handleModalCancel,
    handlePageChange,
    handlePageSizeChange,
    handleSorterChange,
    handleLayoutChange,
    handleOrientationChange,
    handleFloorChange,
    handleAreaChange,
    ORIENTATION_OPTIONS,
    FLOOR_OPTIONS,
    AREA_OPTIONS,
    handleReset
  }
} 