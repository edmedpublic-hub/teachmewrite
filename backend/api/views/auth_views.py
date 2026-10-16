# backend/api/views/auth_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from lessons.models import Profile, UserProfile, TierProgress
from ..serializers import UserSerializer, ProfileSerializer, RegisterSerializer, ChangePasswordSerializer
import logging

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get', 'put'])
    def profile(self, request):
        """Get or update user profile"""
        user = request.user
        
        if request.method == 'GET':
            profile, created = Profile.objects.get_or_create(user=user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PUT':
            profile, created = Profile.objects.get_or_create(user=user)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get user-specific dashboard based on role"""
        user = request.user
        
        if hasattr(user, 'user_profile'):
            role = user.user_profile.role
            
            if role == 'STUDENT':
                from .progress_views import get_student_dashboard
                return get_student_dashboard(request)
            elif role == 'TEACHER':
                from .institute_views import teacher_dashboard
                return teacher_dashboard(request)
            elif role == 'INSTITUTE_ADMIN':
                from .institute_views import institute_dashboard
                return institute_dashboard(request)
            elif role == 'PARENT':
                from .institute_views import parent_dashboard
                return parent_dashboard(request)
        
        # Default student dashboard
        from .progress_views import get_student_dashboard
        return get_student_dashboard(request)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """User registration endpoint"""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change password endpoint"""
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if not user.check_password(serializer.data['old_password']):
            return Response({'error': 'Wrong password'}, status=400)
        
        user.set_password(serializer.data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'})
    return Response(serializer.errors, status=400)