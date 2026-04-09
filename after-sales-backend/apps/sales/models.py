from django.db import models

# 模型定义
class After_sales_index_login(models.Model):
    """用户登录表模型，保存账号与组织信息。"""
    username = models.CharField(max_length=100)  # 用户名
    password = models.CharField(max_length=255)  # 密码
    phone = models.CharField(max_length=11)  # 手机号
    status = models.CharField(max_length=1)  # 状态标识
    flag = models.CharField(max_length=1)  # 标志位
    bm = models.CharField(max_length=20)  # 部门/业务线标识
    ygcode = models.CharField(max_length=10)  # 员工编号
    oa_userid = models.IntegerField()  # OA 用户 ID
    departmentid = models.IntegerField()  # 部门 ID
    subcompanyid = models.IntegerField()  # 分公司 ID
    departmentname = models.CharField(max_length=50)  # 部门名称
    departmentcode = models.CharField(max_length=50)  # 部门编码
    subcompanyname = models.CharField(max_length=50)  # 分公司名称
    subcompanycode = models.CharField(max_length=50)  # 分公司编码
    lastname = models.CharField(max_length=50)  # 姓名
    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    update_time = models.DateTimeField(auto_now=True)  # 更新时间

    @property
    def is_authenticated(self):
        """兼容认证属性，表示该用户已通过认证。"""
        return True

    class Meta:
        managed = False
        db_table = 'after_sales_index_login'


class After_sales_Complaint(models.Model):
    """客诉表模型，保存客诉基础信息与处理信息。"""
    handler = models.CharField(max_length=100, blank=True)  # 客诉处理人
    serial_no = models.CharField(max_length=100)  # 组件序列号
    project_name = models.CharField(max_length=200)  # 项目名称
    location = models.CharField(max_length=200, blank=True)  # 项目地点
    status = models.CharField(max_length=5, default='1')  # 处理状态
    is_warranty = models.CharField(max_length=10)  # 是否质保
    issue_type = models.CharField(max_length=100, blank=True)  # 问题种类
    inverter_info = models.CharField(max_length=200, blank=True)  # 方阵记录/逆变器信息
    process_type = models.CharField(max_length=100, blank=True)  # 处理类型
    replace_serial_no = models.CharField(max_length=100, blank=True)  # 换货序列号
    repair_details = models.JSONField(default=dict, blank=True)  # 维修详情
    repairer = models.CharField(max_length=100, blank=True)  # 维修人
    created_by_id = models.IntegerField(null=True, blank=True)  # 创建人 ID
    create_time = models.DateTimeField(auto_now_add=True)  # 创建时间
    update_time = models.DateTimeField(auto_now=True)  # 更新时间

    class Meta:
        managed = False
        db_table = 'after_sales_Complaint'
