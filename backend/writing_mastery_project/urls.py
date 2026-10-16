from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # 1. Admin Dashboard
    path('admin/', admin.site.urls),

    # 2. Authentication API (JWT)
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 3. Main API v1 (All endpoints)
    # This includes lessons, progress, users, etc.
    path('api/v1/', include('api.urls')),
    
    # 4. Legacy lessons URLs (if needed - consider removing)
    # path('api/lessons/', include('lessons.urls')),  # Comment this out if using api.urls
]