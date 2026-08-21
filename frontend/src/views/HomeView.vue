<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAnnouncements } from '@/api/common'

const router = useRouter()
const announcements = ref<any[]>([])

async function loadAnnouncements() {
  try {
    announcements.value = await getAnnouncements()
  } catch {
    // ignore public endpoint failures
  }
}

onMounted(loadAnnouncements)
</script>

<template>
  <div class="home">
    <nav class="navbar">
      <div class="logo">
        <span class="logo-icon">家</span>
        <span class="logo-text">家教平台</span>
      </div>
      <div class="nav-actions">
        <router-link to="/login">
          <button class="btn-login">登录</button>
        </router-link>
        <router-link to="/register" style="margin-left: 10px;">
          <button class="btn-register">免费注册</button>
        </router-link>
      </div>
    </nav>

    <div class="hero">
      <div class="hero-content">
        <div class="badge">专为家庭教育的智能平台</div>
        <h1 class="hero-title">连接家长、老师与学生</h1>
        <p class="hero-subtitle">让每一次学习都有温度<br>专业的家教匹配，透明的教学进度，及时的沟通反馈</p>
        <div class="hero-actions">
          <router-link to="/register">
            <button class="btn-hero-primary">立即开始</button>
          </router-link>
          <router-link to="/login">
            <button class="btn-hero-outline">了解更多</button>
          </router-link>
        </div>
      </div>
      <div class="hero-visual">
        <div class="floating-card c1">👩‍🏫 名师一对一</div>
        <div class="floating-card c2">📚 全科目覆盖</div>
        <div class="floating-card c3">💬 实时沟通</div>
      </div>
    </div>

    <footer class="footer">
      <p>© 2026 家教平台 · 让教育更有温度</p>
    </footer>
  </div>
</template>

<style scoped>
.home { min-height: 100vh; display: flex; flex-direction: column; }
.navbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 48px; background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
}
.logo { display: flex; align-items: center; gap: 10px; }
.logo-icon {
  width: 36px; height: 36px; border-radius: 10px;
  background: linear-gradient(135deg, #4f7cff, #7c3aed);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 800;
}
.logo-text { font-size: 18px; font-weight: 700; color: var(--color-text-primary); }
.nav-actions { display: flex; gap: 10px; }
.btn-login {
  padding: 9px 20px; border-radius: var(--radius-md); border: 1.5px solid var(--color-border);
  background: transparent; cursor: pointer; font-size: 14px; font-weight: 500; color: var(--color-text-primary);
  transition: all 0.15s;
}
.btn-login:hover { border-color: var(--color-primary); color: var(--color-primary); }
.btn-register {
  padding: 9px 20px; border-radius: var(--radius-md); border: none;
  background: linear-gradient(135deg, #4f7cff, #7c3aed);
  cursor: pointer; font-size: 14px; font-weight: 600; color: #fff;
  transition: opacity 0.15s;
}
.btn-register:hover { opacity: 0.9; }
.hero {
  flex: 1; display: flex; align-items: center;
  padding: 80px 48px; gap: 60px;
  background: linear-gradient(135deg, #4f7cff 0%, #7c3aed 100%);
  color: #fff;
}
.hero-content { max-width: 520px; }
.badge {
  display: inline-block; padding: 6px 16px; border-radius: 20px;
  background: rgba(255,255,255,0.15); font-size: 13px; font-weight: 500;
  margin-bottom: 24px; backdrop-filter: blur(4px);
}
.hero-title { font-size: 48px; font-weight: 800; margin: 0 0 20px; line-height: 1.15; letter-spacing: -1px; }
.hero-subtitle { font-size: 17px; opacity: 0.9; margin: 0 0 36px; line-height: 1.7; white-space: pre-line; }
.hero-actions { display: flex; gap: 14px; }
.btn-hero-primary {
  padding: 14px 32px; border-radius: var(--radius-md); border: none;
  background: #fff; color: #4f7cff; font-size: 16px; font-weight: 700;
  cursor: pointer; transition: transform 0.15s, box-shadow 0.15s;
}
.btn-hero-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.2); }
.btn-hero-outline {
  padding: 14px 32px; border-radius: var(--radius-md); border: 2px solid rgba(255,255,255,0.5);
  background: transparent; color: #fff; font-size: 16px; font-weight: 600;
  cursor: pointer; transition: all 0.15s;
}
.btn-hero-outline:hover { border-color: #fff; background: rgba(255,255,255,0.1); }
.hero-visual { position: relative; width: 320px; height: 280px; flex-shrink: 0; }
.floating-card {
  position: absolute; padding: 16px 24px; border-radius: 16px;
  background: rgba(255,255,255,0.15); backdrop-filter: blur(8px);
  font-size: 16px; font-weight: 600; border: 1px solid rgba(255,255,255,0.2);
}
.c1 { top: 0; right: 0; animation: float 3s ease-in-out infinite; }
.c2 { top: 100px; left: 0; animation: float 3s ease-in-out infinite 0.5s; }
.c3 { bottom: 0; right: 40px; animation: float 3s ease-in-out infinite 1s; }
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
.footer { text-align: center; padding: 24px; background: #f8fafc; color: var(--color-text-muted); font-size: 13px; border-top: 1px solid var(--color-border-light); }
a { text-decoration: none; }
</style>
