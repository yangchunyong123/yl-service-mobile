<script setup>
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { showToast } from "vant";
import { getComplaintDetail, updateComplaint } from "@/api";

// 路由实例与路由参数
const router = useRouter();
const route = useRoute();

// 客诉详情展示数据
const detail = ref({
  handler: "",
  serialNo: "",
  projectName: "",
  location: "",
  isWarranty: "",
  issueType: "",
  inverterInfo: "",
  processType: "",
  replaceSerialNo: "",
  repairDetails: {
    positive: "更换",
    middle: "更换",
    negative: "更换",
  },
  repairer: "",
  status: "待处理",
});

// 详情编辑表单数据
const editForm = ref({
  handler: "",
  serialNo: "",
  projectName: "",
  location: "",
  isWarranty: "",
  issueType: "",
  inverterInfo: "",
  processType: "",
  replaceSerialNo: "",
  repairDetails: {
    positive: "",
    middle: "",
    negative: "",
  },
  repairer: "",
});

// 控制编辑弹窗显示
const showEditDialog = ref(false);
// 保存中状态
const saving = ref(false);

// 根据状态返回颜色，status：状态文本
const getStatusColor = (status) => {
  if (status === "待处理") return "#ff9a9e";
  if (status === "处理中") return "#4facfe";
  return "#43e97b";
};

// 状态选择弹层与可选项
const showStatusAction = ref(false);
const statusActions = [
  { name: "待处理" },
  { name: "处理中" },
  { name: "已完成" },
];

// 选择状态后更新，item：动作项
const onSelectStatus = (item) => {
  updateStatus(item.name);
};

// 打开编辑弹窗并回填数据
const onEdit = () => {
  editForm.value = {
    handler: detail.value.handler,
    serialNo: detail.value.serialNo,
    projectName: detail.value.projectName,
    location: detail.value.location,
    isWarranty: detail.value.isWarranty,
    issueType: detail.value.issueType,
    inverterInfo: detail.value.inverterInfo,
    processType: detail.value.processType,
    replaceSerialNo: detail.value.replaceSerialNo,
    repairDetails: {
      positive: detail.value.repairDetails?.positive || "",
      middle: detail.value.repairDetails?.middle || "",
      negative: detail.value.repairDetails?.negative || "",
    },
    repairer: detail.value.repairer,
  };
  showEditDialog.value = true;
};

// 更新客诉状态，status：状态文本
const updateStatus = async (status) => {
  try {
    saving.value = true;
    const res = await updateComplaint(route.params.id, { status });
    if (res?.ret !== true) {
      showToast(res?.msg || "更新失败");
      return;
    }
    detail.value.status = status;
    showStatusAction.value = false;
    showToast(`状态已更新为：${status}`);
  } catch (error) {
    const message =
      error?.response?.data?.detail || error?.response?.data?.msg || "更新失败";
    showToast(message);
  } finally {
    saving.value = false;
  }
};

// 提交编辑表单
const onConfirmEdit = async () => {
  try {
    saving.value = true;
    const payload = {
      handler: editForm.value.handler,
      serial_no: editForm.value.serialNo,
      project_name: editForm.value.projectName,
      location: editForm.value.location,
      is_warranty: editForm.value.isWarranty,
      issue_type: editForm.value.issueType,
      inverter_info: editForm.value.inverterInfo,
      process_type: editForm.value.processType,
      replace_serial_no: editForm.value.replaceSerialNo,
      repair_details: editForm.value.repairDetails,
      repairer: editForm.value.repairer,
    };
    const res = await updateComplaint(route.params.id, payload);
    if (res?.ret !== true) {
      showToast(res?.msg || "更新失败");
      return;
    }
    detail.value = {
      ...detail.value,
      handler: editForm.value.handler,
      serialNo: editForm.value.serialNo,
      projectName: editForm.value.projectName,
      location: editForm.value.location,
      isWarranty: editForm.value.isWarranty,
      issueType: editForm.value.issueType,
      inverterInfo: editForm.value.inverterInfo,
      processType: editForm.value.processType,
      replaceSerialNo: editForm.value.replaceSerialNo,
      repairDetails: editForm.value.repairDetails,
      repairer: editForm.value.repairer,
    };
    showEditDialog.value = false;
    showToast("更新成功");
  } catch (error) {
    const message =
      error?.response?.data?.detail || error?.response?.data?.msg || "更新失败";
    showToast(message);
  } finally {
    saving.value = false;
  }
};

// 拉取客诉详情
const loadDetail = async () => {
  try {
    const res = await getComplaintDetail(route.params.id);
    detail.value = {
      ...detail.value,
      handler: res?.handler || "",
      serialNo: res?.serial_no || "",
      projectName: res?.project_name || "",
      location: res?.location || "",
      isWarranty: res?.is_warranty || "",
      issueType: res?.issue_type || "",
      inverterInfo: res?.inverter_info || "",
      processType: res?.process_type || "",
      replaceSerialNo: res?.replace_serial_no || "",
      repairDetails: res?.repair_details || detail.value.repairDetails,
      repairer: res?.repairer || "",
      status: res?.status || detail.value.status,
    };
  } catch (error) {
    const message =
      error?.response?.data?.detail || error?.response?.data?.msg || "加载失败";
    showToast(message);
  }
};

onMounted(() => {
  loadDetail();
});
</script>

