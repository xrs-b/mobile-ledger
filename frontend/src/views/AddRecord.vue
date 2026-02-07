<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Toast, Dialog } from 'vant'
import { formatAmount, getTypeLabel, getAmountColor } from '@/utils/amount'
import { formatDate } from '@/utils/date'
import { getCategoryTree } from '@/api/category'
import { createRecord } from '@/api/record'

const router = useRouter()

const type = ref('expense')
const amount = ref('')
const categoryId = ref(null)
const categoryName = ref('选择分类')
const remark = ref('')
const recordDate = ref(formatDate(new Date()))
const showCategoryPicker = ref(false)
const categories = ref([])
const loading = ref(false)

const typeOptions = [
  { text: '支出', value: 'expense' },
  { text: '收入', value: 'income' }
]

const categoryColumns = computed(() => {
  return categories.value.filter(cat => cat.type === type.value)
})

async function fetchCategories() {
  try {
    const res = await getCategoryTree()
    categories.value = res
  } catch (error) {
    Toast.fail('获取分类失败')
  }
}

function onTypeChange(value) {
  type.value = value
  categoryId.value = null
  categoryName.value = '选择分类'
}

function onCategoryConfirm(item) {
  categoryId.value = item.id
  categoryName.value = item.name
  showCategoryPicker.value = false
}

async function handleSubmit() {
  if (!amount.value || Number(amount.value) <= 0) {
    Toast.fail('请输入金额')
    return
  }
  
  if (!categoryId.value) {
    Toast.fail('请选择分类')
    return
  }
  
  loading.value = true
  try {
    await createRecord({
      amount: Number(amount.value),
      type: type.value,
      category_id: categoryId.value,
      remark: remark.value,
      record_date: recordDate.value
    })
    Toast.success('记账成功')
    router.push('/records')
  } catch (error) {
    Toast.fail(error.message || '记账失败')
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

onMounted(() => {
  fetchCategories()
})
</script>

<template>
  <div class="add-record-page">
    <!-- Header -->
    <van-nav-bar title="记一笔" left-arrow @click-left="goBack" />
    
    <!-- Type Tabs -->
    <div class="type-tabs">
      <van-tabs v-model:active="type" @change="onTypeChange">
        <van-tab title="支出" name="expense" />
        <van-tab title="收入" name="income" />
      </van-tabs>
    </div>

    <!-- Amount Input -->
    <div class="amount-section">
      <div class="amount-prefix">¥</div>
      <input 
        type="number" 
        v-model="amount" 
        placeholder="0.00"
        class="amount-input"
        step="0.01"
      />
    </div>

    <!-- Form -->
    <van-form @submit="handleSubmit">
      <van-cell-group inset>
        <van-field
          v-model="categoryName"
          readonly
          label="分类"
          placeholder="请选择分类"
          :rules="[{ required: true, message: '请选择分类' }]"
          @click="showCategoryPicker = true"
        />
        <van-field
          v-model="recordDate"
          type="date"
          label="日期"
          placeholder="请选择日期"
        />
        <van-field
          v-model="remark"
          type="textarea"
          label="备注"
          placeholder="添加备注..."
          :maxlength="200"
          show-word-limit
          rows="2"
        />
      </van-cell-group>

      <div class="submit-section">
        <van-button 
          type="primary" 
          native-type="submit" 
          block 
          :loading="loading"
        >
          保存
        </van-button>
      </div>
    </van-form>

    <!-- Category Picker -->
    <van-popup v-model:show="showCategoryPicker" position="bottom">
      <van-picker
        :columns="categoryColumns.map(c => ({ text: c.name, value: c.id }))"
        @confirm="onCategoryConfirm"
        @cancel="showCategoryPicker = false"
        show-toolbar
      />
    </van-popup>
  </div>
</template>

<style scoped>
.add-record-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 80px;
}

.type-tabs {
  background: #fff;
}

.amount-section {
  display: flex;
  align-items: center;
  padding: 32px 24px;
  background: #fff;
  margin-top: 12px;
}

.amount-prefix {
  font-size: 28px;
  font-weight: 600;
  color: #323233;
  margin-right: 8px;
}

.amount-input {
  flex: 1;
  font-size: 40px;
  font-weight: 700;
  border: none;
  outline: none;
  background: transparent;
  color: #323233;
}

.amount-input::placeholder {
  color: #c8c9cc;
}

.submit-section {
  padding: 24px 16px;
}
</style>
