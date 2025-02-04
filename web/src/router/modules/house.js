export default {
  name: 'house',
  path: '/house',
  component: Layout,
  meta: {
    title: '房源管理'
  },
  children: [
    {
      name: 'community',
      path: 'community',
      component: () => import('@/views/house/community/index.vue'),
      meta: {
        title: '小区信息'
      }
    },
    {
      name: 'ershoufang',
      path: 'ershoufang',
      component: () => import('@/views/house/ershoufang/index.vue'),
      meta: {
        title: '在售房源'
      }
    },
    {
      name: 'deal-record',
      path: 'deal-record',
      component: () => import('@/views/house/deal-record/index.vue'),
      meta: {
        title: '成交记录',
        icon: ''
      }
    },
    {
      name: 'project',
      path: 'project',
      component: () => import('@/views/house/project/index.vue'),
      meta: {
        title: '项目管理',
        icon: 'material-symbols:home-repair-service'
      }
    }
  ]
} 