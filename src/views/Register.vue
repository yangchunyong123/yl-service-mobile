<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { showToast } from "vant";
import { getEmployeeName, register } from "@/api";
import logoUrl from "@/assets/style/img/ylfwsylogo.png";

// 路由实例
const router = useRouter();
// 表单字段
const username = ref("");
const phone = ref("");
const password = ref("");
const employeeId = ref("");
const oaName = ref("");
// 密码显示与加载状态
const showPassword = ref(false);
const loading = ref(false);
const nameLoading = ref(false);

// 提交注册
const onSubmit = async () => {
  loading.value = true;
  try {
    const res = await register({
      username: username.value.trim(),
      password: password.value,
      phone: phone.value.trim(),
      employee_id: employeeId.value.trim(),
      oa_name: oaName.value.trim(),
    });
    if (res?.ret !== true) {
      showToast(res?.msg || "注册失败");
      return;
    }
    showToast("注册成功");
    router.push("/login");
  } catch (error) {
    const message = error?.response?.data?.msg || "注册失败";
    showToast(message);
  } finally {
    loading.value = false;
  }
};

// 员工编号失焦后查询 OA 姓名
const onEmployeeBlur = async () => {
  const value = employeeId.value.trim();
  if (!value) {
    oaName.value = "";
    return;
  }
  if (!/^\d{10}$/.test(value)) {
    oaName.value = "";
    return;
  }
  nameLoading.value = true;
  try {
    const res = await getEmployeeName(value);
    if (res?.ret === true) {
      oaName.value = res?.row[0]?.value || "";
      return;
    }
    showToast(res?.msg || "未找到员工");
    oaName.value = "";
  } catch (error) {
    const message = error?.response?.data?.msg || "未找到员工";
    showToast(message);
    oaName.value = "";
  } finally {
    nameLoading.value = false;
  }
};
</script>

<template>
  <div class="register-container">
    <div class="logo-area">
      <div class="logo-placeholder">
        <img :src="logoUrl" alt="logo" />
        <div class="sun-icon">☀️</div>
      </div>
      <h2 class="app-title">用户注册</h2>
    </div>

    <van-form @submit="onSubmit" class="register-form">
      <!-- 用户名 -->
      <div class="input-wrapper">
        <van-field
          v-model="username"
          name="username"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请输入用户名' }]"
          class="custom-field white-bg"
        >
          <template #left-icon>
            <van-icon name="user-o" class="field-icon" />
          </template>
        </van-field>
      </div>

      <!-- 手机号 -->
      <div class="input-wrapper">
        <van-field
          v-model="phone"
          name="phone"
          placeholder="手机号"
          :rules="[{ required: true, message: '请输入手机号' }]"
          class="custom-field blue-bg"
        >
          <template #left-icon>
            <van-icon name="phone-o" class="field-icon" />
          </template>
        </van-field>
      </div>

      <!-- 密码 -->
      <div class="input-wrapper">
        <van-field
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          name="password"
          placeholder="密码"
          :rules="[{ required: true, message: '请输入密码' }]"
          class="custom-field blue-bg"
        >
          <template #left-icon>
            <van-icon name="lock" class="field-icon" />
          </template>
          <template #right-icon>
            <van-icon
              :name="showPassword ? 'eye-o' : 'closed-eye'"
              class="field-icon cursor-pointer"
              @click="showPassword = !showPassword"
            />
          </template>
        </van-field>
      </div>

      <!-- 员工编号 -->
      <div class="input-wrapper">
        <van-field
          v-model="employeeId"
          name="employeeId"
          placeholder="请输入员工编号"
          :rules="[
            { required: true, message: '请输入员工编号' },
            { pattern: /^\d{10}$/, message: '员工编号必须为10位' },
          ]"
          :loading="nameLoading"
          @blur="onEmployeeBlur"
          class="custom-field white-bg"
        >
          <template #left-icon>
            <van-icon name="orders-o" class="field-icon" />
          </template>
        </van-field>
      </div>

      <!-- OA员工姓名 -->
      <div class="input-wrapper">
        <van-field
          v-model="oaName"
          name="oaName"
          placeholder="OA员工姓名"
          readonly
          class="custom-field grey-bg"
        >
        </van-field>
      </div>

      <div class="submit-btn-wrapper">
        <van-button
          :loading="loading"
          block
          type="primary"
          native-type="submit"
          color="#409eff"
        >
          注册
        </van-button>
      </div>

      <div class="login-link">
        <span @click="router.push('/login')">已有账号？去登陆</span>
      </div>
    </van-form>
  </div>
</template>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #fff;
  padding: 40px 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-area {
  text-align: center;
  margin-bottom: 40px;
  margin-top: 40px;
}

.logo-placeholder {
  font-size: 32px;
  font-weight: bold;
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.sun-icon {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 40px;
  color: #ff9900;
  z-index: -1;
  opacity: 0.5;
}

.app-title {
  font-size: 18px;
  color: #666;
  font-weight: normal;
  margin: 0;
}

.register-form {
  width: 100%;
}

.input-wrapper {
  margin-bottom: 20px;
}

.custom-field {
  border-radius: 8px;
  padding: 10px 16px;
  border: 1px solid #dcdfe6;
}

.blue-bg {
  background-color: #e8f0fe;
}

.white-bg {
  background-color: #fff;
}

.grey-bg {
  background-color: #f7f8fa;
}

.field-icon {
  font-size: 20px;
  color: #909399;
  margin-right: 5px;
}

.cursor-pointer {
  cursor: pointer;
}

.submit-btn-wrapper {
  margin-top: 40px;
  margin-bottom: 15px;
}

.van-button--primary {
  border-radius: 6px;
  height: 44px;
  font-size: 16px;
}

.login-link {
  text-align: right;
  font-size: 14px;
  color: #909399;
}

.login-link span {
  cursor: pointer;
}

:deep(.van-cell) {
  /* background: transparent; */
}
:deep(.van-field__control) {
  color: #333;
}
</style>
