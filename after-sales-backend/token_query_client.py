# 导入必要的标准库模块
# json: 用于 JSON 数据的序列化和反序列化
# os: 用于操作系统相关功能，如环境变量读取
# typing: 提供类型提示支持
import json
import os
import sys
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Optional, Tuple

# 导入 requests 库用于 HTTP 请求
import requests

# 配置默认 API 端点 URL
# 使用环境变量允许在不同部署环境中灵活配置
# 如果环境变量未设置，则使用默认值
LOGIN_URL = os.getenv("TRACE_LOGIN_URL", "http://172.25.1.29:8300/api/login/")
REFRESH_URL = os.getenv("TRACE_REFRESH_URL", "http://172.25.1.29:8300/token/refresh/")
QUERY_URL = os.getenv("TRACE_QUERY_URL", "http://172.25.1.29:8300/api/suyuan-query/?query_params=")
AUTH_SCHEME = os.getenv("TRACE_AUTH_SCHEME", "JWTYF")


def _http_request(
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
        timeout: int = 600,
) -> Tuple[int, Dict[str, str], str]:
    """
    发送 HTTP 请求并返回状态码、响应头与文本内容。
    
    参数:
        url: 请求的目标 URL
        method: HTTP 方法，默认为 GET
        headers: 请求头字典，可选
        body: 请求体数据（字典格式），可选
        timeout: 请求超时时间（秒），默认 15 秒
    
    返回:
        tuple: (状态码，响应头字典，响应内容字符串)
    """
    # 初始化请求头，如果未提供则使用空字典
    request_headers = headers or {}
    
    try:
        # 根据请求方法发送请求
        if method.upper() == "GET":
            response = requests.get(url, headers=request_headers, timeout=timeout)
        elif method.upper() == "POST":
            # 如果有请求体数据，使用 json 参数自动序列化
            if body is not None:
                response = requests.post(url, json=body, headers=request_headers, timeout=timeout)
            else:
                response = requests.post(url, headers=request_headers, timeout=timeout)
        else:
            # 支持其他 HTTP 方法
            response = requests.request(method.upper(), url, json=body, headers=request_headers, timeout=timeout)
        
        # 提取响应信息
        status = response.status_code
        resp_headers = dict(response.headers)
        content = response.text
        
        return status, resp_headers, content
    
    except requests.exceptions.RequestException as e:
        # 处理请求异常（网络错误、超时等）
        # 尝试从异常中提取响应信息
        if hasattr(e, 'response') and e.response is not None:
            return e.response.status_code, dict(e.response.headers), e.response.text
        # 没有响应时返回 0 状态码
        return 0, {}, str(e)


def _parse_json(text: str) -> Dict[str, Any]:
    """
    解析 JSON 文本，解析失败时返回空字典。
    
    参数:
        text: 待解析的 JSON 格式字符串
    
    返回:
        dict: 解析后的字典对象，失败时返回空字典
    """
    # 空文本直接返回空字典
    if not text:
        return {}
    try:
        # 尝试解析 JSON 字符串
        return json.loads(text)
    except json.JSONDecodeError:
        # JSON 格式错误时返回空字典，避免程序崩溃
        return {}


def _build_query_url(base_url: str, query_params: str) -> str:
    """
    拼接查询参数并返回完整查询 URL。
    
    参数:
        base_url: 基础 URL（可能以等号结尾或不带等号）
        query_params: 需要编码的查询参数字符串
    
    返回:
        str: 完整的查询 URL
    """
    # 检查 URL 是否已包含等号，决定拼接方式
    if base_url.endswith("="):
        # URL 已有等号，直接拼接编码后的参数
        from urllib.parse import quote
        return f"{base_url}{quote(query_params, safe='')}"
    # URL 没有等号，需要添加 query_params=前缀
    from urllib.parse import quote
    encoded = quote(query_params, safe="")
    return f"{base_url}?query_params={encoded}"


def login(username: str, password: str) -> Tuple[str, str]:
    """
    使用用户名密码登录并返回 access 与 refresh token。
    
    参数:
        username: 用户名
        password: 密码
    
    返回:
        tuple: (access_token, refresh_token)
    
    异常:
        RuntimeError: 登录失败时抛出
    """
    # 发送 POST 请求到登录接口
    status, _, content = _http_request(
        LOGIN_URL,
        method="POST",
        body={"username": username, "password": password},
    )
    # 解析响应 JSON
    data = _parse_json(content)
    # 验证响应状态和数据完整性
    if status != 200:
        message = data.get("message") or data.get("msg") or content or "登录失败"
        raise RuntimeError(f"登录失败：{message}")
    # API 返回格式为 {code: 2000, msg: '请求成功', data: {...}}
    # 需要从 data 字段中提取 access 和 refresh token
    response_data = data.get("data", {})
    if "access" not in response_data or "refresh" not in response_data:
        message = data.get("message") or data.get("msg") or content or "登录失败"
        raise RuntimeError(f"登录失败：{message}")
    # 返回 access 和 refresh token
    return response_data["access"], response_data["refresh"]


