<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NButton, NInput, NForm, NFormItem, NSpace, NAlert, NTag, NRadioGroup, NRadio } from 'naive-ui'
import { useRouter } from 'vue-router'
import { getMyProfile, updateTeacherProfile } from '@/api/teachers'
import { uploadFile } from '@/api/assignments'

const router = useRouter()
const message = { success: (m: string) => window.alert(m), error: (m: string) => window.alert(m) }
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const hasProfile = ref(false)
const reviewStatus = ref('')
const uploadError = ref('')

const form = ref({
  real_name: '',
  gender: '' as string | null,
  birth_year: null as number | null,
  education: '',
  title: '',
  subject_tags: [] as string[],
  experience_years: 0,
  hourly_rate: 0,
  city: '',
  district: '',
  qualification_url: '',
  bio: '',
})

const subjectOptions = ['语文', '数学', '英语', '物理', '化学', '生物', '政治', '历史', '地理', '科学', '编程', '美术', '音乐', '体育']

async function loadProfile() {
  try {
    const data: any = await getMyProfile()
    if (data && data.real_name) {
      Object.assign(form.value, data)
      form.value.subject_tags = data.subject_tags || []
      hasProfile.value = true
      reviewStatus.value = data.review_status || 'pending'
    } else {
      hasProfile.value = false
    }
  } catch {
    hasProfile.value = false
  }
}

async function onFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploadError.value = ''
  uploading.value = true
  try {
    const res = await uploadFile(file)
    form.value.qualification_url = res.url
    message.success('证书上传成功')
  } catch (err: any) {
    uploadError.value = err?.message || '上传失败'
    message.error(uploadError.value)
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function handleSubmit() {
  if (!form.value.real_name) { message.error('请填写真实姓名'); return }
  if (!form.value.subject_tags.length) { message.error('请选择授课科目'); return }
  if (!form.value.hourly_rate) { message.error('请填写时薪'); return }
  saving.value = true
  try {
    await updateTeacherProfile(form.value)
    message.success('资料已保存，请等待管理员审核')
    hasProfile.value = true
    reviewStatus.value = 'pending'
  } catch (e: any) {
    message.error(e?.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <div>
    <h2 class="page-title">完善个人资料</h2>

    <n-alert v-if="reviewStatus === 'approved'" type="success" :show-icon="false" style="margin-bottom: 20px; border-radius: var(--radius-md);">
      资料已通过审核 <n-tag type="success" size="small" style="margin-left: 8px;">审核通过</n-tag>
    </n-alert>
    <n-alert v-else-if="reviewStatus === 'pending'" type="warning" :show-icon="false" style="margin-bottom: 20px; border-radius: var(--radius-md);">
      资料已提交，正在等待管理员审核 <n-tag type="warning" size="small" style="margin-left: 8px;">审核中</n-tag>
      如需修改请继续编辑，提交后将重新进入审核
    </n-alert>
    <n-alert v-else-if="reviewStatus === 'rejected'" type="error" :show-icon="false" style="margin-bottom: 20px; border-radius: var(--radius-md);">
      资料审核未通过，请修改后重新提交
    </n-alert>
    <n-alert v-else type="info" :show-icon="false" style="margin-bottom: 20px; border-radius: var(--radius-md);">
      请完善以下资料，提交后需管理员审核才能被家长看到
    </n-alert>

    <div class="section-card" style="max-width: 640px;">
      <n-form :model="form" label-placement="left" label-width="90">
        <n-form-item label="真实姓名">
          <n-input v-model:value="form.real_name" placeholder="请输入真实姓名" />
        </n-form-item>
        <n-form-item label="性别">
          <n-radio-group v-model:value="form.gender">
            <n-radio value="male">男</n-radio>
            <n-radio value="female">女</n-radio>
          </n-radio-group>
        </n-form-item>
        <n-form-item label="学历">
          <n-input v-model:value="form.education" placeholder="如：本科、硕士" />
        </n-form-item>
        <n-form-item label="职称/资质">
          <n-input v-model:value="form.title" placeholder="如：高级教师" />
        </n-form-item>
        <n-form-item label="授课科目">
          <n-select v-model:value="form.subject_tags" multiple filterable
            :options="subjectOptions.map(s => ({ label: s, value: s }))"
            placeholder="选择授课科目" />
        </n-form-item>
        <n-form-item label="教龄">
          <n-input-number v-model:value="form.experience_years" :min="0" />
        </n-form-item>
        <n-form-item label="时薪(元)">
          <n-input-number v-model:value="form.hourly_rate" :min="0" />
        </n-form-item>
        <n-form-item label="城市">
          <n-input v-model:value="form.city" placeholder="如：北京" />
        </n-form-item>
        <n-form-item label="区域">
          <n-input v-model:value="form.district" placeholder="如：海淀区" />
        </n-form-item>
        <n-form-item label="资质证书">
          <div>
            <label :style="{ display: 'inline-block', cursor: uploading ? 'not-allowed' : 'pointer', padding: '7px 16px', border: '1.5px solid var(--color-success)', borderRadius: 'var(--radius-sm)', color: 'var(--color-success)', fontSize: '13px', fontWeight: 500 }">
              <input type="file" accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.zip,.rar" style="display: none" @change="onFileSelect" :disabled="uploading" />
              {{ uploading ? '上传中...' : (form.qualification_url ? '重新上传' : '+ 上传证书') }}
            </label>
            <span v-if="form.qualification_url" style="margin-left: 8px; color: var(--color-success); font-size: 13px;">✓ 已上传</span>
            <span v-if="uploadError" style="margin-left: 8px; color: var(--color-danger); font-size: 13px;">{{ uploadError }}</span>
          </div>
        </n-form-item>
        <n-form-item label="个人简介">
          <n-input v-model:value="form.bio" type="textarea" :rows="4" placeholder="介绍一下自己" />
        </n-form-item>
        <n-form-item>
          <n-button type="primary" :loading="saving" @click="handleSubmit">提交资料</n-button>
        </n-form-item>
      </n-form>
    </div>
  </div>
</template>
