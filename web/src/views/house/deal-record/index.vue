<template>
  <CommonPage>
    <n-card :bordered="false" class="proCard">
      <n-space vertical :size="16">
        <!-- 顶部操作栏 -->
        <n-space justify="space-between" align="center">
          <n-space align="center" :size="8">
            <!-- 城市选择器 -->
            <n-select
              v-model:value="selectedCity"
              :options="departmentStore.departments"
              :render-label="renderLabel"
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
            <n-button @click="handleResetAll">
              <template #icon>
                <TheIcon icon="material-symbols:refresh" />
              </template>
              重置
            </n-button>
          </n-space>
          <!-- 新增按钮组 -->
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
              新增成交
            </n-button>
          </n-space>
        </n-space>

        <!-- 筛选条件 -->
        <n-space vertical :size="12">
          <!-- 户型和楼层在同一行 -->
          <n-space align="center" justify="start">
            <span class="label">户型：</span>
            <n-button-group>
              <n-button
                v-for="layout in CUSTOM_LAYOUT_OPTIONS"
                :key="layout.value"
                :type="queryParams.layout === layout.dbValue ? 'primary' : 'default'"
                @click="handleLayoutChange(layout.dbValue)"
              >
                {{ layout.label }}
              </n-button>
            </n-button-group>

            <span class="label" style="margin-left: 24px">楼层：</span>
            <n-button-group>
              <n-button
                v-for="floor in FLOOR_OPTIONS"
                :key="floor.value"
                :type="queryParams.floor_info === floor.value ? 'primary' : 'default'"
                @click="handleFloorChange(floor.value)"
              >
                {{ floor.label }}
              </n-button>
            </n-button-group>
          </n-space>
        </n-space>

        <!-- 表格区域 -->
        <n-data-table
          :columns="columns"
          :data="data"
          :loading="loading"
          :striped="true"
          :pagination="pagination"
          remote
          :row-key="row => row.id"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
          @update:sorter="handleSorterChange"
          v-bind="tableProps"
        />
      </n-space>
    </n-card>

    <!-- Modal 组件 -->
    <DealRecordModal
      v-model:show="showModal"
      :title="modalTitle"
      :form-value="formParams"
      :loading="loading"
      :ORIENTATION_OPTIONS="ORIENTATION_OPTIONS"
      :DECORATION_OPTIONS="DECORATION_OPTIONS"
      :STRUCTURE_OPTIONS="STRUCTURE_OPTIONS"
      :SOURCE_OPTIONS="SOURCE_OPTIONS"
      @submit="handleModalSubmit"
      @cancel="handleModalCancel"
    />
  </CommonPage>
</template>

<script setup>
import { ref, onMounted, reactive, watch } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { request } from '@/utils'
import CommonPage from '@/components/page/CommonPage.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import { useDepartmentStore } from '@/stores/department'
import DealRecordModal from './components/DealRecordModal.vue'
import { useDealRecordCRUD } from '@/composables/useDealRecordCRUD'

const message = useMessage()
const dialog = useDialog()
const departmentStore = useDepartmentStore()

// 选中的城市
const selectedCity = ref(null)

// 查询参数
const queryParams = reactive({
  city: '',
  search_keyword: '',
  page: 1,
  page_size: 10
})

// 处理城市变化
const handleCityChange = (value) => {
  selectedCity.value = value
  queryParams.city = value
  departmentStore.setDepartment(value)
  loadData()
}

// 渲染城市选择器的标签
const renderLabel = (option) => {
  return option.label
}

// 使用 CRUD 函数
const {
  loading,
  columns,
  data,
  pagination,
  showModal,
  modalTitle,
  formParams,
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
  handleReset
} = useDealRecordCRUD({
  list: (params = {}) => request.get('/house/deal-records', { params: { ...params, ...queryParams } }),
  create: (data) => request.post('/house/deal-records', data),
  update: (id, data) => request.put(`/house/deal-records/${id}`, data),
  delete: (id) => request.delete(`/house/deal-records/${id}`)
})

// 处理重置
const handleResetAll = () => {
  queryParams.search_keyword = ''
  handleReset()
  loadData()
}

