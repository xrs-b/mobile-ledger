<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Toast, Dialog } from 'vant'
import { formatAmount } from '@/utils/amount'
import { getBudgets, createBudget, updateBudget, deleteBudget } from '@/api/budget'
import { getCategoryTree } from '@/api/category'
import { getProjects, createProject, updateProject, deleteProject } from '@/api/project'

const router = useRouter()
const projects = ref([])
const loading = ref(false)
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const editingProject = ref(null)

const projectForm = ref({
  name: '',
  description: '',
  budget: '',
  member_count: 1,
  start_date: '',
  end_date: ''
})

const statusOptions = [
  { text: '进行中', value: 'active' },
  { text: '已完成', value: 'completed' },
  { text: '已暂停', value: 'paused' }
]

async function fetchProjects() {
  loading.value = true
  try {
    const res = await getProjects()
    projects.value = res.projects || []
  } catch (error) {
    Toast.fail(error.message || '获取项目列表失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!projectForm.value.name) {
    Toast.fail('请填写项目名称')
    return
  }
  
  if (!projectForm.value.budget || Number(projectForm.value.budget) <= 0) {
    Toast.fail('请填写有效预算')
    return
  }
  
  try {
    const data = {
      name: projectForm.value.name,
      description: projectForm.value.description,
      budget: Number(projectForm.value.budget),
      member_count: projectForm.value.member_count || 1,
      start_date: projectForm.value.start_date || null,
      end_date: projectForm.value.end_date || null
    }
    
    if (editingProject.value) {
      await updateProject(editingProject.value.id, data)
      Toast.success('更新成功')
    } else {
      await createProject(data)
      Toast.success('创建成功')
    }
    
    showAddDialog.value = false
    showEditDialog.value = false
    editingProject.value = null
    resetForm()
    fetchProjects()
  } catch (error) {
    Toast.fail(error.message || '保存失败')
  }
}

async function handleDelete(project) {
  try {
    await Dialog.confirm({
      title: '确认删除',
      message: `确定要删除项目"${project.name}"吗？`
    })
    
    await deleteProject(project.id)
    Toast.success('删除成功')
    fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      Toast.fail(error.message || '删除失败')
    }
  }
}

function openAddDialog() {
  editingProject.value = null
  resetForm()
  showAddDialog.value = true
}

function openEditDialog(project) {
  editingProject.value = project
  projectForm.value = {
    name: project.name,
    description: project.description || '',
    budget: String(project.budget || ''),
    member_count: project.member_count || 1,
    start_date: project.start_date || '',
    end_date: project.end_date || ''
  }
  showEditDialog.value = true
}

function resetForm() {
  projectForm.value = {
    name: '',
    description: '',
    budget: '',
    member_count: 1,
    start_date: '',
    end_date: ''
  }
}

function onCancel() {
  showAddDialog.value = false
  showEditDialog.value = false
  editingProject.value = null
  resetForm()
}

function getStatusColor(status) {
  const colors = {
    active: '#07c160',
    completed: '#1989fa',
    paused: '#969799'
  }
  return colors[status] || '#969799'
}

function getStatusText(status) {
  const texts = {
    active: '进行中',
    completed: '已完成',
    paused: '已暂停'
  }
  return texts[status] || '未知'
}

function goToAddRecord(projectId) {
  router.push({ path: '/add', query: { project_id: projectId } })
}

onMounted(() => {
  fetchProjects()
})
</script>

