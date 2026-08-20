<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NSpace, NPagination } from 'naive-ui'
import { useRouter } from 'vue-router'
import { getMyAssignments } from '@/api/assignments'

const router = useRouter()
const message = { success: (m: string) => window.alert(m), error: (m: string) => window.alert(m) }
const assignments = ref<any[]>([])
const loading = ref(false)
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

async function load(p: number = 1) {
  loading.value = true
  try {
    const res: any = await getMyAssignments({ status_filter: statusFilter.value, page: p, page_size: pageSize.value })
    assignments.value = res.items || []
    total.value = res.total || 0
    page.value = p
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function handleFilter(val: string) {
  statusFilter.value = val
  load(1)
}

onMounted(() => load())
</script>

<template>
  <div>
    <h2 class="page-title">我的作业</h2>
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
      <table v-if="!loading && assignments.length">
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
              <n-button text type="primary" size="small" @click="router.push(`/student/assignments/${a.assignment_id}`)">查看</n-button>
            </td>
          </tr>
        </tbody>
      </table>
      <n-empty v-if="!loading && !assignments.length" description="暂无作业" style="padding:40px;" />
    </div>
    <div v-if="total > pageSize" style="margin-top: 16px; text-align: center;">
      <n-pagination
        v-model:page="page"
        :page-count="Math.ceil(total / pageSize)"
        :page-size="pageSize"
        show-size-picker
        :page-sizes="[10, 20, 50]"
        @update:page="(p) => load(p)"
      />
    </div>
  </div>
</template>
