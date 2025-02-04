import { defineStore } from 'pinia'

export const useCityStore = defineStore('city', {
  state: () => ({
    currentCity: 'shanghai',
    CITY_OPTIONS: [
      { label: '上海市', value: 'shanghai' },
      { label: '北京市', value: 'beijing' },
      { label: '广州市', value: 'guangzhou' },
      { label: '深圳市', value: 'shenzhen' }
    ]
  }),
  actions: {
    setCurrentCity(city) {
      this.currentCity = city
    }
  }
}) 