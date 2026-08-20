<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NModal, NSpace } from 'naive-ui'
import { getMyGrades } from '@/api/assignments'
import { truncate } from '@/utils/text'

const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const grades = ref<any>(null)
const loading = ref(false)
const commentText = ref('')
const showCommentModal = ref(false)

async function load() {
  loading.value = true
  try {
    grades.value = await getMyGrades()
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function viewCommentBtn(g: any) {
  commentText.value = g.comment || ''
  showCommentModal.value = true
}

onMounted(load)
</script>

<template>
  <div>
    <h2 class="page-title">成绩历史</h2>
    <n-spin :show="loading">
      <n-grid :cols="3" :x-gap="16" :y-gap="16" v-if="grades">
        <n-gi>
          <div class="stat-card">
            <div class="stat-value" style="color: var(--color-primary);">{{ grades.total_assignments }}</div>
            <div class="stat-label">总作业数</div>
          </div>
        </n-gi>
        <n-gi>
          <div class="stat-card">
            <div class="stat-value" style="color: var(--color-success);">{{ grades.total_score?.toFixed(1) }}</div>
            <div class="stat-label">总得分</div>
          </div>
        </n-gi>
        <n-gi>
          <div class="stat-card">
            <div class="stat-value" style="color: var(--color-accent);">{{ grades.avg_score?.toFixed(1) }}</div>
            <div class="stat-label">平均分</div>
          </div>
        </n-gi>
      </n-grid>

      <div class="table-wrapper fade-in" style="margin-top: 24px;" v-if="grades?.grades?.length">
        <table>
          <thead><tr><th>作业标题</th><th>分数</th><th>评语</th><th>批改时间</th></tr></thead>
          <tbody>
            <tr v-for="g in grades.grades" :key="g.id">
              <td style="font-weight:500;">{{ g.title || '#' + g.assignment_id }}</td>
              <td><strong style="font-size:16px;">{{ g.score }}</strong></td>
              <td>
                <span v-if="g.comment">{{ truncate(g.comment, 50) }}</span>
                <span v-else style="color:var(--color-text-muted);">-</span>
                <n-button v-if="g.comment?.length > 50" text size="small" type="primary" @click="viewCommentBtn(g)" style="margin-left:4px;">详情</n-button>
              </td>
              <td style="color:var(--color-text-muted);">{{ g.graded_at ? new Date(g.graded_at).toLocaleDateString() : '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <n-empty v-if="!loading && (!grades?.grades?.length)" description="暂无成绩记录" style="padding:40px;" />
    </n-spin>

    <n-modal v-model:show="showCommentModal" preset="card" title="评语详情" style="width: 480px;">
      <p style="white-space: pre-wrap; word-break: break-all; margin: 0; color: var(--color-text-secondary); line-height: 1.7;">{{ commentText }}</p>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCommentModal = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
