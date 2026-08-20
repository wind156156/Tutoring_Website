<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NSpace } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { getStudentAssignmentDetail } from '@/api/parents'
import { truncate } from '@/utils/text'

const router = useRouter()
const route = useRoute()
const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const assignment = ref<any>(null)
const loading = ref(true)
const showFullComment = ref(false)
const studentId = Number(route.params.student_id)
const assignmentId = Number(route.params.id)

async function load() {
  loading.value = true
  try {
    assignment.value = await getStudentAssignmentDetail(studentId, assignmentId)
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
    <n-button text type="primary" style="margin-bottom: 16px; font-weight: 500;" @click="router.back()">← 返回</n-button>
    <div v-if="assignment" class="fade-in">
      <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
        <h1 class="page-title" style="margin:0;">{{ assignment.title }}</h1>
        <n-tag v-if="assignment.subject" type="info">{{ assignment.subject }}</n-tag>
      </div>
      <p style="color: var(--color-text-secondary); margin-bottom: 4px; font-size: 14px;">
        老师: <strong style="color:var(--color-text-primary);">{{ assignment.teacher_name }}</strong>
        &nbsp;·&nbsp; 截止: {{ new Date(assignment.due_at).toLocaleString() }}
        &nbsp;·&nbsp; 满分: {{ assignment.max_score }}
      </p>
      <p v-if="assignment.description" style="white-space: pre-wrap; color: var(--color-text-secondary); margin: 16px 0; line-height: 1.7;">
        {{ assignment.description }}
      </p>

      <!-- Teacher attachments -->
      <div v-if="assignment.teacher_attachments?.length" style="margin: 16px 0;">
        <div style="font-weight: 600; font-size: 14px; color: var(--color-text-primary); margin-bottom: 8px;">📎 教师附件</div>
        <n-space wrap :size="8">
          <n-tag v-for="(att, i) in assignment.teacher_attachments" :key="i" style="cursor:pointer;">
            <a :href="att.url" target="_blank" style="color: inherit; text-decoration: none;">📎 {{ att.name || `附件${i + 1}` }}</a>
          </n-tag>
        </n-space>
      </div>

      <!-- Grade result -->
      <div v-if="assignment.score !== null" class="section-card" style="margin-top: 16px; background: var(--color-info-light);">
        <div style="font-weight: 600; font-size: 14px; color: var(--color-text-primary); margin-bottom: 8px;">📝 批改结果</div>
        <p style="margin: 4px 0; font-size: 15px;">分数: <strong style="color: var(--color-danger); font-size: 22px;">{{ assignment.score }} / {{ assignment.max_score }}</strong></p>
        <p v-if="assignment.comment" style="margin: 8px 0;">
          评语:
          <span v-if="assignment.comment.length > 50">
            {{ truncate(assignment.comment, 50) }}
            <n-button text size="small" type="primary" @click="showFullComment = true" style="margin-left:4px;">查看完整</n-button>
          </span>
          <span v-else>{{ assignment.comment }}</span>
        </p>
        <p v-if="assignment.files?.length" style="margin: 8px 0; font-size: 13px; color: var(--color-text-secondary);">
          提交文件:
          <n-space :size="4" style="margin-top:6px;">
            <n-tag v-for="f in assignment.files" :key="f.url" size="small">
              <a :href="f.url" target="_blank" style="color: inherit; text-decoration: none;">📎 {{ f.name }}</a>
            </n-tag>
          </n-space>
        </p>
      </div>

      <!-- Submitted status -->
      <div v-else-if="assignment.status === 'submitted'" class="section-card" style="margin-top: 16px; background: var(--color-success-light);">
        <p style="margin: 0; font-weight: 500;">✅ 已提交，等待老师批改</p>
      </div>

      <!-- Overdue status -->
      <div v-else-if="assignment.status === 'overdue'" class="section-card" style="margin-top: 16px; background: var(--color-danger-light);">
        <p style="margin: 0; font-weight: 500; color: var(--color-danger);">⚠️ 作业已过期</p>
      </div>

      <!-- Pending status -->
      <div v-else-if="assignment.status === 'pending'" class="section-card" style="margin-top: 16px; background: var(--color-warning-light);">
        <p style="margin: 0; font-weight: 500;">⏳ 待完成</p>
      </div>
    </div>
    <n-spin v-else :show="loading" />

    <!-- Full comment modal -->
    <n-modal v-model:show="showFullComment" preset="card" title="评语详情" style="width: 480px;">
      <p style="white-space: pre-wrap; word-break: break-all; margin: 0; color: var(--color-text-secondary); line-height: 1.7;">{{ assignment?.comment }}</p>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showFullComment = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
