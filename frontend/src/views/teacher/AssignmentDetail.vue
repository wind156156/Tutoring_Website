<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NSpace } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { getAssignment, gradeAssignment } from '@/api/assignments'
import { truncate } from '@/utils/text'

const router = useRouter()
const route = useRoute()
const message = { success: (m: string) => window.alert(m), error: (m: string) => window.alert(m) }

const assignment = ref<any>(null)
const loading = ref(true)
const showGrading = ref(false)
const viewCommentModal = ref(false)
const selectedStudent = ref<number>(0)
const gradeScore = ref(0)
const gradeComment = ref('')
const commentText = ref('')

async function load() {
  loading.value = true
  try {
    assignment.value = await getAssignment(Number(route.params.id))
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function startGrade(sub: any) {
  showGrading.value = true
  selectedStudent.value = sub.student_id
  gradeScore.value = sub.score || 0
  gradeComment.value = sub.comment || ''
}

function viewCommentBtn(sub: any) {
  commentText.value = sub.comment || ''
  viewCommentModal.value = true
}

async function submitGrade() {
  if (!showGrading.value) return
  try {
    await gradeAssignment(Number(route.params.id), selectedStudent.value, {
      score: gradeScore.value,
      comment: gradeComment.value,
    })
    message.success('批改成功')
    showGrading.value = false
    load()
  } catch (e: any) {
    message.error(e?.message || '批改失败')
  }
}

const statusLabels: Record<string, string> = {
  pending: '待提交', submitted: '已提交', graded: '已批改', overdue: '已过期'
}
const statusStyles: Record<string, string> = {
  pending: 'tag-warning', submitted: 'tag-info', graded: 'tag-success', overdue: 'tag-danger'
}

function openFile(url: string) {
  window.open(url)
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
      <p style="color: var(--color-text-secondary); margin-bottom: 20px; font-size: 14px;">
        截止: {{ new Date(assignment.due_at).toLocaleString() }}
        &nbsp;·&nbsp; 满分: {{ assignment.max_score }}
        &nbsp;·&nbsp; 学生数: {{ assignment.submissions?.length || 0 }}
      </p>
      <p v-if="assignment.description" style="white-space: pre-wrap; color: var(--color-text-secondary); margin-bottom: 24px; line-height: 1.7;">
        {{ assignment.description }}
      </p>

      <!-- Teacher attachments -->
      <div v-if="assignment.content_images?.length" style="margin-bottom: 24px;">
        <div style="font-weight: 600; font-size: 14px; color: var(--color-text-primary); margin-bottom: 8px;">📎 教师附件</div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
          <n-tag v-for="(img, i) in assignment.content_images" :key="i" closable style="cursor:pointer;" @close="() => {}">
            <a :href="img" target="_blank" style="color: inherit; text-decoration: none;">📎 附件 {{ i + 1 }}</a>
          </n-tag>
        </div>
      </div>

      <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
        <h3 style="margin: 0; font-size: 16px; font-weight: 600;">提交情况 ({{ assignment.submissions?.length || 0 }})</h3>
      </div>
      <div class="table-wrapper">
        <table>
          <thead><tr><th>学生</th><th>状态</th><th>分数</th><th>评语</th><th>提交文件</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="sub in assignment.submissions" :key="sub.id">
              <td style="font-weight:500;">{{ sub.student_name }}</td>
              <td><span :class="['tag', statusStyles[sub.status]]">{{ statusLabels[sub.status] || sub.status }}</span></td>
              <td style="font-weight:700;">{{ sub.score ?? '-' }}</td>
              <td style="max-width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" :title="sub.comment || ''">{{ truncate(sub.comment, 30) || '-' }}</td>
              <td>
                <n-button v-for="f in sub.files" :key="f.url" text size="small" @click="openFile(f.url)" style="font-size:12px;">📎 {{ f.name }}</n-button>
                <span v-if="!sub.files.length" style="color: var(--color-text-muted);">-</span>
              </td>
              <td>
                <n-button v-if="sub.status !== 'graded'" text type="primary" size="small" style="font-size:12px;" @click="startGrade(sub)">批改</n-button>
                <n-button v-else text size="small" style="font-size:12px;" @click="viewCommentBtn(sub)">详情</n-button>
              </td>
            </tr>
            <tr v-if="!assignment.submissions?.length">
              <td colspan="6" style="text-align: center; color: var(--color-text-muted); padding: 30px;">暂无学生提交</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Grading modal -->
    <n-modal v-model:show="showGrading" preset="card" title="批改作业" style="width: 480px;">
      <n-form label-placement="left" label-width="60">
        <n-form-item label="分数">
          <n-input-number v-model:value="gradeScore" :min="0" :max="assignment?.max_score || 100" />
        </n-form-item>
        <n-form-item label="评语">
          <n-input v-model:value="gradeComment" type="textarea" :rows="3" placeholder="给学生写评语" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showGrading = false">取消</n-button>
          <n-button type="primary" @click="submitGrade">提交</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Comment detail modal -->
    <n-modal v-model:show="viewCommentModal" preset="card" title="评语详情" style="width: 480px;">
      <p style="white-space: pre-wrap; word-break: break-all; margin: 0; color: var(--color-text-secondary); line-height: 1.7;">{{ commentText }}</p>
      <template #footer>
        <n-space justify="end">
          <n-button @click="viewCommentModal = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
