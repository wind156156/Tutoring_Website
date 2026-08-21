<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NModal, NInput, NForm, NFormItem, NSpace, NRadioGroup, NRadio, NSelect } from 'naive-ui'
import { getStudents, createStudent, updateStudent, deleteStudent } from '@/api/parents'
import { getSubjects } from '@/api/common'

const message = { success: (m) => window.alert(m), error: (m) => window.alert(m) }
const students = ref<any[]>([])
const showModal = ref(false)
const editingId = ref<number | null>(null)
const form = ref({ real_name: '', gender: '' as string | null, birth_year: null as number | null, grade: '', school: '', subjects: [] as string[], phone: '', password: '123456' })
const loading = ref(false)

const subjectOptions = ref<{ label: string; value: string }[]>([])

async function loadSubjects() {
  try {
    const list = await getSubjects()
    subjectOptions.value = list.map(s => ({ label: s, value: s }))
  } catch {
    subjectOptions.value = []
  }
}

async function load() {
  students.value = await getStudents()
}

function openCreate() {
  editingId.value = null
  form.value = { real_name: '', gender: null, birth_year: null, grade: '', school: '', subjects: [], phone: '', password: '123456' }
  showModal.value = true
}

function openEdit(s: any) {
  editingId.value = s.id
  form.value = { ...s, subjects: s.subjects || [], phone: '', password: '' }
  showModal.value = true
}

async function handleSubmit() {
  loading.value = true
  try {
    if (editingId.value) {
      await updateStudent(editingId.value, {
        real_name: form.value.real_name,
        grade: form.value.grade,
        school: form.value.school,
        subjects: form.value.subjects || [],
      })
      message.success('更新成功')
    } else {
      if (!form.value.phone) { message.error('请填写学生手机号'); return }
      await createStudent({
        phone: form.value.phone,
        password: form.value.password,
        real_name: form.value.real_name,
        gender: form.value.gender || null,
        birth_year: form.value.birth_year,
        grade: form.value.grade,
        school: form.value.school,
        subjects: form.value.subjects || [],
      })
      message.success('学生添加成功')
    }
    showModal.value = false
    load()
  } catch (e: any) {
    message.error(e?.message || '操作失败')
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteStudent(id)
    message.success('删除成功')
    load()
  } catch (e: any) {
    message.error(e?.message || '删除失败')
  }
}

onMounted(async () => {
  await Promise.all([load(), loadSubjects()])
})
</script>

<template>
  <div>
    <div class="toolbar">
      <h2 class="toolbar-title">学生管理</h2>
      <n-button type="primary" size="small" @click="openCreate">+ 添加学生</n-button>
    </div>

    <div class="table-wrapper fade-in">
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
              <n-button text type="primary" size="small" @click="openEdit(s)" style="margin-right:4px;">编辑</n-button>
              <n-button text type="error" size="small" @click="handleDelete(s.id)">删除</n-button>
            </td>
          </tr>
          <tr v-if="!students.length">
            <td colspan="6" style="text-align: center; color: var(--color-text-muted); padding: 40px;">暂无学生，点击上方按钮添加</td>
          </tr>
        </tbody>
      </table>
    </div>

    <n-modal v-model:show="showModal" preset="card" title="学生信息" style="width: 500px;">
      <n-form :model="form" label-placement="left" label-width="80">
        <n-form-item label="手机号" v-if="!editingId">
          <n-input v-model:value="form.phone" placeholder="学生登录手机号" />
        </n-form-item>
        <n-form-item label="密码" v-if="!editingId">
          <n-input v-model:value="form.password" placeholder="默认 123456" />
        </n-form-item>
        <n-form-item label="姓名">
          <n-input v-model:value="form.real_name" placeholder="学生姓名" />
        </n-form-item>
        <n-form-item label="性别">
          <n-radio-group v-model:value="form.gender">
            <n-radio value="male">男</n-radio>
            <n-radio value="female">女</n-radio>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="年级">
          <n-input v-model:value="form.grade" placeholder="如：初二" />
        </n-form-item>
        <n-form-item label="学校">
          <n-input v-model:value="form.school" placeholder="学校名称" />
        </n-form-item>
        <n-form-item label="薄弱科目">
          <n-select v-model:value="form.subjects" multiple filterable
            :options="subjectOptions.map(s => ({ label: s, value: s }))"
            placeholder="选择科目" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showModal = false">取消</n-button>
          <n-button type="primary" :loading="loading" @click="handleSubmit">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>
