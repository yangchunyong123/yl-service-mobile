from django.db.utils import ProgrammingError
from django.contrib.auth.hashers import check_password, make_password
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
# 导入数据模型
from .models import After_sales_index_login, After_sales_Complaint
# 导入序列化器
from .serializers import ChangePasswordSerializer, RegisterSerializer, TokenLoginSerializer, UserProfileSerializer, \
    ComplaintCreateSerializer, ComplaintListSerializer, ComplaintDetailSerializer, ComplaintUpdateSerializer
from django.db import connection, connections
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.cache import cache
import json
import hashlib
import time
import random
import string
import requests
from urllib import parse, request, error
from datetime import date, datetime
import base64


def decrypt_base64(encoded_str):
    """对Base64编码的字符串进行解码，用于解密前端传输的密码。

    Args:
        encoded_str: Base64编码的字符串

    Returns:
        解码后的原始字符串
    """
    try:
        # 先进行Base64解码，然后处理URL编码
        decoded_bytes = base64.b64decode(encoded_str)
        decoded_str = decoded_bytes.decode('utf-8')
        return decoded_str
    except Exception:
        # 如果解码失败，返回原字符串（兼容未加密的情况）
        return encoded_str


class DateEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，用于处理 datetime 和 date 对象的序列化。"""

    def default(self, obj):
        """序列化 datetime/date 为字符串格式。"""
        if isinstance(obj, datetime):  # 处理 datetime 对象
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):  # 处理 date 对象
            return obj.strftime('%Y-%m-%d')  # 纯日期格式，不含时间
        return super().default(obj)  # 处理其他类型


class TokenLoginView(APIView):
    """用户登录视图，使用账号密码验证并签发 JWT token。"""

    authentication_classes = []  # 禁用身份验证类
    permission_classes = []  # 禁用权限类

    def post(self, request, *args, **kwargs):
        """校验账号密码并签发 access/refresh token。"""
        # 使用序列化器验证请求数据
        serializer = TokenLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        # 对密码进行Base64解码
        password = decrypt_base64(serializer.validated_data['password'])
        try:
            # 从数据库查询用户信息
            user = After_sales_index_login.objects.filter(phone=phone).first()
        except ProgrammingError:
            return Response({'detail': '该用户不存在'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not user:
            return Response({'detail': '手机号或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        is_valid = False
        try:
            # 验证密码（哈希对比）
            is_valid = check_password(password, user.password)
        except Exception:
            is_valid = False
        # 兼容明文密码：如果哈希验证失败但明文匹配，则重新哈希存储
        if not is_valid and user.password == password:
            is_valid = True
            try:
                user.password = make_password(password)
                user.save(update_fields=['password'])
            except Exception:
                pass
        if not is_valid:
            return Response({'detail': '手机号或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        # 生成 JWT token
        refresh = RefreshToken()
        refresh['user_id'] = user.id
        refresh['phone'] = user.phone
        refresh['username'] = user.username
        # 序列化用户信息
        user_data = UserProfileSerializer(user).data
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': user_data
        })


class RegisterView(APIView):
    """用户注册视图，注册用户并同步 OA 员工信息。"""

    authentication_classes = []  # 禁用身份验证类
    permission_classes = []  # 禁用权限类

    def post(self, request, *args, **kwargs):
        """注册用户并同步 OA 员工信息。"""
        # 验证请求数据
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data_mation = serializer.validated_data
        username = data_mation['username']
        password = data_mation['password']
        phone = data_mation['phone']
        # 获取员工编号（支持两种字段名）
        ygcode = data_mation.get('ygcode') or data_mation.get('employee_id', '')
        selected_option = data_mation.get('selectedOption', '')
        try:
            # 检查用户名或手机号是否已注册
            crm_container = After_sales_index_login.objects.filter(
                Q(username=username) | Q(phone=phone)
            )
            if crm_container:
                data = {'ret': False, 'msg': '该用户名或手机号已注册！'}
                return HttpResponse(json.dumps(data, cls=DateEncoder), content_type="application/json")
            # 验证员工编号是否存在
            if ygcode == '':
                data = {'ret': False, 'msg': '员工编号为空，请联系管理员'}
                return HttpResponse(json.dumps(data, cls=DateEncoder), content_type="application/json")
            # 员工编号不足 10 位时左补零
            if len(ygcode) < 10:
                ygcode = ygcode.rjust(10, '0')
            # 连接 OA 系统数据库查询员工信息
            with connections['sqlserver_oa_ecology9'].cursor() as cursor:
                sql = "SELECT id, departmentid, subcompanyid1, lastname FROM HrmResource WHERE workcode = %s"
                cursor.execute(sql, (ygcode,))
                rows = cursor.fetchall()
                if not rows:
                    return JsonResponse({
                        'ret': False,
                        'msg': f'未找到工号为{ygcode}的员工信息'
                    })
                # 获取列名
                columns = [col[0] for col in cursor.description]
                employee_data = [dict(zip(columns, row)) for row in rows]
                # 提取部门 ID 和公司 ID 集合
                department_ids = set(record['departmentid'] for record in employee_data)
                subcompany_ids = set(record['subcompanyid1'] for record in employee_data)
                # 查询部门和公司名称
                department_map = self._get_department_names(cursor, department_ids)
                subcompany_map = self._get_subcompany_names(cursor, subcompany_ids)
                # 将部门和公司名称添加到员工数据中
                for record in employee_data:
                    record['department_name'] = department_map.get(
                        record['departmentid'],
                        {'departmentname': '未知部门', 'departmentcode': ''}
                    )
                    record['subcompany_name'] = subcompany_map.get(
                        record['subcompanyid1'],
                        {'subcompanyname': '未知公司', 'subcompanycode': ''}
                    )
                employee_data = employee_data[0]
                # 创建用户记录
                After_sales_index_login.objects.create(
                    username=username,
                    phone=phone,
                    password=make_password(password),
                    bm=selected_option,
                    ygcode=ygcode,
                    oa_userid=employee_data['id'],
                    lastname=employee_data['lastname'],
                    departmentid=employee_data['departmentid'],
                    subcompanyid=employee_data['subcompanyid1'],
                    departmentname=employee_data['department_name']['departmentname'],
                    departmentcode=employee_data['department_name']['departmentcode'],
                    subcompanyname=employee_data['subcompany_name']['subcompanyname'],
                    subcompanycode=employee_data['subcompany_name']['subcompanycode'],
                    status='1',
                    flag='2'
                )
                data = {'ret': True, 'msg': '注册成功请登录！'}
                return HttpResponse(json.dumps(data, cls=DateEncoder), content_type="application/json")
        except Exception as e:
            data = {'ret': False, 'msg': f'查询过程中发生错误：{str(e)}'}
            return HttpResponse(json.dumps(data, cls=DateEncoder), content_type="application/json")

    def _get_department_names(self, cursor, department_ids):
        """根据部门 ID 集合查询部门名称与编码。
        
        Args:
            cursor: 数据库游标
            department_ids: 部门 ID 集合
            
        Returns:
            部门信息字典 {部门 ID: {'departmentname': 部门名称，'departmentcode': 部门编码}}
        """
        if not department_ids:
            return {}
        # 构建 SQL 占位符
        placeholders = ','.join(['%s'] * len(department_ids))
        sql = f"SELECT id, departmentname, departmentcode FROM HrmDepartment WHERE id IN ({placeholders})"
        cursor.execute(sql, tuple(department_ids))
        rows = cursor.fetchall()
        return {
            row[0]: {'departmentname': row[1], 'departmentcode': row[2]}
            for row in rows
        }

    def _get_subcompany_names(self, cursor, subcompany_ids):
        """根据公司 ID 集合查询公司名称与编码。
        
        Args:
            cursor: 数据库游标
            subcompany_ids: 公司 ID 集合
            
        Returns:
            公司信息字典 {公司 ID: {'subcompanyname': 公司名称，'subcompanycode': 公司编码}}
        """
        if not subcompany_ids:
            return {}
        # 构建 SQL 占位符
        placeholders = ','.join(['%s'] * len(subcompany_ids))
        sql = f"SELECT id, subcompanyname, subcompanycode FROM HrmSubCompany WHERE id IN ({placeholders})"
        cursor.execute(sql, tuple(subcompany_ids))
        rows = cursor.fetchall()
        return {
            row[0]: {'subcompanyname': row[1], 'subcompanycode': row[2]}
            for row in rows
        }


class SelYgbhInfo(APIView):
    """注册页面根据页面输入的员工编号自动查询 OA 系统中的姓名。"""

    def post(self, request):
        """根据员工编号查询 OA 中的姓名。"""
        data = request.data
        row = []
        ygcode = data['ygcode']
        try:
            # 查询外部数据库获取员工信息
            with connections['sqlserver_oa_ecology9'].cursor() as cursor:
                # 查询员工基本信息
                sql = "SELECT lastname FROM HrmResource WHERE workcode = %s"
                cursor.execute(sql, (ygcode,))
                rows = cursor.fetchall()

                if not rows:
                    data = {
                        'ret': False,
                        'msg': f'未找到工号为{ygcode}的员工信息'
                    }
                    return HttpResponse(json.dumps(data, cls=DateEncoder), content_type="application/json")
                # 格式化返回结果
                for item in rows:
                    row.append({
                        'value': item[0],
                    })
                data = {'ret': True, 'row': row}
                return HttpResponse(json.dumps(data, cls=DateEncoder), content_type="application/json")

        except Exception as e:
            # 处理其他意外异常
            data = {'ret': False, 'msg': f'查询过程中发生错误：{str(e)}'}
            return HttpResponse(json.dumps(data, cls=DateEncoder), content_type="application/json")


class ChangePasswordView(APIView):
    """修改密码视图，校验旧密码并更新为新密码。"""

    permission_classes = [IsAuthenticated]  # 需要身份验证

    def post(self, request, *args, **kwargs):
        """校验旧密码并更新为新密码。"""
        # 验证请求数据
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        user = request.user
        # 验证旧密码
        if not self._verify_password(user.password, old_password):
            return Response({'detail': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        # 更新为新密码
        user.password = make_password(new_password)
        user.save(update_fields=['password'])
        return Response({'ret': True, 'msg': '密码修改成功'})

    def _verify_password(self, stored_password, raw_password):
        """校验密码（兼容明文与哈希存储）。
        
        Args:
            stored_password: 存储的密码（可能是哈希或明文）
            raw_password: 用户输入的明文密码
            
        Returns:
            bool: 密码是否正确
        """
        try:
            # 尝试哈希对比
            if check_password(raw_password, stored_password):
                return True
        except Exception:
            pass
        # 如果哈希对比失败，尝试明文对比（兼容旧数据）
        return stored_password == raw_password


class ProfileView(APIView):
    """用户信息视图，获取当前登录用户的基础信息。"""

    permission_classes = [IsAuthenticated]  # 需要身份验证

    def get(self, request, *args, **kwargs):
        """获取当前登录用户的基础信息。"""
        try:
            user = request.user
        except ProgrammingError:
            return Response({'detail': '该用户不存在'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 序列化用户信息
        user_data = UserProfileSerializer(user).data
        return Response(user_data)


class ComplaintCreateView(APIView):
    """投诉创建视图，创建新的投诉记录或获取投诉列表。"""

    permission_classes = [IsAuthenticated]  # 需要身份验证

    def get(self, request, *args, **kwargs):
        """获取投诉记录列表（支持分页，按创建时间倒序）。
        
        查询参数:
            page: 页码（默认1）
            page_size: 每页数量（默认10，最大50）
            search: 搜索关键词（项目名称/序列号/问题类型）
        """
        # 获取分页参数
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 10)), 50)
        search = request.query_params.get('search', '').strip()
        
        # 构建查询条件
        queryset = After_sales_Complaint.objects.all()
        
        # 搜索过滤
        if search:
            queryset = queryset.filter(
                Q(project_name__icontains=search) |
                Q(serial_no__icontains=search) |
                Q(issue_type__icontains=search)
            )
        
        # 按创建时间倒序
        queryset = queryset.order_by('-create_time')
        
        # 计算总数
        total = queryset.count()
        
        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        complaints = queryset[start:end]
        
        # 序列化
        serializer = ComplaintListSerializer(complaints, many=True)
        
        # 返回分页数据
        return Response({
            'results': serializer.data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
            'has_next': end < total,
            'has_prev': page > 1
        })

    def post(self, request, *args, **kwargs):
        """创建新的投诉记录。"""
        # 验证请求数据
        serializer = ComplaintCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 获取处理人信息（默认为当前用户）
        handler = serializer.validated_data.get('handler') or getattr(request.user, 'username', '')
        complaint = serializer.save(
            handler=handler,
            created_by_id=getattr(request.user, 'id', None),
            status=serializer.validated_data.get('status') or '待处理',
        )
        return Response({'ret': True, 'msg': '提交成功', 'id': complaint.id})


class ComplaintDetailView(APIView):
    """投诉详情视图，查看、更新或删除单个投诉记录。"""

    permission_classes = [IsAuthenticated]  # 需要身份验证

    def get(self, request, pk, *args, **kwargs):
        """获取单个投诉记录的详细信息。"""
        complaint = After_sales_Complaint.objects.filter(id=pk).first()
        if not complaint:
            return Response({'detail': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ComplaintDetailSerializer(complaint)
        return Response(serializer.data)

    def patch(self, request, pk, *args, **kwargs):
        """部分更新投诉记录。"""
        complaint = After_sales_Complaint.objects.filter(id=pk).first()
        if not complaint:
            return Response({'detail': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 使用部分更新序列化器
        serializer = ComplaintUpdateSerializer(complaint, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'ret': True, 'msg': '更新成功'})

    def put(self, request, pk, *args, **kwargs):
        """完整更新投诉记录。"""
        complaint = After_sales_Complaint.objects.filter(id=pk).first()
        if not complaint:
            return Response({'detail': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 使用完整更新序列化器
        serializer = ComplaintUpdateSerializer(complaint, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'ret': True, 'msg': '更新成功'})


class RoutingSheetQueryView(APIView):
    """流转单查询视图，通过外部溯源接口查询组件详细信息。
    
    功能说明：
        前端用户扫码提交组件序列号后，本视图负责：
        1. 调用外部溯源系统登录接口获取访问令牌
        2. 使用令牌调用溯源查询接口获取组件数据
        3. 将返回的数据标准化后返回给前端
    
    外部接口依赖：
        - TRACE_LOGIN_URL: 溯源系统登录接口
        - TRACE_REFRESH_URL: Token刷新接口
        - TRACE_QUERY_URL: 组件信息查询接口
        - TRACE_LOGIN_USERNAME/PASSWORD: 溯源系统认证凭证
    """

    permission_classes = [IsAuthenticated]  # 需要用户登录后才能访问

    def get(self, request, *args, **kwargs):
        """GET请求入口：根据序列号查询组件的详细信息。
        
        Token获取策略（优化版）：
            1. 先从缓存中获取refresh_token
            2. 使用refresh_token刷新access_token
            3. 如果刷新失败，才调用登录接口获取新token
        
        Args:
            request: HTTP请求对象
            
        Returns:
            Response: 包含组件详细信息的JSON响应
        """
        # 从请求参数中获取组件序列号（支持两种参数名）
        serial_no = request.query_params.get('serial_no') or request.query_params.get('serial')
        serial_no = ''.join(str(serial_no or '').split())
        if not serial_no:
            return Response({'detail': '序列号不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 步骤1：优先使用refresh_token刷新，失败则登录
        access_token, refresh_token, error_msg = self._get_trace_token()
        if error_msg:
            return Response({'detail': error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 步骤2：使用令牌查询组件信息
        query_payload, query_error = self._trace_query(serial_no, access_token, refresh_token)
        if query_error:
            return Response({'detail': query_error}, status=status.HTTP_502_BAD_GATEWAY)
        
        # 步骤3：将原始数据标准化为统一格式
        component_details = self._normalize_component_details(query_payload, serial_no)
        return Response({
            'ret': True,
            'component_details': component_details
        })

    def _sanitize_url(self, raw_url):
        """清理URL字符串，去除多余空白和反引号。
        
        Args:
            raw_url: 原始URL字符串
            
        Returns:
            str: 清理后的URL字符串
        """
        return str(raw_url or '').strip().strip('`').strip()

    def _http_json(self, url, method='GET', payload=None, headers=None):
        """发起HTTP JSON请求的通用方法。
        
        Args:
            url: 请求URL
            method: HTTP方法，默认GET
            payload: 请求体数据（字典格式）
            headers: 额外的请求头
            
        Returns:
            tuple: (HTTP状态码, 响应JSON数据字典)
            
        Note:
            - 超时时间由settings.TRACE_HTTP_TIMEOUT控制
            - 自动处理HTTP错误和JSON解析错误
        """
        # 设置请求头
        request_headers = {}
        # 只有POST/PUT/PATCH等有请求体的方法才需要Content-Type
        if payload is not None and method != 'GET':
            request_headers['Content-Type'] = 'application/json'
        if headers:
            request_headers.update(headers)
        
        # 如果有请求体数据，转换为JSON字节流
        body = None
        if payload is not None:
            body = json.dumps(payload).encode('utf-8')
        
        # 创建请求对象
        req = request.Request(url=url, data=body, headers=request_headers, method=method)
        
        try:
            # 发起请求并读取响应
            with request.urlopen(req, timeout=settings.TRACE_HTTP_TIMEOUT) as resp:
                content = resp.read().decode('utf-8')
                status_code = resp.getcode()
        except error.HTTPError as exc:
            # 处理HTTP错误（4xx, 5xx）
            content = exc.read().decode('utf-8', errors='ignore')
            status_code = exc.code
        except error.URLError as exc:
            # 处理URL错误（包括超时）
            return 504, {}  # 504 Gateway Timeout
        except Exception as e:
            # 处理网络错误（超时、连接失败等）
            return 504, {}  # 504 Gateway Timeout
        
        # 解析JSON响应
        try:
            parsed_data = json.loads(content) if content else {}
            return status_code, parsed_data
        except json.JSONDecodeError as e:
            # JSON解析失败时返回空字典
            return status_code, {}

    def _find_first(self, data, keys):
        """递归查找嵌套数据结构中的第一个匹配键值。
        
        Args:
            data: 待查找的数据（字典或列表）
            keys: 要查找的键名列表（按优先级排序）
            
        Returns:
            找到的第一个非空值，未找到返回空字符串
            
        Example:
            # 在嵌套字典中查找access或access_token字段
            _find_first({'token': {'access': 'abc'}}, ['access', 'access_token'])
            # 返回: 'abc'
        """
        if isinstance(data, dict):
            # 先查找当前层级的键
            for key in keys:
                value = data.get(key)
                if value not in (None, ''):
                    return value
            # 再递归查找子字典中的键
            for value in data.values():
                found = self._find_first(value, keys)
                if found not in (None, ''):
                    return found
        if isinstance(data, list):
            # 递归查找列表中的每一项
            for item in data:
                found = self._find_first(item, keys)
                if found not in (None, ''):
                    return found
        return ''

    def _pick_dict(self, payload):
        """从溯源接口响应中提取组件数据字典。
        
        支持多种响应结构：
            1. 新结构: {'jhn_data': {'gz_data': [{组件数据}]}}
            2. 旧结构: {'data': [{组件数据}]} 或 {'data': {组件数据}}
            3. 顶层结构: {'xs_data': [...], 'jh_data': {...}}
            4. 代工结构: {'dg_data': [{组件数据}]}
        
        Args:
            payload: 溯源接口返回的完整响应数据
            
        Returns:
            dict: 提取出的单条组件数据字典，未找到返回空字典
        """
        if not isinstance(payload, dict):
            return {}
        
        # 优先尝试顶层 dg_data（代工数据）
        dg_data = payload.get('dg_data')
        if isinstance(dg_data, list) and dg_data:
            return dg_data[0] if isinstance(dg_data[0], dict) else {}
        
        # 尝试 jhn_data 或 jh_data
        data_container = payload.get('jhn_data') or payload.get('jh_data')
        if isinstance(data_container, dict):
            # 提取 gz_data
            gz_data = data_container.get('gz_data')
            if isinstance(gz_data, list) and gz_data:
                return gz_data[0] if isinstance(gz_data[0], dict) else {}
            elif isinstance(gz_data, dict):
                return gz_data
            
            # 提取 dg_data（嵌套在 jh_data 中）
            dg_data_nested = data_container.get('dg_data')
            if isinstance(dg_data_nested, list) and dg_data_nested:
                return dg_data_nested[0] if isinstance(dg_data_nested[0], dict) else {}
        
        # 兼容旧结构：data字段
        data = payload.get('data')
        if isinstance(data, list) and data:
            return data[0] if isinstance(data[0], dict) else {}
        if isinstance(data, dict):
            return data
        
        return payload

    def _get_trace_token(self):
        """获取溯源系统访问令牌（优化版：优先refresh，失败则登录）。
        
        Token获取策略：
            1. 从缓存中读取refresh_token
            2. 使用refresh_token调用刷新接口获取新的access_token
            3. 如果刷新失败，调用登录接口获取新的access_token和refresh_token
            4. 将新的refresh_token保存到缓存（有效期30天）
        
        Returns:
            tuple: (access_token, refresh_token, error_message)
                   成功时error_message为空字符串
        """
        # 缓存键名
        CACHE_KEY = 'trace_refresh_token'
        
        # 步骤1：尝试从缓存获取refresh_token
        cached_refresh_token = cache.get(CACHE_KEY)
        if cached_refresh_token:
            new_access_token = self._trace_refresh(cached_refresh_token)
            if new_access_token:
                return new_access_token, cached_refresh_token, ''
        
        # 步骤2：刷新失败或无缓存，调用登录接口
        access_token, refresh_token, login_error = self._trace_login()
        if login_error:
            return '', '', login_error
        
        # 步骤3：保存refresh_token到缓存（有效期30天）
        if refresh_token:
            cache.set(CACHE_KEY, refresh_token, timeout=60*60*24*30)  # 30天
        
        return access_token, refresh_token, ''
    
    def _trace_login(self):
        """调用溯源系统登录接口获取访问令牌（内部方法）。
        
        登录流程：
            1. 从settings读取登录URL和凭证
            2. 发送POST请求携带用户名密码
            3. 从响应中提取access_token和refresh_token
            
        Returns:
            tuple: (access_token, refresh_token, error_message)
                   成功时error_message为空字符串
        """
        login_url = self._sanitize_url(settings.TRACE_LOGIN_URL)
        if not login_url:
            return '', '', '登录地址未配置'
        username = settings.TRACE_LOGIN_USERNAME
        password = settings.TRACE_LOGIN_PASSWORD
        if not username or not password:
            return '', '', '接口用户名或接口密码未配置'
        
        # 发送登录请求
        status_code, payload = self._http_json(
            login_url,
            method='POST',
            payload={'username': username, 'password': password}
        )
        if status_code >= 400:
            msg = self._find_first(payload, ['msg', 'detail']) or '外部登录失败'
            return '', '', msg
        
        # 提取token（支持多种字段名）
        access_token = self._find_first(payload, ['access', 'access_token', 'token', 'jwt'])
        refresh_token = self._find_first(payload, ['refresh', 'refresh_token'])
        if not access_token:
            return '', '', '外部登录成功但未返回 token'
        return str(access_token), str(refresh_token or ''), ''

    def _trace_refresh(self, refresh_token):
        """调用溯源系统Token刷新接口获取新的access_token。
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            str: 新的access_token，刷新失败返回空字符串
        """
        refresh_url = self._sanitize_url(settings.TRACE_REFRESH_URL)
        if not refresh_url or not refresh_token:
            return ''
        
        # 发送刷新请求
        status_code, payload = self._http_json(
            refresh_url,
            method='POST',
            payload={'refresh': refresh_token}
        )
        if status_code >= 400:
            return ''
        
        # 提取新的access_token
        access_token = self._find_first(payload, ['access', 'access_token', 'token', 'jwt'])
        return str(access_token or '')

    def _build_query_urls(self, query_url, serial_no):
        """构建查询URL。
        
        只使用一种格式：query_params=序列号
        
        Args:
            query_url: 配置的查询接口URL
            serial_no: 组件序列号
            
        Returns:
            list: URL列表（只有一个元素）
        """
        serial_text = str(serial_no)
        serial_encoded = parse.quote(serial_text, safe='')
        
        # 获取基础URL（去掉查询参数）
        if '?' in query_url:
            base_url = query_url.split('?')[0]
        else:
            base_url = query_url.rstrip('/')
        
        # 只使用一种格式：query_params=序列号
        return [f"{base_url}?query_params={serial_encoded}"]

    def _trace_query(self, serial_no, access_token, refresh_token):
        """调用溯源查询接口获取组件详细信息。
        
        查询流程：
            1. 构建多种可能的URL格式（通过_build_query_urls）
            2. 逐一尝试每个URL，直到找到返回有效数据的响应
            3. 如果遇到401/403错误，自动刷新token后重试
            4. 返回第一个成功的响应数据
        
        容错策略：
            - 跳过5xx服务器错误的URL，继续尝试下一个
            - 跳过业务code不符合预期的响应
            - 记录最后一个响应的状态码和内容，用于错误提示
        
        Args:
            serial_no: 组件序列号
            access_token: 访问令牌
            refresh_token: 刷新令牌
            
        Returns:
            tuple: (response_payload, error_message)
                   成功时error_message为空字符串
        """
        query_url = self._sanitize_url(settings.TRACE_QUERY_URL)
        if not query_url:
            return {}, '接口查询地址未配置'
        
        # 构建认证头
        auth_header = {
            'Authorization': f"{settings.TRACE_AUTH_SCHEME} {access_token}"
        }
        
        # 记录最后一次尝试的结果，用于最终错误提示
        last_status_code = 500
        last_payload = {}
        
        # 逐一尝试所有候选URL
        for full_query_url in self._build_query_urls(query_url, serial_no):
            # 发起查询请求
            status_code, payload = self._http_json(full_query_url, method='GET', headers=auth_header)
            
            # 如果Token过期，刷新后重试
            if status_code in (401, 403) and refresh_token:
                new_access_token = self._trace_refresh(refresh_token)
                if new_access_token:
                    auth_header = {
                        'Authorization': f"{settings.TRACE_AUTH_SCHEME} {new_access_token}"
                    }
                    status_code, payload = self._http_json(full_query_url, method='GET', headers=auth_header)
            
            # 记录当前结果
            last_status_code = status_code
            last_payload = payload
            
            # 跳过服务器错误，继续尝试下一个URL
            if status_code >= 500:
                continue
            
            # 检查业务code是否符合预期
            if isinstance(payload, dict):
                code = payload.get('code')
                if code not in (None, 0, 200, 2000):
                    continue
            
            # 提取数据，如果有效则直接返回
            data = self._pick_dict(payload)
            if data:
                return payload, ''
        
        # 所有URL都尝试失败，使用最后一次结果构建错误信息
        status_code = last_status_code
        payload = last_payload
        
        if status_code >= 400:
            # 根据HTTP状态码映射友好的错误提示
            error_messages = {
                400: '请求参数错误',
                401: '认证失败，请重新登录',
                403: '没有权限访问',
                404: '序列号不存在',
                500: '溯源系统内部错误，请联系管理员',
                502: '溯源服务不可用',
                503: '溯源服务维护中',
                504: '溯源服务超时'
            }
            msg = self._find_first(payload, ['msg', 'detail']) or error_messages.get(status_code, f'外部查询失败(HTTP {status_code})')
            return {}, msg
        
        # 检查业务code
        if isinstance(payload, dict):
            code = payload.get('code')
            if code not in (None, 0, 200, 2000):
                msg = payload.get('msg') or payload.get('detail') or f'外部查询失败(code={code})'
                return {}, msg
        
        # 检查是否有有效数据
        if not payload:
            return {}, '未查询到记录'
        if not self._pick_dict(payload):
            return {}, '未查询到记录'
        return payload, ''

    def _get_value(self, data, keys, default=''):
        """从数据字典中按优先级提取字段值。
        
        按 keys 列表的顺序依次查找，返回第一个非空值。
        用于兼容溯源接口返回的不同字段命名风格。
        
        Args:
            data: 数据字典
            keys: 字段名列表（按优先级从高到低排序）
            default: 默认值，未找到时返回
            
        Returns:
            找到的字段值，或默认值
            
        Example:
            _get_value({'serialNo': '123'}, ['serial_no', 'serialNo', '组件序列号'])
            # 返回: '123'
        """
        if not isinstance(data, dict):
            return default
        for key in keys:
            value = data.get(key)
            if value not in (None, ''):
                return value
        return default

    def _normalize_component_details(self, data, serial_no):
        """根据前端需求提取组件详细信息。
        
        只返回前端需要的字段：
        - 组件序列号、测试日期、功率档位、电流档位、EL等级、最终等级
        - Pmax、ISC、VOC、IPM、VPM、FF
        - 电池片厂家
        """
        record = self._pick_dict(data)
        
        # 如果存在 xs_data，合并销售数据字段
        if isinstance(data, dict):
            xs_data = data.get('xs_data')
            if isinstance(xs_data, list) and xs_data:
                xs_record = xs_data[0] if isinstance(xs_data[0], dict) else {}
                if isinstance(record, dict):
                    record = {**record, **xs_record}
        
        # 如果存在 wms_data，合并物料数据字段（电池片厂家信息）
        if isinstance(data, dict):
            wms_data = data.get('wms_data')
            if isinstance(wms_data, list):
                for item in wms_data:
                    if isinstance(item, dict) and item.get('title') == '电池片':
                        fields = item.get('fields')
                        if isinstance(fields, list) and fields:
                            wms_info = fields[0] if isinstance(fields[0], dict) else {}
                            if isinstance(record, dict):
                                record = {**record, **wms_info}
                        break
            elif isinstance(wms_data, dict):
                fields = wms_data.get('fields')
                if isinstance(fields, list) and fields:
                    wms_info = fields[0] if isinstance(fields[0], dict) else {}
                    if isinstance(record, dict):
                        record = {**record, **wms_info}
        
        # 只返回前端需要的字段
        return {
            'serial_no': self._get_value(record, ['组件序列号', 'serial_no', 'serialNo'], serial_no),
            'test_date': self._get_value(record, ['测试日期', 'test_date', 'testDate', 'iv_test_date']),
            'power_grade': self._get_value(record, ['功率档位', '功率档', 'power_grade', 'powerGear', 'power_gear']),
            'current_grade': self._get_value(record, ['电流挡位', '电流档位', '电流档', 'current_grade', 'currentGear', 'current_gear']),
            'el_grade': self._get_value(record, ['EL等级', 'el_grade', 'elGrade', 'el_level']),
            'final_grade': self._get_value(record, ['最终等级', 'final_grade', 'finalGrade']),
            'pmax': self._get_value(record, ['Pmax', 'pmax', 'PMAX']),
            'isc': self._get_value(record, ['ISC', 'isc']),
            'voc': self._get_value(record, ['VOC', 'voc']),
            'ipm': self._get_value(record, ['IPM', 'ipm', 'imp']),
            'vpm': self._get_value(record, ['VPM', 'vpm', 'vmp']),
            'ff': self._get_value(record, ['FF', 'ff']),
            'battery_factory': self._get_value(record, ['电池片厂家', 'battery_factory', '电池片供应商', 'battery_supplier']),
            # xs_data销售数据
            'sales_contract_no': self._get_value(record, ['销售合同号', 'sales_contract_no', 'sales_contract_number', 'contract_no']),
            'customer': self._get_value(record, ['客户', 'customer', 'customer_name'])
        }

class WeComJSConfigView(APIView):
    """
    企业微信 JS-SDK 配置接口，生成 wx.config 需要的 signature 等参数。
    """
    permission_classes = [IsAuthenticated]  # 需要用户登录后才能访问

    def get(self, request, *args, **kwargs):
        url = request.query_params.get('url')
        if not url:
            return Response({'ret': False, 'msg': '缺少 url 参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 去掉 url 的 # 后面的部分
        url = url.split('#')[0]

        corp_id = getattr(settings, 'WECOM_CORP_ID', None)
        corp_secret = getattr(settings, 'WECOM_CORP_SECRET', None)

        if not corp_id or not corp_secret:
            return Response({'ret': False, 'msg': '企业微信配置缺失'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 1. 获取 access_token (缓存2小时)
        access_token = cache.get('wecom_access_token')
        if not access_token:
            token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}"
            resp = requests.get(token_url).json()
            if resp.get('errcode') == 0:
                access_token = resp.get('access_token')
                cache.set('wecom_access_token', access_token, 7000)
            else:
                return Response({'ret': False, 'msg': f"获取access_token失败: {resp.get('errmsg')}"})

        # 2. 获取 jsapi_ticket (缓存2小时)
        jsapi_ticket = cache.get('wecom_jsapi_ticket')
        if not jsapi_ticket:
            ticket_url = f"https://qyapi.weixin.qq.com/cgi-bin/get_jsapi_ticket?access_token={access_token}"
            resp = requests.get(ticket_url).json()
            if resp.get('errcode') == 0:
                jsapi_ticket = resp.get('ticket')
                cache.set('wecom_jsapi_ticket', jsapi_ticket, 7000)
            else:
                return Response({'ret': False, 'msg': f"获取jsapi_ticket失败: {resp.get('errmsg')}"})

        # 3. 生成签名
        noncestr = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        timestamp = int(time.time())
        
        # 参数必须按字典序排序
        sign_str = f"jsapi_ticket={jsapi_ticket}&noncestr={noncestr}&timestamp={timestamp}&url={url}"
        signature = hashlib.sha1(sign_str.encode('utf-8')).hexdigest()

        return Response({
            'ret': True,
            'config': {
                'appId': corp_id,
                'timestamp': timestamp,
                'nonceStr': noncestr,
                'signature': signature,
            }
        })

