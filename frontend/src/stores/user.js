import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, register, getProfile, logout } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const loading = ref(false)

  const isLoggedIn = computed(() => !!token.value)

  async function doLogin(username, password) {
    loading.value = true
    try {
      const res = await login(username, password)
      token.value = res.access_token
      localStorage.setItem('token', token.value)
      
      // Get user profile
      userInfo.value = await getProfile()
      return { success: true }
    } catch (error) {
      return { success: false, message: error.message || '登录失败' }
    } finally {
      loading.value = false
    }
  }

  async function doRegister(username, password, invitationCode) {
    loading.value = true
    try {
      await register(username, password, invitationCode)
      // Auto login after register
      return await doLogin(username, password)
    } catch (error) {
      return { success: false, message: error.message || '注册失败' }
    } finally {
      loading.value = false
    }
  }

  async function fetchUserInfo() {
    if (!token.value) return
    try {
      userInfo.value = await getProfile()
    } catch (error) {
      console.error('Failed to fetch user info:', error)
    }
  }

  function doLogout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    loading,
    isLoggedIn,
    doLogin,
    doRegister,
    fetchUserInfo,
    doLogout
  }
})
