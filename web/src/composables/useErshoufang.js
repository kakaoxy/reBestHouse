// ... 其他导入保持不变 ...

export function useErshoufang() {
  const loading = ref(false)
  const data = ref([])
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
  const getList = async () => {
    loading.value = true
    try {
      const res = await api.getList({
        page: pagination.page,
        page_size: pagination.pageSize
      })
      if (res.code === 200 && res.data) {
        data.value = res.data.items
        pagination.itemCount = res.data.total
      }
    } catch (error) {
      console.error('Failed to get list:', error)
    } finally {
      loading.value = false
    }
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

  // ... 其他方法保持不变 ...

  onMounted(() => {
    getList()
  })

  return {
    loading,
    columns,
    data,
    pagination,
    handlePageChange,
    handlePageSizeChange,
    getList,  // 导出 getList 方法
    handleAdd,
    handleEdit,
    handleDelete
  }
} 