def refresh_access(refresh_token: str) -> Optional[str]:
    """
    使用 refresh token 获取新的 access token，失败时返回 None。
    
    参数:
        refresh_token: 刷新令牌
    
    返回:
        str or None: 新的 access token，失败时返回 None
    """
    # 发送 POST 请求到 token 刷新接口
    status, _, content = _http_request(
        REFRESH_URL,
        method="POST",
        body={"refresh": refresh_token},
    )
    # 解析响应 JSON
    data = _parse_json(content)
    # 检查刷新是否成功
    if status == 200 and "access" in data:
        return data["access"]
    # API 返回格式可能为 {code: 2000, msg: '请求成功', data: {access: ...}}
    # 尝试从 data 字段中提取
    response_data = data.get("data", {})
    if status == 200 and "access" in response_data:
        return response_data["access"]
    # 刷新失败返回 None
    return None


def _is_auth_error(status: int, payload: Dict[str, Any], raw_text: str) -> bool:
    """
    判断响应是否为认证失败或 token 失效。
    
    参数:
        status: HTTP 响应状态码
        payload: 解析后的 JSON 响应数据
        raw_text: 原始响应文本
    
    返回:
        bool: 是否为认证错误
    """
    # 401 未授权和 403 禁止访问直接判定为认证错误
    if status in {401, 403}:
        return True
    # 从响应中提取错误消息
    msg = str(payload.get("msg") or payload.get("detail") or raw_text)
    # 定义认证相关的关键词列表
    keywords = ["身份认证", "认证", "token", "令牌", "未提供", "无效", "过期"]
    # 检查消息中是否包含认证相关关键词
    return any(key in msg for key in keywords)


def query_data(query_params: str, access_token: str) -> Dict[str, Any]:
    """
    使用 access token 调用查询接口并返回解析后的 JSON。
    
    参数:
        query_params: 查询参数字符串
        access_token: 访问令牌
    
    返回:
        dict: 查询结果数据
    
    异常:
        PermissionError: token 失效时抛出
        RuntimeError: 其他查询错误时抛出
    """
    # 构建完整的查询 URL
    url = _build_query_url(QUERY_URL, query_params)
    # 发送带认证的 GET 请求
    status, _, content = _http_request(
        url,
        method="GET",
        headers={"Authorization": f"{AUTH_SCHEME} {access_token}"},
    )
    # 解析响应 JSON
    data = _parse_json(content)

    # 检查是否为认证错误
    if _is_auth_error(status, data, content):
        raise PermissionError("access token 失效或认证失败")
    # 检查其他 HTTP 错误
    if status >= 400:
        raise RuntimeError(content or "查询失败")
    return data


