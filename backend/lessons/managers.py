# backend/lessons/managers.py
"""
Custom model managers for efficient database queries
"""

from django.db import models
from django.db.models import Q, Count, Avg, F, Sum
from django.utils import timezone


class LessonManager(models.Manager):
    """Custom manager for Lesson model"""
    
    def published(self):
        """Return only published lessons"""
        return self.filter(is_published=True)
    
    def for_tier(self, tier):
        """Return lessons for specific tier"""
        return self.filter(tier=tier, is_published=True)
    
    def unlocked_for_user(self, user):
        """Return lessons unlocked for a specific user"""
        from .models import TierProgress, Tier
        
        unlocked_tiers = TierProgress.objects.filter(
            user=user, 
            is_unlocked=True
        ).values_list('tier', flat=True)
        
        if not unlocked_tiers:
            unlocked_tiers = [Tier.BASIC]
        
        return self.filter(tier__in=unlocked_tiers, is_published=True)
    
    def with_progress_for_user(self, user):
        """Annotate lessons with user's progress"""
        from .models import StudentProgress
        
        return self.published().annotate(
            user_mastery_score=models.Subquery(
                StudentProgress.objects.filter(
                    user=user,
                    lesson=models.OuterRef('pk')
                ).values('mastery_score')[:1]
            ),
            user_is_completed=models.Subquery(
                StudentProgress.objects.filter(
                    user=user,
                    lesson=models.OuterRef('pk')
                ).values('is_completed')[:1]
            )
        )
    
    def get_next_lesson(self, user, current_tier, current_order):
        """Get the next lesson in sequence"""
        return self.filter(
            tier=current_tier,
            order__gt=current_order,
            is_published=True
        ).order_by('order').first()


class StudentProgressManager(models.Manager):
    """Custom manager for StudentProgress model"""
    
    def mastered(self):
        """Return only mastered lessons"""
        return self.filter(mastery_score__gte=F('lesson__required_mastery_score'))
    
    def in_progress(self):
        """Return lessons in progress (started but not mastered)"""
        return self.filter(
            mastery_score__gt=0,
            mastery_score__lt=F('lesson__required_mastery_score')
        )
    
    def not_started(self):
        """Return lessons not started yet"""
        return self.filter(mastery_score=0)
    
    def for_user(self, user):
        """Return progress for specific user"""
        return self.filter(user=user)
    
    def for_tier(self, user, tier):
        """Return progress for specific tier"""
        return self.filter(user=user, lesson__tier=tier)
    
    def get_completion_rate(self, user):
        """Calculate completion rate for a user"""
        total = self.filter(user=user).count()
        completed = self.filter(user=user, is_completed=True).count()
        return (completed / total * 100) if total > 0 else 0
    
    def get_total_time_spent(self, user):
        """Get total time spent by user in seconds"""
        result = self.filter(user=user).aggregate(total=Sum('time_spent_seconds'))
        return result['total'] or 0
    
    def get_recent_activity(self, user, limit=10):
        """Get recent user activity"""
        return self.filter(user=user).order_by('-last_attempt_at')[:limit]


class TierProgressManager(models.Manager):
    """Custom manager for TierProgress model"""
    
    def for_user(self, user):
        """Return tier progress for specific user"""
        return self.filter(user=user)
    
    def completed_tiers(self, user):
        """Return tiers completed by user"""
        return self.filter(user=user, is_completed=True)
    
    def unlocked_tiers(self, user):
        """Return tiers unlocked for user"""
        return self.filter(user=user, is_unlocked=True)
    
    def get_current_tier(self, user):
        """Get the current active tier for user"""
        for tier in ['BASIC', 'INTERMEDIATE', 'ADVANCED', 'PROFESSIONAL']:
            try:
                tp = self.get(user=user, tier=tier)
                if not tp.is_completed:
                    return tp
            except self.model.DoesNotExist:
                continue
        return None
    
    def get_mastery_stats(self, user):
        """Get mastery statistics across all tiers"""
        return self.filter(user=user).aggregate(
            avg_mastery=Avg('mastery_percentage'),
            total_mastered=Sum('mastered_lessons'),
            total_lessons=Sum('total_lessons'),
            completed_tiers=Count('id', filter=Q(is_completed=True))
        )


class InstituteManager(models.Manager):
    """Custom manager for Institute model"""
    
    def active(self):
        """Return only active institutes"""
        return self.filter(is_active=True)
    
    def with_valid_subscription(self):
        """Return institutes with valid subscription"""
        return self.filter(
            is_active=True,
            subscription_expiry__gt=timezone.now()
        )
    
    def get_dashboard_stats(self, institute):
        """Get dashboard statistics for an institute"""
        from .models import UserProfile, Class, StudentProgress
        
        students = UserProfile.objects.filter(institute=institute, role='STUDENT')
        teachers = UserProfile.objects.filter(institute=institute, role='TEACHER')
        classes = Class.objects.filter(institute=institute)
        
        # Calculate average mastery
        avg_mastery = StudentProgress.objects.filter(
            user__in=students.values_list('user', flat=True)
        ).aggregate(avg=Avg('mastery_score'))['avg'] or 0
        
        return {
            'total_students': students.count(),
            'total_teachers': teachers.count(),
            'total_classes': classes.count(),
            'average_mastery': avg_mastery
        }


class ClassManager(models.Manager):
    """Custom manager for Class model"""
    
    def active(self):
        """Return only active classes"""
        return self.filter(is_active=True)
    
    def for_teacher(self, teacher):
        """Return classes taught by a teacher"""
        return self.filter(teacher=teacher, is_active=True)
    
    def for_student(self, student):
        """Return classes a student is enrolled in"""
        return self.filter(students=student, is_active=True)
    
    def get_class_stats(self, class_obj):
        """Get statistics for a class"""
        students = class_obj.students.all()
        
        from .models import StudentProgress
        
        avg_mastery = StudentProgress.objects.filter(
            user__in=students
        ).aggregate(avg=Avg('mastery_score'))['avg'] or 0
        
        return {
            'total_students': students.count(),
            'average_mastery': avg_mastery,
            'assignments_count': class_obj.assignments.count()
        }