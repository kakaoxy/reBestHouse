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
              :options="departmentStore.departments"
              :render-label="renderLabel"
              style="width: 120px"
              :disabled="!userStore.isSuperUser"
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
              新增房源
            </n-button>
          </n-space>
        </n-space>

        <!-- 筛选条件 -->
        <n-space vertical :size="12">
          <!-- 户型和朝向在同一行 -->
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

            <span class="label" style="margin-left: 24px">朝向：</span>
            <n-button-group>
              <n-button
                v-for="orientation in ORIENTATION_OPTIONS"
                :key="orientation.value"
                :type="queryParams.orientation === orientation.value ? 'primary' : 'default'"
                @click="handleOrientationChange(orientation.value)"
              >
                {{ orientation.label }}
              </n-button>
            </n-button-group>
          </n-space>

          <!-- 楼层和面积在同一行 -->
          <n-space align="center" justify="start">
            <span class="label">楼层：</span>
            <n-button-group>
              <n-button
                v-for="floor in FLOOR_OPTIONS"
                :key="floor.value"
                :type="queryParams.floor === floor.value ? 'primary' : 'default'"
                @click="handleFloorChange(floor.value)"
              >
                {{ floor.label }}
              </n-button>
            </n-button-group>

            <span class="label" style="margin-left: 24px">面积(m²)：</span>
            <n-button-group>
              <n-button
                v-for="area in AREA_OPTIONS"
                :key="area.label"
                :type="
                  queryParams.size_min === area.value[0] && 
                  queryParams.size_max === area.value[1] 
                    ? 'primary' 
                    : 'default'
                "
                @click="handleAreaChange(area.value)"
              >
                {{ area.label }}
              </n-button>
            </n-button-group>
          </n-space>
        </n-space>
      </n-space>

      <!-- 表格区域 -->
      <n-data-table
        class="mt-4"
        :columns="columns"
        :data="data"
        :loading="loading"
        :pagination="pagination"
        :striped="true"
        remote
        :row-key="row => row.id"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
        @update:sorter="handleSorterChange"
      />
    </n-card>

    <!-- Modal 组件 -->
    <ErshoufangModal
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
import { ref, onMounted, reactive, watch } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { request } from '@/utils'
import CommonPage from '@/components/page/CommonPage.vue'
import ErshoufangModal from './components/ErshoufangModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import { useErshoufangCRUD } from '@/composables/useErshoufangCRUD'
import { useDepartmentStore } from '@/stores/department'
import { useUserStore } from '@/store/modules/user'

const message = useMessage()
const dialog = useDialog()
const departmentStore = useDepartmentStore()
const userStore = useUserStore()

// API 定义
const api = {
  list: (params = {}) => request.get('/house/ershoufangs', { params }),
  create: (data) => request.post('/house/ershoufangs', data),
  update: (id, data) => request.put(`/house/ershoufangs/${id}`, data),
  delete: (id) => request.delete(`/house/ershoufangs/${id}`)
}

// 修改户型选项定义 - 移到这里
const CUSTOM_LAYOUT_OPTIONS = [
  { label: '一房', value: '一房', dbValue: '1室1厅' },
  { label: '二房', value: '二房', dbValue: '2室1厅' },
  { label: '三房', value: '三房', dbValue: '3室1厅' },
  { label: '四房', value: '四房', dbValue: '4室1厅' },
  { label: '其他', value: '其他', dbValue: '其他' }
]

// 使用 CRUD 函数
const {
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
  ORIENTATION_OPTIONS,
  FLOOR_OPTIONS,
  AREA_OPTIONS,
  showModal,
  modalTitle,
  formParams,
  handleAdd,
  handleEdit,
  handleDelete,
  handleModalSubmit,
  handleModalCancel
} = useErshoufangCRUD(api)

// 选中的城市
const selectedCity = ref(null)

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
    // console.error('初始化失败:', error)
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

// 处理下载模板
const handleDownloadTemplate = () => {
  const link = document.createElement('a')
  link.href = '/templates/ershoufang_import_template.xlsx'
  link.download = '二手房导入模板.xlsx'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 处理批量导入
const handleImport = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.xlsx,.xls,.csv'
  
  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    // console.log('开始上传文件:', file.name)
    
    // 读取并输出文件内容
    if (file.name.endsWith('.csv')) {
      const reader = new FileReader()
      reader.onload = (e) => {
        // console.log('CSV文件内容:', e.target.result)
      }
      reader.readAsText(file)
    }
    
    const formData = new FormData()
    formData.append('file', file)
    formData.append('city', selectedCity.value)
    
    try {
      // console.log('发送请求参数:', {
      //   fileName: file.name,
      //   fileSize: file.size,
      //   city: selectedCity.value
      // })
      
      const res = await request.post('/house/ershoufangs/import', formData)
      // console.log('导入响应:', res)
      
      if (res.code === 200) {
        message.success('导入成功')
        loadData()
      } else {
        message.error(res.msg || '导入失败')
        // console.error('导入失败:', res)
      }
    } catch (error) {
      message.error('导入失败')
      // console.error('导入异常:', error)
    }
  }
  
  input.click()
}
</script>

<style scoped>
.n-space {
  width: 100%;
}

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