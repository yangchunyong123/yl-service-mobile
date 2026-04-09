<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { showToast } from "vant";
import { areaList } from "@vant/area-data";
import { createComplaint, getLocalUserInfo } from "@/api";

// 路由实例
const router = useRouter();

// 表单数据
const form = ref({
  handler: "",
  serialNo: "",
  projectName: "",
  location: "",
  isWarranty: "是",
  issueType: "",
  inverterInfo: "",
  processType: "",
  replaceSerialNo: "",
  repairDetails: {
    positive: "无",
    middle: "无",
    negative: "无",
  },
  repairer: "",
});

// 初始化处理人
const localUser = getLocalUserInfo();
form.value.handler = localUser?.lastname || "";

// 弹窗显示控制
const showIssuePicker = ref(false);
const showProcessPicker = ref(false);
const showLocationPicker = ref(false);

// 问题类型选项
const issueTypes = [
  { text: "雷击", value: "lightning" },
  { text: "击穿", value: "breakdown" },
  { text: "碎裂", value: "cracking" },
  { text: "功率异常", value: "power_abnormality" },
  { text: "其他", value: "other" },
];

// 处理类型选项
const processTypes = [
  { text: "维修", value: "repair" },
  { text: "换货", value: "replace" },
  { text: "提供备件", value: "spare" },
  { text: "赔款", value: "refund" },
];

// 地区编码到名称映射
const areaNameMap = {
  ...areaList.province_list,
  ...areaList.city_list,
  ...areaList.county_list,
};

// 选择问题类型，selectedOptions：选中项数组
const onConfirmIssue = ({ selectedOptions }) => {
  form.value.issueType = selectedOptions[0].text;
  showIssuePicker.value = false;
};

// 选择处理类型，selectedOptions：选中项数组
const onConfirmProcess = ({ selectedOptions }) => {
  form.value.processType = selectedOptions[0].text;
  showProcessPicker.value = false;
};

// 选择项目地点，payload：地区选择回调参数
const onConfirmLocation = (payload) => {
  const options = Array.isArray(payload)
    ? payload
    : payload?.selectedOptions || payload?.selectedValues || [];
  if (options.length === 0) {
    form.value.location = "";
    showLocationPicker.value = false;
    return;
  }
  if (typeof options[0] === "string") {
    form.value.location = options
      .map((code) => areaNameMap[code])
      .filter(Boolean)
      .join("/");
    showLocationPicker.value = false;
    return;
  }
  form.value.location = options
    .map((item) => item?.name || item?.text)
    .filter(Boolean)
    .join("/");
  showLocationPicker.value = false;
};

// 提交客诉单
const onSubmit = async () => {
  try {
    const res = await createComplaint({
      handler: form.value.handler,
      serial_no: form.value.serialNo,
      project_name: form.value.projectName,
      location: form.value.location,
      is_warranty: form.value.isWarranty,
      issue_type: form.value.issueType,
      inverter_info: form.value.inverterInfo,
      process_type: form.value.processType,
      replace_serial_no: form.value.replaceSerialNo,
      repair_details: form.value.repairDetails,
      repairer: form.value.repairer,
    });
    if (res?.ret !== true) {
      showToast(res?.msg || "提交失败");
      return;
    }
    showToast("提交成功");
    router.back();
  } catch (error) {
    const message =
      error?.response?.data?.detail || error?.response?.data?.msg || "提交失败";
    showToast(message);
  }
};

// 扫码获取序列号
const onScan = () => {
  showToast("扫码功能待接入");
  form.value.serialNo = "SN202310278888";
};
</script>