<template>
  <div class="projects-page">
    <!-- Header -->
    <van-nav-bar title="项目管理" />

    <!-- Project List -->
    <div class="project-section">
      <div class="section-header">
        <span class="section-title">我的项目</span>
        <van-button type="primary" size="small" @click="openAddDialog">+ 添加项目</van-button>
      </div>

      <van-loading v-if="loading" size="24px" vertical>加载中...</van-loading>

      <div v-if="projects.length > 0" class="project-list">
        <div 
          v-for="project in projects" 
          :key="project.id" 
          class="project-item"
        >
          <div class="project-header">
            <div class="project-info">
              <div class="project-name">{{ project.name }}</div>
              <div class="project-meta">
                <van-tag :color="getStatusColor(project.status)" size="small">
                  {{ getStatusText(project.status) }}
                </van-tag>
                <span class="member-count">{{ project.member_count || 1 }}人</span>
              </div>
            </div>
            <div class="project-budget">
              <div class="budget-label">预算</div>
              <div class="budget-value">{{ formatAmount(project.budget) }}</div>
            </div>
          </div>

          <!-- Stats -->
          <div class="project-stats" v-if="project.stats">
            <div class="stat-item">
              <div class="stat-value">{{ formatAmount(project.stats.total_spent) }}</div>
              <div class="stat-label">已花费</div>
            </div>
            <div class="stat-item">
              <div 
                class="stat-value"
                :class="{ over: project.stats.budget_usage_rate > 100 }"
              >
                {{ project.stats.budget_usage_rate }}%
              </div>
              <div class="stat-label">使用率</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ formatAmount(project.stats.per_person_cost) }}</div>
              <div class="stat-label">人均消费</div>
            </div>
          </div>

          <!-- Date Range -->
          <div class="project-dates" v-if="project.start_date || project.end_date">
            <span>{{ project.start_date || '-' }} 至 {{ project.end_date || '-' }}</span>
          </div>

          <!-- Actions -->
          <div class="project-actions">
            <van-button size="small" @click="openEditDialog(project)">编辑</van-button>
            <van-button size="small" type="primary" @click="goToAddRecord(project.id)">记一笔</van-button>
            <van-button size="small" type="danger" plain @click="handleDelete(project)">删除</van-button>
          </div>
        </div>
      </div>

      <van-empty v-else-if="!loading" description="暂无项目，去添加一个吧">
        <template #image>
          <div style="font-size: 64px;">📋</div>
        </template>
        <van-button type="primary" @click="openAddDialog">添加项目</van-button>
      </van-empty>
    </div>

    <!-- Add/Edit Dialog -->
    <van-dialog 
      v-model:show="showAddDialog || showEditDialog" 
      :title="editingProject ? '编辑项目' : '添加项目'"
      show-cancel-button
      @confirm="handleSave"
      @cancel="onCancel"
    >
      <van-form>
        <van-field
          v-model="projectForm.name"
          label="项目名称"
          placeholder="请输入项目名称"
          :rules="[{ required: true, message: '请输入项目名称' }]"
        />
        <van-field
          v-model="projectForm.description"
          type="textarea"
          label="项目描述"
          placeholder="请输入项目描述"
          rows="2"
        />
        <van-field
          v-model="projectForm.budget"
          type="number"
          label="预算金额"
          placeholder="请输入预算金额"
          :rules="[{ required: true, message: '请输入预算金额' }]"
        />
        <van-field
          v-model.number="projectForm.member_count"
          type="digit"
          label="参与人数"
          placeholder="请输入参与人数"
        />
        <van-field
          v-model="projectForm.start_date"
          type="date"
          label="开始日期"
          placeholder="请选择开始日期"
        />
        <van-field
          v-model="projectForm.end_date"
          type="date"
          label="结束日期"
          placeholder="请选择结束日期"
        />
      </van-form>
    </van-dialog>
  </div>
</template>

<style scoped>
.projects-page {
  min-height: 100vh;
  background: #f7f8fa;
  padding-bottom: 60px;
}

.project-section {
  padding: 0 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
}

.project-list {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.project-item {
  padding: 16px;
  border-bottom: 1px solid #f5f5f5;
}

.project-item:last-child {
  border-bottom: none;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.project-name {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
  margin-bottom: 8px;
}

.project-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.member-count {
  font-size: 12px;
  color: #969799;
}

.project-budget {
  text-align: right;
}

.budget-label {
  font-size: 12px;
  color: #969799;
  margin-bottom: 4px;
}

.budget-value {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.project-stats {
  display: flex;
  justify-content: space-around;
  padding: 12px 0;
  background: #f7f8fa;
  border-radius: 8px;
  margin-bottom: 12px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #323233;
}

.stat-value.over {
  color: #ee0a24;
}

.stat-label {
  font-size: 12px;
  color: #969799;
  margin-top: 4px;
}

.project-dates {
  font-size: 12px;
  color: #969799;
  margin-bottom: 12px;
}

.project-actions {
  display: flex;
  gap: 8px;
}
</style>
