export interface Student {
  id: number
  real_name: string
  gender: string | null
  birth_year: number | null
  grade: string
  school: string
  subjects: string[]
}

export interface Binding {
  id: number
  teacher_id: number
  teacher_name: string
  student_id: number
  student_name: string
  status: 'pending' | 'accepted' | 'rejected' | 'expired'
  reply_message: string | null
  created_at: string
  expire_at: string
}

import request from '@/utils/request'

export function getStudents(): Promise<Student[]> {
  return request.get('/parents/students') as Promise<Student[]>
}

export function createStudent(data: Partial<Student> & { phone: string; password?: string }): Promise<any> {
  return request.post('/parents/students', data) as Promise<any>
}

export function updateStudent(id: number, data: Partial<Student>): Promise<any> {
  return request.put(`/parents/students/${id}`, data) as Promise<any>
}

export function deleteStudent(id: number): Promise<any> {
  return request.delete(`/parents/students/${id}`) as Promise<any>
}

export function createBinding(data: { teacher_id: number; student_id: number; reply_message?: string }): Promise<any> {
  return request.post('/parents/bindings', data) as Promise<any>
}

export function getBindings(): Promise<Binding[]> {
  return request.get('/parents/bindings') as Promise<Binding[]>
}

export function getStudentAssignments(studentId: number, params?: { status_filter?: string; page?: number; page_size?: number }): Promise<{ items: any[]; total: number; page: number; page_size: number }> {
  return request.get(`/parents/students/${studentId}/assignments`, { params }) as Promise<any>
}

export function getStudentAssignmentDetail(studentId: number, assignmentId: number): Promise<any> {
  return request.get(`/parents/students/${studentId}/assignments/${assignmentId}`) as Promise<any>
}
