# 07. 运行手册（本地开发 / 构建 / 排障）

## 7.1 前端（本地开发）

工作目录：仓库根目录。

```bash
npm install
npm run dev
```

- 默认开发端口：`5173`（Vite 默认）
- 页面路由：由前端接管（history 模式），后端仅提供 `/api/*`

构建与预览：

```bash
npm run build
npm run preview
```

## 7.2 后端（本地开发）

工作目录： [after-sales-backend](file:///workspace/after-sales-backend)

仓库未提供依赖清单文件，建议自行创建虚拟环境并安装依赖（按 05 文档中的最低依赖清单）。

启动（示例）：

```bash
python manage.py runserver 0.0.0.0:8000
```

后端地址：`http://127.0.0.1:8000/`

### 7.2.1 必要前置

- MySQL（default）与 SQLServer（OA）能连通；相关表已存在（模型为 `managed=False`）。
- 按需设置环境变量：
  - `TRACE_*`（溯源系统）
  - `WECOM_*`（企业微信）

### 7.2.2 CORS 对齐

后端允许的前端开发地址在 `CORS_ALLOWED_ORIGINS` 中配置（见 [settings.py](file:///workspace/after-sales-backend/after_sales_backend_project/settings.py)）。

如果前端使用非 5173 端口或不同域名，需要同步更新该白名单。

## 7.3 常见排障

### 7.3.1 前端请求 401，页面被跳转登录

排查点：

- access token 过期：前端路由守卫会主动清理并跳转（见 [router/index.js](file:///workspace/src/router/index.js)）
- refresh token 无效：Axios 401 自动 refresh 失败会清理登录态并跳转（见 [api/index.js](file:///workspace/src/api/index.js)）
- 后端认证头格式错误：后端只接受 `Bearer <token>`（见 [authentication.py](file:///workspace/after-sales-backend/apps/sales/authentication.py)）

### 7.3.2 注册失败，提示找不到员工信息

排查点：

- `ygcode` 是否满足 OA 工号规则（代码里会自动左补零到 10 位）
- SQLServer 连接配置是否正确，能否查询到 `HrmResource` 数据

实现位置：`RegisterView`（见 [views.py](file:///workspace/after-sales-backend/apps/sales/views.py)）

### 7.3.3 溯源查询超时或失败

排查点：

- `TRACE_LOGIN_URL/TRACE_REFRESH_URL/TRACE_QUERY_URL` 是否可达
- `TRACE_HTTP_TIMEOUT` 是否过小
- 外部系统返回结构字段不稳定：后端做了兼容提取与字段归一化（见 `RoutingSheetQueryView`）

### 7.3.4 企业微信扫码不可用

排查点：

- 是否在企业微信环境内打开（JS-SDK 限制）
- 后端 `WECOM_CORP_ID/WECOM_CORP_SECRET` 是否有效
- 前端初始化是否成功：`initWeComConfig(['scanQRCode'])`（见 [wecom.js](file:///workspace/src/utils/wecom.js)）

