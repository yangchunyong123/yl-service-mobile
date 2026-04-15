<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { showToast } from "vant";
import { getRoutingSheet } from "@/api";
import { initWeComConfig, scanQRCode } from "@/utils/wecom";

// 路由实例与参数
const router = useRouter();
const route = useRoute();
// 序列号输入值
const searchValue = ref("");
// 查询加载状态
const loading = ref(false);

const createDefaultComponentDetails = () => ({
  serial_no: "",
  test_date: "",
  power_grade: "",
  current_grade: "",
  el_grade: "",
  final_grade: "",
  pmax: "",
  voc: "",
  isc: "",
  vmp: "",
  imp: "",
  ff: "",
  eff: "",
  temp: "",
  materials: {
    cell: { name: "", factory: "", model: "" },
    film: { name: "", factory: "", model: "" },
    frame: { name: "", factory: "", model: "" },
    junctionBox: { name: "", factory: "", model: "" },
  },
  business: {
    contract: "",
    customer: "",
  },
});

// 根据路由参数初始化查询参数
onMounted(async () => {
  const serialNo = route.query.serial_no || route.query.serial;
  if (serialNo) {
    searchValue.value = String(serialNo);
    onSearch();
  }

  // 初始化企业微信 JS-SDK
  try {
    await initWeComConfig(['scanQRCode'])
  } catch (error) {
    console.error('JS-SDK 初始化失败:', error)
  }
});

// 组件明细数据
const componentDetails = ref({
  serial_no: "",
  test_date: "",
  power_grade: "",
  current_grade: "",
  el_grade: "",
  final_grade: "",
  pmax: "",
  voc: "",
  isc: "",
  vmp: "",
  imp: "",
  ff: "",
  eff: "",
  temp: "",
  materials: {
    cell: { name: "", factory: "", model: "" },
    film: { name: "", factory: "", model: "" },
    frame: { name: "", factory: "", model: "" },
    junctionBox: { name: "", factory: "", model: "" },
  },
  business: {
    contract: "",
    customer: "",
  },
});

const normalizeMaterial = (material = {}) => ({
  name: material?.name || "",
  factory: material?.factory || "",
  model: material?.model || "",
});

const setComponentDetails = (
  componentData = {},
  routingSheetData = {},
  searchSerialNo = "",
) => {
  const defaultDetails = createDefaultComponentDetails();
  componentDetails.value = {
    serial_no:
      componentData?.serial_no ||
      componentData?.serialNo ||
      routingSheetData?.serial_no ||
      routingSheetData?.serialNo ||
      searchSerialNo ||
      "",
    test_date:
      componentData?.test_date ||
      componentData?.testDate ||
      componentData?.testing_date ||
      componentData?.testingDate ||
      "",
    power_grade:
      componentData?.power_grade ||
      componentData?.powerGrade ||
      componentData?.power_level ||
      componentData?.powerLevel ||
      "",
    current_grade:
      componentData?.current_grade ||
      componentData?.currentGrade ||
      componentData?.current_level ||
      componentData?.currentLevel ||
      "",
    el_grade:
      componentData?.el_grade ||
      componentData?.elGrade ||
      componentData?.el_level ||
      componentData?.elLevel ||
      "",
    final_grade:
      componentData?.final_grade ||
      componentData?.finalGrade ||
      componentData?.final_level ||
      componentData?.finalLevel ||
      "",
    pmax: componentData?.pmax || "",
    voc: componentData?.voc || componentData?.VOC || "",
    isc: componentData?.isc || componentData?.ISC || "",
    vmp: componentData?.vmp || componentData?.VPM || componentData?.vpm || "",
    imp: componentData?.imp || componentData?.IPM || componentData?.ipm || "",
    ff: componentData?.ff || componentData?.FF || "",
    eff: componentData?.eff || "",
    temp: componentData?.temp || "",
    materials: {
      cell: {
        ...normalizeMaterial(componentData?.materials?.cell),
        factory:
          componentData?.materials?.cell?.factory ||
          componentData?.battery_factory ||
          componentData?.batteryFactory ||
          "",
      },
      film: normalizeMaterial(componentData?.materials?.film),
      frame: normalizeMaterial(componentData?.materials?.frame),
      junctionBox: normalizeMaterial(componentData?.materials?.junctionBox),
    },
    business: {
      contract:
        componentData?.business?.contract ||
        componentData?.sales_contract_no ||
        componentData?.salesContractNo ||
        "",
      customer:
        componentData?.business?.customer ||
        componentData?.customer ||
        componentData?.customer_name ||
        "",
    },
  };
  if (!componentData || Object.keys(componentData).length === 0) {
    componentDetails.value = defaultDetails;
  }
};

