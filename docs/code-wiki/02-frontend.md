# 02. 前端（Vite + Vue 3 + Vant）

## 2.1 技术栈与依赖

- 构建：Vite（见 [package.json](file:///workspace/package.json)）
- 框架：Vue 3
- UI：Vant 4（组件与 API 自动导入，见 [vite.config.js](file:///workspace/vite.config.js)）
- 路由：Vue Router
- 状态：Pinia
- 网络：Axios
- 企业微信：weixin-js-sdk（扫码）

## 2.2 目录结构

```text
src/
  api/          Axios 封装与业务 API
  router/       路由表与全局守卫
  store/        Pinia 实例
  utils/        wecom JS-SDK 封装
  views/        页面组件
  App.vue       根组件（router-view）
  main.js       应用入口
```

## 2.3 启动入口与应用挂载

- HTML 入口： [index.html](file:///workspace/index.html)
- 应用入口： [main.js](file:///workspace/src/main.js)
  - 关键逻辑：`createApp(App)` -> `app.use(router)` -> `app.use(store)` -> `mount('#app')`
- 根组件： [App.vue](file:///workspace/src/App.vue)

## 2.4 路由与鉴权策略

路由定义在 [router/index.js](file:///workspace/src/router/index.js)。

- **Layout 容器路由**：`/home`、`/orders`、`/profile` 作为子路由挂载在 [Layout.vue](file:///workspace/src/views/Layout.vue)
- **独立页面**：登录/注册、客诉创建、客诉详情、扫码查询等
- **全局守卫**：
  - 从 localStorage 读取 `token`
  - 解析 JWT payload 中的 `exp` 判断过期
  - 未登录或过期时跳转 `/login?redirect=...`

建议阅读：

- `getTokenExp` / `isTokenExpired` / `router.beforeEach`： [router/index.js:L72-L125](file:///workspace/src/router/index.js#L72-L125)

## 2.5 API 封装（Axios + Token 自动刷新）

API 封装集中在 [api/index.js](file:///workspace/src/api/index.js)，对外导出业务函数（`login/register/complaints/routing-sheet/wecom-js-config` 等）。

### 2.5.1 存储约定

- `token`：access token
- `refreshToken`：refresh token
- `userInfo`：用户信息 JSON

见： [api/index.js:L5-L48](file:///workspace/src/api/index.js#L5-L48)

### 2.5.2 鉴权头注入

- 请求拦截器自动追加 `Authorization: Bearer <token>`

见： [api/index.js:L57-L69](file:///workspace/src/api/index.js#L57-L69)

### 2.5.3 401 自动刷新与请求队列

关键点：

- 遇到 401 且未重试过：尝试调用 `/token/refresh/`
- 并发 401 时：用 `requests` 队列缓存待重放请求，refresh 成功后统一重放
- refresh 失败：清理本地登录态并跳转登录

见： [api/index.js:L71-L133](file:///workspace/src/api/index.js#L71-L133)

## 2.6 企业微信扫码

封装在 [utils/wecom.js](file:///workspace/src/utils/wecom.js)：

- `initWeComConfig(jsApiList)`：向后端请求签名参数并调用 `wx.config`
- `scanQRCode()`：调用 `wx.scanQRCode` 返回扫码结果

页面侧调用示例：

- 客诉录入页在 `onMounted` 初始化 JS-SDK，并在序列号字段右侧图标触发扫码（见 [ComplaintEntry.vue](file:///workspace/src/views/ComplaintEntry.vue)）

## 2.7 主要页面与职责

| 页面 | 路由 | 主要职责 |
|---|---|---|
| Login | `/login` | 登录、生成图形验证码、保存 token（见 [Login.vue](file:///workspace/src/views/Login.vue)） |
| Register | `/register` | 注册、工号联动查询姓名（见 [Register.vue](file:///workspace/src/views/Register.vue)） |
| Layout | `/` | Tabbar 布局容器（见 [Layout.vue](file:///workspace/src/views/Layout.vue)） |
| Home | `/home` | 首页入口（见 [Home.vue](file:///workspace/src/views/Home.vue)） |
| ComplaintList | `/orders` | 客诉列表（见 [ComplaintList.vue](file:///workspace/src/views/ComplaintList.vue)） |
| ComplaintEntry | `/complaint/new` | 新建客诉 + 扫码填充序列号（见 [ComplaintEntry.vue](file:///workspace/src/views/ComplaintEntry.vue)） |
| ComplaintDetail | `/complaint/detail/:id` | 客诉详情/更新（见 [ComplaintDetail.vue](file:///workspace/src/views/ComplaintDetail.vue)） |
| ScanQuery | `/scan-query` | 扫码/输入序列号调用溯源查询（见 [ScanQuery.vue](file:///workspace/src/views/ScanQuery.vue)） |
| UserProfile | `/profile` | 用户资料/登出/改密入口（见 [UserProfile.vue](file:///workspace/src/views/UserProfile.vue)） |

