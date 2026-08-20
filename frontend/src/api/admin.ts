import request from '@/utils/request'

export function getUsers(params?: any): Promise<any> {
  return request.get('/admin/users', { params }) as Promise<any>
}

export function updateUserStatus(id: number, status: string): Promise<any> {
  return request.put(`/admin/users/${id}/status`, { status })
}

export function deleteUser(id: number): Promise<any> {
  return request.delete(`/admin/users/${id}`) as Promise<any>
}

export function getPendingTeachers(params?: any): Promise<any> {
  return request.get('/admin/teachers', { params }) as Promise<any>
}

export function verifyTeacher(id: number, action: 'approve' | 'reject'): Promise<any> {
  return request.put(`/admin/teachers/${id}/verify`, { action })
}

export function getAnnouncements(params?: any): Promise<any> {
  return request.get('/admin/announcements', { params }) as Promise<any>
}

export function createAnnouncement(data: any): Promise<any> {
  return request.post('/admin/announcements', data)
}

export function updateAnnouncement(id: number, data: any): Promise<any> {
  return request.put(`/admin/announcements/${id}`, data)
}

export function getStats(): Promise<any> {
  return request.get('/admin/stats/overview') as Promise<any>
}
