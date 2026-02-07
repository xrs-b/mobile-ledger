<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Toast, Dialog } from 'vant'
import { useUserStore } from '@/stores/user'
import { getUsers, disableUser, enableUser, deleteUser } from '@/api/admin'
import { getInvitationCodes, createInvitationCode, deleteInvitationCode } from '@/api/invitation'

const router = useRouter()
const userStore = useUserStore()
const activeTab = ref(0)
const loading = ref(false)

// Users
const users = ref([])
const userPage = ref(1)
const userTotal = ref(0)

// Invitations
const invitations = ref([])
const invPage = ref(1)
const invTotal = ref(0)

// Invitation form
const showInvDialog = ref(false)
const newInvCode = ref('')
const newInvDays = ref(30)

// Check if admin
const isAdmin = computed(() => userStore.userInfo?.is_admin)

onMounted(() => {
  if (!isAdmin.value) {
    Toast.fail('只有管理员可以访问')
    router.push('/dashboard')
    return
  }
  fetchUsers()
  fetchInvitations()
})

// Users
async function fetchUsers() {
  loading.value = true
  try {
    const res = await getUsers({ page: userPage.value })
    users.value = res.users || []
    userTotal.value = res.total || 0
  } catch (error) {
    Toast.fail(error.message || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

async function handleDisableUser(user) {
  try {
    await Dialog.confirm({
      title: '确认禁用',
      message: `确定要禁用用户 "${user.username}" 吗？`
    })
    
    await disableUser(user.id)
    Toast.success('已禁用')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      Toast.fail(error.message || '操作失败')
    }
  }
}

async function handleEnableUser(user) {
  try {
    await Dialog.confirm({
      title: '确认启用',
      message: `确定要启用用户 "${user.username}" 吗？`
    })
    
    await enableUser(user.id)
    Toast.success('已启用')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      Toast.fail(error.message || '操作失败')
    }
  }
}

async function handleDeleteUser(user) {
  try {
    await Dialog.confirm({
      title: '确认删除',
      message: `确定要删除用户 "${user.username}" 吗？此操作不可恢复！`
    })
    
    await deleteUser(user.id)
    Toast.success('已删除')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      Toast.fail(error.message || '操作失败')
    }
  }
}

// Invitations
async function fetchInvitations() {
  loading.value = true
  try {
    const res = await getInvitationCodes({ page: invPage.value })
    invitations.value = res.codes || []
    invTotal.value = res.total || 0
  } catch (error) {
    Toast.fail(error.message || '获取邀请码列表失败')
  } finally {
    loading.value = false
  }
}

async function handleCreateInvitation() {
  if (!newInvCode.value) {
    Toast.fail('请输入邀请码')
    return
  }
  
  try {
    await createInvitationCode({
      code: newInvCode.value,
      valid_days: newInvDays.value
    })
    Toast.success('创建成功')
    showInvDialog.value = false
    newInvCode.value = ''
    fetchInvitations()
  } catch (error) {
    Toast.fail(error.message || '创建失败')
  }
}

async function handleDeleteInvitation(code) {
  try {
    await Dialog.confirm({
      title: '确认删除',
      message: `确定要删除邀请码 "${code.code}" 吗？`
    })
    
    await deleteInvitationCode(code.id)
    Toast.success('已删除')
    fetchInvitations()
  } catch (error) {
    if (error !== 'cancel') {
      Toast.fail(error.message || '删除失败')
    }
  }
}

function openCreateDialog() {
  // 生成随机邀请码
  newInvCode.value = 'INV' + Math.random().toString(36).substr(2, 6).toUpperCase()
  showInvDialog.value = true
}

function getStatusColor(isActive) {
  return isActive ? '#07c160' : '#969799'
}

function getStatusText(isActive) {
  return isActive ? '正常' : '禁用'
}

function getUsedStatus(isUsed) {
  return isUsed ? '#ee0a24' : '#07c160'
}
</script>

