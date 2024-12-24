import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCityStore = defineStore('city', () => {
  // 默认城市为上海
  const currentCity = ref('shanghai')
  
  // 城市选项
  const CITY_OPTIONS = [
    { label: '上海', value: 'shanghai' },
    { label: '北京', value: 'beijing' },
    { label: '深圳', value: 'shenzhen' },
    { label: '广州', value: 'guangzhou' }
  ]

  // 更改当前城市
  const setCity = (city) => {
    currentCity.value = city
  }

  return {
    currentCity,
    CITY_OPTIONS,
    setCity
  }
}) 