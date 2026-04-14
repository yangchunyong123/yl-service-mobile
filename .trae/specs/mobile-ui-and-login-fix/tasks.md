# Tasks

- [x] Task 1: 修复移动端输入框聚焦放大问题
  - [x] SubTask 1.1: 在 `index.html` 中修改 `viewport` 的 meta 标签，增加 `user-scalable=no, maximum-scale=1.0, minimum-scale=1.0`。
- [x] Task 2: 改造前端登录页字段
  - [x] SubTask 2.1: 在 `src/views/Login.vue` 中，将变量 `username` 替换为 `phone`，并在调用 `login` API 时传递 `phone` 参数。
- [x] Task 3: 改造后端登录接口序列化器
  - [x] SubTask 3.1: 在 `after-sales-backend/apps/sales/serializers.py` 中，修改 `TokenLoginSerializer`，将 `username` 替换为 `phone`。
- [x] Task 4: 改造后端登录视图逻辑
  - [x] SubTask 4.1: 在 `after-sales-backend/apps/sales/views.py` 中，修改 `TokenLoginView`，接收 `phone`，并使用 `After_sales_index_login.objects.filter(phone=phone)` 查询用户，最后在 token payload 中存入 `phone`。

# Task Dependencies
- [Task 4] depends on [Task 3]
