<template>
  <CommonPage>
    <n-card :bordered="false" class="proCard">
      <!-- 搜索区域 -->
      <n-space vertical :size="16">
        <!-- 第一行：搜索框和按钮 -->
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
                v-model:value="queryParams.search_keyword"
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
            新增房源
          </n-button>
        </n-space>

        <!-- 第二行：户型和朝向 -->
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

        <!-- 第三行：楼层和面积 -->
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

          <span class="label" style="margin-left: 24px">面积：</span>
          <n-button-group>
            <n-button
              v-for="area in AREA_OPTIONS"
              :key="area.label"
              :type="queryParams.size_range === area.value ? 'primary' : 'default'"
              @click="handleAreaChange(area.value)"
            >
              {{ area.label }}
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
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { request } from '@/utils'
import CommonPage from '@/components/page/CommonPage.vue'
import ErshoufangModal from './components/ErshoufangModal.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import { useErshoufangCRUD } from '@/composables/useErshoufangCRUD'

const message = useMessage()

// API 定义
const api = {
  list: (params = {}) => request.get('/house/ershoufangs', { params }),
  create: (data) => request.post('/house/ershoufangs', data),
  update: (id, data) => request.put(`/house/ershoufangs/${id}`, data),
  delete: (id) => request.delete(`/house/ershoufangs/${id}`)
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
  handleOrientationChange,
  handleFloorChange,
  handleAreaChange,
  handleReset,
  CITY_OPTIONS,
  LAYOUT_OPTIONS,
  ORIENTATION_OPTIONS,
  FLOOR_OPTIONS,
  AREA_OPTIONS,
  showModal,
  modalTitle,
  formParams,
  handleEdit,
  handleDelete
} = useErshoufangCRUD(api)

// 处理新增
const handleAdd = () => {
  modalTitle.value = '新增房源'
  formParams.value = {
    community_id: null,
    community_name: '',
    region: '',
    area: '',
    layout: '',
    floor_number: null,
    total_floors: null,
    orientation: null,
    size: null,
    total_price: null,
    data_source: 'store'
  }
  showModal.value = true
}

// 处理 Modal 提交
const handleModalSubmit = async (formData) => {
  try {
    loading.value = true
    const res = modalTitle.value.includes('新增')
      ? await api.create(formData)
      : await api.update(formData.id, formData)

    if (res.code === 200) {
      message.success(res.msg || '操作成功')
      showModal.value = false
      loadData()
    } else {
      message.error(res.msg || '操作失败')
    }
  } catch (error) {
    console.error('Submit error:', error)
    message.error(error.message || '操作失败')
  } finally {
    loading.value = false
  }
}

// 处理 Modal 取消
const handleModalCancel = () => {
  showModal.value = false
}

// 在组件挂载时加载数据
onMounted(() => {
  console.log('Component mounted, loading data...')
  loadData()
})
</script>

<style scoped>
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
  width: 50px;
  text-align: right;
  margin-right: 8px;
}

.mt-4 {
  margin-top: 16px;
}
</style> 