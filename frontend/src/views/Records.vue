<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Toast } from 'vant'
import { formatAmount, getTypeLabel, getAmountColor } from '@/utils/amount'
import { formatDate } from '@/utils/date'
import { getRecords, deleteRecord } from '@/api/record'

const router = useRouter()
const records = ref([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const hasMore = ref(true)

const groupedRecords = computed(() => {
  const groups = {}
  records.value.forEach(record => {
    const date = formatDate(record.record_date, 'YYYY-MM-DD')
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(record)
  })
  return groups
})

const dateGroups = computed(() => Object.keys(groupedRecords.value).sort((a, b) => 
  new Date(b) - new Date(a)
))

async function fetchRecords() {
  if (!hasMore.value) return
  
  loading.value = true
  try {
    const res = await getRecords({
      page: page.value,
      page_size: pageSize.value,
      sort: 'desc'
    })
    
    if (page.value === 1) {
      records.value = res.records || []
    } else {
      records.value = [...records.value, ...(res.records || [])]
    }
    
    total.value = res.total || 0
    hasMore.value = records.value.length < total.value
    page.value++
  } catch (error) {
    Toast.fail(error.message || '获取账单失败')
  } finally {
    loading.value = false
  }
}

function onRefresh() {
  page.value = 1
  hasMore.value = true
  fetchRecords()
}

function onLoadMore() {
  fetchRecords()
}

async function handleDelete(record) {
  try {
    await Dialog.confirm({
      title: '确认删除',
      message: '确定要删除这条记录吗？'
    })
    
    await deleteRecord(record.id)
    Toast.success('删除成功')
    
    // Remove from list
    const index = records.value.findIndex(r => r.id === record.id)
    if (index > -1) {
      records.value.splice(index, 1)
    }
  } catch (error) {
    if (error !== 'cancel') {
      Toast.fail(error.message || '删除失败')
    }
  }
}

function goToAddRecord() {
  router.push('/add')
}

onMounted(() => {
  fetchRecords()
})
</script>

<template>
  <div class="records-page">
    <!-- Header -->
    <van-nav-bar title="账单" />
    
    <!-- Stats -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-label">共</span>
        <span class="stat-value">{{ total }}</span>
        <span class="stat-label">条</span>
      </div>
    </div>

    <!-- Record List -->
    <div class="record-list">
      <van-pull-refresh v-model="loading" @refresh="onRefresh">
        <template v-if="dateGroups.length > 0">
          <div 
            v-for="date in dateGroups" 
            :key="date" 
            class="date-group"
          >
            <div class="date-header">{{ date }}</div>
            <div class="record-items">
              <div 
                v-for="record in groupedRecords[date]" 
                :key="record.id"
                class="record-item"
              >
                <div class="record-info">
                  <div class="record-category">{{ record.category?.name || '未分类' }}</div>
                  <div class="record-date">{{ formatDate(record.record_date, 'HH:mm') }}</div>
                </div>
                <div 
                  class="record-amount"
                  :style="{ color: getAmountColor(record.type) }"
                >
                  {{ record.type === 'income' ? '+' : '-' }}{{ formatAmount(record.amount) }}
                </div>
                <div class="record-actions">
                  <van-button 
                    type="danger" 
                    size="small" 
                    plain
                    @click="handleDelete(record)"
                  >
                    删除
                  </van-button>
                </div>
              </div>
            </div>
          </div>
        </template>
        <template v-else-if="!loading">
          <van-empty description="暂无账单记录" image="https://img.yzcdn.cn/vant/empty-image.png">
            <template #image>
              <div style="font-size: 64px;">📭</div>
            </template>
          </van-empty>
        </template>
      </van-pull-refresh>
      
      <!-- Load More -->
      <div v-if="hasMore && dateGroups.length > 0" class="load-more" @click="onLoadMore">
        <span v-if="loading">加载中...</span>
        <span v-else>加载更多</span>
      </div>
    </div>

    <!-- Add Button -->
    <van-button 
      type="primary" 
      round 
      class="add-btn" 
      @click="goToAddRecord"
    >
      ✏️ 记一笔
    </van-button>
  </div>
</template>

<style scoped>
.records-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 80px;
}

.stats-bar {
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #f5f5f5;
}

.stat-item {
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-label {
  color: #969799;
  font-size: 13px;
}

.stat-value {
  color: #323233;
  font-weight: 600;
  margin: 0 4px;
}

.date-group {
  margin-top: 12px;
}

.date-header {
  padding: 8px 16px;
  font-size: 13px;
  color: #969799;
  background: #f7f8fa;
}

.record-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: #fff;
  border-bottom: 1px solid #f5f5f5;
}

.record-info {
  flex: 1;
}

.record-category {
  font-size: 15px;
  color: #323233;
  margin-bottom: 4px;
}

.record-date {
  font-size: 12px;
  color: #969799;
}

.record-amount {
  font-size: 17px;
  font-weight: 600;
  margin-right: 12px;
}

.record-actions {
  display: flex;
  gap: 8px;
}

.load-more {
  text-align: center;
  padding: 16px;
  color: #969799;
  font-size: 14px;
}

.add-btn {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 56px;
  height: 56px;
  padding: 0;
  border-radius: 28px;
  box-shadow: 0 4px 16px rgba(25, 137, 250, 0.4);
}
</style>
