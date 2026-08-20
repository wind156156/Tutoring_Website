<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NInput, NForm, NFormItem, NSpace, NPagination } from 'naive-ui'
import { useRouter } from 'vue-router'
import { getMyBindings, replyBinding } from '@/api/teachers'

const router = useRouter()
const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const bindings = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const showReplyModal = ref(false)
const replyBindingId = ref<number>(0)
const replyAction = ref<'accept' | 'reject'>('accept')
const teacherReply = ref('')

async function load(p: number = 1) {
  const res: any = await getMyBindings({ status_filter: 'pending', page: p, page_size: pageSize.value })
  bindings.value = res.items || []
  total.value = res.total || 0
  page.value = p
}

function openReply(id: number, action: 'accept' | 'reject') {
  replyBindingId.value = id
  replyAction.value = action
  teacherReply.value = ''
  showReplyModal.value = true
}

async function submitReply() {
  loading.value = true
  try {
    await replyBinding(replyBindingId.value, replyAction.value, teacherReply.value || undefined)
    message.success(replyAction.value === 'accept' ? '已接受绑定' : '已拒绝申请')
    showReplyModal.value = false
    load(page.value)
  } catch (e: any) {
    message.error(e?.message || '操作失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => load())
</script>

<template>
  <div>
    <h2 class="page-title">绑定申请</h2>
    <div class="table-wrapper fade-in">
      <table v-if="bindings.length">
        <thead><tr><th>学生</th><th>家长</th><th>家长留言</th><th>申请时间</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="b in bindings" :key="b.id">
            <td style="font-weight:500;">{{ b.student_name }}</td>
            <td>{{ b.parent_name }}</td>
            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" :title="b.reply_message || ''">{{ b.reply_message || '-' }}</td>
            <td style="color:var(--color-text-muted);">{{ new Date(b.created_at).toLocaleDateString() }}</td>
            <td>
              <n-button text type="success" size="small" style="margin-right:4px;font-size:12px;" @click="openReply(b.id, 'accept')">接受</n-button>
              <n-button text type="error" size="small" style="font-size:12px;" @click="openReply(b.id, 'reject')">拒绝</n-button>
            </td>
          </tr>
        </tbody>
      </table>
      <n-empty v-if="!loading && !bindings.length" description="暂无待处理的绑定申请" style="padding:40px;" />
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

    <n-modal v-model:show="showReplyModal" preset="card" :title="replyAction === 'accept' ? '接受绑定申请' : '拒绝绑定申请'" style="width: 480px;">
      <n-form label-placement="left" label-width="80">
        <n-form-item label="学生">
          <span style="font-weight:500;">{{ bindings.find(b => b.id === replyBindingId)?.student_name }}</span>
        </n-form-item>
        <n-form-item label="家长留言">
          <p style="margin:0;color:var(--color-text-secondary);">{{ bindings.find(b => b.id === replyBindingId)?.reply_message || '无' }}</p>
        </n-form-item>
        <n-form-item label="我的回复（可选）">
          <n-input v-model:value="teacherReply" type="textarea" :rows="3" :placeholder="replyAction === 'accept' ? '可以给家长回个话（选填）' : '请说明拒绝原因（选填）'" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showReplyModal = false">取消</n-button>
          <n-button :type="replyAction === 'accept' ? 'success' : 'error'" :loading="loading" @click="submitReply">
            {{ replyAction === 'accept' ? '确认接受' : '确认拒绝' }}
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