def _init_django() -> None:
    """
    初始化 Django 环境以便脚本中使用 ORM。
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    import django

    # 检查 Django 是否已初始化，避免重复调用 django.setup()
    from django.conf import settings
    if not settings.configured:
        django.setup()





def _coerce_field_value(field: Any, value: Any) -> Any:
    """
    将原始值转换为模型字段可接受的类型。
    """
    from django.db import models
    from django.utils.dateparse import parse_date, parse_datetime

    if value is None:
        return None
    if isinstance(field, models.DateTimeField):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            parsed = parse_datetime(value) or parse_date(value)
            if isinstance(parsed, datetime):
                return parsed
            if parsed:
                return datetime.combine(parsed, datetime.min.time())
        return None
    if isinstance(field, models.DecimalField):
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float, str)):
            try:
                return Decimal(str(value))
            except Exception:
                return None
    return value


def _map_record_to_model_fields(record: Dict[str, Any], model_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据模型字段映射并过滤记录字段。
    支持中文字段到英文模型字段的映射。
    """
    # 构建中文字段到英文字段的映射关系
    chinese_to_english_map = {
        "代工基地": "base",
        "销售合同号": "sales_contract_number",
        "客户": "customer",
        "托盘号": "pallet_number",
        "组件序列号": "component_serial_number",
        "组件条码": "component_serial_number",
        "订单号": "order_number",
        "工单号": "work_order_number",
        "委外申请单号": "component_warehouse_entry_request_number",
        "组件入库申请单号": "component_warehouse_entry_request_number",
        "发货通知单号": "delivery_notice_number",
        "组件柜号": "component_container_number",
        "产品物料编码1": "product_code",
        "profile": "base",
        "组件状态": "component_status",
        "组件颜色": "component_color",
        "绝缘耐压": "insulation_withstand_voltage",
        "外观等级": "appearance_grade",
        "el 等级": "el_grade",
        "最终等级": "final_grade",
        "功率档": "power_gear",
        "最大功率档": "power_gear",
        "电流挡位": "current_gear",
        "当前站点": "current_station",
        "生码时间": "creation_time",
        "包装时间": "packaging_time",
        "ab 胶规格": "ab_glue_spec",
        "ab 胶供应商": "ab_glue_supplier",
        "ab 胶批次号": "ab_glue_batch_number",
        "ab 胶物料编码": "ab_glue_material_code",
        "ab 胶扣料时间": "ab_glue_deduction_time",
        "ab 胶类别": "ab_glue_category",
        "a 胶规格": "a_glue_spec",
        "a 胶供应商": "a_glue_supplier",
        "a 胶批次号": "a_glue_batch_number",
        "a 胶物料编码": "a_glue_material_code",
        "a 胶扣料时间": "a_glue_deduction_time",
        "a 胶类别": "a_glue_category",
        "b 胶规格": "b_glue_spec",
        "b 胶供应商": "b_glue_supplier",
        "b 胶批次号": "b_glue_batch_number",
        "b 胶物料编码": "b_glue_material_code",
        "b 胶扣料时间": "b_glue_deduction_time",
        "b 胶类别": "b_glue_category",
        "背板规格": "backsheet_spec",
        "背板供应商": "backsheet_supplier",
        "背板批次号": "backsheet_batch_number",
        "背板物料编号": "backsheet_material_code",
        "背板扣料时间": "backsheet_deduction_time",
        "背板颜色": "backsheet_color",
        "背板长度": "backsheet_length",
        "背板宽度": "backsheet_width",
        "背板厚度": "backsheet_thickness",
        "背板门幅": "backsheet_door_amplitude",
        "电池片规格": "battery_spec",
        "电池片供应商": "battery_supplier",
        "电池片批次号": "battery_batch_number",
        "电池片物料编号": "battery_material_code",
        "电池片扣料时间": "battery_deduction_time",
        "电池片颜色": "battery_color",
        "电池片效率": "battery_efficiency",
        "电池片等级": "battery_grade",
        "电池片面积": "battery_area",
        "电池片尺寸": "battery_size",
        "电池片类型": "battery_type",
        "单片功率": "single_power",
        "晶体结构": "crystal_structure",
        "eva 规格": "eva_spec",
        "eva 供应商": "eva_supplier",
        "eva 批次号": "eva_batch_number",
        "eva 物料编码": "eva_material_code",
        "eva 扣料时间": "eva_deduction_time",
        "eva 颜色": "eva_color",
        "eva 宽度": "eva_width",
        "eva 长度": "eva_length",
        "eva 门幅": "eva_door_amplitude",
        "eva 厚度": "eva_thickness",
        "高透 eva 规格": "high_transparency_eva_spec",
        "高透 eva 供应商": "high_transparency_eva_supplier",
        "高透 eva 批次号": "high_transparency_eva_batch_number",
        "高透 eva 物料编码": "high_transparency_eva_material_code",
        "高透 eva 扣料时间": "high_transparency_eva_deduction_time",
        "高透 eva 颜色": "high_transparency_eva_color",
        "高透 eva 宽度": "high_transparency_eva_width",
        "高透 eva 长度": "high_transparency_eva_length",
        "高透 eva 门幅": "high_transparency_eva_door_amplitude",
        "高透 eva 厚度": "high_transparency_eva_thickness",
        "白膜 eva 规格": "white_film_eva_spec",
        "白膜 eva 供应商": "white_film_eva_supplier",
        "白膜 eva 批次号": "white_film_eva_batch_number",
        "白膜 eva 物料编码": "white_film_eva_material_code",
        "白膜 eva 扣料时间": "white_film_eva_deduction_time",
        "玻璃规格": "glass_spec",
        "玻璃供应商": "glass_supplier",
        "玻璃批次号": "glass_batch_number",
        "玻璃物料编号": "glass_material_code",
        "玻璃扣料时间": "glass_deduction_time",
        "玻璃长度": "glass_length",
        "玻璃宽度": "glass_width",
        "玻璃尺寸": "glass_size",
        "玻璃厚度": "glass_thickness",
        "焊接过站时间": "welding_station_time",
        "焊接过站机台": "welding_station_machine",
        "焊接车间": "welding_workshop",
        "焊接产线": "welding_production_line",
        "焊接人员": "welding_operator",
        "焊接班组": "welding_team",
        "叠层过站时间": "lamination_station_time",
        "叠层过站机台": "lamination_station_machine",
        "叠层车间": "lamination_workshop",
        "叠层产线": "lamination_production_line",
        "叠层人员": "lamination_operator",
        "叠层班组": "lamination_team",
        "层压过站时间": "pressing_station_time",
        "层压过站机台": "pressing_station_machine",
        "层压车间": "pressing_workshop",
        "层压产线": "pressing_production_line",
        "层压人员": "pressing_operator",
        "层压班组": "pressing_team",
        "层压位置": "pressing_position",
        "层压温度设定值": "pressing_temperature_setting",
        "层压时间设定值": "pressing_time_setting",
        "下充气时间设定值": "lower_inflation_time_setting",
        "抽真空时间设定值": "vacuum_time_setting",
        "上真空延时时间设定值": "upper_vacuum_delay_setting",
        "加压 1 延时设定值": "pressure_1_delay_setting",
        "加压 1 压力设定值": "pressure_1_pressure_setting",
        "加压 2 延时设定加压": "pressure_2_delay_setting",
        "加压 2 压力设定값": "pressure_2_pressure_setting",
        "加压 3 延时设定加压": "pressure_3_delay_setting",
        "加压 3 压力设定값": "pressure_3_pressure_setting",
        "装框过站时间": "framing_station_time",
        "装框过站机台": "framing_station_machine",
        "装框车间": "framing_workshop",
        "装框产线": "framing_production_line",
        "装框人员": "framing_operator",
        "装框班组": "framing_team",
        "qel 测试时间": "qel_test_time",
        "qel 机台": "qel_machine",
        "qel 车间": "qel_workshop",
        "qel 产线": "qel_production_line",
        "qel 人员": "qel_operator",
        "qel 班组": "qel_team",
        "qel 等级": "qel_grade",
        "hel 测试时间": "hel_test_time",
        "hel 机台": "hel_machine",
        "hel 车间": "hel_workshop",
        "hel 产线": "hel_production_line",
        "hel 人员": "hel_operator",
        "hel 班组": "hel_team",
        "hel 等级": "hel_grade",
        "iv 测试时间": "iv_test_time",
        "iv 机台": "iv_machine",
        "iv 车间": "iv_workshop",
        "iv 产线": "iv_production_line",
        "iv 人员": "iv_operator",
        "iv 班组": "iv_team",
        "pmax": "pmax",
        "voc": "voc",
        "isc": "isc",
        "vpm": "vpm",
        "ipm": "ipm",
        "ff": "ff",
        "eff": "eff",
        "rs": "rs",
        "rsh": "rsh",
        "ref": "ref",
        "std_isc": "std_isc",
        "表面温度": "surface_temperature",
        "环境温度": "environment_temperature",
        # 溯源信息
        "是否可溯源": "is_traceable",
        "仓库收货批次号": "warehouse_receipt_batch_number",
        "供应商批次号": "supplier_batch_number",
        "ncc 采购入库单号": "ncc_purchase_inbound_number",
        "ncc采购入库单号": "ncc_purchase_inbound_number",  # 无空格版本
        "原厂供应商": "original_supplier",
        "oa通知明细行号": "oa_notification_detail_line_number",
        "OA通知明细行号": "oa_notification_detail_line_number",  # 支持大写 OA
        "oa通知明细行号": "oa_notification_detail_line_number",  # 无空格版本
        "OA通知明细行号": "oa_notification_detail_line_number",  # 大写 OA 无空格
        "oa到货通知单号": "oa_arrival_notice_number",
        "OA到货通知单号": "oa_arrival_notice_number",  # 支持大写 OA
        "oa到货通知单号": "oa_arrival_notice_number",  # 无空格版本
        "OA到货通知单号": "oa_arrival_notice_number",  # 大写 OA 无空格
        "材料母批号": "material_parent_batch_number",
    }
    
    # 创建规范化字段映射（同时包含英文和中文）
    normalized_fields = {name.lower(): name for name in model_fields.keys()}
    result: Dict[str, Any] = {}
    
    for key, value in record.items():
        target_key = None
        key_str = str(key)
        key_lower = key_str.lower()
        
        # 先尝试直接匹配（英文字段）
        if key_lower in normalized_fields:
            target_key = normalized_fields[key_lower]
        # 再尝试中文映射（精确匹配）
        elif key_lower in chinese_to_english_map:
            english_field = chinese_to_english_map[key_lower]
            if english_field in model_fields:
                target_key = english_field
        # 如果还没匹配到，尝试去除空格后匹配（处理中英文混排的空格差异）
        else:
            # 移除所有空格后再匹配
            key_no_space = key_lower.replace(" ", "")
            if key_no_space in chinese_to_english_map:
                english_field = chinese_to_english_map[key_no_space]
                if english_field in model_fields:
                    target_key = english_field
        
        if target_key:
            result[target_key] = _coerce_field_value(model_fields[target_key], value)
    
    # 如果没有找到组件序列号，尝试使用别名映射
    if "component_serial_number" not in result:
        alias_map = {
            "component_serial": "component_serial_number",
            "componentserial": "component_serial_number",
            "component_serial_no": "component_serial_number",
            "component_sn": "component_serial_number",
        }
        for alias, target in alias_map.items():
            if alias in record and target in model_fields:
                result[target] = _coerce_field_value(model_fields[target], record[alias])
                break
    
    return result


