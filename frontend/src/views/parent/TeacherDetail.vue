<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NResult, NSpace, NDescriptions } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { getTeacher, toggleFavorite } from '@/api/teachers'

const router = useRouter()
const route = useRoute()
const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }

const teacher = ref<any>(null)
const loading = ref(true)
const favoriting = ref(false)

const id = Number(route.params.id)

async function load() {
  loading.value = true
  try {
    teacher.value = await getTeacher(id)
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function handleFavorite() {
  if (!teacher.value) return
  favoriting.value = true
  try {
    const res: any = await toggleFavorite(id)
    teacher.value.is_favorited = res.is_favorited
    message.success(res.is_favorited ? '收藏成功' : '已取消收藏')
  } catch (e: any) {
    message.error(e?.message || '操作失败')
  } finally {
    favoriting.value = false
  }
}

onMounted(load)
</script>

<template>
  <div v-if="!loading">
    <n-button text type="primary" @click="router.back()" style="margin-bottom: 16px; font-weight: 500;">← 返回列表</n-button>
    <n-result
      v-if="!teacher"
      status="404"
      title="老师不存在"
      description="该老师可能已被下架"
    >
      <template #footer>
        <n-button type="primary" @click="router.push('/parent/teachers')">返回列表</n-button>
      </template>
    </n-result>
    <div v-else class="fade-in">
      <div class="detail-header">
        <div class="detail-avatar">{{ teacher.real_name?.[0] || 'T' }}</div>
        <div class="detail-title-row">
          <h1 class="detail-name">{{ teacher.real_name }}</h1>
          <p class="detail-meta">{{ teacher.title }} · {{ teacher.city }} {{ teacher.district }}</p>
          <n-space style="margin-top: 10px;">
            <n-tag v-for="s in (teacher.subject_tags || [])" :key="s" type="info">{{ s }}</n-tag>
            <n-tag v-if="teacher.is_verified" type="success">✓ 已认证</n-tag>
          </n-space>
        </div>
        <n-button
          :type="teacher.is_favorited ? 'primary' : 'default'"
          :soft="!teacher.is_favorited"
          :loading="favoriting"
          @click="handleFavorite"
          style="margin-left: auto;"
        >
          {{ teacher.is_favorited ? '★ 已收藏' : '☆ 收藏' }}
        </n-button>
      </div>

      <n-grid :cols="2" :x-gap="20" :y-gap="20">
        <n-gi>
          <div class="section-card">
            <div class="section-card-title">基本信息</div>
            <n-descriptions :column="1" label-style="width: 80px; color: var(--color-text-secondary); font-weight: 500;" item-style="padding: 8px 0;">
              <n-descriptions-item label="学历">{{ teacher.education }}</n-descriptions-item>
              <n-descriptions-item label="职称">{{ teacher.title }}</n-descriptions-item>
              <n-descriptions-item label="教龄">{{ teacher.experience_years }} 年</n-descriptions-item>
              <n-descriptions-item label="地区">{{ teacher.city }} {{ teacher.district }}</n-descriptions-item>
            </n-descriptions>
          </div>
        </n-gi>
        <n-gi>
          <div class="section-card">
            <div class="section-card-title">个人简介</div>
            <p style="color: var(--color-text-secondary); line-height: 1.8; margin: 0;">{{ teacher.bio || '暂无简介' }}</p>
          </div>
        </n-gi>
      </n-grid>

      <div class="section-card" style="margin-top: 20px; display: flex; align-items: center; gap: 24px;">
        <div>
          <div style="font-size: 13px; color: var(--color-text-muted); margin-bottom: 4px;">课时费用</div>
          <div style="font-size: 32px; font-weight: 800; color: var(--color-accent); letter-spacing: -1px;">
            ¥{{ teacher.hourly_rate }}
            <span style="font-size: 14px; color: var(--color-text-muted); font-weight: 400; letter-spacing: 0;">/ 小时</span>
          </div>
        </div>
        <n-button type="primary" size="large" style="margin-left: auto;" @click="router.push(`/parent/bindings?teacherId=${id}`)">
          发起绑定申请
        </n-button>
      </div>
    </div>
  </div>
  <n-spin v-else :show="true" />
</template>