// API 定义
const api = {
  list: (params = {}) => request.get('/house/deal-records', { params }),
  create: (data) => request.post('/house/deal-records', data),
  update: (id, data) => request.put(`/house/deal-records/${id}`, data),
  delete: (id) => request.delete(`/house/deal-records/${id}`)
}

// 预定义选项
const ORIENTATION_OPTIONS = [
  { label: '南', value: '朝南' },
  { label: '北', value: '朝北' },
  { label: '东', value: '朝东' },
  { label: '西', value: '朝西' }
]

const DECORATION_OPTIONS = [
  { label: '毛坯', value: '毛坯' },
  { label: '简装', value: '简装' },
  { label: '精装', value: '精装' },
  { label: '豪装', value: '豪装' }
]

const STRUCTURE_OPTIONS = [
  { label: '板楼', value: '板楼' },
  { label: '塔楼', value: '塔楼' },
  { label: '板塔结合', value: '板塔结合' }
]

const SOURCE_OPTIONS = [
  { label: '门店', value: 'store' },
  { label: '爬虫', value: 'spider' }
]

// 初始化
onMounted(async () => {
  try {
    // 获取部门列表并初始化当前部门
    await departmentStore.getDepartmentOptions()
    await departmentStore.initCurrentDepartment()
    // 使用初始化后的部门
    selectedCity.value = departmentStore.currentDepartment
    queryParams.city = selectedCity.value
    await loadData()
  } catch (error) {
    console.error('初始化失败:', error)
    // 如果初始化失败，使用上海作为默认值
    selectedCity.value = 'shanghai'
    queryParams.city = 'shanghai'
    await loadData()
  }
})

// 监听部门变化
watch(
  () => departmentStore.currentDepartment,
  (newValue) => {
    if (newValue && newValue !== selectedCity.value) {
      selectedCity.value = newValue
      queryParams.city = newValue
      loadData()
    }
  },
  { immediate: true }
)

// 添加处理下载模板函数
const handleDownloadTemplate = () => {
  const link = document.createElement('a')
  link.href = '/templates/deal_record_import_template.xlsx'
  link.download = '成交记录导入模板.xlsx'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 添加处理批量导入函数
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
      content: `即将导入到城市：${departmentStore.departments.find(item => item.value === departmentStore.currentDepartment)?.label}`,
      positiveText: '继续',
      negativeText: '取消',
      onPositiveClick: async () => {
        try {
          loading.value = true
          const formData = new FormData()
          formData.append('file', file)
          formData.append('city', departmentStore.currentDepartment)
          
          const res = await request.post('/house/deal-records/import', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          })
          
          if ([200, 400, 422].includes(res.code)) {
            // 显示导入结果
            dialog.success({
              title: '导入结果',
              content: () => h('div', [
                h('p', `成功导入：${res.data.success_count} 条`),
                h('p', `失败数量：${res.data.error_count} 条`),
                res.data.error_count > 0 ? h('div', [
                  h('p', { style: 'margin-top: 10px; font-weight: bold;' }, '失败详情：'),
                  h('div', { 
                    style: 'max-height: 200px; overflow-y: auto; margin-top: 5px; padding: 10px; background-color: #f5f5f5; border-radius: 4px;' 
                  }, [
                    ...res.data.errors.map(error => 
                      h('p', { style: 'color: #d03050; margin: 5px 0;' }, 
                        `${error.name}: ${error.error}`
                      )
                    )
                  ])
                ]) : null
              ]),
              positiveText: '确定',
              onPositiveClick: () => {
                if (res.code === 200) {
                  loadData()
                }
              }
            })
          } else {
            throw new Error(res.msg || '导入失败')
          }
        } catch (error) {
          message.error(error.response?.data?.msg || error.message || '导入失败')
        } finally {
          loading.value = false
        }
      }
    })
  }
  
  input.click()
}
</script>

<style scoped>
/* .n-space {
  width: 100%;
} */

.n-button-group {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.n-button {
  min-width: 80px;
}

.label {
  display: inline-block;
  min-width: 50px;
  text-align: right;
  margin-right: 8px;
  white-space: nowrap;
}

.mt-4 {
  margin-top: 16px;
}
</style>