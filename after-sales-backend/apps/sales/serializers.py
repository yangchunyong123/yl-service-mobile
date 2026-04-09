from rest_framework import serializers
from .models import After_sales_index_login, After_sales_Complaint


class TokenLoginSerializer(serializers.Serializer):
    """登录接口序列化器，校验账号与密码字段。"""
    username = serializers.CharField()
    password = serializers.CharField()


class RegisterSerializer(serializers.Serializer):
    """注册接口序列化器，校验注册所需字段与可选信息。"""
    username = serializers.CharField()
    password = serializers.CharField()
    phone = serializers.CharField()
    ygcode = serializers.CharField(required=False, allow_blank=True)
    employee_id = serializers.CharField(required=False, allow_blank=True)
    oa_name = serializers.CharField(required=False, allow_blank=True)
    selectedOption = serializers.CharField(required=False, allow_blank=True)


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器，校验旧密码与新密码字段。"""
    old_password = serializers.CharField()
    new_password = serializers.CharField()


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