def _extract_gz_data_and_base(result: Any) -> Tuple[Iterable[Dict[str, Any]], Optional[str]]:
    """
    从返回结构中提取 gz_data 记录与基地字段。
    支持三种数据结构：
    1. {"data": {"gz_data": [...], "jd": "..."}}
    2. {"code": 200, "jh_data": {"gz_data": [...], "jd": "...", "zj_status": "..."}}
    3. {"xs_data": [...], "jh_data": {...}} (xs_data 在顶层)
    """
    if isinstance(result, dict):
        # 尝试从顶层直接获取 xs_data
        xs_data = result.get("xs_data")
        # 尝试从顶层直接获取 dg_data（代工数据）
        dg_data = result.get("dg_data")
        
        # 尝试从 data 字段获取（旧格式）
        data = result.get("data")
        if not data:
            # 尝试从 jh_data 字段获取（新格式）
            data = result.get("jh_data")
        
        records = []
        base = None
        
        # 优先处理顶层 dg_data 结构
        if isinstance(dg_data, list):
            records = [item for item in dg_data if isinstance(item, dict)]
            if records:
                base = records[0].get("代工基地") or records[0].get("基地") or records[0].get("jd")
        
        # 如果找到了 data/jh_data 对象
        if isinstance(data, dict) and not records:
            gz_data = data.get("gz_data")
            base = data.get("jd")
            dg_data = data.get("dg_data")
            
            # 提取 gz_data 记录
            if isinstance(gz_data, list):
                records = [item for item in gz_data if isinstance(item, dict)]
            
            # 兼容 data/dg_data 结构
            if isinstance(dg_data, list):
                records = [item for item in dg_data if isinstance(item, dict)]
                if records:
                    base = records[0].get("代工基地") or records[0].get("基地") or base
            
            # 新增：提取 wms_data（电池片溯源信息）
            wms_data = data.get("wms_data")
            if isinstance(wms_data, list):
                # wms_data 是数组结构，需要筛选 title 为"电池片"的对象
                for idx, item in enumerate(wms_data):
                    if isinstance(item, dict):
                        title = item.get("title", "")
                
                # 筛选 title 为"电池片"的对象
                battery_chip_data = None
                for item in wms_data:
                    if isinstance(item, dict) and item.get("title") == "电池片":
                        battery_chip_data = item
                        break
                
                if battery_chip_data:
                    # 提取 fields
                    fields = battery_chip_data.get("fields")
                    if isinstance(fields, list) and len(fields) > 0:
                        # 将 wms_data 的 fields 合并到记录中
                        wms_info = fields[0] if isinstance(fields[0], dict) else {}
                        if records:
                            # 合并到每条记录
                            for record in records:
                                record.update(wms_info)
                        else:
                            # 如果没有其他记录，直接使用 wms_info 作为记录
                            records = [wms_info]
            elif isinstance(wms_data, dict):
                # wms_data 可能包含 title 和 fields
                fields = wms_data.get("fields")
                if isinstance(fields, list) and len(fields) > 0:
                    # 将 wms_data 的 fields 合并到记录中
                    wms_info = fields[0] if isinstance(fields[0], dict) else {}
                    if records:
                        # 合并到每条记录
                        for record in records:
                            record.update(wms_info)
                    else:
                        # 如果没有其他记录，直接使用 wms_info 作为记录
                        records = [wms_info]
        
        # 如果存在 xs_data，将其字段合并到记录中
        if isinstance(xs_data, list) and len(xs_data) > 0:
            # 取 xs_data 的第一个对象作为销售数据
            xs_record = xs_data[0] if isinstance(xs_data[0], dict) else {}
            # 将 xs_data 的字段添加到每条记录中
            if records:
                for record in records:
                    record.update(xs_record)
            else:
                # 如果没有其他记录，直接使用 xs_data 作为记录
                records = [xs_record]
        
        return records, base if isinstance(base, str) else None
    return [], None


