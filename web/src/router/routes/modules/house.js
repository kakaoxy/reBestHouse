export default {
  name: 'House',
  path: '/house',
  component: 'Layout',
  meta: {
    title: '房源管理',
    icon: 'material-symbols:home-outline',
    order: 3
  },
  children: [
    {
      name: 'Community',
      path: 'community',
      component: '/house/community/index',
      meta: {
        title: '小区管理',
        icon: 'material-symbols:location-city'
      }
    },
    {
      name: 'Ershoufang',
      path: 'ershoufang',
      component: '/house/ershoufang/index',
      meta: {
        title: '在售房源',
        icon: 'material-symbols:list'
      }
    }
  ]
} 