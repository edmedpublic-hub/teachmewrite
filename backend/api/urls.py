# backend/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()

# Core Learning Endpoints
router.register(r'lessons', views.LessonViewSet, basename='lesson')
router.register(r'progress', views.ProgressViewSet, basename='progress')
router.register(r'tier-progress', views.TierProgressViewSet, basename='tier-progress')

# User Management Endpoints
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'user-profiles', views.UserProfileViewSet, basename='user-profile')

# Institute Management Endpoints
router.register(r'institutes', views.InstituteViewSet, basename='institute')
router.register(r'classes', views.ClassViewSet, basename='class')

# Assignment Endpoints
router.register(r'assignments', views.AssignmentViewSet, basename='assignment')

# Certificate Endpoints
router.register(r'certificates', views.CertificateViewSet, basename='certificate')
router.register(r'units', views.UnitViewSet, basename='unit')
router.register(r'lesson-units', views.LessonUnitViewSet, basename='lesson-unit')
router.register(r'questions', views.QuestionBankViewSet, basename='question')
router.register(r'student-progress', views.StudentLessonProgressViewSet, basename='student-progress')

urlpatterns = [
    # API Root
    path('', include(router.urls)),
    
    # Authentication Endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', views.register, name='register'),
    path('auth/change-password/', views.change_password, name='change_password'),
    
    # Adaptive Learning Endpoints (from adaptive_views)
    path('adaptive/units/<int:unit_id>/lessons/<int:lesson_id>/', 
         views.get_lesson_unit, name='get_lesson_unit'),
    path('adaptive/practice/<int:lesson_unit_id>/questions/', 
         views.get_practice_questions, name='get_practice_questions'),
    path('adaptive/practice/<int:lesson_unit_id>/submit/', 
         views.submit_practice, name='submit_practice'),
    path('adaptive/test/<int:lesson_unit_id>/questions/', 
         views.get_test_questions, name='get_test_questions'),
    path('adaptive/test/<int:lesson_unit_id>/submit/', 
         views.submit_test, name='submit_test'),
    
    # AI & Diagnostics
    path('diagnose-tier/', views.diagnose_tier, name='diagnose_tier'),
    
    # Reports
    path('mastery-report/', views.mastery_report, name='mastery_report'),
    path('export-report/', views.export_report, name='export_report'),
    
    # Dashboards
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('institute-dashboard/', views.institute_dashboard, name='institute_dashboard'),
    path('parent-dashboard/', views.parent_dashboard, name='parent_dashboard'),
]