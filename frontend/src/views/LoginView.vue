<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user.store'
import { validatePhone } from '@/utils/request'

const router = useRouter()
const store = useUserStore()
const phone = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  const phoneErr = validatePhone(phone.value)
  if (phoneErr) { errorMsg.value = phoneErr; return }
  if (!password.value) { errorMsg.value = '请输入密码'; return }
  loading.value = true
  errorMsg.value = ''
  try {
    await store.login(phone.value, password.value)
    const role = store.role
    const map: Record<string, string> = { parent: '/parent', teacher: '/teacher', student: '/student', admin: '/admin' }
    router.push(map[role] || '/')
  } catch (e: any) {
    const msg = e?.response?.data?.detail || e?.message || '手机号或密码错误'
    errorMsg.value = typeof msg === 'string' ? msg : '登录失败，请检查账号密码'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="login-bg">
      <div class="login-left">
        <div class="brand">
          <div class="brand-icon">家</div>
          <div>
            <div class="brand-name">家教平台</div>
            <div class="brand-slogan">连接家长、老师与学生</div>
          </div>
        </div>
        <div class="features">
          <div class="feat-item">
            <span class="feat-icon">👩‍🏫</span>
            <span>专业认证老师</span>
          </div>
          <div class="feat-item">
            <span class="feat-icon">📚</span>
            <span>全科目覆盖</span>
          </div>
          <div class="feat-item">
            <span class="feat-icon">💬</span>
            <span>实时沟通反馈</span>
          </div>
        </div>
      </div>
      <div class="login-right">
        <div class="card fade-in">
          <h1 class="title">欢迎回来</h1>
          <p class="subtitle">登录您的账号继续学习</p>
          <div class="form">
            <div class="field">
              <label>手机号</label>
              <input v-model="phone" type="text" placeholder="请输入手机号" class="input-field" />
            </div>
            <div class="field">
              <label>密码</label>
              <input v-model="password" type="password" placeholder="请输入密码" class="input-field" @keydown.enter="handleLogin" />
            </div>
            <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
            <button class="btn" :disabled="loading" @click="handleLogin">
              {{ loading ? '登录中...' : '登 录' }}
            </button>
          </div>
          <div class="footer">
            没有账号？<router-link to="/register" class="link">立即注册</router-link>
          </div>
          <div class="demo">
            测试账号: 13800000001/admin123 · 13800000002/teacher123 · 13800000003/parent123 · 13800000004/student123
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-bg {
  min-height: 100vh;
  display: flex;
  background: var(--color-bg);
}
.login-left {
  flex: 1;
  background: linear-gradient(135deg, #4f7cff 0%, #7c3aed 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px;
  color: #fff;
}
.brand { display: flex; align-items: center; gap: 16px; margin-bottom: 48px; }
.brand-icon {
  width: 56px; height: 56px; border-radius: 16px;
  background: rgba(255,255,255,0.2);
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 800;
}
.brand-name { font-size: 22px; font-weight: 700; }
.brand-slogan { font-size: 13px; opacity: 0.8; margin-top: 2px; }
.features { display: flex; flex-direction: column; gap: 16px; margin-top: 40px; }
.feat-item { display: flex; align-items: center; gap: 12px; font-size: 15px; opacity: 0.9; }
.feat-icon { font-size: 20px; }
.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}
.card { width: 400px; background: var(--color-surface); border-radius: var(--radius-lg); padding: 40px; box-shadow: var(--shadow-lg); }
.title { font-size: 26px; font-weight: 800; color: var(--color-text-primary); margin: 0 0 4px; letter-spacing: -0.5px; }
.subtitle { color: var(--color-text-secondary); margin: 0 0 28px; font-size: 14px; }
.form { margin-top: 24px; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: var(--color-text-secondary); margin-bottom: 6px; font-weight: 500; }
.error { color: var(--color-danger); font-size: 13px; margin: 8px 0; }
.footer { text-align: center; margin-top: 20px; font-size: 14px; color: var(--color-text-secondary); }
.footer .link { color: var(--color-primary); text-decoration: none; font-weight: 600; }
.demo { margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--color-border-light); font-size: 11px; color: var(--color-text-muted); text-align: center; line-height: 1.6; }
</style>
