import { createRouter, createWebHistory } from 'vue-router'
import { showToast } from 'vant'

// 路由配置
const routes = [
  {
    path: '/',
    redirect: '/home',
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('../views/ComplaintList.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/UserProfile.vue'),
        meta: { requiresAuth: true }
      }
    ]
  },
  {
    path: '/complaint/new',
    name: 'ComplaintEntry',
    component: () => import('../views/ComplaintEntry.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/complaint/detail/:id',
    name: 'ComplaintDetail',
    component: () => import('../views/ComplaintDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/scan-query',
    name: 'ScanQuery',
    component: () => import('../views/ScanQuery.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 从 JWT 中解析过期时间，token：JWT 字符串
const getTokenExp = token => {
  try {
    const payload = token.split('.')[1]
    if (!payload) {
      return null
    }
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/')
    const decoded = decodeURIComponent(
      atob(base64)
        .split('')
        .map(char => `%${`00${char.charCodeAt(0).toString(16)}`.slice(-2)}`)
        .join('')
    )
    const data = JSON.parse(decoded)
    return typeof data.exp === 'number' ? data.exp : null
  } catch (error) {
    return null
  }
}

// 判断 token 是否过期，token：JWT 字符串
const isTokenExpired = token => {
  const exp = getTokenExp(token)
  if (!exp) {
    return false
  }
  return Date.now() >= exp * 1000
}

// 全局路由守卫：校验登录态，to/from/next：路由钩子参数
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && token && isTokenExpired(token)) {
    showToast('请重新登录')
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userInfo')
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }
  if (to.meta.requiresAuth && !token) {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    localStorage.removeItem('userInfo')
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }
  if (to.path === '/login' && token) {
    next('/home')
    return
  }
  next()
})

export default router
