# 自定义限流类

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """登录接口限流，限制每分钟5次"""
    scope = 'login'


class CustomAnonRateThrottle(AnonRateThrottle):
    """自定义匿名用户限流"""
    scope = 'anon'


class CustomUserRateThrottle(UserRateThrottle):
    """自定义登录用户限流"""
    scope = 'user'
