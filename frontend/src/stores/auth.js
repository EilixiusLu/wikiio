import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI, userAPI } from '../api/index.js'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('access_token'))

  const isLoggedIn = computed(() => !!token.value)

  // 登录
  async function login(email, password) {
    const data = await authAPI.login({ email, password })
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('access_token', data.access_token)
  }

  // 注册
  async function register(email, username, password) {
    return await authAPI.register({ email, username, password })
  }

  // 获取当前用户信息
  async function fetchMe() {
    if (!token.value) return
    try {
      user.value = await userAPI.getMe()
    } catch {
      logout()
    }
  }

  // 登出
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
  }

  return { user, token, isLoggedIn, login, register, fetchMe, logout }
})