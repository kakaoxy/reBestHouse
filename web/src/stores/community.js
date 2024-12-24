import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCommunityStore = defineStore('community', () => {
  const CITY_OPTIONS = [
    { label: '上海', value: 'shanghai' },
    { label: '北京', value: 'beijing' }
  ]

  // 默认城市改为上海
  const currentCity = ref('shanghai')

  const setCity = (city) => {
    currentCity.value = city
  }

  return {
    CITY_OPTIONS,
    currentCity,
    setCity
  }
}, {
  persist: true
}) 