def save_query_result_to_db(result: Any, query_params: str = "") -> int:
    """
    将查询结果保存到产品溯源表中并返回写入数量。
    
    参数:
        result: 查询结果数据，可以是任何包含记录的可迭代对象
        query_params: 查询参数
        
    返回:
        int: 成功保存的记录数量
        
    功能说明:
        1. 初始化 Django 环境
        2. 获取 ProductTraceability 模型的所有字段信息
        3. 提取查询结果中的记录
        4. 使用事务批量处理数据
        5. 对每条记录进行字段映射
        6. 根据组件序列号判断是否已存在
        7. 存在则更新，不存在则创建新记录
        8. 统计保存的记录数量
    """
    # 初始化 Django 环境，确保可以访问 Django 模型和数据库
    _init_django()
    
    # 导入 Django 事务管理模块，用于保证数据一致性
    from django.db import transaction
    
    # 导入产品溯源数据模型
    from apps.traceability.models import ProductTraceability

    # 获取 ProductTraceability 模型的所有字段信息，用于后续字段映射
    # _meta.fields 包含模型定义的所有数据库字段对象
    model_fields = {field.name: field for field in ProductTraceability._meta.fields}
    
    gz_records, base_value = _extract_gz_data_and_base(result)
    records = list(gz_records)
    
    # 初始化保存计数器，用于统计成功保存的记录数量
    saved_count = 0
    new_count = 0
    update_count = 0
    
    # 使用事务原子性操作，确保所有记录要么全部保存成功，要么全部回滚
    # 这样可以避免部分数据保存失败导致的数据不一致问题
    with transaction.atomic():
        # 遍历所有提取的记录
        for record in records:
            # 将记录字段映射到模型字段
            # _map_record_to_model_fields 会将输入记录的字段名转换为模型字段名
            mapped = _map_record_to_model_fields(record, model_fields)
            if base_value and "base" in model_fields and "base" not in mapped:
                mapped["base"] = _coerce_field_value(model_fields["base"], base_value)
            
            # 获取组件序列号，这是唯一标识符，用于判断记录是否存在
            component_serial = mapped.get("component_serial_number")
            
            # 如果组件序列号为空，跳过该记录（不保存无效数据）
            if not component_serial:
                continue
            
            # 构建更新字典，排除组件序列号（因为它是查询条件）
            # defaults 中的字段会在 update_or_create 中用于更新或插入
            defaults = {k: v for k, v in mapped.items() if k != "component_serial_number"}
            
            # 执行更新或创建操作：
            # - 如果 component_serial_number 已存在，则用 defaults 更新该记录
            # - 如果不存在，则创建新记录，component_serial_number + defaults
            obj, created = ProductTraceability.objects.update_or_create(
                component_serial_number=component_serial,
                defaults=defaults,
            )
            
            # 每成功保存一条记录，计数器加 1 并打印信息
            saved_count += 1
            if created:
                print(f"[新增] {component_serial}")
                new_count += 1
            else:
                print(f"[更新] {component_serial}")
                update_count += 1
    
    # 返回成功保存的记录总数
    print(f"\n数据保存统计：新增 {new_count} 条，更新 {update_count} 条，共 {saved_count} 条")
    return saved_count


