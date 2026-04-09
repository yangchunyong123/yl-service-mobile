import axios from 'axios'
import { showToast } from 'vant'
import router from '@/router'

// 本地存储键名配置
const ACCESS_TOKEN_KEY = 'token'
const REFRESH_TOKEN_KEY = 'refreshToken'
const USER_INFO_KEY = 'userInfo'

// 后端接口基础地址
const API_BASE_URL = 'http://127.0.0.1:8000/api'

// 业务接口请求实例
const service = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000
})

// 刷新令牌请求实例
const refreshService = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000
})

// 获取本地 access token
const getAccessToken = () => localStorage.getItem(ACCESS_TOKEN_KEY)
// 获取本地 refresh token
const getRefreshToken = () => localStorage.getItem(REFRESH_TOKEN_KEY)

// 保存登录态信息到本地，access/refresh/user：登录态数据
const setAuthData = ({ access, refresh, user }) => {
  if (access) {
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
  }
  if (refresh) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  }
  if (user) {
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(user))
  }
}

// 清空本地登录态信息
const clearAuthData = () => {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_INFO_KEY)
}

// 跳转登录并携带回跳地址
const redirectToLogin = () => {
  const currentPath = router.currentRoute?.value?.fullPath || '/'
  showToast('请重新登录')
  router.replace({ path: '/login', query: { redirect: currentPath } })
}

// 请求拦截：自动附加 Bearer token
service.interceptors.request.use(
  config => {
    const token = getAccessToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 刷新状态与请求队列
let isRefreshing = false
let requests = []

// 响应拦截：401 时尝试刷新 token
service.interceptors.response.use(
  response => {
    return response.data
  },
  async error => {
    const originalRequest = error.config || {}
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise(resolve => {
          requests.push(token => {
            originalRequest.headers['Authorization'] = `Bearer ${token}`
            resolve(service(originalRequest))
          })
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        clearAuthData()
        redirectToLogin()
        return Promise.reject(error)
      }
      try {
        const refreshRes = await refreshService.post('/token/refresh/', {
          refresh: refreshToken
        })
        const newAccessToken = refreshRes.data?.access
        const newRefreshToken = refreshRes.data?.refresh
        if (!newAccessToken) {
          clearAuthData()
          redirectToLogin()
          return Promise.reject(error)
        }
        setAuthData({ access: newAccessToken, refresh: newRefreshToken })

        requests.forEach(cb => cb(newAccessToken))
        requests = []

        originalRequest.headers = originalRequest.headers || {}
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`
        return service(originalRequest)
      } catch (refreshError) {
        requests.forEach(cb => cb(null))
        requests = []
        clearAuthData()
        redirectToLogin()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }
    showToast(error.message || 'Request Error')
    return Promise.reject(error)
  }
)

// 登录并保存 token 与用户信息，payload：登录参数
export const login = async payload => {
  const res = await service.post('/token/', payload)
  setAuthData({
    access: res.access,
    refresh: res.refresh,
    user: res.user
  })
  return res
}

// 注册账号，payload：注册参数
export const register = async payload => {
  const res = await service.post('/register/', payload)
  return res
}

// 根据员工编号获取姓名，employeeId：员工编号
export const getEmployeeName = async employeeId => {
  const res = await service.post('/SelYgbhInfo/', {
    ygcode: employeeId
  })
  return res
}

// 获取当前用户资料
export const getProfile = async () => {
  const res = await service.get('/profile/')
  localStorage.setItem(USER_INFO_KEY, JSON.stringify(res))
  return res
}

// 修改登录密码，payload：旧密码与新密码
export const changePassword = async payload => {
  const res = await service.post('/change-password/', payload)
  return res
}

// 新建客诉单，payload：客诉提交数据
export const createComplaint = async payload => {
  const res = await service.post('/complaints/', payload)
  return res
}

// 获取客诉列表
export const getComplaints = async () => {
  const res = await service.get('/complaints/')
  return res
}

// 获取客诉详情，id：客诉 ID
export const getComplaintDetail = async id => {
  const res = await service.get(`/complaints/${id}/`)
  return res
}

// 更新客诉信息，id：客诉 ID，payload：更新字段
export const updateComplaint = async (id, payload) => {
  const res = await service.patch(`/complaints/${id}/`, payload)
  return res
}

// 根据序列号查询流转单信息，serialNo：序列号
export const getRoutingSheet = async serialNo => {
  const normalizedSerialNo = String(serialNo || '')
    .replace(/\s+/g, '')
    .trim()
  const res = await service.get('/routing-sheet/', {
    params: {
      serial_no: normalizedSerialNo
    }
  })
  return res
}

// 退出登录
export const logout = () => {
  clearAuthData()
}

// 获取本地缓存的用户信息
export const getLocalUserInfo = () => {
  const raw = localStorage.getItem(USER_INFO_KEY)
  if (!raw) {
    return null
  }
  try {
    return JSON.parse(raw)
  } catch (e) {
    return null
  }
}

export default service
