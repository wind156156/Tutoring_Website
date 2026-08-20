import request from '@/utils/request'

export interface LoginRes {
  access_token: string
  token_type: string
  user: {
    id: number
    role: string
    phone: string
    nickname: string
    avatar: string
    status: string
  }
}

export function login(phone: string, password: string): Promise<LoginRes> {
  return request.post('/auth/login/password', { phone, password }) as Promise<LoginRes>
}

export function register(phone: string, password: string, role: string, realName?: string): Promise<LoginRes> {
  return request.post('/auth/register', { phone, password, role, real_name: realName || '' }) as Promise<LoginRes>
}

export function getMe(): Promise<any> {
  return request.get('/auth/me')
}

export function updateProfile(data: { nickname?: string; avatar?: string }): Promise<any> {
  return request.put('/auth/profile', data)
}

export function updatePassword(oldPwd: string, newPwd: string): Promise<any> {
  return request.put('/auth/password', { old_password: oldPwd, new_password: newPwd })
}
