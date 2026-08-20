<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NSpace, NPagination, NModal, NImage } from 'naive-ui'
import { getPendingTeachers, verifyTeacher } from '@/api/admin'

const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const teachers = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const previewUrl = ref('')
const showPreview = ref(false)

function openPreview(url: string) {
  previewUrl.value = url
  showPreview.value = true
}

function isImageUrl(url: string): boolean {
  return /\.(jpg|jpeg|png|gif)$/i.test(url)
}

async function load(p: number = 1) {
  loading.value = true
  try {
    const res: any = await getPendingTeachers({ page: p, page_size: pageSize.value })
    teachers.value = res.items || []
    total.value = res.total || 0
    page.value = p
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function handleVerify(id: number, action: 'approve' | 'reject') {
  try {
    await verifyTeacher(id, action)
    message.success(action === 'approve' ? '审核通过' : '已拒绝')
    load(page.value)
  } catch (e: any) {
    message.error(e?.message || '操作失败')
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="toolbar">
      <h2 class="toolbar-title">老师资质审核</h2>
      <span class="tag tag-warning" v-if="!loading">待审核: {{ total }} 人</span>
    </div>

    <div class="table-wrapper fade-in">
      <table v-if="!loading && teachers.length">
        <thead>
          <tr>
            <th>姓名</th><th>学历</th><th>职称</th><th>授课科目</th><th>时薪</th><th>地区</th><th>资质图</th><th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in teachers" :key="t.id">
            <td>
              <div style="display:flex;align-items:center;gap:8px;">
                <div style="width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,#4f7cff,#7c3aed);color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;flex-shrink:0;">
                  {{ t.real_name?.[0] || 'T' }}
                </div>
                <span style="font-weight:500;">{{ t.real_name }}</span>
              </div>
            </td>
            <td>{{ t.education }}</td>
            <td><span class="tag tag-primary">{{ t.title }}</span></td>
            <td>
              <div style="display:flex;gap:4px;flex-wrap:wrap;">
                <span v-for="s in t.subject_tags" :key="s" class="tag tag-info">{{ s }}</span>
              </div>
            </td>
            <td style="font-weight:700;color:var(--color-accent);">¥{{ t.hourly_rate }}<span style="font-size:11px;color:var(--color-text-muted);font-weight:400;">/h</span></td>
            <td>{{ t.city }} · {{ t.district }}</td>
            <td>
              <n-button v-if="t.qualification_url" text size="small" type="primary" @click="openPreview(t.qualification_url)">查看</n-button>
              <span v-else style="color:var(--color-text-muted);">-</span>
            </td>
            <td>
              <n-button size="small" type="success" style="margin-right:6px;font-size:12px;padding:4px 10px;" @click="handleVerify(t.id, 'approve')">通过</n-button>
              <n-button size="small" type="error" strong secondary style="font-size:12px;padding:4px 10px;" @click="handleVerify(t.id, 'reject')">拒绝</n-button>
            </td>
          </tr>
        </tbody>
      </table>
      <n-empty v-if="!loading && !teachers.length" description="暂无待审核老师" style="padding: 40px;" />
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

    <n-modal v-model:show="showPreview" preset="card" title="资质证书" style="width: 600px;">
      <div v-if="isImageUrl(previewUrl)" style="text-align: center;">
        <n-image :src="previewUrl" :width="560" style="max-width: 100%; border-radius: 8px;" />
      </div>
      <div v-else-if="previewUrl" style="padding: 20px; text-align: center;">
        <a :href="previewUrl" target="_blank" style="color: var(--color-primary);">📄 点击下载查看</a>
      </div>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showPreview = false">关闭</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
