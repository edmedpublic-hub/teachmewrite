# backend/api/views/institute_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from lessons.models import (
    Institute, UserProfile, Class, Assignment, AssignmentSubmission, 
    StudentProgress, TierProgress, Tier, Certificate, Profile
)
from ..serializers import (
    InstituteSerializer, UserProfileSerializer, ClassSerializer
)
import logging

logger = logging.getLogger(__name__)


class InstituteViewSet(viewsets.ModelViewSet):
    """ViewSet for institute management"""
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or (hasattr(user, 'user_profile') and user.user_profile.role == 'SUPER_ADMIN'):
            return Institute.objects.all()
        elif hasattr(user, 'user_profile') and user.user_profile.institute:
            return Institute.objects.filter(id=user.user_profile.institute.id)
        return Institute.objects.none()
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a member to the institute"""
        if not request.user.is_staff and request.user.user_profile.role not in ['SUPER_ADMIN', 'INSTITUTE_ADMIN']:
            return Response({'error': 'Unauthorized'}, status=403)
        
        institute = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role')
        
        if not user_id or not role:
            return Response({'error': 'user_id and role required'}, status=400)
        
        try:
            user = User.objects.get(id=user_id)
            user_profile, created = UserProfile.objects.get_or_create(user=user)
            user_profile.institute = institute
            user_profile.role = role
            user_profile.save()
            
            logger.info(f"Added user {user.username} to institute {institute.name} as {role}")
            return Response({'status': 'member added', 'user': user.username, 'role': role})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for user profiles with roles"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=user)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class ClassViewSet(viewsets.ModelViewSet):
    """ViewSet for class/group management"""
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Class.objects.all()
        elif hasattr(user, 'user_profile'):
            if user.user_profile.role == 'TEACHER':
                return Class.objects.filter(teacher=user)
            elif user.user_profile.role == 'STUDENT':
                return Class.objects.filter(students=user)
            elif user.user_profile.institute:
                return Class.objects.filter(institute=user.user_profile.institute)
        return Class.objects.none()
    
    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """Add a student to the class"""
        class_obj = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id required'}, status=400)
        
        try:
            student = User.objects.get(id=user_id)
            class_obj.students.add(student)
            logger.info(f"Added student {student.username} to class {class_obj.name}")
            return Response({'status': 'student added', 'student': student.username})
        except User.DoesNotExist:
            return Response({'error': 'Student not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teacher_dashboard(request):
    """Teacher view of their classes and assignments"""
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role != 'TEACHER':
        return Response({'error': 'Unauthorized - Teacher access only'}, status=403)
    
    teacher = request.user
    classes = Class.objects.filter(teacher=teacher)
    
    dashboard_data = {
        'classes': [],
        'total_students': 0,
        'pending_assignments': 0,
        'pending_submissions': 0
    }
    
    for class_obj in classes:
        students = class_obj.students.all()
        assignments = Assignment.objects.filter(assigned_to_class=class_obj)
        pending_submissions = AssignmentSubmission.objects.filter(
            assignment__in=assignments,
            score__isnull=True
        ).count()
        
        class_data = {
            'id': class_obj.id,
            'name': class_obj.name,
            'grade_level': class_obj.grade_level,
            'academic_year': class_obj.academic_year,
            'student_count': students.count(),
            'assignment_count': assignments.count(),
            'pending_submissions': pending_submissions
        }
        
        dashboard_data['classes'].append(class_data)
        dashboard_data['total_students'] += students.count()
        dashboard_data['pending_assignments'] += assignments.count()
        dashboard_data['pending_submissions'] += pending_submissions
    
    return Response(dashboard_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def institute_dashboard(request):
    """Institute admin dashboard"""
    if not hasattr(request.user, 'user_profile'):
        return Response({'error': 'User profile not found'}, status=404)
    
    institute = request.user.user_profile.institute
    if not institute:
        return Response({'error': 'No institute associated'}, status=400)
    
    # Get all students in institute
    students = UserProfile.objects.filter(institute=institute, role='STUDENT')
    teachers = UserProfile.objects.filter(institute=institute, role='TEACHER')
    classes = Class.objects.filter(institute=institute)
    
    # Calculate institute-wide stats
    total_students = students.count()
    active_students = StudentProgress.objects.filter(
        user__in=students.values_list('user', flat=True),
        last_attempt_at__gte=timezone.now() - timedelta(days=7)
    ).values('user').distinct().count()
    
    # Average mastery across institute
    avg_mastery = StudentProgress.objects.filter(
        user__in=students.values_list('user', flat=True)
    ).aggregate(avg=Avg('mastery_score'))['avg'] or 0
    
    # Tier breakdown
    tier_breakdown = {}
    for tier in Tier:
        completed_count = TierProgress.objects.filter(
            user__in=students.values_list('user', flat=True),
            tier=tier.value,
            is_completed=True
        ).count()
        tier_breakdown[tier.label] = {
            'completed': completed_count,
            'percentage': (completed_count / total_students * 100) if total_students > 0 else 0
        }
    
    return Response({
        'institute': {
            'id': institute.id,
            'name': institute.name,
            'type': institute.type,
            'subscription_plan': institute.subscription_plan,
            'is_active': institute.is_active
        },
        'statistics': {
            'total_students': total_students,
            'active_students': active_students,
            'total_teachers': teachers.count(),
            'total_classes': classes.count(),
            'average_mastery': round(avg_mastery, 1)
        },
        'tier_breakdown': tier_breakdown
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def parent_dashboard(request):
    """Parent view of their children's progress"""
    if not hasattr(request.user, 'user_profile') or request.user.user_profile.role != 'PARENT':
        return Response({'error': 'Unauthorized - Parent access only'}, status=403)
    
    children = request.user.user_profile.linked_students.all()
    children_data = []
    
    for child in children:
        # Get child's profile
        child_profile = Profile.objects.filter(user=child).first()
        
        # Get child's progress summary
        tier_progress = TierProgress.objects.filter(user=child)
        total_mastery = tier_progress.aggregate(avg=Avg('mastery_percentage'))['avg'] or 0
        
        # Get recent activity
        recent_activity = StudentProgress.objects.filter(
            user=child
        ).order_by('-last_attempt_at')[:5].values('lesson__title', 'mastery_score', 'last_attempt_at')
        
        # Get certificates
        certificates = Certificate.objects.filter(user=child)
        
        children_data.append({
            'id': child.id,
            'name': child.get_full_name() or child.username,
            'email': child.email,
            'overall_mastery': round(total_mastery, 1),
            'streak_days': child_profile.streak_days if child_profile else 0,
            'total_xp': child_profile.total_xp if child_profile else 0,
            'recent_activity': list(recent_activity),
            'certificates_count': certificates.count()
        })
    
    return Response({'children': children_data})