<template>
  <CommonPage>
    <n-card :bordered="false" class="proCard">
      <!-- 顶部操作栏 -->
      <n-space vertical :size="16">
        <n-space justify="space-between" align="center">
          <n-space align="center" :size="8">
            <!-- 城市选择器 -->
            <n-select
              v-model:value="selectedCity"
              :options="communityStore.CITY_OPTIONS"
              style="width: 120px"
              @update:value="handleCityChange"
            />
            <!-- 搜索框和按钮组 -->
            <n-input
              v-model:value="queryParams.search_keyword"
              type="text"
              placeholder="输入小区名称搜索"
              style="width: 200px"
              clearable
            />
            <n-button type="primary" @click="handleSearch">
              <template #icon>
                <TheIcon icon="material-symbols:search" />
              </template>
              搜索
            </n-button>
            <n-button @click="handleReset">
              <template #icon>
                <TheIcon icon="material-symbols:refresh" />
              </template>
              重置
            </n-button>
          </n-space>
          <!-- 新增按钮 -->
          <n-space>
            <n-button @click="handleDownloadTemplate">
              <template #icon>
                <TheIcon icon="material-symbols:download" />
              </template>
              下载模板
            </n-button>
            <n-button @click="handleImport">
              <template #icon>
                <TheIcon icon="material-symbols:upload" />
              </template>
              批量导入
            </n-button>
            <n-button type="primary" @click="handleAdd">
              <template #icon>
                <TheIcon icon="material-symbols:add" />
              </template>
              新增小区
            </n-button>
          </n-space>
        </n-space>

        <!-- 表格区域 -->
        <n-data-table
          :columns="columns"
          :data="data"
          :loading="loading"
          :pagination="pagination"
          :bordered="false"
          :striped="true"
          remote
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </n-space>
    </n-card>

    <!-- Modal 组件 -->
    <CommunityModal
      v-model:show="showModal"
      :title="modalTitle"
      :form-value="formParams"
      :loading="loading"
      @submit="handleModalSubmit"
      @cancel="handleModalCancel"
    />
  </CommonPage>
</template>

<script setup>
import { onMounted, h, reactive, ref } from 'vue'
import { 
  useMessage, 
  NSpace,
  NButton, 
  NPopconfirm,
  NDataTable,
  useDialog
} from 'naive-ui'
import { useCommunityStore } from '@/stores/community'
import { request } from '@/utils'
import CommonPage from '@/components/page/CommonPage.vue'
import CommunityModal from './components/CommunityModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

const message = useMessage()
const dialog = useDialog()
const communityStore = useCommunityStore()

// API 定义
const api = {
  list: (params = {}) => {
    const queryParams = {
      city: params.city || selectedCity.value,
      search_keyword: params.search_keyword || '',
      page: params.page || 1,
      page_size: params.page_size || 10
    }
    console.log('API request params:', queryParams)
    return request.get('/house/communities', { params: queryParams })
  },
  create: (data) => request.post('/house/communities', data),
  update: (id, data) => request.put(`/house/communities/${id}`, data),
  delete: (id) => request.delete(`/house/communities/${id}`)
}

const selectedCity = ref(communityStore.currentCity)

// 查询参数
const queryParams = reactive({
  city: selectedCity.value,
  search_keyword: ''
})

// 表格和模态框状态
const loading = ref(false)
const data = ref([])
const showModal = ref(false)
const modalTitle = ref('')
const formParams = ref({})

// 分页配置
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  showQuickJumper: true,
  pageSizes: [10, 20, 50],
  showSizePicker: true,
  pageSize: 10,
  page: 1,
  pageCount: 1,
  displayOrder: ['size-picker', 'pages', 'quick-jumper'],
  prefix({ itemCount }) {
    return `共 ${itemCount} 条`
  },
  suffix({ itemCount, pageSize }) {
    const pages = Math.ceil(itemCount / pageSize)
    return `共 ${pages} 页`
  }
})

// 定义表格列
const columns = [
  {
    title: '小区名称',
    key: 'name',
    width: 200
  },
  {
    title: '城市',
    key: 'city',
    width: 100,
    render(row) {
      const cityOption = communityStore.CITY_OPTIONS.find(item => item.value === row.city)
      return cityOption ? cityOption.label : row.city
    }
  },
  {
    title: '区域',
    key: 'region',
    width: 120
  },
  {
    title: '商圈',
    key: 'area',
    width: 120
  },
  {
    title: '地址',
    key: 'address',
    width: 200
  },
  {
    title: '建筑类型',
    key: 'building_type',
    width: 120
  },
  {
    title: '交易权属',
    key: 'property_rights',
    width: 150
  },
  {
    title: '房屋总数',
    key: 'total_houses',
    width: 100
  },
  {
    title: '建筑年代',
    key: 'building_year',
    width: 100
  },
  {
    title: '操作',
    key: 'actions',
    width: 150,
    fixed: 'right',
    render(row) {
      return h(NSpace, { justify: 'center' }, {
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
      })
    }
  }
]

