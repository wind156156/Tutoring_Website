<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NSpace, NPagination } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'
import { getStudents, getStudentAssignments } from '@/api/parents'

const route = useRoute()
const router = useRouter()
const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }

// Student list view (initial state)
const students = ref<any[]>([])
const loadingStudents = ref(false)

// Assignment list view
const assignments = ref<any[]>([])
const loadingAssignments = ref(false)
const selectedStudentId = ref<number | null>(null)
const studentName = ref('')
const statusFilter = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const statusOptions = [
  { label: '全部', value: '' },
  { label: '待完成', value: 'pending' },
  { label: '已提交', value: 'submitted' },
  { label: '已批改', value: 'graded' },
  { label: '已过期', value: 'overdue' },
]

const statusLabels: Record<string, string> = {
  pending: '待完成', submitted: '已提交', graded: '已批改', overdue: '已过期'
}
const statusStyles: Record<string, string> = {
  pending: 'tag-warning', submitted: 'tag-info', graded: 'tag-success', overdue: 'tag-danger'
}

async function loadStudents() {
  loadingStudents.value = true
  try {
    students.value = await getStudents()
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loadingStudents.value = false
  }
}

async function loadAssignments(p: number = 1) {
  if (!selectedStudentId.value) return
  loadingAssignments.value = true
  try {
    const res: any = await getStudentAssignments(selectedStudentId.value, {
      status_filter: statusFilter.value || undefined,
      page: p,
      page_size: pageSize.value,
    })
    assignments.value = res.items || []
    total.value = res.total || 0
    page.value = p
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loadingAssignments.value = false
  }
}

function handleView(studentId: number) {
  selectedStudentId.value = studentId
  const student = students.value.find(s => s.id === studentId)
  studentName.value = student?.real_name || ''
  statusFilter.value = ''
  loadAssignments(1)
}

function handleFilter(val: string) {
  statusFilter.value = val
  loadAssignments(1)
}

function goBack() {
  selectedStudentId.value = null
  studentName.value = ''
  assignments.value = []
  total.value = 0
  statusFilter.value = ''
}

onMounted(async () => {
  await loadStudents()
  // If student_id in query params, jump directly to assignments view
  const sid = route.query.student_id
  if (sid) {
    const student = students.value.find(s => s.id === Number(sid))
    if (student) {
      selectedStudentId.value = Number(sid)
      studentName.value = student.real_name
      await loadAssignments()
    }
  }
})
</script>

<template>
  <div>
    <!-- Student selection header (always visible) -->
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 20px;">
      <h2 class="page-title" style="margin:0;">学生作业</h2>
      <n-button v-if="selectedStudentId" text type="primary" size="small" @click="goBack" style="font-weight:500;">
        ← 返回列表
      </n-button>
      <span v-if="studentName" style="color: var(--color-text-secondary); font-size: 14px; margin-left: 4px;">
        — {{ studentName }}
      </span>
    </div>

    <!-- Student list -->
    <div v-if="!selectedStudentId">
      <div v-if="loadingStudents" style="text-align: center; padding: 40px; color: var(--color-text-muted);">加载中...</div>
      <div v-else-if="!students.length" class="section-card" style="text-align: center; padding: 40px; color: var(--color-text-muted);">
        暂无学生，请先在"学生管理"中添加学生
      </div>
      <div v-else class="table-wrapper fade-in">
        <table>
          <thead>
            <tr><th>姓名</th><th>性别</th><th>年级</th><th>学校</th><th>薄弱科目</th><th>操作</th></tr>
          </thead>
          <tbody>
            <tr v-for="s in students" :key="s.id">
              <td style="font-weight:500;">{{ s.real_name }}</td>
              <td>{{ s.gender === 'male' ? '男' : s.gender === 'female' ? '女' : '-' }}</td>
              <td>{{ s.grade }}</td>
              <td>{{ s.school }}</td>
              <td>
                <n-space wrap :size="4">
                  <n-tag v-for="subj in (s.subjects || [])" :key="subj" size="small" type="info">{{ subj }}</n-tag>
                </n-space>
              </td>
              <td>
                <n-button text type="primary" size="small" @click="handleView(s.id)">查看</n-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Assignment list -->
    <div v-else>
      <div class="section-card" style="margin-bottom: 20px; padding: 14px 20px;">
        <n-space :size="8" wrap>
          <n-button
            v-for="opt in statusOptions"
            :key="opt.value"
            :type="statusFilter === opt.value ? 'primary' : 'default'"
            size="small"
            @click="handleFilter(opt.value)"
          >
            {{ opt.label }}
          </n-button>
        </n-space>
      </div>
      <div class="table-wrapper fade-in">
        <div v-if="loadingAssignments" style="text-align: center; padding: 40px; color: var(--color-text-muted);">加载中...</div>
        <table v-else-if="assignments.length">
          <thead><tr><th>标题</th><th>科目</th><th>老师</th><th>截止时间</th><th>状态</th><th>分数</th><th>操作</th></tr></thead>
          <tbody>
            <tr v-for="a in assignments" :key="a.id">
              <td style="font-weight:500;">{{ a.title }}</td>
              <td><span v-if="a.subject" class="tag tag-info">{{ a.subject }}</span><span v-else style="color:var(--color-text-muted);">-</span></td>
              <td>{{ a.teacher_name }}</td>
              <td style="color:var(--color-text-secondary);">{{ new Date(a.due_at).toLocaleDateString() }}</td>
              <td><span :class="['tag', statusStyles[a.status]]">{{ statusLabels[a.status] || a.status }}</span></td>
              <td style="font-weight:600;">{{ a.score ?? '-' }}</td>
              <td>
                <n-button text type="primary" size="small" @click="router.push(`/parent/students/${selectedStudentId}/assignments/${a.assignment_id}`)">查看</n-button>
              </td>
            </tr>
          </tbody>
        </table>
        <n-empty v-else description="暂无作业" style="padding:40px;" />
      </div>
      <div v-if="total > pageSize" style="margin-top: 16px; text-align: center;">
        <n-pagination
          v-model:page="page"
          :page-count="Math.ceil(total / pageSize)"
          :page-size="pageSize"
          show-size-picker
          :page-sizes="[10, 20, 50]"
          @update:page="(p) => loadAssignments(p)"
        />
      </div>
    </div>
  </div>
</template>
