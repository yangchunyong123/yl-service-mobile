# Code Wiki（YL Service Mobile / 售后管理系统）

本仓库包含两部分：

- **前端**：Vite + Vue 3 + Vant（移动端 H5），源码在 [src](file:///workspace/src)。
- **后端**：Django + Django REST Framework（API 服务），源码在 [after-sales-backend](file:///workspace/after-sales-backend)。

## 目录

- [01-architecture.md](file:///workspace/docs/code-wiki/01-architecture.md) 项目整体架构与数据流
- [02-frontend.md](file:///workspace/docs/code-wiki/02-frontend.md) 前端结构、关键模块与运行
- [03-backend.md](file:///workspace/docs/code-wiki/03-backend.md) 后端结构、关键模块与运行
- [04-api-reference.md](file:///workspace/docs/code-wiki/04-api-reference.md) HTTP API 清单与主要字段
- [05-config-and-deps.md](file:///workspace/docs/code-wiki/05-config-and-deps.md) 依赖、配置项与环境变量
- [06-database.md](file:///workspace/docs/code-wiki/06-database.md) 数据库与数据模型
- [07-runbook.md](file:///workspace/docs/code-wiki/07-runbook.md) 本地启动/构建/排障手册

## 快速认知

**前端入口**

- HTML： [index.html](file:///workspace/index.html)
- 应用入口： [main.js](file:///workspace/src/main.js)

**后端入口**

- Django 管理入口： [manage.py](file:///workspace/after-sales-backend/manage.py)
- 路由入口： [urls.py](file:///workspace/after-sales-backend/after_sales_backend_project/urls.py)

**核心链路（从用户视角）**

- 登录：前端 [api/index.js](file:///workspace/src/api/index.js) 调用 `POST /api/token/` 获取 JWT，并在 Axios 拦截器中自动携带 `Authorization: Bearer <token>`。
- 客诉：前端 `ComplaintEntry / List / Detail` 对应后端 `complaints` 接口与 `After_sales_Complaint` 表。
- 溯源查询：前端 `ScanQuery` 调 `GET /api/routing-sheet/`，后端再调用外部溯源系统（TRACE_* 配置）。
- 企业微信扫码：前端 [wecom.js](file:///workspace/src/utils/wecom.js) 初始化 JS-SDK，配置由后端 `GET /api/wecom-js-config/` 生成。

