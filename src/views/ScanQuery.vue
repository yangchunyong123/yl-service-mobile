<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import { showToast } from "vant";
import { getRoutingSheet } from "@/api";

// 路由实例与参数
const router = useRouter();
const route = useRoute();
// 序列号输入值
const searchValue = ref("");
// 当前激活标签页
const activeTab = ref(0);
// 查询加载状态
const loading = ref(false);

const createDefaultComponentDetails = () => ({
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

// 根据路由参数切换默认标签
onMounted(() => {
  if (route.query.tab) {
    activeTab.value = Number(route.query.tab);
  }
  const serialNo = route.query.serial_no || route.query.serial;
  if (serialNo) {
    searchValue.value = String(serialNo);
    onSearch();
  }
});

// 流转单数据
const routingSheet = ref({
  id: "",
  status: "",
  current_node: "",
  steps: [],
});
// 组件明细数据
const componentDetails = ref({
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

const setComponentDetails = (componentData = {}) => {
  const defaultDetails = createDefaultComponentDetails();
  componentDetails.value = {
    pmax: componentData?.pmax || "",
    voc: componentData?.voc || "",
    isc: componentData?.isc || "",
    vmp: componentData?.vmp || "",
    imp: componentData?.imp || "",
    ff: componentData?.ff || "",
    eff: componentData?.eff || "",
    temp: componentData?.temp || "",
    materials: {
      cell: normalizeMaterial(componentData?.materials?.cell),
      film: normalizeMaterial(componentData?.materials?.film),
      frame: normalizeMaterial(componentData?.materials?.frame),
      junctionBox: normalizeMaterial(componentData?.materials?.junctionBox),
    },
    business: {
      contract: componentData?.business?.contract || "",
      customer: componentData?.business?.customer || "",
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
  { label: "胶膜", ...componentDetails.value.materials.film },
  { label: "边框", ...componentDetails.value.materials.frame },
  { label: "接线盒", ...componentDetails.value.materials.junctionBox },
]);

const stepActive = computed(() => {
  if (!routingSheet.value.steps.length) return 0;
  const index = routingSheet.value.steps.findIndex(
    (step) => step === routingSheet.value.current_node,
  );
  return index >= 0 ? index : 0;
});

const hasSteps = computed(() => routingSheet.value.steps.length > 0);

const routingSummary = {
  headers: [
    "车间编号",
    "当前站点",
    "组件编号",
    "客户名称",
    "工单类型",
    "工单编号",
    "产品类型",
    "产品规格",
    "材料备注",
    "当前状态",
  ],
  values: [
    "组件四车间(发展)",
    "已入库",
    "254803050300048",
    "英利",
    "正常工单",
    "2548030503",
    "M0200302020270620 1031200",
    "2382*1134*30",
    "",
    "Good",
  ],
};

const routingSections = [
  {
    title: "分选",
    rows: [
      [
        { label: "片源批号", value: "M2540HNMS2025111 6008" },
        { label: "操作人员", value: "仓库发料" },
      ],
      [
        { label: "片源厂商", value: "通威太阳能（眉山）有限公司" },
        { label: "片源规格", value: "210*182.3" },
      ],
      [
        { label: "片源颜色", value: "蓝" },
        { label: "片源用量", value: "66.33" },
      ],
      [
        { label: "电池效率", value: "25.4" },
        { label: "单片功率", value: "9.7" },
      ],
      [
        { label: "焊接时间", value: "2025-11-27 21:08:49" },
        { label: "操作人员", value: "三车间A线装层002" },
      ],
      [
        { label: "机台名称", value: "三焊接003" },
        { label: "破片数量", value: "" },
      ],
    ],
  },
  {
    title: "焊接",
    rows: [
      [
        { label: "助焊剂厂商", value: "深圳市同方电子新材料有限公司" },
        { label: "互联条厂商", value: "河北佰真新能源材料有限公司" },
      ],
      [
        { label: "助焊剂规格", value: "TFHF9200" },
        { label: "互联条规格", value: "Φ0.24mm/Sn/Pb: 60/40 (15µm)" },
      ],
      [
        { label: "助焊剂批号", value: "10_8325103000003-1" },
        { label: "互联条批号", value: "10_8325112100013-1" },
      ],
      [
        { label: "焊接班次", value: "白班" },
        { label: "虚拟ID", value: "202511272107C003" },
      ],
      [
        { label: "LR侧", value: "" },
        { label: "", value: "" },
      ],
    ],
  },
  {
    title: "叠层",
    rows: [
      [
        { label: "操作时间", value: "2025-11-27 21:08:50" },
        { label: "操作人员", value: "三车间A线装层002" },
      ],
      [
        { label: "机台名称", value: "三车间C线装层001" },
        { label: "叠层班次", value: "乙班" },
      ],
      [
        { label: "POE厂商", value: "上海海优威新材料股份有限公司" },
        { label: "EVA厂商", value: "上海海优威新材料股份有限公司" },
      ],
      [
        { label: "POE规格", value: "0.55mm*1123mm*450" },
        { label: "EVA规格", value: "0.55mm*1123mm*450" },
      ],
      [
        { label: "POE批号", value: "P1073251105B076" },
        { label: "EVA批号", value: "A1070251103B104" },
      ],
      [
        { label: "玻璃厂商(正面)", value: "山西日盛达太阳能科技股份有限公司" },
        { label: "背板厂商", value: "" },
      ],
      [
        { label: "玻璃规格(正面)", value: "2376*1128*2.0mm半钢化布纹单镀" },
        { label: "背板规格", value: "" },
      ],
      [
        { label: "玻璃批号(正面)", value: "10_8325112700003-2" },
        { label: "背板批号", value: "" },
      ],
      [
        { label: "玻璃厂商(背面)", value: "山西日盛达太阳能科技股份有限公司" },
        { label: "汇流条厂商", value: "河北斯卓新能源科技有限责任公司" },
      ],
      [
        { label: "玻璃规格(背面)", value: "2376*1128*2.0mm布纹打孔" },
        { label: "汇流条规格", value: "0.29*4mm/0.29*7mm" },
      ],
      [
        { label: "玻璃批号(背面)", value: "10_8325112700002-1" },
        { label: "汇流条批号", value: "10_8325112700006-1" },
      ],
    ],
  },
  {
    title: "层压前EL",
    rows: [
      [
        { label: "测试时间", value: "2025-11-27 21:15:24" },
        { label: "操作人员", value: "三车间前EL002" },
      ],
      [
        { label: "机台名称", value: "三车间QEL002" },
        { label: "测试结果", value: "A1" },
      ],
    ],
  },
  {
    title: "层压",
    rows: [
      [
        { label: "层压时间", value: "2025-11-27 22:10:21" },
        { label: "操作人员", value: "管理员" },
      ],
      [
        { label: "机台名称", value: "三车间1号层压机下层" },
        { label: "层压层次", value: "1" },
      ],
      [
        { label: "上真空压力设定值", value: "15" },
        { label: "加压压力设定值", value: "-60" },
      ],
      [
        { label: "层压时长设定值", value: "15" },
        { label: "加压时长设定值", value: "15" },
      ],
      [
        { label: "层压压力设定值", value: "1" },
        { label: "抽真空时间设定值", value: "20" },
      ],
    ],
  },
  {
    title: "层压后检验",
    rows: [
      [
        { label: "测试时间", value: "" },
        { label: "操作人员", value: "" },
      ],
      [
        { label: "机台名称", value: "不良" },
        { label: "测试结果", value: "" },
      ],
    ],
  },
  {
    title: "装框",
    rows: [
      [
        { label: "操作时间", value: "2025-11-28 01:45:41" },
        { label: "操作人员", value: "三车间B线装框003" },
      ],
      [
        { label: "机台名称", value: "三车间C线装框001" },
        { label: "接线盒焊接时间", value: "2025-11-28 01:45:41" },
      ],
      [
        { label: "线盒厂商", value: "江苏隆邦电子科技股份有限公司" },
        { label: "长型材厂家", value: "营口瑞达铝业有限公司" },
      ],
      [
        { label: "线盒规格", value: "S4xy/GFT4050SM/0.3 m25A" },
        { label: "长型材规格", value: "2382mm/Q568K长" },
      ],
      [
        { label: "线盒批号", value: "10_8325112700007-1" },
        { label: "长型材批号", value: "10_8325112700100-1" },
      ],
      [
        { label: "A胶厂商", value: "上海回天新材料有限公司" },
        { label: "B胶厂商", value: "上海回天新材料有限公司" },
      ],
      [
        { label: "A胶规格", value: "5299W-S-A" },
        { label: "B胶规格", value: "5299W-S-B" },
      ],
      [
        { label: "A胶批号", value: "10_8325103000006-01" },
        { label: "B胶批号", value: "10_8325103000007-01" },
      ],
      [
        { label: "胶厂商", value: "上海回天新材料有限公司" },
        { label: "胶规格", value: "HT906Z" },
      ],
      [
        { label: "胶批号", value: "10_8325110100006-1" },
        { label: "短型材厂家", value: "营口瑞达铝业有限公司" },
      ],
      [
        { label: "短型材规格", value: "1134mm/Q568K短" },
        { label: "短型材批号", value: "10_8325112700101-1" },
      ],
    ],
  },
  {
    title: "清洗",
    rows: [
      [
        { label: "操作时间", value: "" },
        { label: "操作人员", value: "" },
      ],
      [
        { label: "机台名称", value: "" },
        { label: "", value: "" },
      ],
    ],
  },
  {
    title: "安规测试",
    rows: [
      [
        { label: "测试时间", value: "2025-11-29 06:46:31" },
        { label: "操作人员", value: "" },
      ],
      [
        { label: "机台名称", value: "2" },
        { label: "测试结果", value: "合格" },
      ],
    ],
  },
  {
    title: "电性能测试",
    rows: [
      [
        { label: "测试时间", value: "2025-11-29 06:44:21" },
        { label: "操作人员", value: "" },
      ],
      [
        { label: "机台名称", value: "三车间C线IV001" },
        { label: "测试功率", value: "624.1112671" },
      ],
      [
        { label: "测试电流", value: "15.1493864059" },
        { label: "测试时间", value: "2025-11-29 06:45:39" },
      ],
    ],
  },
  {
    title: "测试后EL",
    rows: [
      [
        { label: "操作人员", value: "三车间后EL001" },
        { label: "机台名称", value: "三车间HEL001" },
      ],
      [
        { label: "测试结果", value: "A1" },
        { label: "HEL不良项", value: "" },
      ],
      [
        { label: "HEL不良位置", value: "" },
        { label: "", value: "" },
      ],
    ],
  },
  {
    title: "包装",
    rows: [
      [
        { label: "操作时间", value: "2025-12-02 15:40:51" },
        { label: "操作人员", value: "三车间包装001" },
      ],
      [
        { label: "机台名称", value: "三车间包装001" },
        { label: "托盘编号", value: "G25X2392253A050300575" },
      ],
    ],
  },
  {
    title: "入库",
    rows: [
      [
        { label: "操作时间", value: "" },
        { label: "操作人员", value: "" },
      ],
      [
        { label: "库位编号", value: "" },
        { label: "出货柜号", value: "" },
      ],
    ],
  },
  {
    title: "检验评审",
    rows: [
      [
        { label: "外观等级", value: "A1" },
        { label: "EL等级", value: "A1" },
      ],
      [
        { label: "不良原因", value: "" },
        { label: "最终等级", value: "A1-1" },
      ],
      [
        { label: "全检不良", value: "" },
        { label: "全检位置", value: "" },
      ],
    ],
  },
  {
    title: "批次扣留",
    rows: [
      [
        { label: "批次扣留备注", value: "" },
        { label: "批次扣留操作人", value: "" },
      ],
      [
        { label: "批次扣留时间", value: "" },
        { label: "", value: "" },
      ],
    ],
  },
];

const onSearch = async () => {
  if (!searchValue.value) return showToast("请输入或扫描条码");
  try {
    loading.value = true;
    const res = await getRoutingSheet(searchValue.value);
    if (res?.ret !== true) {
      showToast(res?.msg || "查询失败");
      return;
    }
    routingSheet.value = {
      id: res?.routing_sheet?.id || "",
      status: res?.routing_sheet?.status || "",
      current_node: res?.routing_sheet?.current_node || "",
      steps: res?.routing_sheet?.steps || [],
    };
    setComponentDetails(res?.component_details);
  } catch (error) {
    const message =
      error?.response?.data?.detail || error?.response?.data?.msg || "查询失败";
    showToast(message);
  } finally {
    loading.value = false;
  }
};

// 扫码获取序列号
const onScan = () => {
  // showToast("调用摄像头扫码...");
  searchValue.value = "251202050231820"; // Mock scan result
  onSearch();
};

// 下载流转单
const downloadSheet = () => {
  showToast("正在下载流转单...");
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
          placeholder="扫描或输入组件序列号"
          @keyup.enter="onSearch"
        />
        <van-icon name="scan" size="24" color="#4364f7" @click="onScan" />
      </div>
    </div>

    <div class="result-section">
      <van-tabs
        v-model:active="activeTab"
        background="transparent"
        color="#4364f7"
        title-active-color="#4364f7"
      >
        <!-- Electronic Routing Sheet -->
        <van-tab title="电子流转单">
          <div class="tab-content">
            <div class="result-card">
              <div class="card-header">
                <span class="title">流转单信息</span>
                <span class="tag success">{{
                  routingSheet.status || "暂无数据"
                }}</span>
              </div>
              <div class="step-progress" v-if="hasSteps">
                <van-steps :active="stepActive" active-color="#4364f7">
                  <van-step v-for="step in routingSheet.steps" :key="step">
                    {{ step }}
                  </van-step>
                </van-steps>
              </div>
              <div class="divider" v-if="hasSteps"></div>
              <div class="routing-table-wrapper">
                <table class="routing-table">
                  <thead>
                    <tr>
                      <th v-for="head in routingSummary.headers" :key="head">
                        {{ head }}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td
                        v-for="(cell, index) in routingSummary.values"
                        :key="`${cell}-${index}`"
                        class="value-cell"
                      >
                        {{ cell || "-" }}
                      </td>
                    </tr>
                  </tbody>
                </table>
                <table class="routing-table routing-detail-table">
                  <tbody>
                    <template
                      v-for="section in routingSections"
                      :key="section.title"
                    >
                      <tr
                        v-for="(row, rowIndex) in section.rows"
                        :key="`${section.title}-${rowIndex}`"
                      >
                        <td
                          v-if="rowIndex === 0"
                          :rowspan="section.rows.length"
                          class="section-cell"
                        >
                          {{ section.title }}
                        </td>
                        <td class="label-cell">{{ row[0].label }}</td>
                        <td class="value-cell">{{ row[0].value || "-" }}</td>
                        <td class="label-cell">{{ row[1].label }}</td>
                        <td class="value-cell">{{ row[1].value || "-" }}</td>
                      </tr>
                    </template>
                  </tbody>
                </table>
              </div>
              <div class="action-btn">
                <van-button
                  round
                  block
                  color="linear-gradient(to right, #4facfe, #00f2fe)"
                  @click="downloadSheet"
                >
                  下载流转单
                </van-button>
              </div>
            </div>
          </div>
        </van-tab>

        <!-- Component Details -->
        <van-tab title="明细报表">
          <div class="tab-content">
            <div class="result-card">
              <div class="card-header">
                <span class="title">组件BOM明细</span>
              </div>
              <div class="info-group">
                <div class="group-title">电性能参数</div>
                <div class="info-grid">
                  <div class="grid-item">
                    <span class="label">最大功率(Pmax)</span>
                    <span class="value">{{
                      displayValue(componentDetails.pmax)
                    }}</span>
                  </div>
                  <div class="grid-item">
                    <span class="label">开路电压(Voc)</span>
                    <span class="value">{{
                      displayValue(componentDetails.voc)
                    }}</span>
                  </div>
                  <div class="grid-item">
                    <span class="label">短路电流(Isc)</span>
                    <span class="value">{{
                      displayValue(componentDetails.isc)
                    }}</span>
                  </div>
                  <div class="grid-item">
                    <span class="label">工作电压(Vmp)</span>
                    <span class="value">{{
                      displayValue(componentDetails.vmp)
                    }}</span>
                  </div>
                  <div class="grid-item">
                    <span class="label">工作电流(Imp)</span>
                    <span class="value">{{
                      displayValue(componentDetails.imp)
                    }}</span>
                  </div>
                  <div class="grid-item">
                    <span class="label">填充因子(FF)</span>
                    <span class="value">{{
                      displayValue(componentDetails.ff)
                    }}</span>
                  </div>
                  <div class="grid-item">
                    <span class="label">转换效率(Eff)</span>
                    <span class="value">{{
                      displayValue(componentDetails.eff)
                    }}</span>
                  </div>
                  <div class="grid-item">
                    <span class="label">环境温度</span>
                    <span class="value">{{
                      displayValue(componentDetails.temp)
                    }}</span>
                  </div>
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
                      <div class="mat-item">
                        <span class="mat-label">型号</span>
                        <span class="mat-value">{{
                          displayValue(item.model)
                        }}</span>
                      </div>
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
        </van-tab>
      </van-tabs>
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

.tag {
  font-size: 12px;
  padding: 4px 8px;
  background: #e8f0fe;
  color: #4364f7;
  border-radius: 4px;
}

.tag.success {
  background: #e6fffa;
  color: #43e97b;
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

/* Step Progress */
.step-progress {
  margin: 8px 0 12px;
}

.routing-table-wrapper {
  width: 100%;
  overflow-x: auto;
}

.routing-table {
  width: 100%;
  min-width: 900px;
  border-collapse: collapse;
  font-size: 12px;
}

.routing-table th,
.routing-table td {
  border: 1px solid #e5e7eb;
  padding: 6px 8px;
  text-align: center;
  vertical-align: middle;
}

.routing-table th {
  background: #f7f8fa;
  color: #333;
  font-weight: 600;
}

.routing-detail-table {
  margin-top: 12px;
}

.section-cell {
  background: #f5f7fa;
  font-weight: 600;
  color: #333;
  width: 80px;
}

.label-cell {
  color: #6b7280;
  width: 140px;
  text-align: left;
}

.value-cell {
  color: #16a34a;
  font-weight: 600;
  text-align: left;
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
