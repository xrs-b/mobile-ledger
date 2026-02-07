<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Toast, Dialog } from 'vant'
import { useUserStore } from '@/stores/user'
import { logout } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()
const showLogoutDialog = ref(false)
const activeTab = ref(2)

function goToAdmin() {
  router.push('/admin')
}

function onTabChange(index) {
  if (index === 0) {
    router.push('/dashboard')
  } else if (index === 1) {
    router.push('/projects')
  }
}

function handleLogout() {
  showLogoutDialog.value = true
}

async function confirmLogout() {
  try {
    await logout()
  } catch (error) {
    // Ignore logout API error
  }
  
  userStore.doLogout()
  Toast.success('已退出登录')
  router.replace('/login')
}

function clearCache() {
  Dialog.alert({
    title: '清除缓存',
    message: '缓存已清除',
  })
}

function about() {
  Dialog.alert({
    title: '关于',
    message: 'Mobile Ledger v1.0.0\n\n轻量级记账应用',
  })
}
</script>

<template>
  <div class="profile-page">
    <!-- User Info -->
    <div class="user-card">
      <div class="avatar">👤</div>
      <div class="user-info">
        <div class="username">{{ userStore.userInfo?.username || '用户' }}</div>
        <div class="user-id" v-if="userStore.userInfo?.id">
          ID: {{ userStore.userInfo.id }}
        </div>
        <div class="user-role" v-if="userStore.userInfo?.is_admin">
          管理员
        </div>
      </div>
    </div>

    <!-- Menu List -->
    <div class="menu-section">
      <van-cell-group inset>
        <van-cell title="个人信息" is-link @click="() => {}">
          <template #icon>
            <span class="menu-icon">👤</span>
          </template>
        </van-cell>
        <van-cell 
          v-if="userStore.userInfo?.is_admin" 
          title="管理后台" 
          is-link 
          @click="goToAdmin"
        >
          <template #icon>
            <span class="menu-icon">⚙️</span>
          </template>
        </van-cell>
        <van-cell title="清除缓存" is-link @click="clearCache">
          <template #icon>
            <span class="menu-icon">🗑️</span>
          </template>
        </van-cell>
        <van-cell title="关于" is-link @click="about">
          <template #icon>
            <span class="menu-icon">ℹ️</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <!-- Logout -->
    <div class="logout-section">
      <van-button 
        type="default" 
        block 
        @click="handleLogout"
      >
        退出登录
      </van-button>
    </div>

    <!-- Logout Dialog -->
    <van-dialog 
      v-model:show="showLogoutDialog" 
      title="退出登录"
      message="确定要退出登录吗？"
      show-cancel-button
      @confirm="confirmLogout"
    />

    <!-- TabBar -->
    <van-tabbar v-model="activeTab" @change="onTabChange">
      <van-tabbar-item name="dashboard" icon="home-o">首页</van-tabbar-item>
      <van-tabbar-item name="projects" icon="todo-list-o">项目</van-tabbar-item>
      <van-tabbar-item name="profile" icon="user-o">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'Profile',
  setup() {
    const active = ref(2)
    return { active }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}

.user-card {
  display: flex;
  align-items: center;
  padding: 32px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 32px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin-right: 16px;
}

.user-info {
  color: #fff;
}

.username {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 4px;
}

.user-id {
  font-size: 12px;
  opacity: 0.8;
  margin-bottom: 4px;
}

.user-role {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  font-size: 12px;
}

.menu-section {
  margin-top: 16px;
}

.menu-icon {
  margin-right: 12px;
  font-size: 18px;
}

.logout-section {
  padding: 24px 16px;
  margin-top: 24px;
}

.logout-section .van-button {
  border-radius: 8px;
}
</style>
