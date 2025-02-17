import { ref, reactive, h } from 'vue'
import { useMessage, NSpace, NButton, NPopconfirm } from 'naive-ui'
import { useCityStore } from '@/stores/city'

export function useDealRecordCRUD(api) {
  const message = useMessage()
  const loading = ref(false)
  const showModal = ref(false)
  const modalTitle = ref('')
  const formParams = ref({})
  const cityStore = useCityStore()
  const communityOptions = ref([]) // 新增小区选项
  
  // 表格数据
  const data = ref([])
  
  // 分页配置
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
    onChange: (page) => handlePageChange(page),
    onUpdatePageSize: (pageSize) => handlePageSizeChange(pageSize)
  })

  // 查询参数
  const queryParams = reactive({
    search_keyword: '',
    layout: null,
    floor_info: null,
    sort_by: 'deal_date',
    sort_direction: 'desc'
  })

  // 修改预定义选项
  const CUSTOM_LAYOUT_OPTIONS = [
    { label: '一房', value: '一房', dbValue: '1室1厅' },
    { label: '二房', value: '二房', dbValue: '2室1厅' },
    { label: '三房', value: '三房', dbValue: '3室1厅' },
    { label: '四房', value: '四房', dbValue: '4室1厅' },
    { label: '其他', value: '其他', dbValue: '其他' }
  ]

  const FLOOR_OPTIONS = [
    { label: '低楼层', value: '低楼层' },
    { label: '中楼层', value: '中楼层' },
    { label: '高楼层', value: '高楼层' }
  ]

  // 表格列定义
  const columns = [
    { 
      title: '小区名称',
      key: 'community_name',
      width: 120,
      fixed: 'left',
      ellipsis: {
        tooltip: true
      }
    },
    { 
      title: '区域',
      key: 'region',
      width: 60
    },
    { 
      title: '商圈',
      key: 'area',
      width: 60
    },
    { 
      title: '户型',
      key: 'layout',
      width: 80
    },
    { 
      title: '建筑面积',
      key: 'size',
      width: 100,
      render: (row) => row.size ? `${row.size}㎡` : '-'
    },
    { 
      title: '楼层信息',
      key: 'floor_info',
      width: 120,
      render: (row) => {
        return row.floor_info || row.floor_info_display || '-'
      }
    },
    { 
      title: '成交价',
      key: 'total_price',
      width: 100,
      render: (row) => row.total_price ? `${row.total_price}万` : '-',
      sorter: true,
      sortOrder: queryParams.sort_by === 'total_price' ? queryParams.sort_direction : false
    },
    { 
      title: '成交时间',
      key: 'deal_date',
      width: 120,
      render: (row) => row.deal_date ? new Date(row.deal_date).toLocaleDateString() : '-',
      sorter: true,
      sortOrder: queryParams.sort_by === 'deal_date' ? queryParams.sort_direction : false
    },
    { 
      title: '单价',
      key: 'unit_price',
      width: 120,
      render: (row) => row.unit_price ? `${Math.round(row.unit_price)}元/㎡` : '-',
      sorter: true,
      sortOrder: queryParams.sort_by === 'unit_price' ? queryParams.sort_direction : false
    },
    { 
      title: '成交周期',
      key: 'deal_cycle',
      width: 90,
      render: (row) => row.deal_cycle ? `${row.deal_cycle}天` : '-'
    },
    { 
      title: '挂牌价',
      key: 'listing_price',
      width: 100,
      render: (row) => row.listing_price ? `${row.listing_price}万` : '-'
    },
    { 
      title: '房屋朝向',
      key: 'orientation',
      width: 90
    },
    { 
      title: '标签',
      key: 'tags',
      width: 120,
      ellipsis: {
        tooltip: true
      }
    },
    { 
      title: '位置',
      key: 'location',
      width: 120,
      ellipsis: {
        tooltip: true
      }
    },
    { 
      title: '装修',
      key: 'decoration',
      width: 80
    },
    { 
      title: '中介公司',
      key: 'agency',
      width: 120,
      ellipsis: {
        tooltip: true
      }
    },
    { 
      title: '数据来源',
      key: 'source',
      width: 90,
      render: (row) => {
        const sourceMap = {
          'store': '门店',
          'spider': '爬虫',
          'import': '导入'
        }
        return sourceMap[row.source] || row.source
      }
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      align: 'center',
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
                  onClick: () => handleEdit(row)
                },
                { default: () => '编辑' }
              ),
              h(
                NPopconfirm,
                {
                  onPositiveClick: () => handleDelete(row.id)
                },
                {
                  default: () => '确认删除？',
                  trigger: () => h(
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
    try {
      loading.value = true
      const params = {
        page: pagination.value.page,
        page_size: pagination.value.pageSize,
        city: queryParams.city || cityStore.currentCity,
        search_keyword: queryParams.search_keyword,
        layout: queryParams.layout,
        floor_info: queryParams.floor_info,
        sort_by: queryParams.sort_by || 'deal_date',
        sort_direction: queryParams.sort_direction || 'desc'
      }

      const cleanParams = Object.entries(params).reduce((acc, [key, value]) => {
        if (key === 'page' || key === 'page_size' || 
            (value !== undefined && value !== null && value !== '')) {
          acc[key] = value
        }
        return acc
      }, {})

      const res = await api.list(cleanParams)
      
      if (res?.code === 200 && res.data) {
        data.value = res.data.items
        pagination.value = {
          ...pagination.value,
          page: parseInt(res.data.page) || 1,
          pageSize: parseInt(res.data.page_size) || 10,
          total: parseInt(res.data.total) || 0,
          itemCount: parseInt(res.data.total) || 0,
          pageCount: Math.ceil((parseInt(res.data.total) || 0) / (parseInt(res.data.page_size) || 10))
        }
      }
    } catch (error) {
      message.error(error.message || '获取数据失败')
    } finally {
      loading.value = false
    }
  }

  // 处理新增
  const handleAdd = () => {

    modalTitle.value = '新增成交'
    formParams.value = {
      id: null,
      community_id: null,
      community_name: '',
      region: '',
      area: '',
      city: cityStore.currentCity,
      source: 'store',
      source_transaction_id: '',
      deal_date: null,
      total_price: null,
      unit_price: null,
      layout: '',
      size: null,
      floor_info: '',
      floor_number: null,
      total_floors: null,
      orientation: '',
      building_year: null,
      agency: '',
      deal_cycle: null,
      house_link: '',
      layout_image: '',
      listing_price: null,
      tags: '',
      location: '',
      decoration: '',
      building_structure: null
    }
    showModal.value = true
  }

  // 处理编辑
  const handleEdit = (row) => {
    modalTitle.value = '编辑成交'
    console.log('编辑行数据:', row)  // 添加调试日志
    
    // 处理日期格式
    let dealDate = null
    if (row.deal_date) {
      // 确保日期字符串格式正确
      const dateStr = row.deal_date.split('T')[0]  // 只取日期部分
      dealDate = new Date(dateStr).getTime()
    }

    // 处理户型数据
    let rooms = null
    let halls = null
    if (row.layout) {
      // 使用更宽松的正则表达式匹配户型
      const match = row.layout.match(/(\d+)\s*[室房]\s*(\d+)\s*[厅]?/)
      if (match) {
        rooms = parseInt(match[1])
        halls = parseInt(match[2])
      }
    }

    // 准备小区选项
    const communityOption = {
      label: row.community_name,
      value: row.community_id,
      region: row.region,
      area: row.area
    }
    communityOptions.value = [communityOption]

    // 确保所有数值类型字段都正确转换
    formParams.value = {
      id: row.id,
      community_id: row.community_id ? parseInt(row.community_id) : null,
      community_name: row.community_name || '',
      region: row.region || '',
      area: row.area || '',
      city: row.city || cityStore.currentCity,
      source: row.source || 'store',
      source_transaction_id: row.source_transaction_id || '',
      deal_date: dealDate,
      total_price: row.total_price ? parseFloat(row.total_price) : null,
      unit_price: row.unit_price ? parseFloat(row.unit_price) : null,
      listing_price: row.listing_price ? parseFloat(row.listing_price) : null,  // 挂牌价
      layout: row.layout || '',
      size: row.size ? parseFloat(row.size) : null,
      floor_info: row.floor_info || '',
      floor_number: row.floor_number ? parseInt(row.floor_number) : null,
      total_floors: row.total_floors ? parseInt(row.total_floors) : null,
      orientation: row.orientation || '',
      building_year: row.building_year ? parseInt(row.building_year) : null,
      agency: row.agency || '',
      deal_cycle: row.deal_cycle ? parseInt(row.deal_cycle) : null,
      house_link: row.house_link || '',  // 房源链接
      layout_image: row.layout_image || '',  // 户型图链接
      tags: row.tags || '',
      location: row.location || '',
      decoration: row.decoration || '',
      building_structure: row.building_structure || '',
      platform_house_id: row.source_transaction_id || '',  // 使用source_transaction_id
      // 户型相关
      rooms,
      halls
    }

    console.log('处理后的表单数据:', formParams.value)  // 添加调试日志
    showModal.value = true
  }

  // 处理删除
  const handleDelete = async (id) => {
    try {
      const res = await api.delete(id)
      if (res.code === 200) {
        message.success('删除成功')
        loadData()
      } else {
        throw new Error(res.msg || '删除失败')
      }
    } catch (error) {

      message.error(error.message || '删除失败')
    }
  }

  // Modal 提交处理
  const handleModalSubmit = async (formData) => {
    try {
      loading.value = true

      
      // 处理提交数据
      const processedData = {
        ...formData,
        city: cityStore.currentCity,
        deal_date: formData.deal_date ? new Date(formData.deal_date).toISOString().split('T')[0] : null,
        total_price: formData.total_price ? parseFloat(formData.total_price) : null,
        unit_price: formData.unit_price ? parseFloat(formData.unit_price) : null,
        size: formData.size ? parseFloat(formData.size) : null,
        building_year: formData.building_year ? parseInt(formData.building_year) : null,
        deal_cycle: formData.deal_cycle ? parseInt(formData.deal_cycle) : null,
        listing_price: formData.listing_price ? parseFloat(formData.listing_price) : null,
        community_id: formData.community_id ? parseInt(formData.community_id) : null,
        // 组合户型字符串
        layout: formData.rooms && formData.halls ? `${formData.rooms}室${formData.halls}厅` : formData.layout
      }

      const res = modalTitle.value.includes('新增')
        ? await api.create(processedData)
        : await api.update(processedData.id, processedData)

      if (res.code === 200) {
        message.success(res.msg || '操作成功')
        showModal.value = false
        loadData()
      } else {
        throw new Error(res.msg || '操作失败')
      }
    } catch (error) {

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
    pagination.value.page = page
    loadData()
  }

  const handlePageSizeChange = (pageSize) => {
    pagination.value.page = 1  // 重置到第一页
    pagination.value.pageSize = pageSize
    loadData()
  }

  // 排序处理
  const handleSorterChange = (sorter) => {
    if (sorter && sorter.columnKey) {
      queryParams.sort_by = sorter.columnKey
      queryParams.sort_direction = sorter.order === 'ascend' ? 'asc' : 'desc'
    } else {
      queryParams.sort_by = 'deal_date'
      queryParams.sort_direction = 'desc'
    }
    loadData()
  }

  // 修改筛选条件处理函数
  const handleLayoutChange = (value) => {
    queryParams.layout = queryParams.layout === value ? null : value
    pagination.value.page = 1  // 重置到第一页
    loadData()
  }

  const handleFloorChange = (value) => {
    if (queryParams.floor_info === value) {
      queryParams.floor_info = null
    } else {
      queryParams.floor_info = value
    }
    pagination.value.page = 1  // 重置到第一页
    loadData()
  }

  // 重置函数
  const handleReset = () => {
    Object.assign(queryParams, {
      search_keyword: '',
      layout: null,
      floor_info: null,
      sort_by: 'deal_date',
      sort_direction: 'desc'
    })
    pagination.value.page = 1  // 重置到第一页
    loadData()
  }

  // 添加城市切换处理函数
  const handleCityChange = (city) => {
    queryParams.city = city
    pagination.value.page = 1  // 重置到第一页
    loadData()  // 重新加载数据
  }

  // 表格配置
  const tableProps = {
    bordered: false,
    striped: true,
    scrollX: 1800,  // 设置固定的滚动宽度
    remote: true,
    size: 'small',
    rowClassName: () => 'table-row'
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
    communityOptions, // 新增小区选项
    CUSTOM_LAYOUT_OPTIONS,
    FLOOR_OPTIONS,
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
    handleFloorChange,
    handleReset,
    handleCityChange,
    tableProps
  }
} 