const displayValue = (value) => value || "-";
// const displayValue = (value) => {
//   if (value === "" || value === null || value === undefined) return "-";
//   // 如果是数字且包含小数点，尝试格式化
//   if (!isNaN(value) && String(value).includes(".")) {
//     const num = Number(value);
//     // 判断是否为浮点数
//     if (!Number.isInteger(num)) {
//       return num.toFixed(2);
//     }
//   }
//   return value;
// };

const materialRows = computed(() => [
  { label: "电池片", ...componentDetails.value.materials.cell },
  // { label: "胶膜", ...componentDetails.value.materials.film },
  // { label: "边框", ...componentDetails.value.materials.frame },
  // { label: "接线盒", ...componentDetails.value.materials.junctionBox },
]);

const queryInfoRows = computed(() => [
  { label: "组件序列号", value: componentDetails.value.serial_no },
  { label: "测试日期", value: componentDetails.value.test_date },
  { label: "功率档位", value: componentDetails.value.power_grade },
  { label: "电流档位", value: componentDetails.value.current_grade },
  { label: "EL等级", value: componentDetails.value.el_grade },
  { label: "最终等级", value: componentDetails.value.final_grade },
  { label: "Pmax", value: componentDetails.value.pmax },
  { label: "ISC", value: componentDetails.value.isc },
  { label: "VOC", value: componentDetails.value.voc },
  { label: "IPM", value: componentDetails.value.imp },
  { label: "VPM", value: componentDetails.value.vmp },
  { label: "FF", value: componentDetails.value.ff },
  // { label: "电池片厂家", value: componentDetails.value.materials.cell.factory },
]);

const onSearch = async () => {
  if (loading.value) return;
  if (!searchValue.value) return showToast("请输入或扫描条码");
  try {
    loading.value = true;
    const res = await getRoutingSheet(searchValue.value);
    if (res?.ret !== true) {
      showToast(res?.msg || "查询失败");
      return;
    }
    setComponentDetails(
      res?.component_details,
      res?.routing_sheet,
      searchValue.value,
    );
  } catch (error) {
    const message =
      error?.response?.data?.detail || error?.response?.data?.msg || "查询失败";
    showToast(message);
  } finally {
    loading.value = false;
  }
};

// 扫码获取序列号
const onScan = async () => {
  if (loading.value) return;
  try {
    const scanResult = await scanQRCode();
    if (!scanResult) return;
    searchValue.value = String(scanResult).trim();
    if (!searchValue.value) return;
    onSearch();
  } catch (error) {
    showToast(error.message || '扫码失败');
  }
};

// 导出明细报表
const exportReport = () => {
  showToast("正在导出明细报表...");
};
</script>

