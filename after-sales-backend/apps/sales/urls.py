from django.conf.urls.static import static
from django.conf import settings
from django.urls import path
from sales import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', views.TokenLoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('SelYgbhInfo/', views.SelYgbhInfo.as_view(), name="SelYgbhInfo"),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('complaints/', views.ComplaintCreateView.as_view(), name='complaint_create'),
    path('complaints/<int:pk>/', views.ComplaintDetailView.as_view(), name='complaint_detail'),
    path('routing-sheet/', views.RoutingSheetQueryView.as_view(), name='routing_sheet_query'),
]
# 添加这行 允许所有的media文件被访问
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
