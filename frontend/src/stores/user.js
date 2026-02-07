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
      token.value = res.token || res.access_token
      localStorage.setItem('token', token.value)
      
      // Get user profile
      userInfo.value = await getProfile()
      return { success: true }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, message: error.message || '登录失败' }
    } finally {
      loading.value = false
    }
  }

  async function doRegister(username, password, invitationCode) {
    loading.value = true
    try {
      const res = await register(username, password, invitationCode)
      console.log('Register response:', res)
      
      // 尝试从响应中获取 token
      // 兼容两种格式：res.token 或 res.access_token
      token.value = res.token || res.access_token
      
      if (token.value) {
        // 保存 token
        localStorage.setItem('token', token.value)
        console.log('Token saved:', token.value)
        
        // 获取用户信息
        try {
          userInfo.value = await getProfile()
        } catch (e) {
          console.error('Failed to get profile:', e)
        }
        
        return { success: true }
      } else {
        // 如果没有返回 token，尝试自动登录
        console.log('No token in register response, trying auto-login...')
        return await doLogin(username, password)
      }
    } catch (error) {
      console.error('Register error:', error)
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
