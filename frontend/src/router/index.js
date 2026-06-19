import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: () => import('../views/Home.vue') },
    { path: '/login', component: () => import('../views/Login.vue') },
    { path: '/register', component: () => import('../views/Register.vue') },
    { path: '/profile', component: () => import('../views/Profile.vue'), meta: { requiresAuth: true } },
    { path: '/search', component: () => import('../views/Search.vue') },
    { path: '/admin', component: () => import('../views/Admin.vue'), meta: { requiresAuth: true } },
    { path: '/rankings', component: () => import('../views/Rankings.vue') },
    { path: '/author/:author', component: () => import('../views/Author.vue') },
    { path: '/mh-author/:author', component: () => import('../views/MhAuthor.vue') },
    { path: '/fd-author/:author', component: () => import('../views/FdAuthor.vue') },
    { path: '/page/:id', component: () => import('../views/PageDetail.vue') },
    { path: '/wiki/:siteId', component: () => import('../views/WikiStats.vue') },
    { path: '/about', component: () => import('../views/About.vue') },
    { path: '/datasources', component: () => import('../views/DataSources.vue') },
    { path: '/verify-email', component: () => import('../views/VerifyEmail.vue') },
    { path: '/resend-verification', component: () => import('../views/ResendVerification.vue') },
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
