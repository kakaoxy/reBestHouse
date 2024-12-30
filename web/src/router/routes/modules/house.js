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
    },
    {
      name: 'DealRecord',
      path: 'deal-record',
      component: '/house/deal-record/index',
      meta: {
        title: '成交记录',
        icon: 'material-symbols:real-estate-agent'
      }
    },
    {
      path: 'opportunity',
      name: 'Opportunity',
      component: () => import('@/views/house/opportunity/index.vue'),
      meta: {
        title: '商机管理',
        icon: 'material-symbols:business-center-outline'
      }
    }
  ]
} 