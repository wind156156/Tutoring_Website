import request from '@/utils/request'

export function getAnnouncements(): Promise<any[]> {
  return request.get('/announcements') as Promise<any[]>
}

export function getSubjects(): Promise<string[]> {
  return request.get('/subjects') as Promise<string[]>
}
