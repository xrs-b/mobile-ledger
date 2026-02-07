import request from './request'

export function getRecords(params = {}) {
  return request.get('/records', { params })
}

export function getRecordSummary(params = {}) {
  return request.get('/records/summary', { params })
}

export function createRecord(data) {
  return request.post('/records', data)
}

export function updateRecord(id, data) {
  return request.put(`/records/${id}`, data)
}

export function deleteRecord(id) {
  return request.delete(`/records/${id}`)
}
