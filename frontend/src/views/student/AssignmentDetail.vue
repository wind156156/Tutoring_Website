<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NSpace } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { getStudentAssignment, submitAssignment, uploadFile } from '@/api/assignments'
import { truncate } from '@/utils/text'

const router = useRouter()
const route = useRoute()
const message = { success: (m) => window.alert(m), error: (m) => window.alert(m), warning: (m) => window.alert(m) }
const assignment = ref<any>(null)
const loading = ref(true)
const submitting = ref(false)
const uploading = ref(false)
const submittedFiles = ref<Array<{ url: string; name: string }>>([])
const showFullComment = ref(false)

async function load() {
  loading.value = true
  try {
    const data: any = await getStudentAssignment(Number(route.params.id))
    assignment.value = data
    submittedFiles.value = data.student_submitted_files || []
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function onNativeFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (!files || files.length === 0) return
  uploading.value = true
  try {
    await Promise.all(Array.from(files).map(async (file) => {
      const res = await uploadFile(file)
      submittedFiles.value.push({ url: res.url, name: res.name })
    }))
    message.success('文件已添加')
  } catch (e: any) {
    message.error(e?.message || '上传失败')
  } finally {
    uploading.value = false
    input.value = ''
  }
}

function removeFile(index: number) {
  submittedFiles.value.splice(index, 1)
}

async function handleSubmit() {
  if (!submittedFiles.value.length) {
    message.warning('请先上传作业文件')
    return
  }
  submitting.value = true
  try {
    await submitAssignment(Number(route.params.id), submittedFiles.value)
    message.success('提交成功')
    load()
  } catch (e: any) {
    message.error(e?.message || '提交失败')
  } finally {
    submitting.value = false
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
        <p v-if="assignment.student_submitted_files?.length" style="margin: 8px 0; font-size: 13px; color: var(--color-text-secondary);">
          你的提交:
          <n-space :size="4" style="margin-top:6px;">
            <n-tag v-for="f in assignment.student_submitted_files" :key="f.url" size="small">
              <a :href="f.url" target="_blank" style="color: inherit; text-decoration: none;">📎 {{ f.name }}</a>
            </n-tag>
          </n-space>
        </p>
      </div>

      <!-- Submitted status -->
      <div v-else-if="assignment.status === 'submitted'" class="section-card" style="margin-top: 16px; background: var(--color-success-light);">
        <p style="margin: 0; font-weight: 500;">✅ 已提交，等待老师批改</p>
        <n-space v-if="assignment.student_submitted_files?.length" :size="4" style="margin-top: 8px;">
          <n-tag v-for="f in assignment.student_submitted_files" :key="f.url" size="small">
            <a :href="f.url" target="_blank" style="color: inherit; text-decoration: none;">📎 {{ f.name }}</a>
          </n-tag>
        </n-space>
      </div>

      <!-- Overdue status -->
      <div v-else-if="assignment.status === 'overdue'" class="section-card" style="margin-top: 16px; background: var(--color-danger-light);">
        <p style="margin: 0; font-weight: 500; color: var(--color-danger);">⚠️ 作业已过期，无法提交</p>
      </div>

      <!-- Submission form -->
      <div v-else>
        <div class="section-card" style="margin-top: 16px;">
          <div style="font-weight: 600; font-size: 14px; color: var(--color-text-primary); margin-bottom: 14px;">提交作业</div>
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 12px;">
            <label :style="{ display: 'inline-block', cursor: submitting || uploading ? 'not-allowed' : 'pointer', padding: '8px 18px', border: '1.5px solid var(--color-primary)', borderRadius: 'var(--radius-sm)', color: 'var(--color-primary)', fontSize: '13px', fontWeight: 500 }">
              <input
                v-if="!submitting && !uploading"
                type="file"
                multiple
                accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.zip,.rar"
                style="display: none"
                @change="onNativeFileSelect"
              >
              <span>{{ uploading ? '上传中...' : '+ 上传文件/图片' }}</span>
            </label>
            <n-tag
              v-for="(f, idx) in submittedFiles"
              :key="idx"
              closable
              @close="removeFile(idx)"
            >
              📎 {{ f.name }}
            </n-tag>
          </div>
          <n-button type="primary" :loading="submitting" :disabled="!submittedFiles.length" @click="handleSubmit">
            提交作业
          </n-button>
        </div>
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
