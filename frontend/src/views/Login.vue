<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Toast } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value || !password.value) {
    Toast.fail('请输入用户名和密码')
    return
  }
  
  loading.value = true
  const result = await userStore.doLogin(username.value, password.value)
  loading.value = false
  
  if (result.success) {
    Toast.success('登录成功')
    const redirect = route.query.redirect || '/dashboard'
    router.replace(redirect)
  } else {
    Toast.fail(result.message || '登录失败')
  }
}

function goToRegister() {
  router.push('/register')
}
</script>

<template>
  <div class="login-page">
    <div class="logo-section">
      <h1>💰 Mobile Ledger</h1>
      <p class="subtitle">轻量级记账应用</p>
    </div>
    
    <div class="form-section">
      <van-form @submit="handleLogin">
        <van-field
          v-model="username"
          name="username"
          label="用户名"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请输入用户名' }]"
        />
        <van-field
          v-model="password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请输入密码' }]"
        />
        <div class="btn-section">
          <van-button 
            type="primary" 
            native-type="submit" 
            block 
            :loading="loading"
          >
            登录
          </van-button>
          <van-button 
            plain 
            hairline 
            block 
            class="mt-12"
            @click="goToRegister"
          >
            还没有账号？去注册
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 24px;
}

.logo-section {
  text-align: center;
  color: #fff;
  margin-bottom: 48px;
}

.logo-section h1 {
  font-size: 32px;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  opacity: 0.8;
}

.form-section {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.btn-section {
  margin-top: 24px;
}

.mt-12 {
  margin-top: 12px;
}
</style>
