import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/reservations'
    },
    {
      path: '/reservations',
      name: 'Reservations',
      component: () => import('@/views/Reservations.vue'),
      meta: { title: '预约排期' }
    },
    {
      path: '/tea-plans',
      name: 'TeaPlans',
      component: () => import('@/views/TeaPlans.vue'),
      meta: { title: '主题方案' }
    },
    {
      path: '/utensils',
      name: 'Utensils',
      component: () => import('@/views/Utensils.vue'),
      meta: { title: '器物库' }
    },
    {
      path: '/borrow-lists',
      name: 'BorrowLists',
      component: () => import('@/views/BorrowLists.vue'),
      meta: { title: '布席清单' }
    },
    {
      path: '/reviews',
      name: 'Reviews',
      component: () => import('@/views/Reviews.vue'),
      meta: { title: '活动复盘' }
    },
    {
      path: '/statistics',
      name: 'Statistics',
      component: () => import('@/views/Statistics.vue'),
      meta: { title: '数据统计' }
    }
  ]
})

export default router
