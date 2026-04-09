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
import json
from datetime import date, datetime


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
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        try:
            # 从数据库查询用户信息
            user = After_sales_index_login.objects.filter(username=username).first()
        except ProgrammingError:
            return Response({'detail': '该用户不存在'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not user:
            return Response({'detail': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
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
            return Response({'detail': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
        # 生成 JWT token
        refresh = RefreshToken()
        refresh['user_id'] = user.id
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
        """获取所有投诉记录列表（按创建时间倒序）。"""
        complaints = After_sales_Complaint.objects.all().order_by('-create_time')
        serializer = ComplaintListSerializer(complaints, many=True)
        return Response(serializer.data)

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
    """流转 单查询视图，根据序列号查询组件详细信息及合同客户信息。"""

    permission_classes = [IsAuthenticated]  # 需要身份验证

    def get(self, request, *args, **kwargs):
        """根据序列号查询组件的详细信息。"""
        row = []
        # 获取序列号参数（支持两种参数名）
        serial_no = request.query_params.get('serial_no') or request.query_params.get('serial')
        if not serial_no:
            return Response({'detail': '序列号不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # 查询组件技术参数
            with connections['DataBase'].cursor() as cursor:
                cursor.execute(
                    """
                    SELECT iv_pmax,iv_voc,iv_isc,iv_vpm,iv_ipm,iv_ff,iv_eff,iv_surf_temp,iv_env_temp,cell_supdesc,cell_spec,jbox_supdesc,jbox_spec,eva_supdesc,
                    eva_spec
                    FROM poly115_poly_lixian_serial
                    WHERE serial_nbr = %s
                    ORDER BY _updated DESC
                    LIMIT 1
                    """,
                    (serial_no,)
                )
            row = cursor.fetchone()
        except Exception as e:
            print('数据库报错：', e)
            return Response({'detail': '数据库查询失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not row:
            return Response({'detail': '记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        # 查询合同和客户信息
        contract = self.contract_customer_query(serial_no)
        print('contract', contract)
        return Response({
            'ret': True,
            'component_details': {
                # 电气参数
                'pmax': row[0],  # 最大功率
                'voc': row[1],  # 开路电压
                'isc': row[2],  # 短路电流
                'vmp': row[3],  # 最佳工作电压
                'imp': row[4],  # 最佳工作电流
                'ff': row[5],  # 填充因子
                'eff': row[6],  # 转换效率
                'temp': row[7],  # 表面温度
                # 材料信息
                'materials': {
                    'cell': {'name': '', 'factory': row[9], 'model': row[8]},  # 电池片
                    'film': {'name': '', 'factory': row[13], 'model': row[12]},  # EVA 膜
                    'frame': {'name': '', 'factory': '', 'model': ''},  # 边框
                    'junctionBox': {'name': '', 'factory': row[11], 'model': row[10]}  # 接线盒
                },
                # 业务信息
                'business': {
                    'contract': contract['contract'],  # 合同号
                    'customer': contract['customer']  # 客户名称
                }
            }
        })

    def contract_customer_query(self, serial_no):
        """根据组件序列号查询销售合同号和客户信息。
            
        Args:
            serial_no: 组件序列号
                
        Returns:
            dict: {'contract': 合同号，'customer': 客户名称}
        """
        # SQL 查询语句：从仓储管理系统联表查询合同和客户信息
        sql = """
            SELECT
                c.contract_no AS 销售合同号,
                c.customer AS 客户
            FROM wms113_wh_yingli_wh_container a
            LEFT JOIN wms113_wh_yingli_wh_combine b
                ON a._key = b.container_key
            LEFT JOIN wms113_wh_yingli_wh_delivery_batch c
                ON a.batch_key = c._key
            LEFT JOIN wms113_wh_yingli_wh_delivery_ord d
                ON c.ord_key = d._key
            LEFT JOIN wms113_wh_yingli_wh_pack_pallets e
                ON b.pallet_key = e._key
            LEFT JOIN wms113_wh_yingli_wh_assembly_status f
                ON e._key = f.pallet_key
            WHERE
                f.serial_nbr = %s
        """
        try:
            with connections['DataBase'].cursor() as cursor:
                cursor.execute(sql, (serial_no,))
                row = cursor.fetchone()
                return {
                    'contract': row[0],
                    'customer': row[1]
                }
        except Exception:
            return Response({'detail': '数据库查询失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
