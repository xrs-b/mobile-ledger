<script setup>
import { ref, onMounted, computed } from 'vue'
import { Toast, Dialog } from 'vant'
import { formatAmount } from '@/utils/amount'
import { getBudgets, getBudgetSummary, createBudget, updateBudget, deleteBudget } from '@/api/budget'
import { getCategoryTree } from '@/api/category'

const budgets = ref([])
const summary = ref(null)
const loading = ref(false)
const showAddDialog = ref(false)
const editingBudget = ref(null)

const budgetForm = ref({
  name: '',
  amount: '',
  type: 'expense',
  category_id: null,
  month: new Date().toISOString().slice(0, 7)
})

const categories = ref([])

async function fetchData() {
  loading.value = true
  try {
    const [budgetsRes, summaryRes, catsRes] = await Promise.all([
      getBudgets(),
      getBudgetSummary(),
      getCategoryTree()
    ])
    
    budgets.value = budgetsRes || []
    summary.value = summaryRes
    categories.value = catsRes || []
  } catch (error) {
    Toast.fail(error.message || '获取数据失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!budgetForm.value.name || !budgetForm.value.amount) {
    Toast.fail('请填写预算名称和金额')
    return
  }
  
  try {
    const data = {
      name: budgetForm.value.name,
      amount: Number(budgetForm.value.amount),
      type: budgetForm.value.type,
      category_id: budgetForm.value.category_id,
      month: budgetForm.value.month
    }
    
    if (editingBudget.value) {
      await updateBudget(editingBudget.value.id, data)
      Toast.success('更新成功')
    } else {
      await createBudget(data)
      Toast.success('创建成功')
    }
    
    showAddDialog.value = false
    editingBudget.value = null
    resetForm()
    fetchData()
  } catch (error) {
    Toast.fail(error.message || '保存失败')
  }
}

async function handleDelete(budget) {
  try {
    await Dialog.confirm({
      title: '确认删除',
      message: '确定要删除这个预算吗？'
    })
    
    await deleteBudget(budget.id)
    Toast.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      Toast.fail(error.message || '删除失败')
    }
  }
}

function openAddDialog() {
  editingBudget.value = null
  resetForm()
  showAddDialog.value = true
}

function openEditDialog(budget) {
  editingBudget.value = budget
  budgetForm.value = {
    name: budget.name,
    amount: String(budget.amount),
    type: budget.type,
    category_id: budget.category_id,
    month: budget.month
  }
  showAddDialog.value = true
}

function resetForm() {
  budgetForm.value = {
    name: '',
    amount: '',
    type: 'expense',
    category_id: null,
    month: new Date().toISOString().slice(0, 7)
  }
}

function onCancel() {
  showAddDialog.value = false
  editingBudget.value = null
  resetForm()
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="budget-page">
    <!-- Header -->
    <van-nav-bar title="预算" />

    <!-- Summary -->
    <div class="summary-section" v-if="summary">
      <div class="summary-card">
        <div class="summary-title">本月预算执行</div>
        <div class="summary-progress">
          <van-progress 
            :percentage="summary.percent || 0" 
            :color="summary.percent > 100 ? '#ee0a24' : '#1989fa'"
            :stroke-width="8"
          />
          <div class="progress-info">
            <span>{{ formatAmount(summary.spent) }} / {{ formatAmount(summary.budget) }}</span>
            <span>{{ summary.percent || 0 }}%</span>
          </div>
        </div>
        <div class="remaining" :class="{ negative: summary.remaining < 0 }">
          {{ summary.remaining >= 0 ? '剩余' : '超支' }}: {{ formatAmount(Math.abs(summary.remaining)) }}
        </div>
      </div>
    </div>

    <!-- Budget List -->
    <div class="budget-section">
      <div class="section-header">
        <span class="section-title">预算列表</span>
        <van-button type="primary" size="small" @click="openAddDialog">+ 添加预算</van-button>
      </div>

      <van-loading v-if="loading" size="24px" vertical>加载中...</van-loading>

      <div v-else-if="budgets.length > 0" class="budget-list">
        <div 
          v-for="budget in budgets" 
          :key="budget.id" 
          class="budget-item"
        >
          <div class="budget-info">
            <div class="budget-name">{{ budget.name }}</div>
            <div class="budget-meta">
              {{ budget.month }} · {{ budget.type === 'income' ? '收入' : '支出' }}
              <span v-if="budget.category_name"> · {{ budget.category_name }}</span>
            </div>
          </div>
          <div class="budget-progress">
            <van-progress 
              :percentage="Math.min((budget.spent / budget.amount) * 100, 100)" 
              :color="budget.spent > budget.amount ? '#ee0a24' : '#07c160'"
              :stroke-width="6"
            />
            <div class="progress-text">
              {{ formatAmount(budget.spent) }} / {{ formatAmount(budget.amount) }}
            </div>
          </div>
          <div class="budget-actions">
            <van-button size="small" @click="openEditDialog(budget)">编辑</van-button>
            <van-button size="small" type="danger" plain @click="handleDelete(budget)">删除</van-button>
          </div>
        </div>
      </div>

      <van-empty v-else description="暂无预算，去添加一个吧">
        <template #image>
          <div style="font-size: 64px;">💰</div>
        </template>
        <van-button type="primary" @click="openAddDialog">添加预算</van-button>
      </van-empty>
    </div>

    <!-- Add/Edit Dialog -->
    <van-dialog 
      v-model:show="showAddDialog" 
      :title="editingBudget ? '编辑预算' : '添加预算'"
      show-cancel-button
      @confirm="handleSave"
      @cancel="onCancel"
    >
      <van-form>
        <van-field
          v-model="budgetForm.name"
          label="预算名称"
          placeholder="请输入预算名称"
          :rules="[{ required: true, message: '请输入预算名称' }]"
        />
        <van-field
          v-model="budgetForm.amount"
          type="number"
          label="预算金额"
          placeholder="请输入预算金额"
          :rules="[{ required: true, message: '请输入预算金额' }]"
        />
        <van-field
          v-model="budgetForm.type"
          label="类型"
          readonly
        />
        <van-field
          v-model="budgetForm.month"
          type="month"
          label="月份"
          placeholder="请选择月份"
        />
      </van-form>
    </van-dialog>
  </div>
</template>

<style scoped>
.budget-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}

.summary-section {
  padding: 16px;
}

.summary-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.summary-title {
  font-size: 14px;
  color: #969799;
  margin-bottom: 12px;
}

.summary-progress {
  margin-bottom: 12px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 13px;
  color: #323233;
}

.remaining {
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  color: #07c160;
}

.remaining.negative {
  color: #ee0a24;
}

.budget-section {
  padding: 0 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
}

.budget-list {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.budget-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f5f5f5;
}

.budget-item:last-child {
  border-bottom: none;
}

.budget-info {
  width: 120px;
  flex-shrink: 0;
}

.budget-name {
  font-size: 15px;
  font-weight: 500;
  color: #323233;
  margin-bottom: 4px;
}

.budget-meta {
  font-size: 12px;
  color: #969799;
}

.budget-progress {
  flex: 1;
  margin: 0 16px;
}

.progress-text {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}

.budget-actions {
  display: flex;
  gap: 8px;
}
</style>
