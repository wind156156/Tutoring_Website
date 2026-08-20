import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user.store'

const routes: RouteRecordRaw[] = [
  { path: '/', component: () => import('@/views/HomeView.vue') },
  { path: '/login', component: () => import('@/views/LoginView.vue') },
  { path: '/register', component: () => import('@/views/RegisterView.vue') },

  // 家长
  {
    path: '/parent',
    component: () => import('@/views/parent/Layout.vue'),
    meta: { requiresAuth: true, roles: ['parent'] },
    children: [
      { path: '', redirect: '/parent/students' },
      { path: 'students', component: () => import('@/views/parent/StudentList.vue') },
      { path: 'student-assignments', component: () => import('@/views/parent/StudentAssignments.vue') },
      { path: 'students/:student_id/assignments/:id', component: () => import('@/views/parent/StudentAssignmentDetail.vue') },
      { path: 'teachers', component: () => import('@/views/parent/TeacherSearch.vue') },
      { path: 'teachers/:id', component: () => import('@/views/parent/TeacherDetail.vue') },
      { path: 'bindings', component: () => import('@/views/parent/BindingList.vue') },
      { path: 'favorites', component: () => import('@/views/parent/Favorites.vue') },
    ],
  },

  // 老师
  {
    path: '/teacher',
    component: () => import('@/views/teacher/Layout.vue'),
    meta: { requiresAuth: true, roles: ['teacher'] },
    children: [
      { path: '', redirect: '/teacher/profile' },
      { path: 'profile', component: () => import('@/views/teacher/MyProfile.vue') },
      { path: 'bindings', component: () => import('@/views/teacher/Bindings.vue') },
      { path: 'students', component: () => import('@/views/teacher/MyStudents.vue') },
      { path: 'assignments', component: () => import('@/views/teacher/Assignments.vue') },
      { path: 'assignments/new', component: () => import('@/views/teacher/AssignmentEditor.vue') },
      { path: 'assignments/:id', component: () => import('@/views/teacher/AssignmentDetail.vue') },
      { path: 'platform-teachers', component: () => import('@/views/teacher/PlatformTeachers.vue') },
      { path: 'platform-teachers/:id', component: () => import('@/views/teacher/TeacherDetail.vue') },
    ],
  },

  // 学生
  {
    path: '/student',
    component: () => import('@/views/student/Layout.vue'),
    meta: { requiresAuth: true, roles: ['student'] },
    children: [
      { path: '', redirect: '/student/assignments' },
      { path: 'assignments', component: () => import('@/views/student/MyAssignments.vue') },
      { path: 'assignments/:id', component: () => import('@/views/student/AssignmentDetail.vue') },
      { path: 'grades', component: () => import('@/views/student/GradeHistory.vue') },
      { path: 'teachers', component: () => import('@/views/student/MyTeachers.vue') },
      { path: 'teachers/:id', component: () => import('@/views/student/TeacherDetail.vue') },
    ],
  },

  // 管理员
  {
    path: '/admin',
    component: () => import('@/views/admin/Layout.vue'),
    meta: { requiresAuth: true, roles: ['admin'] },
    children: [
      { path: '', redirect: '/admin/users' },
      { path: 'users', component: () => import('@/views/admin/UserManage.vue') },
      { path: 'teachers', component: () => import('@/views/admin/TeacherAudit.vue') },
      { path: 'announcements', component: () => import('@/views/admin/AnnouncementManage.vue') },
      { path: 'stats', component: () => import('@/views/admin/StatsView.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    return '/login'
  }

  const allowedRoles = to.meta.roles as string[] | undefined
  if (allowedRoles && userStore.user?.role && !allowedRoles.includes(userStore.user.role)) {
    const roleHome: Record<string, string> = {
      parent: '/parent',
      teacher: '/teacher',
      student: '/student',
      admin: '/admin',
    }
    return roleHome[userStore.user.role] || '/'
  }
})

export default router
