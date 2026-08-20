<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag } from 'naive-ui'
import { useRouter } from 'vue-router'
import { getMyTeachers } from '@/api/assignments'

const router = useRouter()
const teachers = ref<any[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    teachers.value = await getMyTeachers()
  } catch (e: any) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <h2 class="page-title">我的老师</h2>
    <n-grid :cols="3" :x-gap="16" :y-gap="16" v-if="!loading && teachers.length">
      <n-gi v-for="t in teachers" :key="t.id">
        <div class="section-card fade-in" style="cursor:pointer;" @click="router.push(`/student/teachers/${t.id}`)">
          <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
            <div style="width:48px;height:48px;border-radius:12px;background:linear-gradient(135deg,#4f7cff,#7c3aed);color:#fff;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;flex-shrink:0;">
              {{ t.real_name?.[0] || 'T' }}
            </div>
            <div style="flex:1;">
              <div style="font-weight:600;font-size:16px;">{{ t.real_name }}</div>
              <div style="font-size:12px;color:var(--color-text-muted);margin-top:2px;">{{ t.education }} · {{ t.title }}</div>
            </div>
            <n-tag v-if="t.is_verified" type="success" size="small" style="margin-left:auto;">✓ 已认证</n-tag>
          </div>
          <div style="margin-bottom:10px;">
            <n-tag v-for="s in t.subject_tags" :key="s" size="small" type="info">{{ s }}</n-tag>
          </div>
          <div style="font-size:12px;color:var(--color-text-muted);display:flex;gap:4px;flex-wrap:wrap;">
            <span>📚 {{ t.experience_years }}年教龄</span>
            <span>·</span>
            <span>📍 {{ t.city }} {{ t.district }}</span>
          </div>
          <div style="font-size:18px;font-weight:800;color:var(--color-accent);margin-top:10px;">
            ¥{{ t.hourly_rate }}<span style="font-size:12px;color:var(--color-text-muted);font-weight:400;">/小时</span>
          </div>
        </div>
      </n-gi>
    </n-grid>
    <n-empty v-if="!loading && !teachers.length" description="暂无绑定的老师" style="padding:60px;" />
  </div>
</template>
