// 防抖函数，用于限制函数执行频率
// fn: 要执行的函数
// delay: 延迟时间（毫秒）
// 返回防抖后的函数
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

// 节流函数，用于限制函数执行频率
// fn: 要执行的函数
// interval: 间隔时间（毫秒）
// 返回节流后的函数
export function throttle(fn, interval = 300) {
  let lastTime = 0
  return function (...args) {
    const now = Date.now()
    if (now - lastTime >= interval) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

// 深拷贝函数
// obj: 要拷贝的对象
// 返回拷贝后的新对象
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  if (obj instanceof Date) {
    return new Date(obj.getTime())
  }
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item))
  }
  if (obj instanceof Object) {
    const cloned = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key])
      }
    }
    return cloned
  }
  return obj
}

// 格式化日期
// date: 日期对象或时间戳
// format: 格式字符串，如 'YYYY-MM-DD HH:mm:ss'
// 返回格式化后的日期字符串
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

// 本地存储封装，支持过期时间
export const storage = {
  // 设置存储项
  // key: 键名
  // value: 值
  // expire: 过期时间（毫秒）
  set(key, value, expire) {
    const data = {
      value,
      expire: expire ? Date.now() + expire : null
    }
    localStorage.setItem(key, JSON.stringify(data))
  },
  
  // 获取存储项
  // key: 键名
  // 返回值或null
  get(key) {
    const item = localStorage.getItem(key)
    if (!item) return null
    
    try {
      const data = JSON.parse(item)
      if (data.expire && Date.now() > data.expire) {
        localStorage.removeItem(key)
        return null
      }
      return data.value
    } catch {
      return null
    }
  },
  
  // 移除存储项
  remove(key) {
    localStorage.removeItem(key)
  },
  
  // 清空所有存储项
  clear() {
    localStorage.clear()
  }
}

// API 请求缓存管理
class ApiCache {
  constructor() {
    this.cache = new Map()
    this.defaultTTL = 5 * 60 * 1000 // 默认缓存5分钟
  }

  // 生成缓存key
  generateKey(url, params) {
    const paramsStr = params ? JSON.stringify(params) : ''
    return `${url}?${paramsStr}`
  }

  // 设置缓存
  set(key, data, ttl = this.defaultTTL) {
    this.cache.set(key, {
      data,
      expire: Date.now() + ttl,
      timestamp: Date.now()
    })
  }

  // 获取缓存
  get(key) {
    const cached = this.cache.get(key)
    if (!cached) return null
    
    // 检查是否过期
    if (Date.now() > cached.expire) {
      this.cache.delete(key)
      return null
    }
    
    return cached.data
  }

  // 删除缓存
  delete(key) {
    this.cache.delete(key)
  }

  // 清空缓存
  clear() {
    this.cache.clear()
  }

  // 清除过期的缓存
  clearExpired() {
    const now = Date.now()
    for (const [key, value] of this.cache.entries()) {
      if (now > value.expire) {
        this.cache.delete(key)
      }
    }
  }
}

// 创建全局缓存实例
export const apiCache = new ApiCache()

// 带缓存的请求封装
// requestFn: 请求函数
// cacheKey: 缓存key
// options: { ttl: 缓存时间(毫秒), forceRefresh: 是否强制刷新 }
export async function cachedRequest(requestFn, cacheKey, options = {}) {
  const { ttl = 5 * 60 * 1000, forceRefresh = false } = options
  
  // 如果不强制刷新，先尝试从缓存获取
  if (!forceRefresh) {
    const cached = apiCache.get(cacheKey)
    if (cached) {
      return cached
    }
  }
  
  // 执行请求
  const result = await requestFn()
  
  // 存入缓存
  apiCache.set(cacheKey, result, ttl)
  
  return result
}

// 清除指定 URL 的缓存
export function clearApiCache(urlPattern) {
  for (const [key] of apiCache.cache.entries()) {
    if (key.includes(urlPattern)) {
      apiCache.delete(key)
    }
  }
}
