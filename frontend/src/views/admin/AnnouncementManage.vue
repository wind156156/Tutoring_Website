<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NInput, NModal, NForm, NFormItem, NSpace, NPagination } from 'naive-ui'
import { getAnnouncements, createAnnouncement, updateAnnouncement } from '@/api/admin'

const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const announcements = ref<any[]>([])
const loading = ref(false)
const showCreate = ref(false)
const form = ref({ title: '', content: '', publish_from: '', publish_to: '', is_active: 1 })
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

async function load(p: number = 1) {
  loading.value = true
  try {
    const res: any = await getAnnouncements({ page: p, page_size: pageSize.value })
    announcements.value = res.items || []
    total.value = res.total || 0
    page.value = p
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.value = { title: '', content: '', publish_from: '', publish_to: '', is_active: 1 }
  showCreate.value = true
}

async function handleSubmit() {
  if (!form.value.title || !form.value.content || !form.value.publish_from) {
    message.error('请填写完整信息')
    return
  }
  try {
    await createAnnouncement(form.value)
    message.success('创建成功')
    showCreate.value = false
    load(page.value)
  } catch (e: any) {
    message.error(e?.message || '创建失败')
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="toolbar">
      <h2 class="toolbar-title">公告管理</h2>
      <n-button type="primary" size="small" @click="openCreate">+ 新建公告</n-button>
    </div>

    <div class="table-wrapper fade-in">
      <table v-if="!loading && announcements.length">
        <thead>
          <tr><th>标题</th><th>状态</th><th>发布时间</th><th>创建时间</th></tr>
        </thead>
        <tbody>
          <tr v-for="a in announcements" :key="a.id">
            <td style="font-weight:500;">{{ a.title }}</td>
            <td>
              <span :class="['tag', a.is_active ? 'tag-success' : 'tag-default']">
                {{ a.is_active ? '已发布' : '已下架' }}
              </span>
            </td>
            <td style="color:var(--color-text-secondary);">
              {{ new Date(a.publish_from).toLocaleDateString() }} ~
              {{ a.publish_to ? new Date(a.publish_to).toLocaleDateString() : '长期' }}
            </td>
            <td style="color:var(--color-text-muted);">{{ new Date(a.created_at).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>
      <n-empty v-if="!loading && !announcements.length" description="暂无公告" style="padding:40px;" />
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

    <n-modal v-model:show="showCreate" preset="card" title="新建公告" style="width: 500px;">
      <n-form label-placement="left" label-width="80">
        <n-form-item label="标题">
          <n-input v-model:value="form.title" placeholder="公告标题" />
        </n-form-item>
        <n-form-item label="内容">
          <n-input v-model:value="form.content" type="textarea" :rows="4" placeholder="公告内容" />
        </n-form-item>
        <n-form-item label="发布时间">
          <n-date-picker v-model:formatted-value="form.publish_from" type="datetime" value-format="yyyy-MM-dd HH:mm" />
        </n-form-item>
        <n-form-item label="下架时间">
          <n-date-picker v-model:formatted-value="form.publish_to" type="datetime" value-format="yyyy-MM-dd HH:mm" clearable />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" @click="handleSubmit">发布</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
