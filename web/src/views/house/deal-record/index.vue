<template>
  <CommonPage>
    <n-card :bordered="false" class="proCard">
      <n-space vertical :size="16">
        <!-- 顶部操作栏 -->
        <n-space justify="space-between" align="center">
          <n-space align="center" :size="8">
            <!-- 城市选择器 -->
            <n-select
              v-model:value="cityStore.currentCity"
              :options="cityStore.CITY_OPTIONS"
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
            新增成交
          </n-button>
        </n-space>

        <!-- 筛选条件 -->
        <n-space vertical :size="12">
          <!-- 户型和楼层在同一行 -->
          <n-space align="center" justify="start">
            <span class="label">户型：</span>
            <n-button-group>
              <n-button
                v-for="layout in LAYOUT_OPTIONS"
                :key="layout.value"
                :type="queryParams.layout === layout.value ? 'primary' : 'default'"
                @click="handleLayoutChange(layout.value)"
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
          class="mt-4"
          :columns="columns"
          :data="data"
          :loading="loading"
          :pagination="pagination"
          remote
          :row-key="row => row.id"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
          @update:sorter="handleSorterChange"
        />
      </n-space>
    </n-card>

    <!-- Modal 组件 -->
    <DealRecordModal
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
import { ref, onMounted, reactive } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { request } from '@/utils'
import CommonPage from '@/components/page/CommonPage.vue'
import DealRecordModal from './components/DealRecordModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import { useDealRecordCRUD } from '@/composables/useDealRecordCRUD'
import { useCityStore } from '@/stores/city'

const message = useMessage()
const dialog = useDialog()
const cityStore = useCityStore()

// API 定义 - 修正重复的 API 路径
const api = {
  list: (params = {}) => request.get('/house/deal-records', { params }),
  create: (data) => request.post('/house/deal-records', data),
  update: (id, data) => request.put(`/house/deal-records/${id}`, data),
  delete: (id) => request.delete(`/house/deal-records/${id}`)
}

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
  handleFloorChange,
  LAYOUT_OPTIONS,
  FLOOR_OPTIONS,
  showModal,
  modalTitle,
  formParams,
  handleAdd,
  handleEdit,
  handleDelete,
  handleModalSubmit,
  handleModalCancel,
  handleReset
} = useDealRecordCRUD(api)

// 处理城市变化
const handleCityChange = async (city) => {
  try {
    cityStore.setCurrentCity(city)
    queryParams.city = city
    await loadData()
  } catch (error) {
    message.error('加载数据失败：' + (error.message || '未知错误'))
  }
}

// 在组件挂载时加载数据，并设置默认城市
onMounted(async () => {
  try {
    queryParams.city = cityStore.currentCity
    await loadData()
  } catch (error) {
    message.error('加载数据失败：' + (error.message || '未知错误'))
  }
})
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