<template>
  <div class="complaint-detail-container">
    <van-nav-bar
      title="客诉详情"
      left-text="返回"
      left-arrow
      @click-left="router.back()"
      class="tech-navbar"
    />

    <div class="detail-content">
      <!-- Status Card -->
      <div class="status-card">
        <div class="status-header">
          <span class="label">当前状态</span>
          <span
            class="status-text"
            :style="{ color: getStatusColor(detail.status) }"
            @click="showStatusAction = true"
          >
            {{ detail.status }} <van-icon name="edit" />
          </span>
        </div>
        <div class="complaint-no">序列号：{{ detail.serialNo }}</div>
      </div>

      <!-- Basic Info -->
      <div class="info-group">
        <div class="group-title">基础信息</div>
        <div class="info-list">
          <div class="info-item">
            <span class="label">客诉处理人</span>
            <span class="value">{{ detail.handler }}</span>
          </div>
          <div class="info-item">
            <span class="label">项目名称</span>
            <span class="value">{{ detail.projectName }}</span>
          </div>
          <div class="info-item">
            <span class="label">项目地点</span>
            <span class="value">{{ detail.location }}</span>
          </div>
        </div>
      </div>

      <!-- Judgment Info -->
      <div class="info-group">
        <div class="group-title">判定信息</div>
        <div class="info-list">
          <div class="info-item">
            <span class="label">是否质保</span>
            <span class="value">{{ detail.isWarranty }}</span>
          </div>
          <div class="info-item">
            <span class="label">问题种类</span>
            <span class="value">{{ detail.issueType }}</span>
          </div>
          <div class="info-item">
            <span class="label">方阵记录(逆变器)</span>
            <span class="value">{{ detail.inverterInfo }}</span>
          </div>
        </div>
      </div>

      <!-- Process Info -->
      <div class="info-group">
        <div class="group-title">处理与维修</div>
        <div class="info-list">
          <div class="info-item">
            <span class="label">处理类型</span>
            <span class="value">{{ detail.processType }}</span>
          </div>
          <div class="info-item">
            <span class="label">换货序列号</span>
            <span class="value">{{ detail.replaceSerialNo }}</span>
          </div>
          <div class="info-item">
            <span class="label">维修人</span>
            <span class="value">{{ detail.repairer }}</span>
          </div>
          <div class="divider"></div>
          <div class="repair-grid">
            <div class="repair-item">
              <span class="r-label">正极</span>
              <span class="r-value">{{ detail.repairDetails.positive }}</span>
            </div>
            <div class="repair-item">
              <span class="r-label">中间</span>
              <span class="r-value">{{ detail.repairDetails.middle }}</span>
            </div>
            <div class="repair-item">
              <span class="r-label">负极</span>
              <span class="r-value danger">{{
                detail.repairDetails.negative
              }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="action-btn">
        <van-button
          round
          block
          type="primary"
          color="linear-gradient(to right, #0052d4, #4364f7)"
          @click="onEdit"
        >
          编辑工单
        </van-button>
      </div>

      <van-action-sheet
        v-model:show="showStatusAction"
        :actions="statusActions"
        cancel-text="取消"
        close-on-click-action
        @select="onSelectStatus"
      />
      <van-dialog
        v-model:show="showEditDialog"
        title="编辑工单"
        show-cancel-button
        :confirm-loading="saving"
        @confirm="onConfirmEdit"
      >
        <van-form style="margin: 16px 0">
          <van-field v-model="editForm.handler" label="客诉处理人" />
          <van-field v-model="editForm.serialNo" label="组件序列号" />
          <van-field v-model="editForm.projectName" label="项目名称" />
          <van-field v-model="editForm.location" label="项目地点" />
          <van-field v-model="editForm.isWarranty" label="是否质保" />
          <van-field v-model="editForm.issueType" label="问题种类" />
          <van-field v-model="editForm.inverterInfo" label="方阵记录" />
          <van-field v-model="editForm.processType" label="处理类型" />
          <van-field v-model="editForm.replaceSerialNo" label="换货序列号" />
          <van-field v-model="editForm.repairer" label="维修人" />
          <van-field
            v-model="editForm.repairDetails.positive"
            label="正极处理"
          />
          <van-field v-model="editForm.repairDetails.middle" label="中间处理" />
          <van-field
            v-model="editForm.repairDetails.negative"
            label="负极处理"
          />
        </van-form>
      </van-dialog>
    </div>
  </div>
</template>

<style scoped>
.complaint-detail-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding-bottom: 40px;
}

:deep(.tech-navbar) {
  background-color: #fff;
}
:deep(.tech-navbar .van-nav-bar__title) {
  font-weight: 600;
}

.detail-content {
  padding: 16px;
}

/* Status Card */
.status-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  text-align: center;
}

.status-header {
  margin-bottom: 8px;
}

.status-header .label {
  font-size: 14px;
  color: #999;
  margin-right: 8px;
}

.status-text {
  font-size: 20px;
  font-weight: bold;
}

.complaint-no {
  font-size: 12px;
  color: #666;
  background: #f5f7fa;
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
}

/* Info Group */
.info-group {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.group-title {
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-left: 8px;
  border-left: 4px solid #4364f7;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.info-item .label {
  color: #909399;
}

.info-item .value {
  color: #333;
  text-align: right;
  flex: 1;
  margin-left: 20px;
}

.divider {
  height: 1px;
  background: #ebedf0;
  margin: 8px 0;
}

/* Repair Grid */
.repair-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 8px;
}

.repair-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f7f8fa;
  padding: 12px;
  border-radius: 8px;
}

.r-label {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.r-value {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.r-value.danger {
  color: #ee0a24;
}

.action-btn {
  margin-top: 32px;
}
</style>
