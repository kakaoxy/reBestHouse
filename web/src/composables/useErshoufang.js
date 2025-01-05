import { ref, reactive, onMounted } from 'vue'
import { useMessage } from 'naive-ui'

export function useErshoufang(api) {
  const message = useMessage()
  const loading = ref(false)
  const data = ref([])
  
  // 查询参数
  const queryParams = reactive({
    search_keyword: '',
    community_id: null,  // 新增 community_id 参数
    page: 1,
    page_size: 10
  })

  const pagination = reactive({
    page: 1,
    pageSize: 10,
    showSizePicker: true,
    pageSizes: [10, 20, 30, 40],
    onChange: (page) => {
      pagination.page = page
      getList()
    },
    onUpdatePageSize: (pageSize) => {
      pagination.pageSize = pageSize
      pagination.page = 1
      getList()
    }
  })

  // 获取列表数据
  const getList = async (params = {}) => {
    loading.value = true
    try {
      // 合并默认参数和传入的参数
      const requestParams = {
        page: pagination.page,
        page_size: pagination.pageSize,
        ...queryParams,
        ...params
      }

      // 移除值为 null 或 undefined 的参数
      const cleanParams = Object.entries(requestParams).reduce((acc, [key, value]) => {
        if (value != null) {
          acc[key] = value
        }
        return acc
      }, {})

      const res = await api.list(cleanParams)
      
      if (res.code === 200 && res.data) {
        data.value = res.data.items
        pagination.itemCount = res.data.total
      }
    } catch (error) {
      console.error('Failed to get list:', error)
      message.error(error.message || '获取数据失败')
    } finally {
      loading.value = false
    }
  }

  // 根据小区ID获取房源列表
  const getListByCommunityId = async (communityId) => {
    if (!communityId) return
    queryParams.community_id = communityId
    pagination.page = 1  // 重置页码
    await getList()
  }

  // 清除小区ID筛选
  const clearCommunityFilter = async () => {
    queryParams.community_id = null
    pagination.page = 1
    await getList()
  }

  // 页码改变
  const handlePageChange = (page) => {
    pagination.page = page
    getList()
  }

  // 每页条数改变
  const handlePageSizeChange = (pageSize) => {
    pagination.pageSize = pageSize
    pagination.page = 1
    getList()
  }

  // ... 其他现有方法保持不变 ...

  onMounted(() => {
    getList()
  })

  return {
    loading,
    data,
    pagination,
    queryParams,          // 导出查询参数
    getList,             // 导出获取列表方法
    getListByCommunityId, // 导出按小区ID获取列表方法
    clearCommunityFilter, // 导出清除小区筛选方法
    handlePageChange,
    handlePageSizeChange,
    // ... 其他现有返回值保持不变 ...
  }
} 