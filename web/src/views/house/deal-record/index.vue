<template>
  <CommonPage>
    <n-card :bordered="false" class="proCard">
      <n-space vertical :size="16">
        <!-- 顶部操作栏 -->
        <n-space vertical :size="12">
          <!-- 第一行：城市选择和搜索 -->
          <n-space justify="space-between">
            <!-- 左侧搜索区域 -->
            <n-space align="center" :size="8">
              <n-select
                v-model:value="cityStore.currentCity"
                :options="cityStore.CITY_OPTIONS"
                style="width: 120px"
                @update:value="handleCityChange"
              />
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
            
            <!-- 右侧新增按钮 -->
            <n-button type="primary" @click="handleAdd">
              <template #icon>
                <TheIcon icon="material-symbols:add" />
              </template>
              新增成交
            </n-button>
          </n-space>

          <!-- 第二行：筛选条件 -->
          <n-space align="center" :size="24">
            <n-space align="center">
              <span class="label">户型：</span>
              <n-button-group>
                <n-button
                  v-for="option in LAYOUT_OPTIONS"
                  :key="option.value"
                  :type="queryParams.layout === option.value ? 'primary' : 'default'"
                  @click="handleLayoutChange(option.value)"
                >
                  {{ option.label }}
                </n-button>
              </n-button-group>
            </n-space>

            <n-space align="center">
              <span class="label">楼层：</span>
              <n-button-group>
                <n-button
                  v-for="option in FLOOR_OPTIONS"
                  :key="option.value"
                  :type="queryParams.floor_info === option.value ? 'primary' : 'default'"
                  @click="handleFloorChange(option.value)"
                >
                  {{ option.label }}
                </n-button>
              </n-button-group>
            </n-space>
          </n-space>
        </n-space>

        <!-- 数据表格 -->
        <n-data-table
          :loading="loading"
          :columns="columns"
          :data="data"
          :pagination="pagination"
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
          @update:sorter="handleSorterChange"
        />
      </n-space>
    </n-card>

    <!-- Modal 组件 -->
    <deal-record-modal
      v-model:show="showModal"
      :title="modalTitle"
      :loading="modalLoading"
      :form-value="formValue"
      @submit="handleSubmit"
      @cancel="handleModalCancel"
    />
  </CommonPage>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useMessage } from 'naive-ui'
import { useCityStore } from '@/stores/city'
import { useDealRecordCRUD } from '@/composables/useDealRecordCRUD'
import { dealRecordApi } from '@/api/house'
import CommonPage from '@/components/page/CommonPage.vue'
import DealRecordModal from './components/DealRecordModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

const message = useMessage()
const cityStore = useCityStore()

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
  handleReset,
  LAYOUT_OPTIONS,
  FLOOR_OPTIONS,
  showModal,
  modalTitle,
  modalLoading,
  formValue,
  handleSubmit
} = useDealRecordCRUD(dealRecordApi)

// 处理城市变化
const handleCityChange = (value) => {
  cityStore.setCurrentCity(value)
  queryParams.city = value
  pagination.page = 1
  queryParams.search_keyword = ''
  queryParams.layout = undefined
  queryParams.floor_info = undefined
  loadData()
}

// 搜索处理
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 新增处理
const handleAdd = () => {
  formValue.value = {
    source: 'manual',
    city: cityStore.currentCity
  }
  modalTitle.value = '新增成交'
  showModal.value = true
}

// 取消处理
const handleModalCancel = () => {
  showModal.value = false
  formValue.value = {}
}

// 在组件挂载时加载数据
onMounted(() => {
  queryParams.city = cityStore.currentCity
  loadData()
})

// 监听全局城市变化
watch(() => cityStore.currentCity, (newCity) => {
  if (newCity !== queryParams.city) {
    queryParams.city = newCity
    pagination.page = 1
    queryParams.search_keyword = ''
    queryParams.layout = undefined
    queryParams.floor_info = undefined
    loadData()
  }
}, { immediate: true })
</script>

<style scoped>
.proCard {
  margin: 16px;
}

.n-space {
  width: 100%;
}

.n-button-group {
  display: inline-flex;
  gap: 4px;
}

.n-button-group .n-button {
  min-width: 80px;
  padding: 0 16px;
}

.label {
  display: inline-block;
  min-width: 50px;
  color: #666;
  font-size: 14px;
}
</style> 