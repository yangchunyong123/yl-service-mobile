# 03. 后端（Django + DRF）

## 3.1 技术栈概览

- Web 框架：Django（项目包： [after_sales_backend_project](file:///workspace/after-sales-backend/after_sales_backend_project)）
- API 框架：Django REST Framework
- JWT：djangorestframework-simplejwt（后端登录接口自行签发 refresh/access）
- 跨域：django-cors-headers
- DB：
  - MySQL：售后业务库（default）
  - SQLServer：OA/组织人员信息库（用于注册校验）
  - 额外 MySQL：`syncdb`（代码内配置但本项目未见对应业务模块）

## 3.2 启动入口与路由入口

- Django CLI： [manage.py](file:///workspace/after-sales-backend/manage.py)
- 顶层路由： [urls.py](file:///workspace/after-sales-backend/after_sales_backend_project/urls.py)
  - `/api/` -> `sales.urls`
  - `/admin/` -> Django Admin
  - `/media/` -> 资源访问
- App 路由： [apps/sales/urls.py](file:///workspace/after-sales-backend/apps/sales/urls.py)

## 3.3 核心配置（settings）

配置文件： [settings.py](file:///workspace/after-sales-backend/after_sales_backend_project/settings.py)

重点项：

- `INSTALLED_APPS`：启用 `corsheaders`、`rest_framework`、`rest_framework_simplejwt.token_blacklist`、`sales`
- `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES`：使用自定义 `sales.authentication.AfterSalesJWTAuthentication`
- `SIMPLE_JWT`：`Bearer` 头；access/refresh 生命周期；rotate + blacklist
- `DATABASES`：default(MySQL) + `sqlserver_oa_ecology9`(SQLServer) + `DataBase`(MySQL)
- `CORS_ALLOWED_ORIGINS`：允许前端开发地址（5173）
- 外部依赖配置：`TRACE_*`（溯源系统）与 `WECOM_*`（企业微信）

建议：将敏感信息（如密钥、外部系统凭证）完全迁移到环境变量/密钥管理，不要在仓库中硬编码。

## 3.4 认证与用户对象

### 3.4.1 自定义 JWT 认证

实现： [authentication.py](file:///workspace/after-sales-backend/apps/sales/authentication.py)

- 只接受 `Authorization: Bearer <access>`（拒绝 refresh）
- 通过 SimpleJWT 的 `TokenBackend` 解码并验签
- 从 payload 取 `user_id` 并查 `After_sales_index_login`
- 返回 `(user, validated_token)` 给 DRF

### 3.4.2 用户模型

实现： [models.py](file:///workspace/after-sales-backend/apps/sales/models.py)

- `After_sales_index_login`
  - `managed = False`：映射既有表 `after_sales_index_login`
  - 通过 `is_authenticated` property 兼容 DRF 需要的认证属性

## 3.5 业务 App：sales

目录： [apps/sales](file:///workspace/after-sales-backend/apps/sales)

### 3.5.1 路由与接口入口

见： [apps/sales/urls.py](file:///workspace/after-sales-backend/apps/sales/urls.py)

- `POST /api/token/`：登录签发 JWT
- `POST /api/token/refresh/`：刷新（SimpleJWT 内置视图）
- `GET /api/profile/`：获取当前用户
- `POST /api/register/`：注册（对接 OA SQLServer 获取员工信息）
- `POST /api/SelYgbhInfo/`：根据工号查姓名
- `POST /api/change-password/`：改密
- `GET/POST /api/complaints/`：客诉列表/创建
- `GET/PATCH/PUT /api/complaints/<id>/`：客诉详情/更新
- `GET /api/routing-sheet/`：外部溯源查询代理
- `GET /api/wecom-js-config/`：企业微信 JS-SDK 签名参数

### 3.5.2 序列化器（输入输出契约）

实现： [serializers.py](file:///workspace/after-sales-backend/apps/sales/serializers.py)

- `TokenLoginSerializer`：`username/password`
- `RegisterSerializer`：`username/password/phone` + `ygcode|employee_id` + `selectedOption`
- `UserProfileSerializer`：对外返回用户基础字段
- `Complaint*Serializer`：客诉创建/列表/详情/更新字段集合

### 3.5.3 视图（核心业务逻辑）

实现： [views.py](file:///workspace/after-sales-backend/apps/sales/views.py)

- `TokenLoginView.post`：账号密码验证并签发 JWT（兼容历史明文密码：明文匹配后自动重新哈希）
- `RegisterView.post`：注册并查询 OA（SQLServer）写入用户表
- `SelYgbhInfo.post`：根据工号查姓名
- `ProfileView.get`：返回当前用户信息
- `ChangePasswordView.post`：校验旧密码并更新（兼容明文/哈希）
- `ComplaintCreateView.get/post`：客诉列表与创建
- `ComplaintDetailView.get/patch/put`：客诉详情与更新
- `RoutingSheetQueryView.get`：溯源查询代理（带 refresh_token 缓存、失败回退登录、响应字段归一化）
- `WeComJSConfigView.get`：企业微信 `wx.config` 所需参数（`access_token/jsapi_ticket` 缓存）

## 3.6 运维/管理脚本

### 3.6.1 明文密码迁移为哈希

命令： [hash_login_passwords.py](file:///workspace/after-sales-backend/apps/sales/management/commands/hash_login_passwords.py)

运行方式（示例）：

```bash
python manage.py hash_login_passwords --dry-run
python manage.py hash_login_passwords --limit 100
```

### 3.6.2 token_query_client.py（独立客户端脚本）

文件： [token_query_client.py](file:///workspace/after-sales-backend/token_query_client.py)

- 作用：调用外部溯源接口并将结果写入某个 `traceability` 相关表
- 现状：本仓库中未包含 `apps/traceability` 模块，因此该脚本在当前仓库内无法直接运行（需要补齐对应 app 或迁移到正确项目）