def save_query_result_to_db_with_check(result: Any, query_params: str = "") -> Tuple[int, int, int]:
    """
    将查询结果保存到产品溯源表中，返回保存数量和新增/更新数量。
    
    参数:
        result: 查询结果数据
        query_params: 查询参数
        
    返回:
        tuple: (总保存数，新增数，更新数)
    """
    # 初始化 Django 环境，确保可以访问 Django 模型和数据库
    _init_django()
    
    # 导入 Django 事务管理模块，用于保证数据一致性
    from django.db import transaction
    
    # 导入产品溯源数据模型
    from apps.traceability.models import ProductTraceability

    # 获取 ProductTraceability 模型的所有字段信息，用于后续字段映射
    model_fields = {field.name: field for field in ProductTraceability._meta.fields}
    
    gz_records, base_value = _extract_gz_data_and_base(result)
    records = list(gz_records)
    
    # 初始化计数器
    saved_count = 0
    new_count = 0
    update_count = 0
    
    # 使用事务原子性操作
    with transaction.atomic():
        # 遍历所有提取的记录
        for record in records:
            # 将记录字段映射到模型字段
            mapped = _map_record_to_model_fields(record, model_fields)
            if base_value and "base" in model_fields and "base" not in mapped:
                mapped["base"] = _coerce_field_value(model_fields["base"], base_value)
            
            # 获取组件序列号
            component_serial = mapped.get("component_serial_number")
            
            # 如果组件序列号为空，跳过该记录
            if not component_serial:
                continue
            
            # 检查该 component_serial_number 是否已存在
            exists = ProductTraceability.objects.filter(
                component_serial_number=component_serial
            ).exists()
            
            # 如果已存在，跳过不保存
            if exists:
                update_count += 1  # 已存在的算作更新
                print(f"[跳过] {component_serial} 已存在")
                continue
            
            # 构建保存字典
            save_data = {k: v for k, v in mapped.items() if k != "component_serial_number"}
            
            # 创建新记录
            ProductTraceability.objects.create(
                component_serial_number=component_serial,
                **save_data
            )
            
            saved_count += 1
            new_count += 1
            print(f"[新增] {component_serial}")
    
    return saved_count, new_count, update_count


