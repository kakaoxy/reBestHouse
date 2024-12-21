<template>
  <div class="query-bar" :class="{ 'mb-30': mb30 }">
    <n-space wrap>
      <slot />
    </n-space>
    <div class="action">
      <slot name="action">
        <n-space>
          <n-button type="primary" @click="$emit('search')">
            <template #icon>
              <TheIcon icon="material-symbols:search" :size="18" />
            </template>
            搜索
          </n-button>
          <n-button @click="$emit('reset')">
            <template #icon>
              <TheIcon icon="material-symbols:refresh" :size="18" />
            </template>
            重置
          </n-button>
        </n-space>
      </slot>
    </div>
  </div>
</template>

<script setup>
import { NSpace, NButton } from 'naive-ui'
import TheIcon from '@/components/icon/TheIcon.vue'

defineProps({
  mb30: {
    type: Boolean,
    default: true,
  },
})

defineEmits(['search', 'reset'])
</script>

<style lang="scss" scoped>
.query-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: flex-start;

  &.mb-30 {
    margin-bottom: 30px;
  }

  .action {
    margin-left: auto;
  }
}
</style>