<template>
  <div class="scan-query-container">
    <van-nav-bar
      title="扫码查询"
      left-text="返回"
      left-arrow
      @click-left="router.back()"
      class="tech-navbar"
    />

    <div class="search-section">
      <div class="search-box">
        <input
          type="text"
          v-model="searchValue"
          :disabled="loading"
          placeholder="扫描或输入组件序列号"
          @keyup.enter="onSearch"
        />
        <van-icon
          name="scan"
          size="24"
          color="#4364f7"
          @click="onScan"
          :class="{ disabled: loading }"
        />
      </div>
    </div>
    <van-overlay :show="loading" class="query-loading-overlay">
      <div class="query-loading-content">
        <van-loading type="spinner" size="26px" />
        <span>查询中，请稍候...</span>
      </div>
    </van-overlay>

    <div class="result-section">
      <div class="tab-content">
        <div class="result-card">
          <div class="card-header">
            <span class="title">组件BOM明细</span>
          </div>
          <div class="info-group">
            <div class="group-title">关键参数</div>
            <div class="query-table-wrapper">
              <table class="query-table vertical-table">
                <tbody>
                  <tr v-for="item in queryInfoRows" :key="item.label">
                    <th class="label-cell">{{ item.label }}</th>
                    <td class="value-cell">{{ displayValue(item.value) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div class="divider"></div>
          <div class="info-group">
            <div class="group-title">材料信息</div>
            <div class="material-table">
              <div
                v-for="item in materialRows"
                :key="item.label"
                class="material-card"
              >
                <div class="mat-header">{{ item.label }}</div>
                <div class="mat-content">
                  <div class="mat-item">
                    <span class="mat-label">厂家</span>
                    <span class="mat-value">{{
                      displayValue(item.factory)
                    }}</span>
                  </div>
                  <!-- <div class="mat-item">
                    <span class="mat-label">型号</span>
                    <span class="mat-value">{{
                      displayValue(item.model)
                    }}</span>
                  </div> -->
                </div>
              </div>
            </div>
          </div>
          <div class="divider"></div>
          <div class="info-group">
            <div class="group-title">业务信息</div>
            <div class="info-list">
              <div class="info-item">
                <span class="label">合同号</span>
                <span class="value">{{
                  displayValue(componentDetails.business.contract)
                }}</span>
              </div>
              <div class="info-item">
                <span class="label">客户名称</span>
                <span class="value">{{
                  displayValue(componentDetails.business.customer)
                }}</span>
              </div>
            </div>
          </div>
          <div class="action-btn">
            <van-button
              round
              block
              color="linear-gradient(to right, #43e97b, #38f9d7)"
              @click="exportReport"
            >
              导出报表
            </van-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scan-query-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

:deep(.tech-navbar) {
  background-color: #fff;
}
:deep(.tech-navbar .van-nav-bar__title) {
  font-weight: 600;
}

.search-section {
  padding: 20px;
  background: #fff;
  margin-bottom: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.search-box {
  display: flex;
  align-items: center;
  background: #f7f8fa;
  border-radius: 12px;
  padding: 10px 16px;
  border: 1px solid #ebedf0;
}

.search-box input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  margin-right: 10px;
}

.search-box input:disabled {
  color: #9ca3af;
}

.search-box :deep(.van-icon.disabled) {
  opacity: 0.45;
  pointer-events: none;
}

.query-loading-overlay {
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.query-loading-content {
  background: rgba(17, 24, 39, 0.78);
  color: #fff;
  border-radius: 10px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.tab-content {
  padding: 20px;
}

.result-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  border-left: 4px solid #4364f7;
  padding-left: 8px;
}

/* Image Wrapper */
.image-wrapper {
  width: 100%;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
  margin-bottom: 20px;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  padding: 8px;
  text-align: center;
  font-size: 12px;
}

/* Info List */
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

.label {
  color: #909399;
}

.value {
  color: #333;
  font-weight: 500;
}

.query-table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.query-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.query-table th,
.query-table td {
  border: 1px solid #f0f2f5;
  padding: 12px 16px;
}

.vertical-table .label-cell {
  background: #f8fafc;
  color: #64748b;
  font-weight: 500;
  width: 35%;
  text-align: left;
}

.vertical-table .value-cell {
  color: #334155;
  font-weight: 600;
  text-align: right;
  background: #fff;
}

/* Grid Info */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 12px;
}

.grid-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #f7f8fa;
  padding: 12px;
  border-radius: 8px;
  overflow: hidden;
}

.grid-item .label {
  font-size: 12px;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 100%;
  text-align: center;
}

.grid-item .value {
  font-size: 14px;
  font-weight: 600;
  color: #4364f7;
  word-break: break-all;
  text-align: center;
}

.group-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.divider {
  height: 1px;
  background: #ebedf0;
  margin: 20px 0;
}

/* Material Table */
.material-table {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.material-card {
  background: #f7f8fa;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #ebedf0;
}

.mat-header {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px dashed #ebedf0;
}

.mat-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mat-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  font-size: 13px;
  gap: 12px;
}

.mat-label {
  color: #909399;
  white-space: nowrap;
  min-width: 32px;
}

.mat-value {
  color: #333;
  text-align: right;
  word-break: break-all;
  flex: 1;
}

.action-btn {
  margin-top: 24px;
}
</style>
