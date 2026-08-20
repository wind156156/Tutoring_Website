<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NInput, NForm, NFormItem, NSpace, NSelect } from 'naive-ui'
import { useRouter, useRoute } from 'vue-router'
import { getBindings, createBinding } from '@/api/parents'
import { getStudents } from '@/api/parents'
import { getTeacher } from '@/api/teachers'

const router = useRouter()
const route = useRoute()
const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }

const bindings = ref<any[]>([])
const students = ref<any[]>([])
const loading = ref(false)
const submitting = ref(false)

const teacherId = ref<number | null>(null)
const teacherName = ref<string>('')
const selectedStudentId = ref<number | null>(null)
const replyMessage = ref('')
const showForm = ref(false)

const statusLabels: Record<string, string> = {
  pending: '待审核', accepted: '已接受', rejected: '已拒绝', expired: '已过期'
}

async function load() {
  loading.value = true
  try {
    const [bindingsRes, studentsRes] = await Promise.all([
      getBindings(),
      getStudents(),
    ])
    bindings.value = bindingsRes || []
    students.value = studentsRes || []

    // 如果 URL 带了 teacherId，自动展开表单
    const tid = Number(route.query.teacherId)
    if (tid && !teacherId.value) {
      teacherId.value = tid
      try {
        const t = await getTeacher(tid)
        teacherName.value = t.real_name || `老师 #${tid}`
        showForm.value = true
      } catch {
        teacherName.value = `老师 #${tid}`
        showForm.value = true
      }
    }
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function handleSubmit() {
  if (!selectedStudentId.value) { message.error('请选择学生'); return }
  if (!teacherId.value) { message.error('老师信息缺失'); return }
  submitting.value = true
  try {
    await createBinding({
      teacher_id: teacherId.value,
      student_id: selectedStudentId.value,
      reply_message: replyMessage.value || undefined,
    })
    message.success('绑定申请已发送，等待老师确认')
    showForm.value = false
    selectedStudentId.value = null
    replyMessage.value = ''
    await load()
  } catch (e: any) {
    message.error(e?.message || '发送失败')
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  showForm.value = false
  selectedStudentId.value = null
  replyMessage.value = ''
}

onMounted(load)
</script>

<template>
  <div>
    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px;">
      <h2 class="page-title" style="margin: 0;">绑定申请</h2>
      <n-button @click="router.push('/parent/teachers')">+ 发起申请</n-button>
    </div>

    <n-card v-if="showForm" title="发起新的绑定申请" style="margin-bottom: 20px;" class="section-card">
      <n-form label-placement="left" label-width="80">
        <n-form-item label="目标老师">
          <span style="font-weight: 500;">{{ teacherName || '—' }}</span>
        </n-form-item>
        <n-form-item label="选择学生">
          <n-select
            v-model:value="selectedStudentId"
            placeholder="选择要绑定的学生"
            :options="students.map(s => ({ label: s.real_name, value: s.id }))"
          />
        </n-form-item>
        <n-form-item label="留言（可选）">
          <n-input
            v-model:value="replyMessage"
            type="textarea"
            placeholder="可以给老师留个话"
            :rows="2"
          />
        </n-form-item>
        <n-form-item>
          <n-space>
            <n-button type="primary" :loading="submitting" @click="handleSubmit">发送申请</n-button>
            <n-button @click="resetForm">取消</n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>

    <div class="table-wrapper fade-in" v-if="!loading && bindings.length">
      <table>
        <thead>
          <tr><th>老师</th><th>学生</th><th>状态</th><th>我的留言</th><th>老师回复</th><th>申请时间</th></tr>
        </thead>
        <tbody>
          <tr v-for="b in bindings" :key="b.id">
            <td style="font-weight:500;">{{ b.teacher_name || '—' }}</td>
            <td>{{ b.student_name || '—' }}</td>
            <td><span :class="['binding-status', b.status]">{{ statusLabels[b.status] || b.status }}</span></td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" :title="b.reply_message || ''">{{ b.reply_message || '-' }}</td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" :title="b.teacher_reply || ''">{{ b.teacher_reply || '-' }}</td>
            <td style="color:var(--color-text-muted);">{{ new Date(b.created_at).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <n-empty v-if="!loading && !bindings.length" description="暂无绑定申请，点击右上角发起申请" style="padding: 60px;" />
  </div>
</template>
