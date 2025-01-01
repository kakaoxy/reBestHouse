import { ref } from 'vue'
import { useCityStore } from '@/stores/city'
import { request } from '@/utils'

export function useErshoufangModal() {
  const cityStore = useCityStore()
  const communityOptions = ref([])
  const loading = ref(false)

  // 加载小区列表
  const loadCommunityOptions = async () => {
    try {
      loading.value = true
      const res = await request.get('/house/communities', {
        params: {
          city: cityStore.currentCity,
          page_size: 1000
        }
      })
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