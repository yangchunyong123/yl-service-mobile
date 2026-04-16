# 统一异常处理

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db.utils import DatabaseError
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
    Throttled
)

logger = logging.getLogger('sales')


def custom_exception_handler(exc, context):
    """自定义异常处理，统一返回格式并记录日志。
    
    Args:
        exc: 异常对象
        context: 上下文信息
        
    Returns:
        Response: 统一格式的错误响应
    """
    # 先调用 DRF 默认的异常处理
    response = exception_handler(exc, context)
    
    # 获取请求信息
    request = context.get('request')
    view = context.get('view')
    
    # 构建日志信息
    log_data = {
        'path': request.path if request else 'unknown',
        'method': request.method if request else 'unknown',
        'view': view.__class__.__name__ if view else 'unknown',
        'error': str(exc),
    }
    
    if response is not None:
        # DRF 已处理的异常
        error_code = response.status_code
        error_message = get_error_message(exc, response)
        
        # 记录警告日志
        logger.warning(f"API异常: {log_data}")
        
        # 统一响应格式
        response.data = {
            'ret': False,
            'code': error_code,
            'msg': error_message,
            'data': None
        }
    else:
        # DRF 未处理的异常
        if isinstance(exc, DatabaseError):
            # 数据库错误
            logger.error(f"数据库错误: {log_data}", exc_info=True)
            response = Response({
                'ret': False,
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'msg': '数据库操作失败，请稍后重试',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # 其他未知错误
            logger.error(f"系统错误: {log_data}", exc_info=True)
            response = Response({
                'ret': False,
                'code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'msg': '服务器内部错误，请稍后重试',
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


def get_error_message(exc, response):
    """获取友好的错误提示信息。
    
    Args:
        exc: 异常对象
        response: 响应对象
        
    Returns:
        str: 错误提示信息
    """
    if isinstance(exc, AuthenticationFailed):
        return '认证失败，请重新登录'
    elif isinstance(exc, NotAuthenticated):
        return '请先登录'
    elif isinstance(exc, PermissionDenied):
        return '没有权限执行此操作'
    elif isinstance(exc, ValidationError):
        # 格式化验证错误
        if isinstance(response.data, dict):
            errors = []
            for field, error_list in response.data.items():
                if isinstance(error_list, list):
                    errors.append(f"{field}: {', '.join(error_list)}")
                else:
                    errors.append(f"{field}: {error_list}")
            return '; '.join(errors) if errors else '参数验证失败'
        return '参数验证失败'
    elif isinstance(exc, Throttled):
        return '请求过于频繁，请稍后重试'
    elif isinstance(exc, APIException):
        return str(exc.detail) if hasattr(exc, 'detail') else str(exc)
    else:
        # 尝试从 response 中提取错误信息
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                return response.data['detail']
            elif 'msg' in response.data:
                return response.data['msg']
        return '操作失败，请稍后重试'


# 自定义业务异常
class BusinessException(APIException):
    """业务逻辑异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '业务处理失败'
    default_code = 'business_error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        self.detail = {'ret': False, 'code': code, 'msg': detail, 'data': None}


class ResourceNotFoundException(BusinessException):
    """资源不存在异常"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = '请求的资源不存在'
    default_code = 'resource_not_found'


class ParameterException(BusinessException):
    """参数错误异常"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = '参数错误'
    default_code = 'parameter_error'
