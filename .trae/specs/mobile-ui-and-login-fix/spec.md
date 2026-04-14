# Mobile UI & Login Field Spec

## Why
1. 在移动端企业微信等浏览器中，点击输入框时页面会自动放大，影响用户体验，需要通过禁用页面缩放来解决。
2. 登录页面的输入框提示是“手机号”，但后端实际校验时使用的是 `username` 字段，且数据库查询可能没有适配只用手机号登录的情况。需要将登录逻辑统一为使用 `phone` 字段进行验证，保证前后端语义与实际校验逻辑一致。

## What Changes
- 修改前端 `index.html` 的 `meta name="viewport"` 标签，添加 `user-scalable=no, maximum-scale=1.0, minimum-scale=1.0` 属性。
- 修改前端 `Login.vue`，将表单绑定的 `username` 变量及接口参数名修改为 `phone`。
- 修改后端 `TokenLoginSerializer`，将 `username` 字段替换为 `phone`。
- 修改后端 `TokenLoginView`，将接收和查询的条件由 `username=username` 改为 `phone=phone`，并生成对应包含 `phone` 信息的 JWT token。

## Impact
- Affected specs: 移动端页面缩放体验、用户登录认证流程
- Affected code:
  - `index.html`
  - `src/views/Login.vue`
  - `after-sales-backend/apps/sales/serializers.py`
  - `after-sales-backend/apps/sales/views.py`

## MODIFIED Requirements
### Requirement: 移动端页面防缩放
修改全局 viewport 设置，强制页面在移动端不可缩放，解决输入框聚焦时的放大问题。

### Requirement: 手机号登录验证
登录接口及前端表单的账号字段，由原来的 `username` 统一修改为 `phone`。用户输入手机号即可登录，后端使用 `phone` 字段去数据库匹配用户。
