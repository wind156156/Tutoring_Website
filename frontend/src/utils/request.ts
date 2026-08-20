import axios from 'axios'
import { useUserStore } from '@/stores/user.store'
import { useRouter } from 'vue-router'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

/** Extract user-friendly error message from axios error */
function getErrorMessage(err: any): string {
  const d = err?.response?.data
  if (!d) return err?.message || '网络错误，请稍后重试'

  // FastAPI Pydantic v2 validation error (422): detail is array of {type, msg, loc}
  if (Array.isArray(d.detail)) {
    const first = d.detail[0]
    if (first?.msg) return first.msg
    if (first?.loc && first?.msg) return `${first.loc.join('.')} - ${first.msg}`
    return '请求参数错误'
  }
  // FastAPI Pydantic v1 or simple string error
  if (typeof d.detail === 'string') return d.detail
  if (typeof d.detail === 'object' && d.detail?.msg) return d.detail.msg

  return '请求失败，请稍后重试'
}

/** Pre-submit validation errors (shown before network request) */
export function validatePhone(phone: string): string | null {
  if (!phone) return '请输入手机号'
  if (!/^1[3-9]\d{9}$/.test(phone)) return '手机号格式不正确，请输入11位手机号'
  return null
}

request.interceptors.request.use((config) => {
  const store = useUserStore()
  if (store.token) {
    config.headers.Authorization = `Bearer ${store.token}`
  }
  return config
})

request.interceptors.response.use(
  (res) => res.data?.data ?? res.data,
  (err) => {
    // 401 仅在非登录页时才跳转，避免循环重定向
    if (err.response?.status === 401 && !location.pathname.includes('/login')) {
      const store = useUserStore()
      const router = useRouter()
      store.logout()
      router.push('/login')
    }
    return Promise.reject(new Error(getErrorMessage(err)))
  }
)

export default request
