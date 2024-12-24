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
            <n-button type="primary" @click="loadData">
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
          <n-button type="primary" @click="handleAdd">
            <template #icon>
              <TheIcon icon="material-symbols:add" />
            </template>
            新增小区
          </n-button>
        </n-space>

        <!-- 表格区域 -->
        <n-data-table
          :columns="columns"
          :data="data"
          :loading="loading"
          :pagination="pagination"
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
  NDataTable
} from 'naive-ui'
import { useCommunityStore } from '@/stores/community'
import { request } from '@/utils'
import CommonPage from '@/components/page/CommonPage.vue'
import CommunityModal from './components/CommunityModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

const message = useMessage()
const communityStore = useCommunityStore()

// API 定义
const api = {
  list: (params = {}) => {
    // 确保参数中包含城市
    const queryParams = {
      ...params,
      city: params.city || selectedCity.value
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
  search_keyword: '',
  page: 1,
  page_size: 10
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
  showSizePicker: true,
  pageSizes: [10, 20, 50]
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

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    const params = {
      ...queryParams,
      city: selectedCity.value,
      page: pagination.page,
      page_size: pagination.pageSize
    }
    console.log('Sending request with params:', params)
    
    const res = await api.list(params)
    console.log('API response:', res)
    
    if (res.code === 200) {
      // 确保只显示当前城市的数据
      data.value = res.data.items.filter(item => item.city === selectedCity.value)
      pagination.itemCount = data.value.length
      pagination.page = res.data.page
      pagination.pageSize = res.data.page_size
      
      console.log('Filtered data:', {
        currentCity: selectedCity.value,
        totalItems: data.value.length,
        items: data.value
      })
    }
  } catch (error) {
    console.error('Failed to load data:', error)
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 处理分页
const handlePageChange = (page) => {
  queryParams.page = page
  loadData()
}

const handlePageSizeChange = (pageSize) => {
  queryParams.page_size = pageSize
  loadData()
}

// 处理城市变化
const handleCityChange = (city) => {
  console.log('City changed to:', city)
  selectedCity.value = city
  queryParams.city = city
  communityStore.setCity(city)
  // 重置分页
  pagination.page = 1
  // 重新加载数据
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
      city: formData.city || communityStore.currentCity // 如果没有设置城市，使用当前选中的城市
    }
    const res = await (formData.id ? api.update(formData.id, submitData) : api.create(submitData))
    if (res.code === 200) {
      message.success(res.msg || '操作成功')
      showModal.value = false
      loadData()
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
  queryParams.city = selectedCity.value
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