// 处理API返回的数据
const processData = (response) => {
  if (response.code === 200) {
    data.value = response.data.items
    const total = response.data.total
    const pageSize = response.data.page_size || 10
    
    pagination.itemCount = total
    pagination.pageCount = Math.ceil(total / pageSize)
    pagination.page = response.data.page || 1
    pagination.pageSize = pageSize
    
    return {
      items: response.data.items,
      total: response.data.total,
      page: response.data.page,
      pageSize: response.data.page_size,
      currentCity: selectedCity.value
    }
  }
  return null
}

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    const params = {
      city: selectedCity.value,
      search_keyword: queryParams.search_keyword || '',
      page: pagination.page,
      page_size: pagination.pageSize
    }
    console.log('Sending request with params:', params)
    const res = await api.list(params)
    console.log('API response:', res)
    const processedData = processData(res)
    console.log('Processed data:', processedData)
    if (!processedData) {
      message.error('加载数据失败')
    }
  } catch (error) {
    console.error('Load data error:', error)
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 处理页码变化
const handlePageChange = (page) => {
  if (page === pagination.page) return
  pagination.page = page
  loadData()
}

// 处理每页条数变化
const handlePageSizeChange = (pageSize) => {
  if (pageSize === pagination.pageSize) return
  pagination.pageSize = pageSize
  pagination.page = 1  // 切换每页条数时重置到第一页
  loadData()
}

// 处理城市变化
const handleCityChange = (city) => {
  selectedCity.value = city
  queryParams.city = city
  communityStore.setCity(city)
  pagination.page = 1
  loadData()
}

// 处理新增
const handleAdd = () => {
  modalTitle.value = '新增小区'
  formParams.value = {
    name: '',
    city: selectedCity.value,
    region: '',
    area: '',
    address: '',
    building_type: null,
    property_rights: [],
    total_houses: null,
    building_year: null
  }
  showModal.value = true
}

// 处理模态框提交
const handleModalSubmit = async (formData) => {
  try {
    loading.value = true
    // 确保城市字段正确设置
    const submitData = {
      ...formData,
      city: formData.city || communityStore.currentCity
    }
    const res = await (formData.id ? api.update(formData.id, submitData) : api.create(submitData))
    if (res.code === 400) {
      dialog.warning({
        title: '小区已存在',
        content: res.msg,
        positiveText: '确定',
        onPositiveClick: () => {
          // 可以选择是否关闭模态框
          // showModal.value = false
        }
      })
    } else if (res.code === 200) {
      message.success(res.msg || '操作成功')
      showModal.value = false
      loadData()
    } else {
      message.error(res.msg || '操作失败')
    }
  } catch (error) {
    console.error('Submit error:', error)
    message.error('操作失败')
  } finally {
    loading.value = false
  }
}

const handleModalCancel = () => {
  showModal.value = false
}

// 重置查询
const handleReset = () => {
  queryParams.search_keyword = ''
  queryParams.city = selectedCity.value // 确保重置时保持当前城市
  pagination.page = 1
  loadData()
}

// 处理编辑
const handleEdit = (row) => {
  modalTitle.value = '编辑小区'
  formParams.value = { ...row }
  showModal.value = true
}

// 处理删除
const handleDelete = async (row) => {
  try {
    loading.value = true
    const res = await api.delete(row.id)
    if (res.code === 200) {
      message.success('删除成功')
      loadData()
    }
  } catch (error) {
    console.error('Delete error:', error)
    message.error('删除失败')
  } finally {
    loading.value = false
  }
}

// 修改搜索按钮点击事件处理
const handleSearch = () => {
  pagination.page = 1
  queryParams.city = selectedCity.value // 确保搜索时使用当前城市
  loadData()
}

// 处理下载模板
const handleDownloadTemplate = () => {
  const link = document.createElement('a')
  link.href = '/templates/community_import_template.xlsx'
  link.download = '小区导入模板.xlsx'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 处理批量导入
const handleImport = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.xlsx,.xls'
  
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    // 验证文件类型
    if (!file.name.match(/\.(xlsx|xls)$/)) {
      message.error('请上传 Excel 文件 (.xlsx, .xls)')
      return
    }
    
    // 提示用户当前选择的城市
    dialog.info({
      title: '导入提示',
      content: `即将导入到城市：${communityStore.CITY_OPTIONS.find(item => item.value === selectedCity.value)?.label}`,
      positiveText: '继续',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          loading.value = true
          const formData = new FormData()
          formData.append('file', file)
          formData.append('city', selectedCity.value)
          
          const res = await request.post('/house/communities/import', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Accept': 'application/json'
            }
          })
          
          if ([200, 400, 422].includes(res.code)) {
            message.success(res.msg)
            // 显示导入结果
            if (res.data?.error_count > 0) {
              dialog.warning({
                title: '导入结果',
                content: () => h('div', [
                  h('p', `成功：${res.data.success_count} 条`),
                  h('p', `失败：${res.data.error_count} 条`),
                  h('div', { style: 'max-height: 200px; overflow-y: auto;' }, [
                    ...res.data.errors.map(error => 
                      h('p', { style: 'color: #d03050;' }, `${error.name}: ${error.error}`)
                    )
                  ])
                ]),
                positiveText: '确定'
              })
            }
            if (res.code === 200) {
              loadData()
            }
          } else {
            throw new Error(res.msg || '导入失败')
          }
        } catch (error) {
          message.error(error.response?.data?.detail || error.message || '导入失败')
        } finally {
          loading.value = false
        }
      }
    })
  }
  
  input.click()
}

// 初始化
onMounted(() => {
  // 确保使用 store 中的默认城市
  selectedCity.value = communityStore.currentCity
  queryParams.city = selectedCity.value
  loadData()
})
</script>

<style scoped>
.proCard {
  margin: 16px;
}

.n-button {
  min-width: 80px;
}
</style> 