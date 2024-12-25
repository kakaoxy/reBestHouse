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
            <!-- 搜索框 -->
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
            新增成交记录
          </n-button>
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
    <DealRecordModal
      v-model:show="showModal"
      :title="modalTitle"
      :form-value="formValue"
      :loading="modalLoading"
      @submit="handleSubmit"
      @cancel="handleModalCancel"
    />
  </CommonPage>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { useCityStore } from '@/stores/city'
import { useDealRecordCRUD } from '@/composables/useDealRecordCRUD'
import { dealRecordApi } from '@/api/house'
import CommonPage from '@/components/page/CommonPage.vue'
import DealRecordModal from './components/DealRecordModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'

const message = useMessage()
const cityStore = useCityStore()

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
  handleReset,
  LAYOUT_OPTIONS,
  FLOOR_OPTIONS,
  showModal,
  modalTitle,
  modalLoading,
  formValue,
  handleDelete
} = useDealRecordCRUD(dealRecordApi)

// 处理城市变化
const handleCityChange = (value) => {
  queryParams.city = value
  loadData()
}

// 处理新增
const handleAdd = () => {
  modalTitle.value = '新增成交记录'
  formValue.value = {
    source: 'manual',
    city: cityStore.currentCity
  }
  showModal.value = true
}

// 处理提交
const handleSubmit = async (data) => {
  modalLoading.value = true
  try {
    if (data.id) {
      await dealRecordApi.update(data.id, data)
    } else {
      await dealRecordApi.create(data)
    }
    message.success('操作成功')
    showModal.value = false
    loadData()
  } catch (error) {
    console.error('Submit error:', error)
    message.error('操作失败')
  } finally {
    modalLoading.value = false
  }
}

// 处理 Modal 取消
const handleModalCancel = () => {
  showModal.value = false
}

// 在组件挂载时加载数据
onMounted(() => {
  queryParams.city = cityStore.currentCity
  loadData()
})
</script>

<style scoped>
.proCard {
  margin: 16px;
}

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