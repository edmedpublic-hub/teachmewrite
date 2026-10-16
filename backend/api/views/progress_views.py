# backend/api/views/progress_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models as django_models
from django.db.models import Q, Count, Avg, F
from lessons.models import Lesson, StudentProgress, TierProgress, Tier, Profile
from ..serializers import ProgressSerializer, TierProgressSerializer


class ProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for tracking user progress"""
    queryset = StudentProgress.objects.none()
    serializer_class = ProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return StudentProgress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get progress summary across all tiers"""
        user = request.user
        
        tier_progress = TierProgress.objects.filter(user=user)
        tier_serializer = TierProgressSerializer(tier_progress, many=True)
        
        total_lessons = Lesson.objects.filter(is_published=True).count()
        mastered_lessons = StudentProgress.objects.filter(
            user=user,
            mastery_score__gte=F('lesson__required_mastery_score')
        ).count()
        
        active_tier = None
        for tier in [Tier.BASIC, Tier.INTERMEDIATE, Tier.ADVANCED, Tier.PROFESSIONAL]:
            try:
                tp = TierProgress.objects.get(user=user, tier=tier)
                if not tp.is_completed and tp.is_unlocked:
                    active_tier = tier
                    break
                elif not tp.is_completed and tier == Tier.BASIC:
                    active_tier = tier
                    break
            except TierProgress.DoesNotExist:
                if tier == Tier.BASIC:
                    active_tier = tier
        
        return Response({
            'tier_progress': tier_serializer.data,
            'overall': {
                'total_lessons': total_lessons,
                'mastered_lessons': mastered_lessons,
                'completion_percentage': (mastered_lessons / total_lessons * 100) if total_lessons > 0 else 0
            },
            'active_tier': active_tier,
            'next_tier': self._get_next_tier(user)
        })
    
    def _get_next_tier(self, user):
        for tier in [Tier.BASIC, Tier.INTERMEDIATE, Tier.ADVANCED, Tier.PROFESSIONAL]:
            try:
                tp = TierProgress.objects.get(user=user, tier=tier)
                if not tp.is_completed:
                    return tier
            except TierProgress.DoesNotExist:
                return tier
        return None


class TierProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tier-level progress"""
    queryset = TierProgress.objects.none()
    serializer_class = TierProgressSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TierProgress.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def unlock_tier(self, request):
        if not request.user.is_staff:
            return Response({'error': 'Admin only'}, status=status.HTTP_403_FORBIDDEN)
        
        tier = request.data.get('tier')
        if tier and tier.upper() in [t.value for t in Tier]:
            tier_progress, created = TierProgress.objects.get_or_create(
                user=request.user,
                tier=tier.upper()
            )
            tier_progress.is_unlocked = True
            tier_progress.save()
            return Response({'status': 'unlocked', 'tier': tier})
        
        return Response({'error': 'Invalid tier'}, status=status.HTTP_400_BAD_REQUEST)


def get_student_dashboard(request):
    """Get student dashboard data"""
    user = request.user
    profile = Profile.objects.get(user=user)
    tier_progress = TierProgress.objects.filter(user=user)
    recent_lessons = StudentProgress.objects.filter(user=user).order_by('-last_attempt_at')[:5]
    
    statistics = {
        'total_xp': profile.total_xp,
        'streak_days': profile.streak_days,
        'average_score': profile.average_score,
        'total_lessons_completed': profile.total_lessons_completed,
    }
    
    return Response({
        'profile': ProfileSerializer(profile).data,
        'tier_progress': TierProgressSerializer(tier_progress, many=True).data,
        'recent_lessons': ProgressSerializer(recent_lessons, many=True).data,
        'statistics': statistics
    })