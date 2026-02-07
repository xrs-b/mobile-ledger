<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Toast } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const invitationCode = ref('')
const loading = ref(false)

async function handleRegister() {
  if (!username.value || !password.value) {
    Toast.fail('请填写必要信息')
    return
  }
  
  if (password.value !== confirmPassword.value) {
    Toast.fail('两次密码不一致')
    return
  }
  
  if (password.value.length < 6) {
    Toast.fail('密码至少6位')
    return
  }
  
  loading.value = true
  const result = await userStore.doRegister(
    username.value, 
    password.value, 
    invitationCode.value
  )
  loading.value = false
  
  if (result.success) {
    Toast.success('注册成功')
    router.replace('/dashboard')
  } else {
    Toast.fail(result.message || '注册失败')
  }
}

function goToLogin() {
  router.push('/login')
}
</script>

<template>
  <div class="register-page">
    <div class="header">
      <h1>📝 注册</h1>
      <p>创建您的账户</p>
    </div>
    
    <div class="form-section">
      <van-form @submit="handleRegister">
        <van-field
          v-model="username"
          name="username"
          label="用户名"
          placeholder="请输入用户名（至少3位）"
          :rules="[{ required: true, message: '请输入用户名' }]"
        />
        <van-field
          v-model="password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码（至少6位）"
          :rules="[{ required: true, message: '请输入密码' }]"
        />
        <van-field
          v-model="confirmPassword"
          type="password"
          name="confirmPassword"
          label="确认密码"
          placeholder="请再次输入密码"
          :rules="[{ required: true, message: '请确认密码' }]"
        />
        <van-field
          v-model="invitationCode"
          name="invitationCode"
          label="邀请码"
          placeholder="请输入邀请码（选填）"
        />
        <div class="btn-section">
          <van-button 
            type="primary" 
            native-type="submit" 
            block 
            :loading="loading"
          >
            注册
          </van-button>
          <van-button 
            plain 
            hairline 
            block 
            class="mt-12"
            @click="goToLogin"
          >
            已有账号？去登录
          </van-button>
        </div>
      </van-form>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding: 24px;
}

.header {
  text-align: center;
  margin-bottom: 32px;
  padding-top: 32px;
}

.header h1 {
  font-size: 28px;
  color: #323233;
  margin-bottom: 8px;
}

.header p {
  color: #969799;
  font-size: 14px;
}

.form-section {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
}

.btn-section {
  margin-top: 24px;
}

.mt-12 {
  margin-top: 12px;
}
</style>
