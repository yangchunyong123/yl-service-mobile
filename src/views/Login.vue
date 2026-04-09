<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { showToast } from "vant";
import { login } from "@/api";
import logoUrl from "@/assets/style/img/ylfwsylogo.png";

// 路由实例与路由参数
const router = useRouter();
const route = useRoute();
// 表单输入数据
const username = ref("");
const password = ref("");
const captcha = ref("");
// 验证码图片与明文
const captchaUrl = ref("");
const captchaCode = ref("");
// 密码显示与加载状态
const showPassword = ref(false);
const loading = ref(false);

// Canvas for generating captcha
// 绘制图形验证码
// 生成并渲染图形验证码
const drawCaptcha = () => {
  // 创建 canvas 元素
  const canvas = document.createElement("canvas");
  canvas.width = 120;
  canvas.height = 40;
  const ctx = canvas.getContext("2d");

  // Background
  // 填充背景色
  ctx.fillStyle = "#f7f8fa";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Random text
  // 绘制随机文本
  const chars = "0123456789";
  let code = "";
  for (let i = 0; i < 4; i++) {
    const char = chars[Math.floor(Math.random() * chars.length)];
    code += char;
    ctx.font = "24px Arial";
    // 随机颜色
    // 确保生成6位十六进制颜色代码，避免位数不足导致颜色无效（可能显示为透明或上一颜色）
    // 另外避免颜色过浅导致看不清（限制RGB值）
    const r = Math.floor(Math.random() * 200); // 0-199
    const g = Math.floor(Math.random() * 200); // 0-199
    const b = Math.floor(Math.random() * 200); // 0-199
    ctx.fillStyle = `rgb(${r},${g},${b})`;

    // 绘制文字，并设置位置
    ctx.fillText(char, 20 + i * 25, 30);
  }
  captchaCode.value = code;

  // Random lines
  // 绘制随机干扰线
  for (let i = 0; i < 5; i++) {
    ctx.beginPath();
    // 随机起点和终点
    ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
    ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
    // 随机线条颜色
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    ctx.strokeStyle = `rgb(${r},${g},${b})`;
    ctx.stroke();
  }

  // Random dots
  // 绘制随机干扰点
  for (let i = 0; i < 20; i++) {
    ctx.beginPath();
    // 随机圆心和半径
    ctx.arc(
      Math.random() * canvas.width,
      Math.random() * canvas.height,
      1,
      0,
      2 * Math.PI,
    );
    // 随机填充颜色
    const r = Math.floor(Math.random() * 256);
    const g = Math.floor(Math.random() * 256);
    const b = Math.floor(Math.random() * 256);
    ctx.fillStyle = `rgb(${r},${g},${b})`;
    ctx.fill();
  }

  // 将 canvas 内容转换为 Base64 图片 URL
  captchaUrl.value = canvas.toDataURL();
};

onMounted(() => {
  // 组件挂载时生成验证码
  drawCaptcha();
});

// 提交登录请求
const onSubmit = async () => {
  if (captcha.value.trim() !== captchaCode.value) {
    showToast("验证码错误");
    drawCaptcha();
    return;
  }
  loading.value = true;
  try {
    await login({
      username: username.value.trim(),
      password: password.value,
    });
    showToast("登录成功");
    const redirect = route.query.redirect || "/home";
    router.replace(redirect);
  } catch (error) {
    const message = error?.response?.data?.detail || "用户名或密码错误";
    showToast(message);
    drawCaptcha();
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="login-container">
    <div class="logo-area">
      <!-- Placeholder for Logo -->
      <div class="logo-placeholder">
        <img :src="logoUrl" alt="logo" />
      </div>
      <h2 class="app-title">售后管理系统</h2>
    </div>

    <van-form @submit="onSubmit" class="login-form">
      <div class="input-wrapper">
        <van-field
          v-model="username"
          name="username"
          placeholder="手机号"
          :rules="[{ required: true, message: '请输入账号' }]"
          class="custom-field"
        >
          <template #left-icon>
            <van-icon name="contact" class="field-icon" />
          </template>
        </van-field>
      </div>

      <div class="input-wrapper">
        <van-field
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          name="password"
          placeholder="密码"
          :rules="[{ required: true, message: '请输入密码' }]"
          class="custom-field"
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

      <div class="captcha-wrapper">
        <van-field
          v-model="captcha"
          name="captcha"
          placeholder="验证码"
          :rules="[{ required: true, message: '请输入验证码' }]"
          class="captcha-field"
        />
        <div class="captcha-image" @click="drawCaptcha">
          <img :src="captchaUrl" alt="验证码" />
        </div>
      </div>

      <div class="submit-btn-wrapper">
        <van-button
          :loading="loading"
          block
          type="primary"
          native-type="submit"
          color="#409eff"
        >
          登录
        </van-button>
      </div>

      <div class="register-link">
        <span @click="router.push('/register')">点击注册</span>
      </div>
    </van-form>
  </div>
</template>

<style scoped>
.login-container {
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
  margin-top: 60px;
}

.logo-placeholder {
  font-size: 32px;
  font-weight: bold;
  position: relative;
  display: inline-block;
  margin-bottom: 20px;
}

.logo-text-blue {
  color: #0099ff;
}

.logo-text-orange {
  color: #ff9900;
}

.sun-icon {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 40px;
  color: #ff9900;
  z-index: -1;
  opacity: 0.5; /* Just a simple representation */
}

.app-title {
  font-size: 18px;
  color: #666;
  font-weight: normal;
  margin: 0;
}

.login-form {
  width: 100%;
}

.input-wrapper {
  margin-bottom: 20px;
}

.custom-field {
  background-color: #e8f0fe; /* Light blue background */
  border-radius: 8px;
  padding: 10px 16px;
  border: 1px solid #dcdfe6; /* Light border */
}

.field-icon {
  font-size: 20px;
  color: #909399;
  margin-right: 5px;
}

.cursor-pointer {
  cursor: pointer;
}

.captcha-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;
}

.captcha-field {
  flex: 1;
  margin-right: 15px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  padding: 10px;
}

.captcha-image {
  width: 120px;
  height: 44px; /* Slightly taller to match input height */
  cursor: pointer;
  display: flex;
  align-items: center;
}

.captcha-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.submit-btn-wrapper {
  margin-bottom: 15px;
}

.van-button--primary {
  border-radius: 6px;
  height: 44px;
  font-size: 16px;
}

.register-link {
  text-align: right;
  font-size: 14px;
  color: #909399;
}

.register-link span {
  cursor: pointer;
}

/* Override Vant field styles to remove default background if needed */
:deep(.van-cell) {
  background: transparent;
}
/* Restore white background for captcha field */
.captcha-field {
  background-color: #fff;
}
/* Ensure input text color is visible */
:deep(.van-field__control) {
  color: #333;
}
</style>
