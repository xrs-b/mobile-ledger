import request from './request'

export function getInvitationCodes(params = {}) {
  return request.get('/invitations', { params })
}

export function createInvitationCode(data) {
  return request.post('/invitations', data)
}

export function deleteInvitationCode(id) {
  return request.delete(`/invitations/${id}`)
}
