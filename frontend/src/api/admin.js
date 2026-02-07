import request from './request'

export function getUsers(params = {}) {
  return request.get('/admin/users', { params })
}

export function disableUser(userId) {
  return request.post(`/admin/users/${userId}/disable`)
}

export function enableUser(userId) {
  return request.post(`/admin/users/${userId}/enable`)
}

export function deleteUser(userId) {
  return request.delete(`/admin/users/${userId}`)
}
