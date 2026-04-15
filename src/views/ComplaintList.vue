<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { showToast } from "vant";
import { getComplaints } from "@/api";

// 路由实例
const router = useRouter();
// 搜索关键词
const searchText = ref("");

// 原始客诉列表
const complaints = ref([]);

// 格式化日期为 YYYY-MM-DD，value：时间字符串或时间戳
const formatDate = (value) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, "0");
  const day = `${date.getDate()}`.padStart(2, "0");
  return `${year}-${month}-${day}`;
};

// 处理状态文本兜底，item：客诉项
const statusText = (item) => item.status || "待处理";

// 映射列表展示字段
const displayComplaints = computed(() =>
  complaints.value.map((item) => ({
    id: item.id,
    serialNo: item.serial_no || "",
    project: item.project_name || "",
    status: statusText(item),
    date: formatDate(item.create_time),
    type: item.issue_type || "",
  })),
);

// 根据搜索关键词过滤列表
const filteredComplaints = computed(() => {
  if (!searchText.value) return displayComplaints.value;
  const lower = searchText.value.toLowerCase();
  return displayComplaints.value.filter(
    (item) =>
      item.project.toLowerCase().includes(lower) ||
      item.serialNo.toLowerCase().includes(lower) ||
      item.type.toLowerCase().includes(lower) ||
      String(item.id).toLowerCase().includes(lower),
  );
});

// 统计不同状态数量
const statusCounts = computed(() => {
  const counts = {
    pending: 0,
    processing: 0,
    done: 0,
  };
  displayComplaints.value.forEach((item) => {
    if (item.status === "待处理") counts.pending += 1;
    else if (item.status === "处理中") counts.processing += 1;
    else if (item.status === "已完成") counts.done += 1;
  });
  return counts;
});

// 跳转新建客诉页面
const onAdd = () => {
  router.push("/complaint/new");
};

// 跳转客诉详情页面，id：客诉 ID
const onDetail = (id) => {
  router.push(`/complaint/detail/${id}`);
};

// 获取状态颜色，status：状态文本
const getStatusColor = (status) => {
  if (status === "待处理") return "#ff9a9e";
  if (status === "处理中") return "#4facfe";
  return "#43e97b";
};

// 拉取客诉列表数据
const loadComplaints = async () => {
  try {
    const res = await getComplaints();
    complaints.value = Array.isArray(res) ? res : [];
  } catch (error) {
    const message =
      error?.response?.data?.detail || error?.response?.data?.msg || "加载失败";
    showToast(message);
  }
};

onMounted(() => {
  loadComplaints();
});
</script>

<template>
  <div class="complaint-list-container">
    <div class="header-section">
      <div class="nav-header">
        <div class="header-title">客诉管理</div>
      </div>

      <div class="search-box">
        <van-search
          v-model="searchText"
          placeholder="搜索项目名称/序列号/类型"
          shape="round"
          background="transparent"
        />
      </div>

      <div class="header-stats">
        <div class="stat-item">
          <span class="num">{{ statusCounts.pending }}</span>
          <span class="label">待处理</span>
        </div>
        <div class="stat-item">
          <span class="num">{{ statusCounts.processing }}</span>
          <span class="label">处理中</span>
        </div>
        <div class="stat-item">
          <span class="num">{{ statusCounts.done }}</span>
          <span class="label">已完成</span>
        </div>
      </div>
    </div>

    <div class="list-content">
      <div
        v-for="item in filteredComplaints"
        :key="item.id"
        class="complaint-card"
        @click="onDetail(item.id)"
      >
        <div class="card-header">
          <span class="complaint-id">{{ item.serialNo || item.id }}</span>
          <span
            class="status-tag"
            :style="{
              color: getStatusColor(item.status),
              borderColor: getStatusColor(item.status),
            }"
          >
            {{ item.status }}
          </span>
        </div>
        <div class="card-body">
          <div class="info-row">
            <van-icon name="location-o" />
            <span>{{ item.project }}</span>
          </div>
          <div class="info-row">
            <van-icon name="warning-o" />
            <span>{{ item.type }}</span>
          </div>
          <div class="info-row date">
            <van-icon name="clock-o" />
            <span>{{ item.date }}</span>
          </div>
        </div>
        <div class="card-footer">
          <van-button
            size="small"
            plain
            round
            type="primary"
            @click.stop
          >
            查看详情
          </van-button>
        </div>
      </div>
    </div>

    <div class="fab-btn" @click="onAdd">
      <van-icon name="plus" />
    </div>
  </div>
</template>

<style scoped>
.complaint-list-container {
  height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header Section */
.header-section {
  background: linear-gradient(135deg, #0052d4 0%, #4364f7 50%, #6fb1fc 100%);
  padding: 20px;
  border-bottom-left-radius: 24px;
  border-bottom-right-radius: 24px;
  color: #fff;
  box-shadow: 0 4px 20px rgba(0, 82, 212, 0.3);
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.nav-header {
  margin-bottom: 10px;
  text-align: center;
}

.search-box {
  margin-bottom: 16px;
}

:deep(.van-search) {
  padding-left: 0;
  padding-right: 0;
}

:deep(.van-search .van-search__content) {
  background-color: rgba(255, 255, 255, 0.2);
}
:deep(.van-search .van-field__control) {
  color: #fff;
}
:deep(.van-search .van-field__left-icon) {
  color: rgba(255, 255, 255, 0.8);
}
:deep(.van-search .van-field__control::placeholder) {
  color: rgba(255, 255, 255, 0.6);
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  letter-spacing: 1px;
}

.header-stats {
  display: flex;
  justify-content: space-around;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-item .num {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 4px;
}

.stat-item .label {
  font-size: 12px;
  opacity: 0.8;
}

.list-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  padding-bottom: 100px;
  position: relative;
  z-index: 1;
}

.complaint-card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.complaint-id {
  font-weight: 600;
  color: #333;
}

.status-tag {
  font-size: 12px;
  padding: 2px 8px;
  border: 1px solid;
  border-radius: 4px;
}

.card-body {
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.info-row .van-icon {
  margin-right: 8px;
  font-size: 16px;
}

.info-row.date {
  color: #999;
  font-size: 12px;
}

.card-footer {
  text-align: right;
}

.fab-btn {
  position: fixed;
  bottom: calc(50px + constant(safe-area-inset-bottom) + 5px);
  bottom: calc(50px + env(safe-area-inset-bottom) + 5px);
  right: 20px;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0052d4 0%, #4364f7 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 28px;
  box-shadow: 0 4px 12px rgba(67, 100, 247, 0.4);
  z-index: 999;
}

.fab-btn .van-icon {
  margin-top: -2px;
}
</style>
