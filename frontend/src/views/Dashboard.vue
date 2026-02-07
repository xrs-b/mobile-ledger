<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Toast } from 'vant'
import { formatAmount } from '@/utils/amount'
import { formatDate, getCurrentMonth } from '@/utils/date'
import { getStatisticsOverview } from '@/api/statistics'

const router = useRouter()
const currentMonth = ref(getCurrentMonth())
const overview = ref(null)
const loading = ref(false)

const monthIncome = computed(() => overview.value?.month_income || 0)
const monthExpense = computed(() => overview.value?.month_expense || 0)
const monthBalance = computed(() => monthIncome.value - monthExpense.value)

const incomeColor = computed(() => '#07c160')
const expenseColor = computed(() => '#ee0a24')
const balanceColor = computed(() => monthBalance.value >= 0 ? incomeColor.value : expenseColor.value)

async function fetchOverview() {
  loading.value = true
  try {
    const res = await getStatisticsOverview({
      month: currentMonth.value
    })
    overview.value = res
  } catch (error) {
    Toast.fail(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

function goToAddRecord() {
  router.push('/add')
}

function goToRecords() {
  router.push('/records')
}

function goToStatistics() {
  router.push('/statistics')
}

function goToBudget() {
  router.push('/budget')
}

onMounted(() => {
  fetchOverview()
})
</script>

<template>
  <div class="dashboard-page">
    <!-- Header -->
    <div class="header">
      <div class="user-info">
        <span class="date">{{ currentMonth }} 月</span>
      </div>
    </div>

    <!-- Overview Card -->
    <div class="overview-card">
      <div class="overview-title">本月概况</div>
      <van-loading v-if="loading" size="24px" vertical>加载中...</van-loading>
      <template v-else>
        <div class="balance-section">
          <div class="balance-label">结余</div>
          <div class="balance-amount" :style="{ color: balanceColor }">
            {{ formatAmount(monthBalance) }}
          </div>
        </div>
        
        <div class="stats-row">
          <div class="stat-item">
            <div class="stat-label">收入</div>
            <div class="stat-value income">{{ formatAmount(monthIncome) }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">支出</div>
            <div class="stat-value expense">{{ formatAmount(monthExpense) }}</div>
          </div>
        </div>
      </template>
    </div>

    <!-- Quick Actions -->
    <div class="card quick-actions">
      <div class="card-title">快捷操作</div>
      <div class="action-grid">
        <div class="action-item" @click="goToAddRecord">
          <div class="action-icon">✏️</div>
          <div class="action-text">记一笔</div>
        </div>
        <div class="action-item" @click="goToRecords">
          <div class="action-icon">📋</div>
          <div class="action-text">账单</div>
        </div>
        <div class="action-item" @click="goToStatistics">
          <div class="action-icon">📊</div>
          <div class="action-text">统计</div>
        </div>
        <div class="action-item" @click="goToBudget">
          <div class="action-icon">💰</div>
          <div class="action-text">预算</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #667eea 0%, #f7f8fa 40%);
  padding-bottom: 80px;
}

.header {
  padding: 20px 16px;
  color: #fff;
}

.user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.date {
  font-size: 18px;
  font-weight: 600;
}

.overview-card {
  margin: 0 16px;
  padding: 24px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.overview-title {
  font-size: 14px;
  color: #969799;
  margin-bottom: 16px;
}

.balance-section {
  text-align: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f5f5f5;
}

.balance-label {
  font-size: 14px;
  color: #969799;
  margin-bottom: 8px;
}

.balance-amount {
  font-size: 36px;
  font-weight: 700;
}

.stats-row {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  text-align: center;
}

.stat-label {
  font-size: 13px;
  color: #969799;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
}

.stat-value.income {
  color: #07c160;
}

.stat-value.expense {
  color: #ee0a24;
}

.card {
  margin: 16px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border-radius: 12px;
  background: #f7f8fa;
  transition: all 0.2s;
}

.action-item:active {
  background: #e8e8e8;
  transform: scale(0.95);
}

.action-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.action-text {
  font-size: 12px;
  color: #323233;
}
</style>
