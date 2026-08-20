<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NEmpty, NSpace, NPagination, NInput } from 'naive-ui'
import { useRouter } from 'vue-router'
import { getTeachers } from '@/api/teachers'

const router = useRouter()
const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const teachers = ref<any[]>([])
const loading = ref(false)
const searchSubject = ref('')
const searchCity = ref('')
const page = ref(1)
const pageSize = ref(12)
const total = ref(0)

async function load(p: number = 1) {
  loading.value = true
  try {
    const res: any = await getTeachers({
      subject: searchSubject.value || undefined,
      city: searchCity.value || undefined,
      page: p,
      page_size: pageSize.value,
    })
    teachers.value = res.items || []
    total.value = res.total || 0
    page.value = p
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function doSearch() { load(1) }
function resetSearch() {
  searchSubject.value = ''
  searchCity.value = ''
  load(1)
}

onMounted(() => load())
</script>

<template>
  <div>
    <h2 class="page-title">平台老师</h2>

    <div class="section-card" style="margin-bottom: 20px;">
      <n-space :size="12" wrap>
        <n-input v-model:value="searchSubject" placeholder="按科目筛选" style="width: 140px;" clearable @keydown.enter="doSearch" />
        <n-input v-model:value="searchCity" placeholder="按城市筛选" style="width: 140px;" clearable @keydown.enter="doSearch" />
        <n-button type="primary" size="small" @click="doSearch">搜索</n-button>
        <n-button size="small" @click="resetSearch">重置</n-button>
      </n-space>
    </div>

    <n-grid :cols="4" :x-gap="16" :y-gap="16" v-if="!loading">
      <n-gi v-for="t in teachers" :key="t.id">
        <div class="teacher-card fade-in">
          <div class="teacher-header">
            <div class="teacher-avatar">{{ t.real_name?.[0] || 'T' }}</div>
            <div>
              <p class="teacher-name">{{ t.real_name }}</p>
              <p class="teacher-title">{{ t.title || '教师' }}</p>
            </div>
          </div>
          <div style="margin-bottom: 10px;">
            <n-space wrap :size="4">
              <n-tag v-for="s in (t.subject_tags || [])" :key="s" size="small" type="info">{{ s }}</n-tag>
            </n-space>
          </div>
          <div class="teacher-info">📍 {{ t.city }} {{ t.district }}</div>
          <div class="teacher-info">📚 {{ t.experience_years }}年教学经验</div>
          <div class="teacher-price">¥{{ t.hourly_rate }}<span>/小时</span></div>
          <div class="teacher-actions">
            <n-button block size="small" @click="router.push(`/teacher/platform-teachers/${t.id}`)">查看详情</n-button>
          </div>
        </div>
      </n-gi>
    </n-grid>
    <n-empty v-if="!loading && !teachers.length" description="暂无老师" style="padding: 60px;" />

    <div v-if="total > pageSize" style="margin-top: 16px; text-align: center;">
      <n-pagination
        v-model:page="page"
        :page-count="Math.ceil(total / pageSize)"
        :page-size="pageSize"
        show-size-picker
        :page-sizes="[12, 20, 40]"
        @update:page="(p) => load(p)"
      />
    </div>
  </div>
</template>
