# 04. API 参考（/api）

后端 API 路由入口： [apps/sales/urls.py](file:///workspace/after-sales-backend/apps/sales/urls.py)

## 4.1 通用约定

- Base URL（前端默认）：`http://127.0.0.1:8000/api`（见 [api/index.js](file:///workspace/src/api/index.js)）
- 鉴权方式：`Authorization: Bearer <access_token>`
- 返回风格：
  - 部分接口返回 DRF 原生结构（如 profile/complaints list 直接是对象/数组）
  - 部分接口返回业务包装 `{ret: boolean, msg: string, ...}`

## 4.2 认证相关

### POST /token/

登录并获取 JWT。

- Request Body

```json
{ "username": "string", "password": "string" }
```

- Response（示例）

```json
{
  "refresh": "jwt-refresh",
  "access": "jwt-access",
  "user": {
    "id": 1,
    "username": "xxx",
    "phone": "xxx",
    "lastname": "xxx",
    "departmentname": "xxx",
    "subcompanyname": "xxx",
    "ygcode": "0000000000"
  }
}
```

对应实现：`TokenLoginView.post`（见 [views.py](file:///workspace/after-sales-backend/apps/sales/views.py)）

### POST /token/refresh/

刷新 access token（由 SimpleJWT 提供）。

- Request Body

```json
{ "refresh": "jwt-refresh" }
```

- Response
  - 默认返回 `{"access": "..."}`
  - 若启用了 refresh rotate，可能同时返回新的 `refresh`

前端 refresh 逻辑见： [api/index.js:L75-L129](file:///workspace/src/api/index.js#L75-L129)

## 4.3 用户相关

### GET /profile/

获取当前登录用户信息。

- Response（字段见序列化器）
  - `UserProfileSerializer`： [serializers.py:L28-L41](file:///workspace/after-sales-backend/apps/sales/serializers.py#L28-L41)

### POST /register/

注册用户，并对接 OA SQLServer 查询员工信息补全组织字段。

- Request Body（常用）

```json
{
  "username": "string",
  "password": "string",
  "phone": "string",
  "ygcode": "string",
  "selectedOption": "string"
}
```

- Response（示例）

```json
{ "ret": true, "msg": "注册成功请登录！" }
```

### POST /SelYgbhInfo/

根据工号查询 OA 中的姓名（用于注册页联动）。

- Request Body

```json
{ "ygcode": "string" }
```

- Response（示例）

```json
{ "ret": true, "row": [{ "value": "张三" }] }
```

### POST /change-password/

修改当前用户密码。

- Request Body

```json
{ "old_password": "string", "new_password": "string" }
```

- Response（示例）

```json
{ "ret": true, "msg": "密码修改成功" }
```

## 4.4 客诉相关

### GET /complaints/

获取客诉列表（按创建时间倒序）。

- Response：数组，每条字段见 `ComplaintListSerializer`
  - [serializers.py:L62-L80](file:///workspace/after-sales-backend/apps/sales/serializers.py#L62-L80)

### POST /complaints/

创建客诉。

- Request Body（主要字段）

```json
{
  "handler": "string",
  "serial_no": "string",
  "project_name": "string",
  "location": "string",
  "is_warranty": "是|否",
  "issue_type": "string",
  "inverter_info": "string",
  "process_type": "string",
  "replace_serial_no": "string",
  "repair_details": { "positive": "无|更换", "middle": "无|更换", "negative": "无|更换" },
  "repairer": "string"
}
```

- Response（示例）

```json
{ "ret": true, "msg": "提交成功", "id": 123 }
```

前端提交映射： [ComplaintEntry.vue](file:///workspace/src/views/ComplaintEntry.vue)

### GET /complaints/<id>/

- Response：对象，字段见 `ComplaintDetailSerializer`
  - [serializers.py:L82-L103](file:///workspace/after-sales-backend/apps/sales/serializers.py#L82-L103)

### PATCH /complaints/<id>/ 或 PUT /complaints/<id>/

- Request Body：可更新字段见 `ComplaintUpdateSerializer`
  - [serializers.py:L105-L122](file:///workspace/after-sales-backend/apps/sales/serializers.py#L105-L122)
- Response（示例）

```json
{ "ret": true, "msg": "更新成功" }
```

## 4.5 溯源与企业微信

### GET /routing-sheet/

通过外部溯源系统查询组件信息并做字段归一化。

- Query Params
  - `serial_no`：组件序列号（也兼容 `serial`）
- Response（示例）

```json
{
  "ret": true,
  "component_details": {
    "serial_no": "string",
    "test_date": "string",
    "power_grade": "string",
    "current_grade": "string",
    "el_grade": "string",
    "final_grade": "string",
    "pmax": "string",
    "isc": "string",
    "voc": "string",
    "ipm": "string",
    "vpm": "string",
    "ff": "string",
    "battery_factory": "string",
    "sales_contract_no": "string",
    "customer": "string"
  }
}
```

### GET /wecom-js-config/

生成企业微信 `wx.config` 所需签名参数。

- Query Params
  - `url`：当前页面 URL（后端会自动去掉 `#` 后内容）
- Response（示例）

```json
{
  "ret": true,
  "config": {
    "appId": "string",
    "timestamp": 0,
    "nonceStr": "string",
    "signature": "string"
  }
}
```

