<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NSpace, NCard } from 'naive-ui'
import { useRouter } from 'vue-router'
import { getMyFavorites } from '@/api/teachers'

const router = useRouter()
const favorites = ref<any[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    favorites.value = await getMyFavorites()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <h2 class="page-title">收藏老师</h2>
    <n-grid :cols="3" :x-gap="16" :y-gap="16" v-if="!loading && favorites.length">
      <n-gi v-for="t in favorites" :key="t.id">
        <div class="teacher-card fade-in">
          <div class="teacher-header">
            <div class="teacher-avatar">{{ t.real_name?.[0] || 'T' }}</div>
            <div>
              <p class="teacher-name">{{ t.real_name }}</p>
              <p class="teacher-title" style="margin-top:4px;">
                <n-space wrap :size="4">
                  <n-tag v-for="s in (t.subject_tags || [])" :key="s" size="small" type="info">{{ s }}</n-tag>
                </n-space>
              </p>
            </div>
          </div>
          <div class="teacher-actions" style="margin-top: auto; padding-top: 14px;">
            <n-button block size="small" @click="router.push(`/parent/teachers/${t.id}`)">查看详情</n-button>
          </div>
        </div>
      </n-gi>
    </n-grid>
    <n-empty v-if="!loading && !favorites.length" description="暂无收藏老师" style="padding: 60px;" />
  </div>
</template>
