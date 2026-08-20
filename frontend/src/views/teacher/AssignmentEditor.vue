<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NInput, NDatePicker, NSelect, NSpace, NTag } from 'naive-ui'
import { useRouter } from 'vue-router'
import { createAssignment, uploadFile, getMySubjects } from '@/api/assignments'
import { getMyStudents } from '@/api/teachers'

const router = useRouter()
const message = { success: (m: string) => window.alert(m), error: (m: string) => window.alert(m) }
const loading = ref(false)
const uploading = ref(false)
const ready = ref(false)
const errorMsg = ref('')

const students = ref<any[]>([])
const subjects = ref<string[]>([])
const attachments = ref<Array<{ url: string; name: string }>>([])

const dueDate = ref<Date | null>(null)

const form = ref({
  title: '',
  subject: '',
  description: '',
  due_at: '' as string,
  max_score: 100,
  student_ids: [] as number[],
})

async function load() {
  try {
    const [sRes, subjRes] = await Promise.all([
      getMyStudents(),
      getMySubjects(),
    ])
    students.value = sRes || []
    subjects.value = subjRes || []
    ready.value = true

    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    tomorrow.setHours(18, 0, 0, 0)
    dueDate.value = tomorrow
    form.value.due_at = formatDate(tomorrow)
  } catch (e: any) {
    errorMsg.value = '加载数据失败: ' + (e?.message || '请重试')
    console.error('Load error:', e)
  }
}

function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

function onDateChange(date: Date | null) {
  dueDate.value = date
  if (date) {
    form.value.due_at = formatDate(date)
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
      attachments.value.push({ url: res.url, name: res.name })
    }))
    message.success('附件上传成功')
  } catch (e: any) {
    message.error(e?.message || '上传失败')
  } finally {
    uploading.value = false
    input.value = ''
  }
}

function removeAttachment(index: number) {
  attachments.value.splice(index, 1)
}

async function handleSubmit() {
  if (!form.value.title || !form.value.title.trim()) {
    message.error('请填写作业标题')
    return
  }
  if (!form.value.due_at) {
    message.error('请选择截止时间')
    return
  }
  if (!form.value.student_ids.length) {
    message.error('请选择至少一个学生')
    return
  }

  loading.value = true
  try {
    const data = {
      title: form.value.title.trim(),
      subject: form.value.subject,
      description: form.value.description,
      content_images: attachments.value.map(a => a.url),
      due_at: form.value.due_at,
      max_score: form.value.max_score,
      student_ids: form.value.student_ids,
    }
    await createAssignment(data)
    message.success('作业发布成功')
    router.push('/teacher/assignments')
  } catch (e: any) {
    message.error(e?.message || '发布失败，请重试')
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <h2 class="page-title">发布作业</h2>
    <n-alert v-if="errorMsg" type="error" style="margin-bottom: 16px; border-radius: var(--radius-md);">{{ errorMsg }}</n-alert>
    <n-spin :show="!ready">
      <div class="section-card" v-if="ready" style="max-width: 680px;">
        <n-form :model="form" label-placement="left" label-width="90">
          <n-form-item label="作业标题">
            <n-input v-model:value="form.title" placeholder="请输入作业标题" />
          </n-form-item>
          <n-form-item label="科目">
            <n-select
              v-model:value="form.subject"
              filterable
              placeholder="选择相关科目（可为空）"
              :options="subjects.map(s => ({ label: s, value: s }))"
            />
          </n-form-item>
          <n-form-item label="截止时间">
            <n-date-picker
              v-model:value="dueDate"
              type="datetime"
              @change="onDateChange"
              placeholder="选择截止时间"
              style="width: 100%;"
            />
          </n-form-item>
          <n-form-item label="满分">
            <n-input-number v-model:value="form.max_score" :min="1" :max="9999" />
          </n-form-item>
          <n-form-item label="选择学生">
            <n-select
              v-model:value="form.student_ids"
              multiple
              filterable
              placeholder="选择接收作业的学生"
              :options="students.map(s => ({ label: s.real_name, value: s.id }))"
            />
          </n-form-item>
          <n-form-item label="附件">
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
              <label :style="{ display: 'inline-block', cursor: uploading ? 'not-allowed' : 'pointer', padding: '7px 16px', border: '1.5px solid var(--color-primary)', borderRadius: 'var(--radius-sm)', color: 'var(--color-primary)', fontSize: '13px', fontWeight: 500 }">
                <input
                  v-if="!uploading"
                  type="file"
                  multiple
                  accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.zip,.rar"
                  style="display: none"
                  @change="onNativeFileSelect"
                >
                <span>{{ uploading ? '上传中...' : '+ 上传文件/图片' }}</span>
              </label>
              <n-tag
                v-for="(att, idx) in attachments"
                :key="idx"
                closable
                @close="removeAttachment(idx)"
              >
                📎 {{ att.name }}
              </n-tag>
            </div>
          </n-form-item>
          <n-form-item label="作业描述">
            <n-input
              v-model:value="form.description"
              type="textarea"
              :rows="4"
              placeholder="填写作业内容要求"
            />
          </n-form-item>
          <n-form-item>
            <n-space>
              <n-button type="primary" :loading="loading" @click="handleSubmit">发布作业</n-button>
              <n-button @click="router.push('/teacher/assignments')">取消</n-button>
            </n-space>
          </n-form-item>
        </n-form>
      </div>
    </n-spin>
  </div>
</template>