def get_self_produced_product_codes() -> List[str]:
    """
    获取 SelfProducedProduct 表中的 product_code 列表。
    """
    _init_django()
    from apps.traceability.models import SelfProducedProduct

    queryset = (
        SelfProducedProduct.objects.exclude(product_code__isnull=True)
        .exclude(product_code__exact="")
        .values_list("product_code", flat=True)
        .distinct()
    )
    return list(queryset)


def get_oem_component_barcodes() -> List[str]:
    """
    获取 OEMProduct 表中的 component_barcode 列表。
    """
    _init_django()
    from apps.traceability.models import OEMProduct
    
    queryset = (
        OEMProduct.objects.exclude(component_barcode__isnull=True)
        .exclude(component_barcode__exact="")
        .values_list("component_barcode", flat=True)
        .distinct()
    )
    return list(queryset)


def find_missing_product_codes_in_traceability() -> List[str]:
    """
    对比 SelfProducedProduct.product_code 与 ProductTraceability.component_serial_number。
    返回在 ProductTraceability 中不存在的 product_code 列表。
    """
    _init_django()
    from apps.traceability.models import ProductTraceability, SelfProducedProduct

    # 获取 SelfProducedProduct 的 product_code 列表
    product_codes = list(
        SelfProducedProduct.objects.exclude(product_code__isnull=True)
        .exclude(product_code__exact="")
        .values_list("product_code", flat=True)
        .distinct()
    )

    if not product_codes:
        return []

    # 查询 ProductTraceability 中存在的 component_serial_number
    existing_serials = set(
        ProductTraceability.objects.filter(
            component_serial_number__in=product_codes
        ).values_list("component_serial_number", flat=True)
    )

    # 找出缺失的 product_code
    missing_codes = [code for code in product_codes if code not in existing_serials]
    return missing_codes


def batch_query_and_save(product_codes: Iterable[str], username: str, password: str) -> int:
    """
    批量调用接口并保存到 ProductTraceability 表。
    优化逻辑：先检查 product_code 是否存在，只查询不存在的记录
    """
    _init_django()
    from apps.traceability.models import ProductTraceability
    
    # 转换为列表以便多次遍历
    product_codes_list = list(product_codes)
    total_product_codes = len(product_codes_list)
    print(f"共 {total_product_codes} 个产品编号需要处理")
    
    existing_product_codes = set(
        ProductTraceability.objects.filter(
            product_code__in=product_codes_list
        ).values_list("product_code", flat=True)
    )
    print(f"数据库中已存在 {len(existing_product_codes)} 条产品编号记录")
    
    # 筛选出需要查询的产品编号（组件序列号不存在的）
    codes_to_query = []
    skipped_count = 0
    
    for product_code in product_codes_list:
        if product_code in existing_product_codes:
            skipped_count += 1
            print(f"[跳过] 产品编号 {product_code} 已存在")
        else:
            codes_to_query.append(product_code)
    
    print(f"\n需要调用接口的产品编号数：{len(codes_to_query)}")
    print(f"跳过的产品编号数：{skipped_count}")
    
    # 如果没有需要查询的，直接返回
    if not codes_to_query:
        print("所有记录都已存在，无需调用接口")
        return 0
    
    # 登录获取 token
    access_token, refresh_token = login(username, password)
    total_saved = 0
    query_count = 0
    
    for idx, product_code in enumerate(codes_to_query, start=1):
        try:
            print(f"[{idx}/{len(codes_to_query)}] 正在查询产品编号：{product_code}")
            result = query_data(product_code, access_token)
            query_count += 1
        except PermissionError:
            new_access = refresh_access(refresh_token)
            if new_access:
                access_token = new_access
                try:
                    result = query_data(product_code, access_token)
                    query_count += 1
                except PermissionError:
                    access_token, refresh_token = login(username, password)
                    result = query_data(product_code, access_token)
                    query_count += 1
            else:
                access_token, refresh_token = login(username, password)
                result = query_data(product_code, access_token)
                query_count += 1
        
        # 保存查询结果
        saved = save_query_result_to_db(result, product_code)
        total_saved += saved
    
    print(f"\n处理完成统计:")
    print(f"总产品编号数：{total_product_codes}")
    print(f"实际调用接口数：{query_count}")
    print(f"成功保存/更新记录数：{total_saved}")
    print(f"跳过记录数：{skipped_count}")
    
    return total_saved


