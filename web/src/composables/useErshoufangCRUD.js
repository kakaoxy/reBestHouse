import { ref, reactive } from 'vue'
import { useMessage } from 'naive-ui'
import { h } from 'vue'
import { NSpace, NButton, NPopconfirm } from 'naive-ui'

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
  { label: '150以上', value: [150, 999999] }
]

export function useErshoufangCRUD(api) {
  const message = useMessage()
  const loading = ref(false)
  const data = ref([])
  const showModal = ref(false)
  const modalTitle = ref('')
  const formParams = ref({})

  // 分页配置
  const pagination = reactive({
    page: 1,
    pageSize: 20,
    itemCount: 0,
    showSizePicker: true,
    pageSizes: [10, 20, 50, 100],
    prefix({ itemCount }) {
      return `共 ${itemCount} 条`
    }
  })

  // 查询参数
  const queryParams = reactive({
    search_keyword: '',
    sort_by: 'listing_date',
    sort_direction: 'desc',
    page: 1,
    page_size: 20
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
      width: 100
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
      align: 'right'
    },
    { 
      title: '总价(万)',
      key: 'total_price',
      width: 100,
      align: 'right',
      sorter: true
    },
    { 
      title: '单价(元/㎡)',
      key: 'unit_price',
      width: 120,
      align: 'right',
      sorter: true
    },
    { 
      title: '挂牌时间',
      key: 'listing_date',
      width: 150,
      sorter: true
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
              onPositiveClick: () => handleDelete(row)
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
      // 只发送有值的参数，不包含 city
      const params = Object.entries({
        ...queryParams,
        page: pagination.page,
        page_size: pagination.pageSize,
        layout: queryParams.layout || undefined,
        orientation: queryParams.orientation || undefined,
        floor: queryParams.floor || undefined,
        size_min: queryParams.size_min || undefined,
        size_max: queryParams.size_max || undefined,
        // 如果选择了城市才发送
        ...(queryParams.city ? { city: queryParams.city } : {})
      }).reduce((acc, [key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          acc[key] = value
        }
        return acc
      }, {})

      console.log('Loading data with params:', params)
      const res = await api.list(params)
      console.log('API response:', res)

      if (res.code === 200 && res.data) {
        if (Array.isArray(res.data.items)) {
          data.value = res.data.items.map(item => ({
            ...item,
            listing_date: item.listing_date ? item.listing_date.split('T')[0] : null,
            total_price: Number(item.total_price),
            unit_price: Number(item.unit_price),
            size: Number(item.size),
            floor: item.floor || (item.floor_number && item.total_floors 
              ? `${item.floor_number}/${item.total_floors}层`
              : item.floor_number 
                ? `${item.floor_number}层` 
                : item.total_floors 
                  ? `共${item.total_floors}层`
                  : '暂无楼层信息')
          }))
        } else {
          data.value = []
        }
        
        pagination.itemCount = res.data.total || 0
        console.log('Processed data:', {
          items: data.value,
          total: pagination.itemCount,
          page: pagination.page,
          pageSize: pagination.pageSize
        })
      } else {
        message.error(res.msg || '获取数据失败')
      }
    } catch (error) {
      console.error('Failed to load data:', error)
      message.error('获取数据失败')
    } finally {
      loading.value = false
    }
  }

  // 页码改变
  const handlePageChange = (page) => {
    pagination.page = page
    loadData()
  }

  // 每页条数改变
  const handlePageSizeChange = (pageSize) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    loadData()
  }

  // 排序改变
  const handleSorterChange = (sorter) => {
    if (sorter) {
      queryParams.sort_by = sorter.columnKey
      queryParams.sort_direction = sorter.order === 'ascend' ? 'asc' : 'desc'
    } else {
      queryParams.sort_by = 'listing_date'
      queryParams.sort_direction = 'desc'  // 默认按挂牌时间降序
    }
    loadData()
  }

  // 处理筛选条件变化
  const handleLayoutChange = (value) => {
    queryParams.layout = queryParams.layout === value ? null : value
    loadData()
  }

  const handleOrientationChange = (value) => {
    queryParams.orientation = queryParams.orientation === value ? null : value
    loadData()
  }

  const handleFloorChange = (value) => {
    queryParams.floor = queryParams.floor === value ? null : value
    loadData()
  }

  const handleAreaChange = (value) => {
    if (value) {
      const [min, max] = value
      queryParams.size_min = min
      queryParams.size_max = max
    } else {
      queryParams.size_min = null
      queryParams.size_max = null
    }
    loadData()
  }

  // 重置查询条件
  const handleReset = () => {
    Object.assign(queryParams, {
      search_keyword: '',
      layout: undefined,
      orientation: undefined,
      floor: undefined,
      size_min: undefined,
      size_max: undefined,
      sort_by: 'listing_date',
      sort_direction: 'desc'
    })
    pagination.page = 1
    loadData()
  }

  // 初始化时设置默认排序
  queryParams.sort_by = 'listing_date'
  queryParams.sort_direction = 'desc'

  // 修改编辑处理函数
  const handleEdit = (row) => {
    modalTitle.value = '编辑房源'
    // 深拷贝原始数据
    formParams.value = {
      id: row.id,
      community_id: row.community_id,
      community_name: row.community_name,
      region: row.region,
      area: row.area,
      layout: row.layout,
      floor_number: row.floor_number || null,
      total_floors: row.total_floors || null,
      orientation: row.orientation,
      size: row.size,
      total_price: row.total_price,
      unit_price: row.unit_price,
      ladder_ratio: row.ladder_ratio,
      mortgage_info: row.mortgage_info,
      house_id: row.house_id,
      ke_code: row.ke_code,
      house_link: row.house_link,
      data_source: row.data_source || 'store',
      listing_date: row.listing_date
    }
    showModal.value = true
    console.log('Edit form data:', formParams.value)
  }

  // 添加删除处理函数
  const handleDelete = async (row) => {
    try {
      loading.value = true
      const res = await api.delete(row.id)
      if (res.code === 200) {
        message.success('删除成功')
        await loadData() // 重新加载数据
      } else {
        message.error(res.msg || '删除失败')
      }
    } catch (error) {
      console.error('Delete error:', error)
      message.error('删除失败')
    } finally {
      loading.value = false
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
    handleOrientationChange,
    handleFloorChange,
    handleAreaChange,
    handleReset,
    CITY_OPTIONS,
    ORIENTATION_OPTIONS,
    FLOOR_OPTIONS,
    AREA_OPTIONS,
    showModal,
    modalTitle,
    formParams,
    handleEdit,
    handleDelete
  }
} 