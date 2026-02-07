import request from './request'

export function getCategories(params = {}) {
  return request.get('/categories', { params })
}

export function getCategoryTree(type = null) {
  return request.get('/categories/tree', { params: type ? { type } : {} })
}

export function createCategory(data) {
  return request.post('/categories', data)
}

export function updateCategory(id, data) {
  return request.put(`/categories/${id}`, data)
}

export function deleteCategory(id) {
  return request.delete(`/categories/${id}`)
}
