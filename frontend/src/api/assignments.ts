import request from '@/utils/request'

export interface Assignment {
  id: number
  title: string
  subject: string
  description: string | null
  content_images: string[]
  due_at: string
  max_score: number
  student_count: number
  graded_count: number
  created_at: string
}

export interface AssignmentWithStudent {
  id: number
  assignment_id: number
  title: string
  subject: string
  description: string | null
  content_images: string[]
  due_at: string
  max_score: number
  teacher_name: string
  status: 'pending' | 'submitted' | 'graded' | 'overdue'
  score: number | null
  comment: string | null
  submitted_at: string | null
  graded_at: string | null
  files: { url: string; name: string }[]
}

export interface Attachment {
  url: string
  name: string
}

// Upload a file and return its URL
export function uploadFile(file: File): Promise<{ url: string; name: string }> {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/files/upload', formData) as Promise<{ url: string; name: string }>
}

// Teacher endpoints
export function getAssignments(params?: { page?: number; page_size?: number }): Promise<{ items: Assignment[]; total: number }> {
  return request.get('/assignments', { params }) as Promise<any>
}

export function getAssignment(id: number): Promise<any> {
  return request.get(`/assignments/${id}`) as Promise<any>
}

export function createAssignment(data: any): Promise<{ id: number }> {
  return request.post('/assignments', data) as Promise<any>
}

export function updateAssignment(id: number, data: any): Promise<any> {
  return request.put(`/assignments/${id}`, data) as Promise<any>
}

export function deleteAssignment(id: number): Promise<any> {
  return request.delete(`/assignments/${id}`) as Promise<any>
}

export function gradeAssignment(assignmentId: number, studentId: number, data: { score: number; comment?: string }): Promise<any> {
  return request.post(`/assignments/${assignmentId}/grade/${studentId}`, data) as Promise<any>
}

export function getMySubjects(): Promise<string[]> {
  return request.get('/assignments/my-subjects') as Promise<string[]>
}

// Student endpoints
export function getMyAssignments(params?: { status_filter?: string; page?: number; page_size?: number }): Promise<{ items: AssignmentWithStudent[]; total: number }> {
  return request.get('/students/my-assignments', { params }) as Promise<any>
}

export function getStudentAssignment(id: number): Promise<any> {
  return request.get(`/students/assignments/${id}`) as Promise<any>
}

export function submitAssignment(assignmentId: number, files: any[]): Promise<any> {
  return request.post(`/students/assignments/${assignmentId}/submit`, files) as Promise<any>
}

export function getMyGrades(): Promise<any> {
  return request.get('/students/my-grades') as Promise<any>
}

export function getMyTeachers(): Promise<any[]> {
  return request.get('/students/my-teachers') as Promise<any[]>
}
