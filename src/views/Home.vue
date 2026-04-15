<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { showToast } from "vant";

// 路由实例
const router = useRouter();
// 搜索框输入值
const searchValue = ref("");

// 顶部快捷入口
const quickActions = [
  { icon: "scan", text: "扫一扫", color: "#4facfe", route: "/scan-query" },
  {
    icon: "bar-chart-o",
    text: "明细报表",
    color: "#fa709a",
    route: "/scan-query",
  },
];

// 核心功能入口
const menuItems = [
  {
    icon: "records",
    text: "客诉录入",
    color: "#ff9a9e",
    route: "/complaint/new",
  },
  { icon: "todo-list-o", text: "客诉列表", color: "#a18cd1", route: "/orders" },
  // { icon: "clock-o", text: "维修记录", color: "#fad0c4", route: "" },
  // { icon: "search", text: "备件查询", color: "#ffecd2", route: "" },
];

// 搜索并跳转匹配的功能入口，val：搜索关键词
const onSearch = (val) => {
  if (!val) {
    showToast("请输入搜索内容");
    return;
  }
  // 查找所有菜单项（包括 quickActions 和 menuItems）
  const allItems = [...quickActions, ...menuItems];
  const target = allItems.find((item) => item.text.includes(val));

  if (target) {
    if (target.route) {
      router.push(target.route);
    } else {
      showToast("该功能暂未开放");
    }
  } else {
    showToast("未找到相关功能");
  }
};

// 资讯列表数据
const newsList = [
  { id: 1, title: "系统升级通知", date: "2023-10-01", tag: "公告" },
  { id: 2, title: "关于国庆放假的通知", date: "2023-09-28", tag: "行政" },
  { id: 3, title: "第三季度业绩报表已发布", date: "2023-09-25", tag: "财务" },
];
</script>

<template>
  <div class="home-dashboard">
    <!-- Top Search & Scan Area -->
    <div class="top-bar">
      <div class="search-box" @click="$refs.searchInput.focus()">
        <van-icon name="search" size="18" color="#fff" @click.stop="onSearch(searchValue)" />
        <input
          ref="searchInput"
          type="text"
          v-model="searchValue"
          placeholder="搜索功能、服务"
          @keyup.enter="onSearch(searchValue)"
        />
      </div>
    </div>

    <!-- Main Banner / Dashboard Card -->
    <div class="dashboard-card">
      <div class="card-header">
        <div class="welcome-text">
          <h2>YINGLI SERVICE</h2>
          <p>售后现场移动终端系统</p>
        </div>
        <!-- <div class="weather-icon">☁️ 24°C</div> -->
      </div>

      <!-- Quick Action Grid -->
      <div class="quick-actions">
        <van-grid :column-num="quickActions.length" :border="false">
          <van-grid-item
            v-for="(item, index) in quickActions"
            :key="index"
            class="action-item-grid"
            @click="item.route && router.push(item.route)"
          >
            <div class="icon-circle" :style="{ background: item.color }">
              <van-icon :name="item.icon" color="#fff" size="20" />
            </div>
            <span class="action-text">{{ item.text }}</span>
          </van-grid-item>
        </van-grid>
      </div>
    </div>

    <!-- Service Grid -->
    <div class="service-section">
      <div class="section-title">核心功能</div>
      <van-grid
        :column-num="menuItems.length"
        :border="false"
        class="glass-grid"
      >
        <van-grid-item
          v-for="(item, index) in menuItems"
          :key="index"
          class="glass-grid-item"
          @click="item.route && router.push(item.route)"
        >
          <template #icon>
            <van-icon :name="item.icon" :color="item.color" size="28" />
          </template>
          <template #text>
            <span class="grid-text">{{ item.text }}</span>
          </template>
        </van-grid-item>
      </van-grid>
    </div>

    <!-- Data / News Section -->
    <!-- <div class="data-section">
      <div class="section-title">最新资讯</div>
      <div class="news-list">
        <div v-for="news in newsList" :key="news.id" class="news-item">
          <div class="news-tag">{{ news.tag }}</div>
          <div class="news-content">
            <div class="news-title">{{ news.title }}</div>
            <div class="news-date">{{ news.date }}</div>
          </div>
          <van-icon name="arrow" color="#ccc" />
        </div>
      </div>
    </div> -->
  </div>
</template>

<style scoped>
.home-dashboard {
  min-height: 100vh;
  background-color: #f2f4f8;
  padding-bottom: 20px;
  position: relative;
  overflow: hidden;
}

/* Background Decoration */
.home-dashboard::before {
  content: "";
  position: absolute;
  top: -100px;
  left: -50px;
  width: 400px;
  height: 400px;
  background: radial-gradient(
    circle,
    rgba(67, 100, 247, 0.2) 0%,
    rgba(255, 255, 255, 0) 70%
  );
  border-radius: 50%;
  z-index: 0;
}

/* Top Bar */
.top-bar {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #0052d4 0%, #4364f7 100%);
  position: relative;
  z-index: 1;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 8px 12px;
  margin-right: 16px;
  backdrop-filter: blur(4px);
}

.search-box input {
  background: transparent;
  border: none;
  color: #fff;
  margin-left: 8px;
  width: 100%;
  font-size: 14px;
}

.search-box input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.scan-btn {
  display: flex;
  align-items: center;
}

/* Dashboard Card */
.dashboard-card {
  margin: 20px;
  margin-top: 10px;
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.welcome-text h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
  letter-spacing: 1px;
}

.welcome-text p {
  margin: 4px 0 0;
  font-size: 12px;
  color: #999;
}

.weather-icon {
  font-size: 14px;
  color: #666;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 12px;
}

.quick-actions {
  /* display: flex; */
  /* justify-content: space-between; */
  margin-top: 10px;
}

/* .action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
} */

.icon-circle {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

/* .action-item:active .icon-circle {
  transform: scale(0.95);
} */

/* .action-item span {
  font-size: 12px;
  color: #666;
} */

.action-text {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
}

:deep(.action-item-grid .van-grid-item__content) {
  padding: 0;
  background: transparent;
}

/* Service Section */
.service-section {
  padding: 0 20px;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 4px solid #4364f7;
}

.glass-grid {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
}

.grid-text {
  font-size: 13px;
  color: #555;
  margin-top: 8px;
}

/* Data / News Section */
.data-section {
  padding: 0 20px;
  margin-bottom: 24px;
}

.news-list {
  background: #fff;
  border-radius: 16px;
  padding: 0 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.news-item {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.news-item:last-child {
  border-bottom: none;
}

.news-tag {
  font-size: 10px;
  color: #4364f7;
  background: rgba(67, 100, 247, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 12px;
}

.news-content {
  flex: 1;
}

.news-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
}

.news-date {
  font-size: 12px;
  color: #999;
}

/* Promo Banner */
.promo-banner {
  margin: 0 20px 20px;
  background: linear-gradient(135deg, #2c3e50 0%, #000000 100%);
  border-radius: 16px;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.promo-content h3 {
  margin: 0;
  font-size: 16px;
  color: #ffd700;
}

.promo-content p {
  margin: 4px 0 0;
  font-size: 12px;
  opacity: 0.8;
}
</style>
