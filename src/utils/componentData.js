// 组件数据规范化工具函数

/**
 * 创建默认的组件明细数据结构
 * @returns {Object} 默认组件明细对象
 */
export function createDefaultComponentDetails() {
  return {
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
  };
}

/**
 * 规范化材料数据
 * @param {Object} material - 材料原始数据
 * @returns {Object} 规范化后的材料数据
 */
export function normalizeMaterial(material = {}) {
  return {
    name: material?.name || "",
    factory: material?.factory || "",
    model: material?.model || "",
  };
}

/**
 * 从多个可能的字段名中获取第一个有效值
 * @param {Object} data - 数据源对象
 * @param {Array<string>} fields - 可能的字段名数组
 * @param {string} defaultValue - 默认值
 * @returns {string} 第一个有效值或默认值
 */
export function getFieldValue(data, fields, defaultValue = "") {
  if (!data || typeof data !== "object") return defaultValue;
  for (const field of fields) {
    if (data[field] !== undefined && data[field] !== null && data[field] !== "") {
      return data[field];
    }
  }
  return defaultValue;
}

/**
 * 设置组件明细数据
 * @param {Object} componentData - 组件数据
 * @param {Object} routingSheetData - 流转单数据
 * @param {string} searchSerialNo - 搜索的序列号
 * @returns {Object} 处理后的组件明细数据
 */
export function setComponentDetails(
  componentData = {},
  routingSheetData = {},
  searchSerialNo = ""
) {
  const defaultDetails = createDefaultComponentDetails();

  return {
    serial_no: getFieldValue(
      componentData,
      ["serial_no", "serialNo"],
      getFieldValue(routingSheetData, ["serial_no", "serialNo"], searchSerialNo)
    ),
    test_date: getFieldValue(componentData, [
      "test_date",
      "testDate",
      "testing_date",
      "testingDate",
    ]),
    power_grade: getFieldValue(componentData, [
      "power_grade",
      "powerGrade",
      "power_level",
      "powerLevel",
    ]),
    current_grade: getFieldValue(componentData, [
      "current_grade",
      "currentGrade",
      "current_level",
      "currentLevel",
    ]),
    el_grade: getFieldValue(componentData, [
      "el_grade",
      "elGrade",
      "el_level",
      "elLevel",
    ]),
    final_grade: getFieldValue(componentData, [
      "final_grade",
      "finalGrade",
      "final_level",
      "finalLevel",
    ]),
    pmax: componentData?.pmax || "",
    voc: getFieldValue(componentData, ["voc", "VOC"]),
    isc: getFieldValue(componentData, ["isc", "ISC"]),
    vmp: getFieldValue(componentData, ["vmp", "VPM", "vpm"]),
    imp: getFieldValue(componentData, ["imp", "IPM", "ipm"]),
    ff: getFieldValue(componentData, ["ff", "FF"]),
    eff: componentData?.eff || "",
    temp: componentData?.temp || "",
    materials: {
      cell: {
        ...normalizeMaterial(componentData?.materials?.cell),
        factory:
          getFieldValue(componentData?.materials?.cell, ["factory"]) ||
          getFieldValue(componentData, ["battery_factory", "batteryFactory"]),
      },
      film: normalizeMaterial(componentData?.materials?.film),
      frame: normalizeMaterial(componentData?.materials?.frame),
      junctionBox: normalizeMaterial(componentData?.materials?.junctionBox),
    },
    business: {
      contract: getFieldValue(componentData?.business, [
        "contract",
        "sales_contract_no",
        "salesContractNo",
      ]),
      customer: getFieldValue(componentData?.business, [
        "customer",
        "customer_name",
      ]),
    },
  };
}

/**
 * 获取查询信息行数据
 * @param {Object} componentDetails - 组件明细数据
 * @returns {Array<Object>} 查询信息行数组
 */
export function getQueryInfoRows(componentDetails) {
  return [
    { label: "组件序列号", value: componentDetails.serial_no },
    { label: "测试日期", value: componentDetails.test_date },
    { label: "功率档位", value: componentDetails.power_grade },
    { label: "电流档位", value: componentDetails.current_grade },
    { label: "EL等级", value: componentDetails.el_grade },
    { label: "最终等级", value: componentDetails.final_grade },
    { label: "Pmax", value: componentDetails.pmax },
    { label: "ISC", value: componentDetails.isc },
    { label: "VOC", value: componentDetails.voc },
    { label: "IPM", value: componentDetails.imp },
    { label: "VPM", value: componentDetails.vmp },
    { label: "FF", value: componentDetails.ff },
  ];
}

/**
 * 获取材料行数据
 * @param {Object} materials - 材料数据
 * @returns {Array<Object>} 材料行数组
 */
export function getMaterialRows(materials) {
  return [
    { label: "电池片", ...materials.cell },
    // { label: "胶膜", ...materials.film },
    // { label: "边框", ...materials.frame },
    // { label: "接线盒", ...materials.junctionBox },
  ];
}
