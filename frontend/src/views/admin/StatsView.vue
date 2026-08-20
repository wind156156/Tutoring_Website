<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NCard, NGi, NGrid } from 'naive-ui'
import { getStats } from '@/api/admin'

const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const stats = ref<any>(null)
const loading = ref(false)

const statItems = [
  { label: '总用户数', key: 'total_users', color: '#4f7cff', bg: 'var(--color-primary-light)' },
  { label: '认证老师', key: 'total_teachers', color: '#22c55e', bg: 'var(--color-success-light)' },
  { label: '家长数', key: 'total_parents', color: '#3b82f6', bg: 'var(--color-info-light)' },
  { label: '学生数', key: 'total_students', color: '#f59e0b', bg: 'var(--color-warning-light)' },
  { label: '作业总量', key: 'total_assignments', color: '#8b5cf6', bg: '#f5f3ff' },
  { label: '提交次数', key: 'total_submissions', color: '#14b8a6', bg: '#f0fdfa' },
  { label: '绑定关系', key: 'total_bindings', color: '#ef4444', bg: 'var(--color-danger-light)' },
]

async function load() {
  loading.value = true
  try {
    stats.value = await getStats()
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <h2 class="page-title">数据统计</h2>
    <n-grid :cols="4" :x-gap="16" :y-gap="16" v-if="!loading && stats">
      <n-gi v-for="item in statItems" :key="item.key">
        <div class="stat-card">
          <div class="stat-value" :style="{ color: item.color }">
            {{ stats[item.key] || 0 }}
          </div>
          <div class="stat-label">{{ item.label }}</div>
        </div>
      </n-gi>
    </n-grid>
    <n-spin v-else :show="true" />
  </div>
</template>
