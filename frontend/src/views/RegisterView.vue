<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user.store'
import { validatePhone } from '@/utils/request'

const router = useRouter()
const store = useUserStore()
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const role = ref('parent')
const realName = ref('')
const loading = ref(false)
const errorMsg = ref('')

const roleOptions = [
  { label: '家长', value: 'parent', icon: '👨‍👩‍👧' },
  { label: '老师', value: 'teacher', icon: '👩‍🏫' },
]

async function handleRegister() {
  const phoneErr = validatePhone(phone.value)
  if (phoneErr) { errorMsg.value = phoneErr; return }
  if (!password.value) { errorMsg.value = '请填写密码'; return }
  if (password.value !== confirmPassword.value) { errorMsg.value = '两次密码不一致'; return }
  if (password.value.length < 6) { errorMsg.value = '密码至少6位'; return }
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await store.register(phone.value, password.value, role.value, realName.value)
    const roleMap: Record<string, string> = { parent: '/parent', teacher: '/teacher' }
    router.push(roleMap[res.user.role] || '/')
  } catch (e: any) {
    errorMsg.value = e?.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="register-bg">
      <div class="card fade-in">
        <div class="card-header">
          <div class="brand-icon">家</div>
          <div>
            <h1 class="title">创建账号</h1>
            <p class="subtitle">加入家教平台，开启学习之旅</p>
          </div>
        </div>
        <div class="form">
          <div class="field">
            <label>手机号</label>
            <input v-model="phone" type="text" placeholder="请输入手机号" class="input-field" />
          </div>
          <div class="field">
            <label>密码</label>
            <input v-model="password" type="password" placeholder="至少6位" class="input-field" />
          </div>
          <div class="field">
            <label>确认密码</label>
            <input v-model="confirmPassword" type="password" placeholder="再次输入密码" class="input-field" />
          </div>
          <div class="field">
            <label>注册角色</label>
            <div class="roles">
              <label v-for="r in roleOptions" :key="r.value" :class="['role-item', role === r.value ? 'active' : '']">
                <input type="radio" v-model="role" :value="r.value" />
                <span class="role-icon">{{ r.icon }}</span>
                <span>{{ r.label }}</span>
              </label>
            </div>
          </div>
          <div v-if="role === 'parent'" class="field">
            <label>真实姓名</label>
            <input v-model="realName" type="text" placeholder="请输入您的真实姓名" class="input-field" />
          </div>
          <p v-if="errorMsg" class="error">{{ errorMsg }}</p>
          <button class="btn" :disabled="loading" @click="handleRegister">
            {{ loading ? '注册中...' : '注 册' }}
          </button>
        </div>
        <div class="footer">
          已有账号？<router-link to="/login" class="link">去登录</router-link>
        </div>
        <div class="note">注：管理员账号由系统创建；学生账号需由家长绑定后创建</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-bg {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4f7cff 0%, #7c3aed 100%);
  padding: 20px;
}
.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 40px;
  width: 460px;
  box-shadow: var(--shadow-lg);
}
.card-header { display: flex; align-items: center; gap: 14px; margin-bottom: 28px; }
.brand-icon {
  width: 48px; height: 48px; border-radius: 12px;
  background: linear-gradient(135deg, #4f7cff, #7c3aed);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 800; flex-shrink: 0;
}
.title { font-size: 22px; font-weight: 800; color: var(--color-text-primary); margin: 0 0 2px; letter-spacing: -0.3px; }
.subtitle { font-size: 13px; color: var(--color-text-secondary); margin: 0; }
.form { margin-top: 24px; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; color: var(--color-text-secondary); margin-bottom: 6px; font-weight: 500; }
.roles { display: flex; gap: 12px; }
.role-item {
  flex: 1;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 12px; border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md); cursor: pointer;
  font-size: 14px; font-weight: 500; color: var(--color-text-secondary);
  transition: all 0.15s;
}
.role-item:hover { border-color: var(--color-primary); color: var(--color-primary); }
.role-item.active { border-color: var(--color-primary); background: var(--color-primary-light); color: var(--color-primary); }
.role-icon { font-size: 18px; }
.btn { width: 100%; padding: 13px; background: linear-gradient(135deg, #4f7cff, #7c3aed); color: #fff; border: none; border-radius: var(--radius-md); font-size: 16px; font-weight: 700; cursor: pointer; margin-top: 8px; letter-spacing: 2px; transition: opacity 0.15s; }
.btn:hover { opacity: 0.92; }
.btn:disabled { opacity: 0.55; }
.error { color: var(--color-danger); font-size: 13px; margin: 8px 0; }
.footer { text-align: center; margin-top: 20px; font-size: 14px; color: var(--color-text-secondary); }
.footer .link { color: var(--color-primary); text-decoration: none; font-weight: 600; }
.note { margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--color-border-light); font-size: 12px; color: var(--color-text-muted); text-align: center; line-height: 1.6; }
</style>
