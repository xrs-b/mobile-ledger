<script setup>
import { ref, onMounted, computed } from 'vue'
import { Toast } from 'vant'
import { formatAmount, getAmountColor } from '@/utils/amount'
import { formatMonth, getCurrentMonth } from '@/utils/date'
import * as echarts from 'echarts'
import { getStatisticsOverview, getStatisticsCategory, getStatisticsTrend } from '@/api/statistics'

const currentMonth = ref(getCurrentMonth())
const overview = ref(null)
const categoryData = ref([])
const trendData = ref([])
const loading = ref(false)
const activeTab = ref('overview')

const monthIncome = computed(() => overview.value?.month_income || 0)
const monthExpense = computed(() => overview.value?.month_expense || 0)
const dayAverage = computed(() => {
  const days = new Date().getDate()
  return days > 0 ? monthExpense.value / days : 0
})

// Chart instances
let trendChart = null
let categoryChart = null

async function fetchData() {
  loading.value = true
  try {
    const [ov, cat, trend] = await Promise.all([
      getStatisticsOverview({ month: currentMonth.value }),
      getStatisticsCategory({ month: currentMonth.value }),
      getStatisticsTrend({ month: currentMonth.value })
    ])
    
    overview.value = ov
    categoryData.value = cat || []
    trendData.value = trend || []
    
    // Render charts after data is fetched
    setTimeout(() => {
      renderTrendChart()
      renderCategoryChart()
    }, 100)
  } catch (error) {
    Toast.fail(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

function renderTrendChart() {
  const chartDom = document.getElementById('trend-chart')
  if (!chartDom) return
  
  if (trendChart) {
    trendChart.dispose()
  }
  
  trendChart = echarts.init(chartDom)
  
  const dates = trendData.value.map(d => d.date)
  const incomes = trendData.value.map(d => d.income)
  const expenses = trendData.value.map(d => d.expense)
  
  trendChart.setOption({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['收入', '支出'],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '收入',
        type: 'line',
        smooth: true,
        data: incomes,
        itemStyle: { color: '#07c160' },
        areaStyle: { color: 'rgba(124, 199, 96, 0.1)' }
      },
      {
        name: '支出',
        type: 'line',
        smooth: true,
        data: expenses,
        itemStyle: { color: '#ee0a24' },
        areaStyle: { color: 'rgba(238, 10, 36, 0.1)' }
      }
    ]
  })
}

function renderCategoryChart() {
  const chartDom = document.getElementById('category-chart')
  if (!chartDom) return
  
  if (categoryChart) {
    categoryChart.dispose()
  }
  
  categoryChart = echarts.init(chartDom)
  
  const expenseData = categoryData.value
    .filter(c => c.type === 'expense')
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 6)
  
  categoryChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        data: expenseData.map(c => ({
          value: c.amount,
          name: c.category_name || c.name,
          itemStyle: { color: c.color || '#1989fa' }
        }))
      }
    ]
  })
}

function onMonthChange(value) {
  currentMonth.value = value
  fetchData()
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="statistics-page">
    <!-- Header -->
    <van-nav-bar title="统计" />
    
    <!-- Month Picker -->
    <div class="month-picker">
      <van-cell 
        title="月份" 
        :value="currentMonth" 
        is-link 
        @click="() => {}"
      />
      <van-popup v-model:show="false" position="bottom">
        <van-picker
          :columns="[]"
          @confirm="onMonthChange"
          show-toolbar
        />
      </van-popup>
    </div>

    <!-- Tabs -->
    <van-tabs v-model:active="activeTab" class="stats-tabs">
      <!-- Overview Tab -->
      <van-tab title="概览" name="overview">
        <van-loading v-if="loading" size="24px" vertical>加载中...</van-loading>
        <template v-else>
          <!-- Summary Card -->
          <div class="summary-card">
            <div class="summary-row">
              <div class="summary-item">
                <div class="summary-label">本月收入</div>
                <div class="summary-value income">{{ formatAmount(monthIncome) }}</div>
              </div>
              <div class="summary-item">
                <div class="summary-label">本月支出</div>
                <div class="summary-value expense">{{ formatAmount(monthExpense) }}</div>
              </div>
            </div>
            <div class="summary-row">
              <div class="summary-item full">
                <div class="summary-label">日均支出</div>
                <div class="summary-value">{{ formatAmount(dayAverage) }}</div>
              </div>
            </div>
          </div>

          <!-- Trend Chart -->
          <div class="chart-card">
            <div class="card-title">月度趋势</div>
            <div id="trend-chart" class="chart-container"></div>
          </div>

          <!-- Category Chart -->
          <div class="chart-card">
            <div class="card-title">支出分类</div>
            <div id="category-chart" class="chart-container"></div>
          </div>
        </template>
      </van-tab>

      <!-- Category Tab -->
      <van-tab title="分类" name="category">
        <div class="category-list">
          <div 
            v-for="item in categoryData" 
            :key="item.category_id"
            class="category-item"
          >
            <div class="category-info">
              <div class="category-name">{{ item.category_name || item.name }}</div>
              <div class="category-percent">{{ item.percent }}%</div>
            </div>
            <div 
              class="category-bar"
              :style="{ width: item.percent + '%', background: item.color || '#1989fa' }"
            ></div>
            <div class="category-amount">{{ formatAmount(item.amount) }}</div>
          </div>
        </div>
      </van-tab>
    </van-tabs>
  </div>
</template>

<style scoped>
.statistics-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}

.month-picker {
  margin-bottom: 8px;
}

.stats-tabs {
  background: #fff;
}

.summary-card {
  margin: 12px 16px;
  padding: 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.summary-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.summary-row:last-child {
  margin-bottom: 0;
}

.summary-item {
  text-align: center;
}

.summary-item.full {
  width: 100%;
}

.summary-label {
  font-size: 13px;
  color: #969799;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 20px;
  font-weight: 600;
}

.summary-value.income {
  color: #07c160;
}

.summary-value.expense {
  color: #ee0a24;
}

.chart-card {
  margin: 12px 16px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
}

.chart-container {
  height: 250px;
}

.category-list {
  padding: 12px 16px;
}

.category-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f5f5f5;
}

.category-info {
  width: 120px;
  flex-shrink: 0;
}

.category-name {
  font-size: 14px;
  color: #323233;
  margin-bottom: 4px;
}

.category-percent {
  font-size: 12px;
  color: #969799;
}

.category-bar {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  margin: 0 12px;
}

.category-amount {
  width: 80px;
  text-align: right;
  font-size: 15px;
  font-weight: 500;
  color: #323233;
}
</style>
