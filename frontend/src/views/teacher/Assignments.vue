<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NSpace, NPagination } from 'naive-ui'
import { useRouter } from 'vue-router'
import { getAssignments, deleteAssignment } from '@/api/assignments'

const router = useRouter()
const message = { success: (m: string) => window.alert(m), error: (m: string) => window.alert(m) }
const assignments = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const statusLabels: Record<string, string> = {
  pending: '待提交', submitted: '已提交', graded: '已批改', overdue: '已过期'
}

async function load(p: number = 1) {
  loading.value = true
  try {
    const res: any = await getAssignments({ page: p, page_size: pageSize.value })
    assignments.value = res.items || []
    total.value = res.total || 0
    page.value = p
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteAssignment(id)
    message.success('删除成功')
    load(page.value)
  } catch (e: any) {
    message.error(e?.message || '删除失败')
  }
}

onMounted(() => load())
</script>

<template>
  <div>
    <div class="toolbar">
      <h2 class="toolbar-title">作业管理</h2>
      <n-button type="primary" size="small" @click="router.push('/teacher/assignments/new')">+ 发布作业</n-button>
    </div>
    <div class="table-wrapper fade-in">
      <table v-if="!loading && assignments.length">
        <thead>
          <tr><th>标题</th><th>科目</th><th>截止时间</th><th>学生数</th><th>已批改</th><th>操作</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in assignments" :key="a.id">
            <td style="font-weight:500;">{{ a.title }}</td>
            <td><span v-if="a.subject" class="tag tag-info">{{ a.subject }}</span><span v-else style="color:var(--color-text-muted);">-</span></td>
            <td style="color:var(--color-text-secondary);">{{ new Date(a.due_at).toLocaleDateString() }}</td>
            <td>{{ a.student_count }}</td>
            <td>
              <span style="font-weight:600;color:var(--color-success);">{{ a.graded_count }}</span>
              <span style="color:var(--color-text-muted);">/{{ a.student_count }}</span>
            </td>
            <td>
              <n-button text type="primary" size="small" style="margin-right:4px;font-size:12px;" @click="router.push(`/teacher/assignments/${a.id}`)">详情</n-button>
              <n-button text type="error" size="small" style="font-size:12px;" @click="handleDelete(a.id)">删除</n-button>
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
