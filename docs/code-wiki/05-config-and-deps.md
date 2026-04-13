# 05. 依赖与配置

## 5.1 前端依赖（Node）

见 [package.json](file:///workspace/package.json)。

**运行依赖**

- `vue` / `vue-router` / `pinia`
- `vant` / `@vant/area-data`
- `axios`
- `weixin-js-sdk`
- `unplugin-auto-import` / `unplugin-vue-components`

**构建依赖**

- `vite`
- `@vitejs/plugin-vue`

## 5.2 后端依赖（Python）

仓库中未提供 `requirements.txt/pyproject.toml`，需按代码显式依赖自行准备环境。最低依赖通常包括：

- `Django`
- `djangorestframework`
- `django-cors-headers`
- `djangorestframework-simplejwt`
- `PyMySQL`（见 [after_sales_backend_project/__init__.py](file:///workspace/after-sales-backend/after_sales_backend_project/__init__.py)）
- `requests`（用于外部溯源系统与企业微信接口调用，见 [views.py](file:///workspace/after-sales-backend/apps/sales/views.py)）
- SQLServer 后端驱动（取决于 DB Engine 配置）
  - settings 中使用 `ENGINE = 'mssql'`，通常需要 `mssql-django` 或其它 Django SQLServer backend
  - 若通过 ODBC：还需要系统安装 `ODBC Driver 17 for SQL Server`

建议在后端目录补齐依赖清单文件，并锁定版本以便可复现部署。

## 5.3 环境变量与配置项

后端集中在 [settings.py](file:///workspace/after-sales-backend/after_sales_backend_project/settings.py) 读取环境变量（未设置时使用默认值）。

### 5.3.1 溯源系统（TRACE_*）

用途：`/api/routing-sheet/` 调用外部系统查询组件信息。

- `TRACE_LOGIN_URL`：登录接口地址
- `TRACE_REFRESH_URL`：token 刷新地址
- `TRACE_QUERY_URL`：查询接口地址
- `TRACE_LOGIN_USERNAME` / `TRACE_LOGIN_PASSWORD`：外部系统凭证
- `TRACE_AUTH_SCHEME`：Authorization scheme（如 `JWTYF`）
- `TRACE_HTTP_TIMEOUT`：外部 HTTP 超时（秒）

### 5.3.2 企业微信（WECOM_*）

用途：`/api/wecom-js-config/` 获取企业微信 `access_token/jsapi_ticket` 并签名。

- `WECOM_CORP_ID`
- `WECOM_CORP_SECRET`

### 5.3.3 Django/DRF/JWT

用途：后端鉴权与跨域。

- `SECRET_KEY`：用于 Django 与 JWT 签名（SimpleJWT `SIGNING_KEY` 默认也取此值）
- `SIMPLE_JWT`：token 生命周期、rotate、blacklist 策略
- `CORS_ALLOWED_ORIGINS`：本地前端开发域名（默认 5173）

## 5.4 前后端接口对齐点

- 前端 baseURL：`/api`（见 [api/index.js](file:///workspace/src/api/index.js)）
- 后端路由前缀：`path('api/', include(...))`（见 [after_sales_backend_project/urls.py](file:///workspace/after-sales-backend/after_sales_backend_project/urls.py)）
- Token Header：前端固定 `Bearer`；后端认证也只接受 `Bearer`（见 [authentication.py](file:///workspace/after-sales-backend/apps/sales/authentication.py)）

## 5.5 配置安全建议（工程化）

- 将所有敏感信息（密钥、数据库密码、外部系统凭证、企业微信 secret）迁移到环境变量或密钥管理服务。
- 本地开发可用 `.env` 文件（仅在本机）并在版本控制中忽略，仓库仅保留 `.env.example`。