def batch_query_and_save_oem(component_barcodes: Iterable[str], username: str, password: str) -> int:
    """
    批量调用接口并保存 OEM 组件条码数据到 ProductTraceability 表。
    优化逻辑：先检查 component_serial_number 是否存在，只查询不存在的记录。
    """
    _init_django()
    from apps.traceability.models import ProductTraceability
    
    # 转换为列表以便多次遍历
    component_barcodes_list = list(component_barcodes)
    total_component_barcodes = len(component_barcodes_list)
    print(f"共 {total_component_barcodes} 个组件条码需要处理")
    
    # 查询已存在的组件序列号，避免重复调用接口
    existing_component_barcodes = set(
        ProductTraceability.objects.filter(
            component_serial_number__in=component_barcodes_list
        ).values_list("component_serial_number", flat=True)
    )
    print(f"数据库中已存在 {len(existing_component_barcodes)} 条组件条码记录")
    
    # 筛选出需要查询的组件条码
    codes_to_query = []
    skipped_count = 0
    
    for component_barcode in component_barcodes_list:
        if component_barcode in existing_component_barcodes:
            skipped_count += 1
            print(f"[跳过] 组件条码 {component_barcode} 已存在")
        else:
            codes_to_query.append(component_barcode)
    
    print(f"\n需要调用接口的组件条码数：{len(codes_to_query)}")
    print(f"跳过的组件条码数：{skipped_count}")
    
    # 如果没有需要查询的，直接返回
    if not codes_to_query:
        print("所有记录都已存在，无需调用接口")
        return 0
    
    # 登录获取 token
    access_token, refresh_token = login(username, password)
    total_saved = 0
    query_count = 0
    
    for idx, component_barcode in enumerate(codes_to_query, start=1):
        try:
            print(f"[{idx}/{len(codes_to_query)}] 正在查询组件条码：{component_barcode}")
            result = query_data(component_barcode, access_token)
            query_count += 1
        except PermissionError:
            new_access = refresh_access(refresh_token)
            if new_access:
                access_token = new_access
                try:
                    result = query_data(component_barcode, access_token)
                    query_count += 1
                except PermissionError:
                    access_token, refresh_token = login(username, password)
                    result = query_data(component_barcode, access_token)
                    query_count += 1
            else:
                access_token, refresh_token = login(username, password)
                result = query_data(component_barcode, access_token)
                query_count += 1
        
        # 保存查询结果
        saved = save_query_result_to_db(result, component_barcode)
        total_saved += saved
    
    print(f"\n处理完成统计:")
    print(f"总组件条码数：{total_component_barcodes}")
    print(f"实际调用接口数：{query_count}")
    print(f"成功保存/更新记录数：{total_saved}")
    print(f"跳过记录数：{skipped_count}")
    
    return total_saved


def query_with_auto_refresh(query_params: str, username: str, password: str) -> Dict[str, Any]:
    """
    自动处理 token 过期并完成查询流程。
    支持自动刷新 token，刷新失败则重新登录。
    
    参数:
        query_params: 查询参数字符串
        username: 用户名
        password: 密码
    
    返回:
        dict: 查询结果数据
    """
    # 首次登录获取 token
    access_token, refresh_token = login(username, password)
    try:
        # 尝试使用当前 access token 查询
        return query_data(query_params, access_token)
    except PermissionError:
        # token 失效，尝试使用 refresh token 刷新
        new_access = refresh_access(refresh_token)
        if new_access:
            try:
                # 使用刷新后的 token 查询
                return query_data(query_params, new_access)
            except PermissionError:
                # 刷新也失败，继续下面的重新登录流程
                pass
        # 重新登录获取新 token
        access_token, refresh_token = login(username, password)
        # 使用新 token 查询
        return query_data(query_params, access_token)


def main() -> None:
    """
    单独查询指定产品编号并保存到 ProductTraceability 表。
    """
    # 从环境变量读取配置，使用默认值作为后备
    username = os.getenv("TRACE_USERNAME", "yladmim")
    password = os.getenv("TRACE_PASSWORD", "admin123456")
    query_params = os.getenv("TRACE_QUERY_PARAMS", "252904050405793")
    # 默认走 OEM 模式，设置 TRACE_OEM_MODE=0 可切换为单条查询
    use_oem = os.getenv("TRACE_OEM_MODE", "1") != "0"
    # 验证必要的环境变量是否已设置
    if not username or not password:
        raise RuntimeError("请设置 TRACE_USERNAME 与 TRACE_PASSWORD 环境变量")
    if use_oem:
        component_barcodes = get_oem_component_barcodes()
        saved_count = batch_query_and_save_oem(component_barcodes, username, password)
        print(f"已写入/更新记录数: {saved_count}")
    else:
        if not query_params:
            raise RuntimeError("请设置 TRACE_QUERY_PARAMS 环境变量")
        result = query_with_auto_refresh(query_params, username, password)
        saved_count = save_query_result_to_db(result, query_params)
        # print("查询返回数据", json.dumps(result, ensure_ascii=False, indent=2))
        print(f"已写入/更新记录数: {saved_count}")


if __name__ == "__main__":
    main()
