import request from './request'

export function getBudgets(params = {}) {
  return request.get('/budgets', { params })
}

export function getBudgetSummary(params = {}) {
  return request.get('/budgets/summary/current', { params })
}

export function getBudgetAlerts() {
  return request.get('/budgets/alerts')
}

export function createBudget(data) {
  return request.post('/budgets', data)
}

export function updateBudget(id, data) {
  return request.put(`/budgets/${id}`, data)
}

export function deleteBudget(id) {
  return request.delete(`/budgets/${id}`)
}
