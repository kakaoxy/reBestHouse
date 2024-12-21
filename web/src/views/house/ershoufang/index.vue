<script setup>
import { h, onMounted, ref, resolveDirective } from 'vue'
import { NButton, NSelect, NInput } from 'naive-ui'
import CommonPage from '@/components/page/CommonPage.vue'
import QueryBarItem from '@/components/query-bar/QueryBarItem.vue'
import CrudTable from '@/components/table/CrudTable.vue'
import TheIcon from '@/components/icon/TheIcon.vue'
import api from '@/api'

defineOptions({ name: '在售房源' })

const $table = ref(null)
const queryItems = ref({
  city: '上海',
  community: ''
})

// 城市选项
const cityOptions = [
  { label: '上海', value: '上海' },
  { label: '北京', value: '北京' },
  { label: '广州', value: '广州' },
  { label: '深圳', value: '深圳' }
]

// 重置搜索
function handleReset() {
  queryItems.value = {
    city: '上海',
    community: ''
  }
  $table.value?.handleSearch()
}

onMounted(() => {
  $table.value?.handleSearch()
})

const columns = [
  {
    title: '区域',
    key: 'district',
    width: 100,
    align: 'center',
    render(row) {
      return row.区域 || '-'
    }
  },
  {
    title: '商圈',
    key: 'area',
    width: 100,
    align: 'center',
    render(row) {
      return row.商圈 || '-'
    }
  },
  {
    title: '小区名',
    key: 'community',
    width: 180,
    align: 'center',
    render(row) {
      return h(
        'a',
        {
          href: row.房源链接,
          target: '_blank',
          style: 'color: #18a058; text-decoration: none;'
        },
        row.小区名
      )
    }
  },
  {
    title: '户型',
    key: 'layout',
    width: 100,
    align: 'center',
    sorter: true,
    render(row) {
      return row.户型 || '-'
    }
  },
  {
    title: '面积(㎡)',
    key: 'area',
    width: 100,
    align: 'center',
    render(row) {
      return row.面积 ? row.面积.toFixed(2) : '-'
    }
  },
  {
    title: '楼层',
    key: 'floor',
    width: 120,
    align: 'center',
    render(row) {
      return row.楼层 || '-'
    }
  },
  {
    title: '朝向',
    key: 'direction',
    width: 100,
    align: 'center',
    render(row) {
      return row.朝向 || '-'
    }
  },
  {
    title: '总价(万)',
    key: 'total_price',
    width: 100,
    align: 'center',
    sorter: true,
    render(row) {
      return row.总价 ? row.总价.toFixed(0) : '-'
    }
  },
  {
    title: '单价(元/㎡)',
    key: 'unit_price',
    width: 120,
    align: 'center',
    sorter: true,
    render(row) {
      return row.单价 ? row.单价.toFixed(0) : '-'
    }
  },
  {
    title: '挂牌时间',
    key: 'list_time',
    width: 120,
    align: 'center',
    sorter: true,
    render(row) {
      return row.挂牌时间 || '-'
    }
  },
  {
    title: '上次交易',
    key: 'last_deal',
    width: 120,
    align: 'center',
    render(row) {
      return row.上次交易 || '-'
    }
  }
]
</script>

<template>
  <CommonPage show-footer title="在售房源列表">
    <!-- 表格 -->
    <CrudTable
      ref="$table"
      v-model:query-items="queryItems"
      :columns="columns"
      :get-data="api.getErshoufangList"
      :pagination="{
        pageSize: 20
      }"
    >
      <template #queryBar>
        <QueryBarItem label="城市" :label-width="40">
          <NSelect
            v-model:value="queryItems.city"
            :options="cityOptions"
            clearable
            @update:value="$table?.handleSearch()"
          />
        </QueryBarItem>
        <QueryBarItem label="小区名" :label-width="55">
          <NInput
            v-model:value="queryItems.community"
            type="text"
            clearable
            placeholder="请输入小区名"
            @keydown.enter="$table?.handleSearch()"
          />
        </QueryBarItem>
      </template>
    </CrudTable>
  </CommonPage>
</template> 