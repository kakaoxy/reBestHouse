export default {
  name: '基础数据',
  path: '/house',
  component: 'Layout',
  meta: {
    icon: 'material-symbols:home',
    order: 0
  },
  children: [
    {
      name: '在售房源',
      path: 'ershoufang',
      component: 'house/ershoufang/index',
      meta: {
        icon: 'material-symbols:home-outline',
        order: 1
      }
    }
  ]
} 