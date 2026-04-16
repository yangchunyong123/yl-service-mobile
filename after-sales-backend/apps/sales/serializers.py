import re
from rest_framework import serializers
from .models import After_sales_index_login, After_sales_Complaint


class TokenLoginSerializer(serializers.Serializer):
    """登录接口序列化器，校验账号与密码字段。"""
    phone = serializers.CharField(
        required=True,
        min_length=11,
        max_length=11,
        error_messages={
            'required': '手机号不能为空',
            'min_length': '手机号必须为11位',
            'max_length': '手机号必须为11位',
        }
    )
    password = serializers.CharField(
        required=True,
        min_length=6,
        max_length=128,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码长度不能少于6位',
            'max_length': '密码长度不能超过128位',
        }
    )

    def validate_phone(self, value):
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value


class RegisterSerializer(serializers.Serializer):
    """注册接口序列化器，校验注册所需字段与可选信息。"""
    username = serializers.CharField(
        required=True,
        min_length=2,
        max_length=50,
        error_messages={
            'required': '用户名不能为空',
            'min_length': '用户名长度不能少于2位',
            'max_length': '用户名长度不能超过50位',
        }
    )
    password = serializers.CharField(
        required=True,
        min_length=6,
        max_length=128,
        error_messages={
            'required': '密码不能为空',
            'min_length': '密码长度不能少于6位',
            'max_length': '密码长度不能超过128位',
        }
    )
    phone = serializers.CharField(
        required=True,
        min_length=11,
        max_length=11,
        error_messages={
            'required': '手机号不能为空',
            'min_length': '手机号必须为11位',
            'max_length': '手机号必须为11位',
        }
    )
    ygcode = serializers.CharField(required=False, allow_blank=True, max_length=20)
    employee_id = serializers.CharField(required=False, allow_blank=True, max_length=20)
    oa_name = serializers.CharField(required=False, allow_blank=True, max_length=50)
    selectedOption = serializers.CharField(required=False, allow_blank=True, max_length=100)

    def validate_phone(self, value):
        """验证手机号格式"""
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('手机号格式不正确')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器，校验旧密码与新密码字段。"""
    old_password = serializers.CharField(
        required=True,
        error_messages={'required': '旧密码不能为空'}
    )
    new_password = serializers.CharField(
        required=True,
        min_length=6,
        max_length=128,
        error_messages={
            'required': '新密码不能为空',
            'min_length': '新密码长度不能少于6位',
            'max_length': '新密码长度不能超过128位',
        }
    )

    def validate_new_password(self, value):
        """验证新密码复杂度"""
        # 至少包含字母和数字
        if not re.search(r'[A-Za-z]', value) or not re.search(r'\d', value):
            raise serializers.ValidationError('密码必须同时包含字母和数字')
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """用户信息序列化器，返回当前登录用户基础信息。"""
    class Meta:
        model = After_sales_index_login
        fields = (
            'id',
            'username',
            'phone',
            'lastname',
            'departmentname',
            'subcompanyname',
            'ygcode',
        )


class ComplaintCreateSerializer(serializers.ModelSerializer):
    """客诉创建序列化器，校验并保存客诉基础与处理信息。"""
    serial_no = serializers.CharField(
        required=True,
        min_length=5,
        max_length=50,
        error_messages={
            'required': '组件序列号不能为空',
            'min_length': '序列号长度不能少于5位',
            'max_length': '序列号长度不能超过50位',
        }
    )
    project_name = serializers.CharField(
        required=True,
        min_length=2,
        max_length=100,
        error_messages={
            'required': '项目名称不能为空',
            'min_length': '项目名称长度不能少于2位',
            'max_length': '项目名称长度不能超过100位',
        }
    )
    issue_type = serializers.CharField(
        required=True,
        error_messages={'required': '问题类型不能为空'}
    )
    
    class Meta:
        model = After_sales_Complaint
        fields = (
            'handler',
            'serial_no',
            'project_name',
            'location',
            'is_warranty',
            'issue_type',
            'inverter_info',
            'process_type',
            'replace_serial_no',
            'repair_details',
            'repairer',
        )
    
    def validate_serial_no(self, value):
        """验证序列号格式（字母数字下划线中划线）"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise serializers.ValidationError('序列号只能包含字母、数字、下划线和中划线')
        return value.upper()  # 统一转为大写
    
    def validate_replace_serial_no(self, value):
        """验证更换序列号格式"""
        if value and not re.match(r'^[a-zA-Z0-9_-]+$', value):
            raise serializers.ValidationError('更换序列号只能包含字母、数字、下划线和中划线')
        return value.upper() if value else value


class ComplaintListSerializer(serializers.ModelSerializer):
    """客诉列表序列化器，用于列表页展示字段。"""
    class Meta:
        model = After_sales_Complaint
        fields = (
            'id',
            'handler',
            'serial_no',
            'project_name',
            'location',
            'status',
            'is_warranty',
            'issue_type',
            'process_type',
            'create_time',
            'update_time',
            'repairer',
        )


class ComplaintDetailSerializer(serializers.ModelSerializer):
    """客诉详情序列化器，用于详情页展示完整字段。"""
    class Meta:
        model = After_sales_Complaint
        fields = (
            'id',
            'handler',
            'serial_no',
            'project_name',
            'location',
            'status',
            'is_warranty',
            'issue_type',
            'inverter_info',
            'process_type',
            'replace_serial_no',
            'repair_details',
            'repairer',
            'create_time',
            'update_time',
        )


class ComplaintUpdateSerializer(serializers.ModelSerializer):
    """客诉更新序列化器，校验可编辑字段。"""
    class Meta:
        model = After_sales_Complaint
        fields = (
            'handler',
            'serial_no',
            'project_name',
            'location',
            'status',
            'is_warranty',
            'issue_type',
            'inverter_info',
            'process_type',
            'replace_serial_no',
            'repair_details',
            'repairer',
        )
