import { ref, reactive, h } from 'vue'
import { useMessage, NSpace, NButton, NPopconfirm, NTag } from 'naive-ui'
import { useCityStore } from '@/stores/city'
import { communityApi } from '@/api/house'
import { debounce } from 'lodash-es'

const communityOptions = ref([])
const loadingCommunities = ref(false)
const layoutInfo = ref({
  rooms: null,
  halls: null
})

export function useDealRecordCRUD(api) {
  const message = useMessage()
  const loading = ref(false)
  const showModal = ref(false)
  const modalTitle = ref('')
  const formRef = ref(null)
  const cityStore = useCityStore()
  const formParams = ref({})

  // 表格数据
  const data = ref([])
  const pagination = reactive({
    page: 1,
    pageSize: 10,
    total: 0,
    pageSizes: [10, 20, 50],
    showSizePicker: true,
    prefix({ itemCount }) {
      return `共 ${itemCount} 条`
    }
  })

  // 查询参数
  const queryParams = reactive({
    search_keyword: '',
    city: cityStore.currentCity || '',
    layout: null,
    floor_info: null,
    page: 1,
    page_size: 10,
    sort_by: 'deal_date',
    sort_direction: 'desc'
  })

  // 表单数据
  const formValue = reactive({
    city: '',
    community_id: null,
    community_name: '',
    region: '',
    area: '',
    layout: null,
    size: null,
    floor_number: null,
    total_floors: null,
    floor_info: null,
    orientation: null,
    total_price: null,
    unit_price: null,
    deal_date: null,
    deal_cycle: null,
    agency: null,
    source: 'store',
    tags: [],
    building_year: null,
    decoration: null,
    building_structure: null,
    listing_price: null,
    house_img_url: '',
    house_url: '',
    platform_house_id: ''
  })

  // 预定义选项
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

  const DECORATION_OPTIONS = [
    { label: '毛坯', value: '毛坯' },
    { label: '简装', value: '简装' },
    { label: '精装', value: '精装' },
    { label: '豪装', value: '豪装' }
  ]

  const STRUCTURE_OPTIONS = [
    { label: '砖混', value: '砖混' },
    { label: '钢混', value: '钢混' },
    { label: '框架', value: '框架' },
    { label: '其他', value: '其他' }
  ]

  const SOURCE_OPTIONS = [
    { label: '线下门店', value: 'store' },
    { label: '网络数据', value: 'web' },
    { label: '其他来源', value: 'other' }
  ]

  // 表格列定义
  const columns = [
    {
      title: '小区名称',
      key: 'community_name',
      width: 160,
    },
    {
      title: '区域/商圈',
      key: 'region',
      width: 140,
      render: (row) => {
        console.log('Region/Area from row:', {
          id: row.id,
          region: row.region,
          area: row.area
        })
        
        const region = row.region || '-'
        const area = row.area || '-'
        return `${region}/${area}`
      }
    },
    {
      title: '户型',
      key: 'layout',
      width: 100,
      render: (row) => row.layout || '-'
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
      width: 160,
      render: (row) => row.floor_info || '-'
    },
    {
      title: '房屋朝向',
      key: 'orientation',
      width: 100,
      render: (row) => row.orientation || '-'
    },
    {
      title: '挂牌价',
      key: 'listing_price',
      width: 100,
      render: (row) => {
        // console.log('Listing price data:', row.listing_price)
        return row.listing_price ? `${row.listing_price}万` : '-'
      }
    },
    {
      title: '成交价',
      key: 'total_price',
      width: 100,
      render: (row) => {
        // console.log('Total price data:', row.total_price)
        return row.total_price ? `${row.total_price}万` : '-'
      }
    },
    {
      title: '单价',
      key: 'unit_price',
      width: 120,
      render: (row) => {
        // console.log('Unit price data:', row.unit_price)
        return row.unit_price ? `${row.unit_price}元/㎡` : '-'
      }
    },
    {
      title: '成交时间',
      key: 'deal_date',
      width: 120,
      sorter: true,
      render: (row) => {
        // console.log('Deal date data:', row.deal_date)
        return row.deal_date || '-'
      }
    },
    {
      title: '成交周期',
      key: 'deal_cycle',
      width: 100,
      render: (row) => {
        // console.log('Deal cycle data:', row.deal_cycle)
        return row.deal_cycle ? `${row.deal_cycle}天` : '-'
      }
    },
    {
      title: '标签',
      key: 'tags',
      width: 200,
      render: (row) => {
        // console.log('Tags data:', row.tags)
        if (!row.tags) return null
        
        const tagsArray = Array.isArray(row.tags) 
          ? row.tags 
          : typeof row.tags === 'string' 
            ? row.tags.split(',')
            : []

        if (tagsArray.length === 0) return null

        return h(NSpace, { wrap: true }, {
          default: () => tagsArray.map(tag => 
            h(NTag, {
              style: {
                marginRight: '6px',
                marginBottom: '4px'
              },
              type: 'info',
              size: 'small'
            }, { default: () => tag })
          )
        })
      }
    },
    {
      title: '位置',
      key: 'address',
      width: 160,
    },
    {
      title: '装修',
      key: 'decoration',
      width: 100,
    },
    {
      title: '操作',
      key: 'actions',
      width: 120,
      fixed: 'right',
      render: (row) => {
        return h(NSpace, { justify: 'center' }, {
          default: () => [
            h(NButton, {
              size: 'small',
              type: 'primary',
              onClick: () => handleEdit(row)
            }, { default: () => '编辑' }),
            h(NButton, {
              size: 'small',
              type: 'error',
              onClick: () => handleDelete(row.id)
            }, { default: () => '删除' })
          ]
        })
      }
    }
  ]

  // 加载小区列表
  const loadCommunities = async (keyword = '') => {
    loadingCommunities.value = true
    try {
      console.log('Loading communities with params:', {
        name: keyword,
        city: formValue.city || cityStore.currentCity
      })

      const res = await communityApi.list({
        name: keyword,
        city: formValue.city || cityStore.currentCity,
        page_size: 100
      })

      console.log('Community API response:', res)  // 添加日志

      if (res.code === 200) {
        communityOptions.value = res.data.items.map(item => {
          console.log('Processing community item:', item)  // 添加日志
          return {
            label: `${item.name} (${item.region || ''})`,
            value: item.id,
            region: item.region,
            area: item.area,
            raw: item
          }
        })
        console.log('Processed community options:', communityOptions.value)  // 添加日志
      }
    } catch (error) {
      console.error('Load community options error:', error)
      message.error('加载小区列表失败')
    } finally {
      loadingCommunities.value = false
    }
  }

  // 处理小区选择
  const handleCommunityChange = (value) => {
    console.log('Selected community value:', value)
    console.log('Available community options:', communityOptions.value)
    
    if (!value) {
      formValue.community_id = null
      formValue.community_name = ''
      formValue.region = ''
      formValue.area = ''
      return
    }

    const selected = communityOptions.value.find(item => item.value === value)
    console.log('Selected community data:', selected)
    
    if (selected && selected.raw) {
      formValue.community_id = selected.value
      formValue.community_name = selected.raw.name
      formValue.region = selected.raw.region || ''
      formValue.area = selected.raw.area || ''
      
      // 打印更新后的表单值
      console.log('Updated form values:', {
        community_id: formValue.community_id,
        community_name: formValue.community_name,
        region: formValue.region,
        area: formValue.area
      })
    } else {
      console.error('Selected community data is invalid:', selected)
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

  // 处理面积变化
  const handleSizeChange = (value) => {
    if (value && formValue.total_price) {
      formValue.unit_price = Math.round((formValue.total_price * 10000) / value)
    }
  }

  // 处理总价变化
  const handleTotalPriceChange = (value) => {
    if (value && formValue.size) {
      formValue.unit_price = Math.round((value * 10000) / formValue.size)
    }
  }

  // 处理户型变化
  const handleLayoutChange = () => {
    if (layoutInfo.rooms) {
      formValue.layout = `${layoutInfo.rooms}室${layoutInfo.halls || 0}厅`
    } else {
      formValue.layout = null
    }
  }

  // 处理楼层变化
  const handleFloorChange = () => {
    if (formValue.floor_number && formValue.total_floors) {
      const floorRatio = formValue.floor_number / formValue.total_floors
      let floorDesc = ''
      if (floorRatio <= 0.33) {
        floorDesc = '低楼层'
      } else if (floorRatio <= 0.66) {
        floorDesc = '中楼层'
      } else {
        floorDesc = '高楼层'
      }
      formValue.floor_info = `${floorDesc}/共${formValue.total_floors}层`
    } else {
      formValue.floor_info = null
    }
  }

  // 处理日期变化
  const handleDateChange = (value) => {
    formValue.deal_date = value
  }

  // 表单验证规则
  const rules = {
    community_id: {
      required: true,
      type: 'number',
      message: '请选择小区',
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
    deal_date: {
      required: true,
      type: 'number',
      message: '请选择成交日期',
      trigger: ['blur', 'change']
    }
  }

  // 重置表单
  const resetForm = () => {
    Object.assign(formValue, {
      community_id: null,
      community_name: '',
      region: '',
      area: '',
      layout: null,
      size: null,
      floor_number: null,
      total_floors: null,
      floor_info: null,
      orientation: null,
      total_price: null,
      unit_price: null,
      deal_date: null,
      deal_cycle: null,
      agency: null,
      source: 'store',
      tags: [],
      building_year: null,
      decoration: null,
      building_structure: null,
      listing_price: null,
      house_img_url: '',
      house_url: '',
      platform_house_id: ''
    })
    Object.assign(layoutInfo, {
      rooms: null,
      halls: null
    })
    formRef.value?.restoreValidation()
  }

  // 处理新增
  const handleAdd = () => {
    modalTitle.value = '新增成交'
    resetForm()
    Object.assign(formValue, {
      city: cityStore.currentCity,
      source: 'store'
    })
    showModal.value = true
  }

  // 处理编辑
  const handleEdit = (row) => {
    modalTitle.value = '编辑成交'
    resetForm()
    Object.assign(formValue, {
      id: row.id,
      community_id: parseInt(row.community_id),
      community_name: row.community_name || '',
      region: row.region || '',
      area: row.area || '',
      city: row.city || cityStore.currentCity,
      layout: row.layout || null,
      size: row.size ? parseFloat(row.size) : null,
      floor_number: row.floor_number ? parseInt(row.floor_number) : null,
      total_floors: row.total_floors ? parseInt(row.total_floors) : null,
      floor_info: row.floor_info || null,
      orientation: row.orientation || null,
      total_price: row.total_price ? parseFloat(row.total_price) : null,
      unit_price: row.unit_price ? parseInt(row.unit_price) : null,
      deal_date: row.deal_date ? row.deal_date * 1000 : null,  // 转换为毫秒时间戳
      deal_cycle: row.deal_cycle || null,
      agency: row.agency || null,
      source: row.source || 'store',
      tags: row.tags || [],
      building_year: row.building_year || null,
      decoration: row.decoration || null,
      building_structure: row.building_structure || null
    })
    showModal.value = true
  }

  // Modal 提交处理
  const handleModalSubmit = async (formData) => {
    try {
      loading.value = true
      console.log('Form data before submit:', formData)  // 添加日志

      const submitData = {
        ...formData,
        city: formData.city || cityStore.currentCity,
        community_id: parseInt(formData.community_id),
        community_name: formData.community_name,
        region: formData.region,
        area: formData.area,
        size: formData.size ? parseFloat(formData.size) : null,
        floor_number: formData.floor_number ? parseInt(formData.floor_number) : null,
        total_floors: formData.total_floors ? parseInt(formData.total_floors) : null,
        total_price: formData.total_price ? parseFloat(formData.total_price) : null,
        unit_price: formData.unit_price ? parseInt(formData.unit_price) : null,
        deal_date: formData.deal_date 
          ? Math.floor(new Date(formData.deal_date).setHours(0, 0, 0, 0) / 1000)
          : null,
        deal_cycle: formData.deal_cycle ? parseInt(formData.deal_cycle) : null,
        building_year: formData.building_year ? parseInt(formData.building_year) : null
      }

      console.log('Submit data after processing:', submitData)  // 添加日志

      // 确保区域和商圈数据不会被移除
      const res = formData.id
        ? await api.update(formData.id, submitData)
        : await api.create(submitData)

      console.log('API response:', res)  // 添加日志

      if (res.code === 200) {
        message.success(res.msg || '操作成功')
        showModal.value = false
        loadData()
      }
    } catch (error) {
      console.error('Submit error:', error)
      message.error(error.message || '操作失败')
    } finally {
      loading.value = false
    }
  }

  // 添加 Modal 取消处理
  const handleModalCancel = () => {
    showModal.value = false
    resetForm()
  }

  // 监听城市变化
  watch(() => cityStore.currentCity, (newCity) => {
    if (newCity) {
      formValue.city = newCity
      communityOptions.value = []
      if (formValue.community_id) {
        resetForm()
      }
    }
  }, { immediate: true })

  // 添加排序参数
  const sortParams = ref({
    key: 'deal_date',
    order: 'desc'
  })

  // 加载数据方法
  const loadData = async () => {
    try {
      loading.value = true
      const res = await api.list({
        ...queryParams,
        page: pagination.page,
        page_size: pagination.pageSize,
        sort_by: sortParams.value.key,
        sort_direction: sortParams.value.order
      })

      if (res.code === 200) {
        console.log('API response data:', res.data.items.map(item => ({
          id: item.id,
          region: item.region,
          area: item.area
        })))
        
        data.value = processApiResponse(res)
      }
    } catch (error) {
      console.error('Load data error:', error)
      message.error('加载数据失败')
    } finally {
      loading.value = false
    }
  }

  // 处理分页变化
  const handlePageChange = (page) => {
    queryParams.page = page
    loadData()
  }

  // 处理每页条数变化
  const handlePageSizeChange = (pageSize) => {
    queryParams.page_size = pageSize
    queryParams.page = 1
    loadData()
  }

  // 处理删除
  const handleDelete = async (id) => {
    try {
      loading.value = true
      const res = await api.delete(id)
      if (res.code === 200) {
        message.success(res.msg || '删除成功')
        loadData()
      }
    } catch (error) {
      message.error(error.message || '删除失败')
    } finally {
      loading.value = false
    }
  }

  // 处理排序变化
  const handleSorterChange = (sorter) => {
    if (sorter) {
      sortParams.value = {
        key: sorter.key,
        order: sorter.order === 'ascend' ? 'asc' : 'desc'
      }
    } else {
      sortParams.value = {
        key: 'deal_date',
        order: 'desc'
      }
    }
    loadData()
  }

  // 处理 API 响应数据
  const processApiResponse = (response) => {
    if (response.code === 200) {
      console.log('Raw API response items:', response.data.items)
      return response.data.items.map(item => {
        console.log('Processing item region/area:', {
          id: item.id,
          region: item.region,
          area: item.area
        })
        
        return {
          ...item,
          region: item.region || '',
          area: item.area || '',
        }
      })
    }
    return []
  }

  return {
    loading,
    data,
    pagination,
    queryParams,
    showModal,
    modalTitle,
    formRef,
    formValue,
    formParams,
    columns,
    ORIENTATION_OPTIONS,
    DECORATION_OPTIONS,
    STRUCTURE_OPTIONS,
    SOURCE_OPTIONS,
    handleAdd,
    handleEdit,
    handleDelete,
    handleModalSubmit,
    handleModalCancel,
    handlePageChange,
    handlePageSizeChange,
    handleSorterChange,
    handleCommunityChange,
    handleCommunitySearch,
    handleCommunityFocus,
    handleSizeChange,
    handleTotalPriceChange,
    handleLayoutChange,
    handleFloorChange,
    handleDateChange,
    resetForm,
    loadData,
    communityOptions,
    loadingCommunities,
    layoutInfo,
    rules,
    sortParams
  }
} 