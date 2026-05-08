import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('../views/Home.vue') },
    { path: '/login', component: () => import('../views/Login.vue') },
    { path: '/register', component: () => import('../views/Register.vue') },
    { path: '/profile', component: () => import('../views/Profile.vue'), meta: { requiresAuth: true } },
    { path: '/page/:id', component: () => import('../views/PageDetail.vue') },
    { path: '/search', component: () => import('../views/Search.vue') },
    { path: '/admin', component: () => import('../views/Admin.vue'), meta: { requiresAuth: true } },
    { path: '/rankings', component: () => import('../views/Rankings.vue') },
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
