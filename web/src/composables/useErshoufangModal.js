import { ref } from 'vue'
import { useDepartmentStore } from '@/stores/department'
import { communityApi } from '@/api'

export function useErshoufangModal() {
  const departmentStore = useDepartmentStore()
  const communityOptions = ref([])
  const loading = ref(false)

  // 加载小区列表
  const loadCommunityOptions = async (params = {}) => {
    try {
      loading.value = true
      // console.log('Loading communities with params:', params)
      const res = await communityApi.list({
        ...params,
        city: departmentStore.currentDepartment,
        page_size: 1000
      })
      // console.log('API response:', res)
      if (res.code === 200) {
        communityOptions.value = res.data.items.map(item => ({
          value: item.id,
          label: item.name,
          city: item.city,
          region: item.region,
          area: item.area
        }))
      }
    } catch (error) {
      console.error('Failed to load communities:', error)
    } finally {
      loading.value = false
    }
  }

  return {
    communityOptions,
    loading,
    loadCommunityOptions
  }
}