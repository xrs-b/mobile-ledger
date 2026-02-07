import request from './request'

export function login(username, password) {
  return request.post('/auth/login', {
    username,
    password
  })
}

export function register(username, password, invitation_code) {
  return request.post('/auth/register', {
    username,
    password,
    invitation_code
  })
}

export function getProfile() {
  return request.get('/auth/profile')
}

export function logout() {
  return request.post('/auth/logout')
}
