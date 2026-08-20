import request from '@/utils/request'

export function getTeachers(params?: {
  subject?: string
  city?: string
  min_rate?: number
  max_rate?: number
  min_rating?: number
  page?: number
  page_size?: number
}): Promise<{ items: any[]; total: number; page: number; page_size: number }> {
  return request.get('/teachers', { params }) as Promise<any>
}

export function getTeacher(id: number): Promise<any> {
  return request.get(`/teachers/${id}`)
}

export function toggleFavorite(teacherId: number): Promise<{ is_favorited: boolean }> {
  return request.post(`/teachers/favorite/${teacherId}`)
}

export function getMyFavorites(): Promise<any[]> {
  return request.get('/teachers/my-favorites')
}

// Teacher-specific endpoints
export function getMyBindings(params?: { status_filter?: string }): Promise<{ items: any[]; total: number }> {
  return request.get('/teachers/my-bindings', { params }) as Promise<any>
}

export function replyBinding(bindingId: number, action: 'accept' | 'reject', teacherReply?: string): Promise<any> {
  return request.post(`/teachers/bindings/${bindingId}/reply`, null, { params: { action, teacher_reply: teacherReply } })
}

export function getMyStudents(): Promise<any[]> {
  return request.get('/teachers/my-students')
}

export function updateTeacherProfile(data: any): Promise<any> {
  return request.post('/teachers/my-profile', data)
}

export function getMyProfile(): Promise<any> {
  return request.get('/teachers/my-profile')
}

export function getMyAssignments(params?: any): Promise<any> {
  return request.get('/assignments', { params }) as Promise<any>
}
