<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NSpace } from 'naive-ui'
import { useRouter } from 'vue-router'
import { getMyStudents } from '@/api/teachers'

const router = useRouter()
const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const students = ref<any[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    students.value = await getMyStudents()
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
    <h2 class="page-title">我的学生</h2>
    <n-grid :cols="3" :x-gap="16" :y-gap="16" v-if="!loading && students.length">
      <n-gi v-for="s in students" :key="s.id">
        <div class="section-card fade-in">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
            <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#4f7cff,#7c3aed);color:#fff;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;flex-shrink:0;">
              {{ s.real_name?.[0] || 'S' }}
            </div>
            <div>
              <div style="font-weight:600;font-size:16px;">{{ s.real_name }}</div>
              <div style="font-size:12px;color:var(--color-text-muted);margin-top:2px;">{{ s.grade }} · {{ s.school }}</div>
            </div>
          </div>
          <div style="margin-bottom:14px;font-size:13px;color:var(--color-text-secondary);">
            <span style="font-weight:500;color:var(--color-text-primary);">薄弱科目:</span>
            <n-space wrap :size="4" style="margin-top:6px;">
              <n-tag v-for="subj in (s.subjects || [])" :key="subj" size="small" type="info">{{ subj }}</n-tag>
              <span v-if="!s.subjects?.length" style="color:var(--color-text-muted);">未设置</span>
            </n-space>
          </div>
          <n-button block size="small" @click="router.push(`/teacher/assignments?studentId=${s.id}`)">发布作业</n-button>
        </div>
      </n-gi>
    </n-grid>
    <n-empty v-if="!loading && !students.length" description="暂无绑定的学生" style="padding:60px;" />
  </div>
</template>