<template>
  <div class="complaint-entry-container">
    <van-nav-bar
      title="新建客诉单"
      left-text="返回"
      left-arrow
      @click-left="router.back()"
      class="tech-navbar"
    />

    <van-form @submit="onSubmit" class="entry-form">
      <!-- Basic Info -->
      <div class="form-group">
        <div class="group-title">基础信息</div>
        <van-field v-model="form.handler" label="客诉处理人" readonly />
        <van-field
          v-model="form.serialNo"
          label="组件序列号"
          placeholder="扫码或输入"
          right-icon="scan"
          @click-right-icon="onScan"
          :rules="[{ required: true, message: '必填' }]"
        />
        <van-field
          v-model="form.projectName"
          label="项目名称"
          placeholder="公司+地点+容量+类型"
          :rules="[{ required: true, message: '必填' }]"
        />
        <van-field
          v-model="form.location"
          is-link
          readonly
          label="项目地点"
          placeholder="选择地区"
          @click="showLocationPicker = true"
        />
        <van-popup v-model:show="showLocationPicker" position="bottom">
          <van-area
            :area-list="areaList"
            :columns-num="3"
            @confirm="onConfirmLocation"
            @cancel="showLocationPicker = false"
          />
        </van-popup>
      </div>

      <!-- Judgment Info -->
      <div class="form-group">
        <div class="group-title">判定信息</div>
        <van-field name="isWarranty" label="是否质保">
          <template #input>
            <van-radio-group v-model="form.isWarranty" direction="horizontal">
              <van-radio name="是">是</van-radio>
              <van-radio name="否">否</van-radio>
            </van-radio-group>
          </template>
        </van-field>
        <van-field
          v-model="form.issueType"
          is-link
          readonly
          label="问题种类"
          placeholder="选择问题种类"
          @click="showIssuePicker = true"
        />
        <van-popup v-model:show="showIssuePicker" position="bottom">
          <van-picker
            :columns="issueTypes"
            @confirm="onConfirmIssue"
            @cancel="showIssuePicker = false"
          />
        </van-popup>
        <van-field
          v-model="form.inverterInfo"
          label="方阵记录"
          placeholder="逆变器信息"
        />
      </div>

      <!-- Processing Info -->
      <div class="form-group">
        <div class="group-title">处理信息</div>
        <van-field
          v-model="form.processType"
          is-link
          readonly
          label="处理类型"
          placeholder="选择处理类型"
          @click="showProcessPicker = true"
        />
        <van-popup v-model:show="showProcessPicker" position="bottom">
          <van-picker
            :columns="processTypes"
            @confirm="onConfirmProcess"
            @cancel="showProcessPicker = false"
          />
        </van-popup>
        <van-field
          v-if="form.processType === '换货'"
          v-model="form.replaceSerialNo"
          label="换货序列号"
          placeholder="扫码或输入"
          right-icon="scan"
        />
      </div>

      <!-- Repair Details -->
      <div class="form-group">
        <div class="group-title">维修详情</div>
        <van-cell title="正极处理" center>
          <template #right-icon>
            <van-radio-group
              v-model="form.repairDetails.positive"
              direction="horizontal"
            >
              <van-radio name="无">无</van-radio>
              <van-radio name="更换">更换</van-radio>
            </van-radio-group>
          </template>
        </van-cell>
        <van-cell title="中间处理" center>
          <template #right-icon>
            <van-radio-group
              v-model="form.repairDetails.middle"
              direction="horizontal"
            >
              <van-radio name="无">无</van-radio>
              <van-radio name="更换">更换</van-radio>
            </van-radio-group>
          </template>
        </van-cell>
        <van-cell title="负极处理" center>
          <template #right-icon>
            <van-radio-group
              v-model="form.repairDetails.negative"
              direction="horizontal"
            >
              <van-radio name="无">无</van-radio>
              <van-radio name="更换">更换</van-radio>
            </van-radio-group>
          </template>
        </van-cell>
        <van-field
          v-model="form.repairer"
          label="维修人"
          placeholder="请输入维修人姓名"
        />
      </div>

      <div class="submit-btn">
        <van-button
          round
          block
          type="primary"
          native-type="submit"
          color="linear-gradient(to right, #0052d4, #4364f7)"
        >
          提交客诉单
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<style scoped>
.complaint-entry-container {
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

.entry-form {
  padding: 16px;
}

.form-group {
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
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 4px solid #4364f7;
}

:deep(.van-cell) {
  padding-left: 0;
  padding-right: 0;
}

:deep(.van-field__label) {
  width: 6em;
  color: #666;
}

.submit-btn {
  margin-top: 32px;
}
</style>
