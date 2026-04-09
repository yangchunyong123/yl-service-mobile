from django.conf import settings
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend
from .models import After_sales_index_login


class AfterSalesJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """解析并校验 JWT，返回用户与 token 载荷。"""
        auth = get_authorization_header(request).split()
        if not auth:
            return None
        if auth[0].lower() != b'bearer':
            return None
        if len(auth) != 2:
            raise AuthenticationFailed('Authorization 头格式错误')
        raw_token = auth[1].decode('utf-8')
        token_backend = TokenBackend(
            algorithm=settings.SIMPLE_JWT.get('ALGORITHM', 'HS256'),
            signing_key=settings.SIMPLE_JWT.get('SIGNING_KEY', settings.SECRET_KEY),
            verifying_key=settings.SIMPLE_JWT.get('VERIFYING_KEY', ''),
        )
        try:
            validated_token = token_backend.decode(raw_token, verify=True)
        except Exception:
            raise AuthenticationFailed('Token 无效或已过期')
        if validated_token.get('token_type') != 'access':
            raise AuthenticationFailed('仅允许使用 access token')
        user_id = validated_token.get('user_id')
        if not user_id:
            raise AuthenticationFailed('Token 缺少用户信息')
        user = After_sales_index_login.objects.filter(id=user_id).first()
        if not user:
            raise AuthenticationFailed('用户不存在')
        return user, validated_token

    def authenticate_header(self, request):
        """返回认证头类型提示。"""
        return 'Bearer'
