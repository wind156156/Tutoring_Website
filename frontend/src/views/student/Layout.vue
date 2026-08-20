<script setup lang="ts">
import { NLayout, NLayoutSider, NLayoutContent, NAvatar, NDropdown } from 'naive-ui'
import { useUserStore } from '@/stores/user.store'
import { useRouter, useRoute } from 'vue-router'
import { onMounted } from 'vue'

const store = useUserStore()
const router = useRouter()
const route = useRoute()

const menuOptions = [
  { label: '我的作业', key: '/student/assignments', icon: '📝' },
  { label: '我的老师', key: '/student/teachers', icon: '👩‍🏫' },
  { label: '成绩历史', key: '/student/grades', icon: '📊' },
]

const roleMenuOptions = [
  { label: '学生中心', key: 'role', disabled: true },
  { type: 'divider' as const },
  { label: '退出登录', key: 'logout' },
]

function handleMenuSelect(key: string) {
  if (key === 'logout') { store.logout(); router.push('/login') }
  else router.push(key)
}
function handleDropdownSelect(key: string) {
  if (key === 'logout') { store.logout(); router.push('/login') }
}
onMounted(() => { store.fetchUser() })
</script>

<template>
  <n-layout has-sider style="height: 100vh">
    <n-layout-sider :width="220" bordered collapse-mode="width" :collapsed-width="64" style="background: linear-gradient(180deg, #8b5cf6 0%, #7c3aed 100%);">
      <div class="sider-logo">
        <span style="font-size: 13px; font-weight: 500; opacity: 0.8; display: block; text-align: center; letter-spacing: 1px;">家教平台</span>
        <span style="font-size: 15px; font-weight: 700; display: block; text-align: center;">学生中心</span>
      </div>
      <div style="padding: 8px 0;">
        <div v-for="item in menuOptions" :key="item.key"
          :class="['menu-item', route.path.startsWith(item.key) ? 'active' : '']"
          @click="handleMenuSelect(item.key)">
          <span class="menu-icon">{{ item.icon }}</span>
          <span class="menu-label">{{ item.label }}</span>
        </div>
      </div>
    </n-layout-sider>
    <n-layout>
      <n-layout-header style="padding: 0 24px; height: 60px; display: flex; align-items: center; justify-content: flex-end; border-bottom: 1px solid var(--color-border); background: var(--color-surface);">
        <n-dropdown :options="roleMenuOptions" @select="handleDropdownSelect" placement="bottom-end">
          <div class="user-info">
            <n-avatar :size="32" style="background: linear-gradient(135deg, #8b5cf6, #7c3aed); border-radius: 8px;">
              {{ store.user?.nickname?.[0] || 'U' }}
            </n-avatar>
            <span class="username">{{ store.user?.nickname || store.user?.phone }}</span>
          </div>
        </n-dropdown>
      </n-layout-header>
      <n-layout-content style="padding: 24px; overflow-y: auto; background: var(--color-bg);">
        <router-view />
      </n-layout-content>
    </n-layout>
  </n-layout>
</template>

<style scoped>
.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 20px;
  cursor: pointer;
  color: rgba(255,255,255,0.75);
  transition: all 0.15s;
  border-left: 3px solid transparent;
}
.menu-item:hover { background: rgba(255,255,255,0.12); color: #fff; }
.menu-item.active {
  background: rgba(255,255,255,0.2);
  color: #fff;
  border-left-color: #fff;
}
.menu-icon { font-size: 16px; width: 20px; text-align: center; }
.menu-label { font-size: 14px; font-weight: 500; }
</style>