<template>
  <div class="admin-page">
    <!-- Header -->
    <van-nav-bar title="管理后台" />

    <!-- Admin Info -->
    <div class="admin-banner">
      <span class="admin-badge">管理员</span>
      <span class="admin-text">用户管理 & 邀请码管理</span>
    </div>

    <!-- Tabs -->
    <van-tabs v-model:active="activeTab">
      <!-- Users Tab -->
      <van-tab title="用户管理">
        <div class="tab-content">
          <van-loading v-if="loading" size="24px">加载中...</van-loading>
          
          <div v-else-if="users.length > 0" class="user-list">
            <div v-for="user in users" :key="user.id" class="user-item">
              <div class="user-info">
                <div class="user-name">{{ user.username }}</div>
                <div class="user-meta">
                  <van-tag :color="getStatusColor(user.is_active)" size="small">
                    {{ getStatusText(user.is_active) }}
                  </van-tag>
                  <span class="record-count">{{ user.record_count || 0 }} 条记录</span>
                </div>
              </div>
              <div class="user-actions">
                <van-button 
                  v-if="user.is_active" 
                  size="small" 
                  type="warning"
                  @click="handleDisableUser(user)"
                >
                  禁用
                </van-button>
                <van-button 
                  v-else 
                  size="small" 
                  type="primary"
                  @click="handleEnableUser(user)"
                >
                  启用
                </van-button>
                <van-button 
                  size="small" 
                  type="danger" 
                  plain
                  @click="handleDeleteUser(user)"
                >
                  删除
                </van-button>
              </div>
            </div>
          </div>
          
          <van-empty v-else description="暂无用户" />
        </div>
      </van-tab>

      <!-- Invitations Tab -->
      <van-tab title="邀请码管理">
        <div class="tab-content">
          <div class="action-bar">
            <van-button type="primary" size="small" @click="openCreateDialog">
              + 生成邀请码
            </van-button>
          </div>
          
          <van-loading v-if="loading" size="24px">加载中...</van-loading>
          
          <div v-else-if="invitations.length > 0" class="inv-list">
            <div v-for="code in invitations" :key="code.id" class="inv-item">
              <div class="inv-code">{{ code.code }}</div>
              <div class="inv-meta">
                <van-tag :color="getUsedStatus(code.is_used)" size="small">
                  {{ code.is_used ? '已使用' : '未使用' }}
                </van-tag>
                <span v-if="code.used_by_name" class="used-by">
                  用户: {{ code.used_by_name }}
                </span>
              </div>
              <div class="inv-actions">
                <van-button 
                  v-if="!code.is_used"
                  size="small" 
                  type="danger" 
                  plain
                  @click="handleDeleteInvitation(code)"
                >
                  删除
                </van-button>
              </div>
            </div>
          </div>
          
          <van-empty v-else description="暂无邀请码" />
        </div>
      </van-tab>
    </van-tabs>

    <!-- Create Invitation Dialog -->
    <van-dialog 
      v-model:show="showInvDialog" 
      title="生成邀请码"
      show-cancel-button
      @confirm="handleCreateInvitation"
    >
      <van-form>
        <van-field
          v-model="newInvCode"
          label="邀请码"
          placeholder="请输入邀请码"
        />
        <van-field
          v-model.number="newInvDays"
          type="digit"
          label="有效天数"
          placeholder="请输入有效天数"
        />
      </van-form>
    </van-dialog>
  </div>
</template>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}

.admin-banner {
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  text-align: center;
}

.admin-badge {
  display: inline-block;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  font-size: 14px;
  margin-bottom: 8px;
}

.admin-text {
  display: block;
  font-size: 14px;
  opacity: 0.9;
}

.tab-content {
  padding: 16px;
}

.action-bar {
  margin-bottom: 16px;
}

.user-list, .inv-list {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.user-item, .inv-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #f5f5f5;
}

.user-item:last-child, .inv-item:last-child {
  border-bottom: none;
}

.user-name, .inv-code {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.user-meta, .inv-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.record-count, .used-by {
  font-size: 12px;
  color: #969799;
}

.user-actions, .inv-actions {
  display: flex;
  gap: 8px;
}
</style>
