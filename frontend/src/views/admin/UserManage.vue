<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NTag, NPagination, NModal, NInput, NForm, NFormItem, NSpace, NPopconfirm } from 'naive-ui'
import { getUsers, updateUserStatus, deleteUser } from '@/api/admin'

const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const users = ref<any[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showSearch = ref(false)
const searchQuery = ref('')

async function load(p: number = 1) {
  loading.value = true
  try {
    const params: any = { page: p, page_size: pageSize.value }
    if (searchQuery.value) params.search = searchQuery.value
    const res: any = await getUsers(params)
    users.value = res?.items || []
    total.value = res?.total || 0
    page.value = p
  } catch (e: any) {
    message.error(e?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

async function handleToggleStatus(user: any) {
  const newStatus = user.status === 'active' ? 'frozen' : 'active'
  try {
    await updateUserStatus(user.id, newStatus)
    user.status = newStatus
    message.success(newStatus === 'active' ? '已解冻' : '已冻结')
  } catch (e: any) {
    message.error(e?.message || '操作失败')
  }
}

async function handleDelete(user: any) {
  try {
    await deleteUser(user.id)
    message.success(`已删除用户 ${user.phone}`)
    load(page.value)
  } catch (e: any) {
    message.error(e?.message || '删除失败')
  }
}

const roleColors: Record<string, string> = { parent: 'default', teacher: 'success', student: 'info', admin: 'primary' }
const statusColors: Record<string, string> = { active: 'success', frozen: 'danger', pending: 'warning' }

onMounted(() => load())
</script>

<template>
  <div>
    <div class="toolbar">
      <h2 class="toolbar-title">用户管理</h2>
      <n-button type="primary" size="small" @click="showSearch = !showSearch">
        {{ showSearch ? '收起筛选' : '搜索用户' }}
      </n-button>
    </div>

    <div v-if="showSearch" class="section-card" style="margin-bottom: 20px;">
      <n-form label-placement="inline" label-width="60">
        <n-form-item label="关键词">
          <n-input v-model:value="searchQuery" placeholder="手机号/昵称" style="width: 200px;" clearable @keydown.enter="load(1)" />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" size="small" @click="load(1)">搜索</n-button>
          <n-button size="small" style="margin-left: 8px;" @click="searchQuery='';load(1)">重置</n-button>
        </n-form-item>
      </n-form>
    </div>

    <template v-if="!loading">
      <div class="table-wrapper fade-in">
        <table>
          <thead>
            <tr>
              <th>序号</th><th>手机号</th><th>昵称</th><th>角色</th><th>状态</th><th>注册时间</th><th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(u, index) in users" :key="u.id">
              <td style="color: var(--color-text-muted); font-weight: 500;">{{ (page - 1) * pageSize + index + 1 }}</td>
              <td style="font-family: monospace; color: var(--color-text-secondary);">{{ u.phone }}</td>
              <td style="font-weight: 500;">{{ u.nickname }}</td>
              <td><span :class="['tag', `tag-${roleColors[u.role] || 'default'}`]">{{ u.role }}</span></td>
              <td><span :class="['tag', `tag-${statusColors[u.status] || 'default'}`]">{{ u.status }}</span></td>
              <td style="color: var(--color-text-secondary);">{{ new Date(u.created_at).toLocaleDateString() }}</td>
              <td>
                <n-button size="small" :type="u.status === 'active' ? 'default' : 'success'" style="margin-right: 6px; font-size: 12px; padding: 4px 10px;" @click="handleToggleStatus(u)">
                  {{ u.status === 'active' ? '冻结' : '解冻' }}
                </n-button>
                <n-popconfirm @positive-click="handleDelete(u)">
                  <template #trigger>
                    <n-button size="small" type="error" strong secondary style="font-size: 12px; padding: 4px 10px;">删除</n-button>
                  </template>
                  确认删除用户 {{ u.phone }}？此操作不可恢复。
                </n-popconfirm>
              </td>
            </tr>
            <tr v-if="!users.length">
              <td colspan="7" style="text-align: center; color: var(--color-text-muted); padding: 40px;">暂无用户数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
    <n-spin v-else :show="true" />

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
