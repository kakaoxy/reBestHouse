<template>
  <CommonPage>
    <n-card>
      <!-- 搜索区域 -->
      <n-space vertical :size="16">
        <!-- 搜索框和按钮 -->
        <n-space justify="space-between" align="center">
          <n-space align="center">
            <!-- 城市和搜索组合 -->
            <n-space align="center" :size="4">
              <n-select
                v-model:value="queryParams.city"
                :options="CITY_OPTIONS"
                style="width: 100px"
              />
              <n-input
                v-model:value="queryParams.name"
                type="text"
                placeholder="输入小区名称搜索"
                style="width: 200px"
                clearable
              />
            </n-space>
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
          <!-- 新增按钮右对齐 -->
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
        class="mt-4"
        :columns="columns"
        :data="tableData"
        :loading="loading"
        :pagination="pagination"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
        @update:sorter="handleSorterChange"
      />
    </n-card>

    <!-- 使用自定义的 Modal 组件 -->
    <CommunityModal
      v-model:show="modalVisible"
      :title="modalTitle"
      :loading="modalLoading"
      :form-value="formParams"
      :rules="rules"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />
  </CommonPage>
</template>

<script setup>
import { ref, reactive, onMounted, h } from 'vue'
import { useMessage, NSpace, NButton, NButtonGroup, NPopconfirm, NInput, NSelect, NCard, NDataTable, NForm, NFormItem, NCheckbox, NCheckboxGroup, NInputNumber } from 'naive-ui'
import { useCRUD } from '@/composables'
import { request } from '@/utils'
import CommonPage from '@/components/page/CommonPage.vue'
import CommunityModal from './components/CommunityModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import { useCommunityModal } from '@/composables/useCommunityModal'

const message = useMessage()

// 城市选项
const CITY_OPTIONS = [
  { label: '上海', value: 'shanghai' },
  { label: '北京', value: 'beijing' },
  { label: '深圳', value: 'shenzhen' },
  { label: '广州', value: 'guangzhou' }
]

// 添加选项定义
const BUILDING_TYPE_OPTIONS = [
  { label: '板楼', value: '板楼' },
  { label: '塔楼', value: '塔楼' },
  { label: '板塔结合', value: '板塔结合' }
]

const PROPERTY_RIGHTS_OPTIONS = [
  { label: '商品房', value: '商品房' },
  { label: '动迁房', value: '动迁房' },
  { label: '商住', value: '商住' },
  { label: '其他', value: '其他' }
]

// 查询参数
const queryParams = reactive({
  city: 'shanghai',  // 默认上海
  name: '',
  sort_by: 'created_at',
  sort_direction: 'desc',
  page: 1,
  page_size: 10
})

// API 定义 - 修改 API 路径，参考在售房源列表的格式
const api = {
  list: (params = {}) => request.get('/house/communities', { params }),
  create: (data) => request.post('/house/communities', data),
  update: (id, data) => request.put(`/house/communities/${id}`, data),
  delete: (id) => request.delete(`/house/communities/${id}`)
}

// 使用专门的 Community Modal
const {
  modalVisible,
  modalTitle,
  modalLoading,
  formRef,
  formParams,
  rules,
  handleAdd,
  handleEdit,
  handleDelete,
  handleSubmit,
  resetForm
} = useCommunityModal(api)

// 表格数据
const tableData = ref([])
const pagination = reactive({
  page: 1,
  pageSize: 10,
  itemCount: 0,
  pageSizes: [10, 20, 50]
})

// 加载数据函数
const loadData = async () => {
  try {
    const res = await api.list(queryParams)
    if (res.code === 200 && res.data) {
      tableData.value = res.data.items || []
      pagination.itemCount = res.data.total || 0
      pagination.page = queryParams.page
      pagination.pageSize = queryParams.page_size
    }
  } catch (error) {
    console.error('Failed to load data:', error)
    tableData.value = []
    pagination.itemCount = 0
  }
}

// 使用 CRUD 组合式函数
const crud = useCRUD({
  tag: 'community',
  api,
  page: queryParams,
  form: formParams,
  rules,
  onSuccess: (res) => {
    console.log('CRUD onSuccess:', res)
    if (res.code === 200) {
      message.success(res.msg || '操作成功')
      modalVisible.value = false
      loadData()
    } else {
      message.error(res.msg || '操作失败')
    }
  }
})

const {
  loading,
  handlePageChange,
  handlePageSizeChange,
  handleSorterChange,
  resetQuery
} = crud

// 修改重置函数
const handleReset = () => {
  resetQuery()
  loadData()
}

// 表格列定义
const columns = [
  { 
    title: '小区名称',
    key: 'name',
    width: 200
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
    width: 250
  },
  { 
    title: '建筑类型',
    key: 'building_type',
    width: 120
  },
  { 
    title: '建筑年代',
    key: 'building_year',
    width: 100,
    sorter: true
  },
  { 
    title: '房屋总数',
    key: 'total_houses',
    width: 100,
    align: 'right'
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
            onPositiveClick: () => handleDelete({ id: row.id })
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

const handleCancel = () => {
  formRef.value?.restoreValidation()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.n-button {
  min-width: 80px;
}

.mt-4 {
  margin-top: 16px;
}
</style> 