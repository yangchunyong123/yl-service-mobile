<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { showToast } from "vant";
import { changePassword, getLocalUserInfo, getProfile, logout as clearLoginState } from "@/api";

// 路由实例
const router = useRouter();
// 控制修改密码弹窗
const showPasswordDialog = ref(false);
// 用户信息
const userInfo = ref({
  username: "未登录",
  lastname: "未登录",
  departmentname: "",
});
// 修改密码表单
const passwordForm = ref({
  oldPassword: "",
  newPassword: "",
  confirmPassword: "",
});

// 右上角设置入口
const onClickRight = () => {
  showToast("设置");
};

// 打开修改密码弹窗
const onChangePassword = () => {
  showPasswordDialog.value = true;
};

// 加载用户资料
const loadProfile = async () => {
  const localUser = getLocalUserInfo();
  if (localUser) {
    userInfo.value = {
      ...userInfo.value,
      ...localUser,
    };
  }
  try {
    const profile = await getProfile();
    userInfo.value = {
      ...userInfo.value,
      ...profile,
    };
  } catch (error) {
    showToast("用户信息获取失败");
  }
};

// 提交修改密码
const onConfirmPassword = async () => {
  if (!passwordForm.value.oldPassword) return showToast("请输入旧密码");
  if (!passwordForm.value.newPassword) return showToast("请输入新密码");
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    return showToast("两次输入的密码不一致");
  }
  try {
    const res = await changePassword({
      old_password: passwordForm.value.oldPassword,
      new_password: passwordForm.value.newPassword,
    });
    if (res?.ret !== true) {
      showToast(res?.msg || "密码修改失败");
      return;
    }
    showToast("密码修改成功");
    showPasswordDialog.value = false;
    passwordForm.value = {
      oldPassword: "",
      newPassword: "",
      confirmPassword: "",
    };
  } catch (error) {
    const message = error?.response?.data?.detail || "密码修改失败";
    showToast(message);
  }
};

// 退出登录
const logout = () => {
  clearLoginState();
  router.push("/login");
};

onMounted(() => {
  loadProfile();
});
</script>

<template>
  <div class="user-profile-container">
    <!-- Header Section -->
    <div class="header-section">
      <div class="nav-header">
        <div class="header-title">个人中心</div>
        <!-- <div class="header-right" @click="onClickRight">
          <van-icon name="setting-o" size="24" color="#fff" />
        </div> -->
      </div>

      <!-- User Info / Welcome -->
      <div class="user-banner">
        <div class="user-info">
          <div class="avatar">{{ (userInfo.lastname || userInfo.username || "用").slice(0, 1) }}</div>
          <div class="greeting">
            <h3>{{ userInfo.lastname || userInfo.username }}</h3>
            <p>{{ userInfo.departmentname || "开启高效的一天" }}</p>
          </div>
        </div>
      </div>

      <!-- Quick Stats -->
      <!-- <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-num">12</span>
          <span class="stat-label">待办事项</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">5</span>
          <span class="stat-label">进行中</span>
        </div>
        <div class="stat-item">
          <span class="stat-num">89%</span>
          <span class="stat-label">完成率</span>
        </div>
      </div> -->
    </div>

    <!-- Main Content Body -->
    <div class="main-content">
      <!-- Quick Actions -->
      <div class="section-header">
        <span class="section-title">常用功能</span>
      </div>
      <van-grid :column-num="4" :border="false" class="menu-grid">
        <van-grid-item
          icon="lock"
          text="修改密码"
          class="tech-grid-item"
          @click="onChangePassword"
        />
        <!-- <van-grid-item icon="records" text="工单" class="tech-grid-item" />
        <van-grid-item icon="gold-coin-o" text="报销" class="tech-grid-item" />
        <van-grid-item
          icon="chart-trending-o"
          text="报表"
          class="tech-grid-item"
        /> -->
      </van-grid>

      <!-- Password Dialog -->
      <van-dialog
        v-model:show="showPasswordDialog"
        title="修改密码"
        show-cancel-button
        @confirm="onConfirmPassword"
      >
        <van-form style="margin: 20px 0">
          <van-field
            v-model="passwordForm.oldPassword"
            type="password"
            label="旧密码"
            placeholder="请输入旧密码"
          />
          <van-field
            v-model="passwordForm.newPassword"
            type="password"
            label="新密码"
            placeholder="请输入新密码"
          />
          <van-field
            v-model="passwordForm.confirmPassword"
            type="password"
            label="确认密码"
            placeholder="请再次输入新密码"
          />
        </van-form>
      </van-dialog>

      <!-- Recent Activity / List -->
      <div class="section-header" style="margin-top: 20px">
        <span class="section-title">最新动态</span>
      </div>
      <div class="activity-list">
        <div class="activity-card">
          <div class="card-icon blue-bg"><van-icon name="volume-o" /></div>
          <div class="card-content">
            <div class="card-title">系统通知</div>
            <div class="card-desc">系统维护将于今晚进行...</div>
          </div>
          <div class="card-arrow"><van-icon name="arrow" /></div>
        </div>
        <div class="activity-card">
          <div class="card-icon orange-bg"><van-icon name="todo-list-o" /></div>
          <div class="card-content">
            <div class="card-title">新工单提醒</div>
            <div class="card-desc">您有一个新的售后工单待处理</div>
          </div>
          <div class="card-arrow"><van-icon name="arrow" /></div>
        </div>
      </div>

      <div class="logout-section">
        <van-button class="tech-btn" block @click="logout">退出登录</van-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-profile-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 20px;
}

/* Header Section */
.header-section {
  background: linear-gradient(135deg, #0052d4 0%, #4364f7 50%, #6fb1fc 100%);
  padding: 20px;
  padding-top: 40px; /* Status bar area */
  border-bottom-left-radius: 24px;
  border-bottom-right-radius: 24px;
  color: #fff;
  box-shadow: 0 4px 20px rgba(0, 82, 212, 0.3);
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 1px;
}

.user-banner {
  margin-bottom: 24px;
}

.user-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 50px;
  height: 50px;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 16px;
  border: 2px solid rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
}

.greeting h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
}

.greeting p {
  margin: 4px 0 0;
  font-size: 13px;
  opacity: 0.8;
}

.stats-grid {
  display: flex;
  justify-content: space-around;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px 0;
  backdrop-filter: blur(8px);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
}

/* Main Content */
.main-content {
  padding: 20px;
  margin-top: -10px;
}

.section-header {
  margin-bottom: 12px;
  padding-left: 4px;
  border-left: 4px solid #4364f7;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-left: 8px;
}

/* Grid Menu */
.menu-grid {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  background: #fff;
  margin-bottom: 24px;
}

:deep(.van-grid-item__content) {
  padding: 20px 8px;
}

:deep(.van-grid-item__icon) {
  font-size: 28px;
  color: #4364f7;
  margin-bottom: 8px;
}

:deep(.van-grid-item__text) {
  color: #555;
  font-weight: 500;
}

/* Activity List */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-card {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
  transition: transform 0.2s;
}

.activity-card:active {
  transform: scale(0.98);
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 16px;
  color: #fff;
}

.blue-bg {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.orange-bg {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%);
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.card-desc {
  font-size: 12px;
  color: #999;
}

.card-arrow {
  color: #ccc;
}

/* Logout Button */
.logout-section {
  margin-top: 30px;
}

.tech-btn {
  background: #fff;
  color: #ff4d4f;
  border: none;
  border-radius: 12px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
</style>
