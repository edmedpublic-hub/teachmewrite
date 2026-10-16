# backend/lessons/services.py
"""
Business logic services for lessons app
"""

from django.db.models import Q, F, Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    Lesson, StudentProgress, TierProgress, Profile,
    Institute, UserProfile, Class, Assignment, 
    AssignmentSubmission, Announcement, Certificate, Tier
)

logger = logging.getLogger(__name__)


class MasteryService:
    """Service for mastery-based learning logic"""
    
    @staticmethod
    def calculate_mastery_score(practice_score, test_score, practice_weight=0.3, test_weight=0.7):
        """
        Calculate overall mastery score from practice and test scores
        """
        return (practice_score * practice_weight) + (test_score * test_weight)
    
    @staticmethod
    def check_tier_completion(user, tier):
        """
        Check if a user has completed all lessons in a tier
        """
        tier_progress = TierProgress.objects.filter(user=user, tier=tier).first()
        if not tier_progress:
            return False
        
        return tier_progress.mastered_lessons == tier_progress.total_lessons
    
    @staticmethod
    def unlock_next_tier(user, current_tier):
        """
        Unlock the next tier if current tier is completed
        """
        next_tier = Tier.get_next_tier(current_tier)
        if not next_tier:
            return None
        
        if MasteryService.check_tier_completion(user, current_tier):
            tier_progress, _ = TierProgress.objects.get_or_create(
                user=user,
                tier=next_tier
            )
            tier_progress.is_unlocked = True
            tier_progress.save()
            logger.info(f"Unlocked {next_tier} for user {user.username}")
            return next_tier
        
        return None
    
    @staticmethod
    def get_next_lesson(user, current_tier, current_order):
        """
        Get the next recommended lesson for a user
        """
        next_lesson = Lesson.objects.filter(
            tier=current_tier,
            order__gt=current_order,
            is_published=True
        ).order_by('order').first()
        
        if not next_lesson:
            # Check if there are lessons in the next tier
            next_tier = Tier.get_next_tier(current_tier)
            if next_tier and MasteryService.check_tier_completion(user, current_tier):
                next_lesson = Lesson.objects.filter(
                    tier=next_tier,
                    order=1,
                    is_published=True
                ).first()
        
        return next_lesson


class AnalyticsService:
    """Service for analytics and reporting"""
    
    @staticmethod
    def get_user_analytics(user, days=30):
        """
        Get comprehensive analytics for a user
        """
        since_date = timezone.now() - timedelta(days=days)
        
        progress = StudentProgress.objects.filter(
            user=user,
            last_attempt_at__gte=since_date
        )
        
        return {
            'total_lessons_attempted': progress.count(),
            'total_lessons_mastered': progress.filter(
                mastery_score__gte=F('lesson__required_mastery_score')
            ).count(),
            'average_score': progress.aggregate(avg=Avg('mastery_score'))['avg'] or 0,
            'total_time_spent': progress.aggregate(total=Sum('time_spent_seconds'))['total'] or 0,
            'streak_days': user.profile.streak_days if hasattr(user, 'profile') else 0,
            'total_xp': user.profile.total_xp if hasattr(user, 'profile') else 0,
        }
    
    @staticmethod
    def get_institute_analytics(institute):
        """
        Get analytics for an institute
        """
        students = UserProfile.objects.filter(institute=institute, role='STUDENT')
        student_users = [sp.user for sp in students]
        
        progress = StudentProgress.objects.filter(user__in=student_users)
        
        return {
            'total_students': students.count(),
            'total_lessons_completed': progress.filter(is_completed=True).count(),
            'average_mastery': progress.aggregate(avg=Avg('mastery_score'))['avg'] or 0,
            'active_students': progress.filter(
                last_attempt_at__gte=timezone.now() - timedelta(days=7)
            ).values('user').distinct().count(),
            'tier_breakdown': AnalyticsService._get_tier_breakdown(students)
        }
    
    @staticmethod
    def _get_tier_breakdown(students):
        """Helper method for tier breakdown"""
        breakdown = {}
        for tier in Tier:
            completed = 0
            for student in students:
                if MasteryService.check_tier_completion(student.user, tier.value):
                    completed += 1
            breakdown[tier.label] = {
                'completed': completed,
                'percentage': (completed / students.count() * 100) if students.count() > 0 else 0
            }
        return breakdown


class NotificationService:
    """Service for sending notifications"""
    
    @staticmethod
    def send_assignment_notification(assignment, submission=None):
        """
        Send notifications for assignments
        """
        from api.communication import CommunicationManager
        
        if submission:
            # Notify teacher about new submission
            message = f"Student {submission.student.get_full_name()} has submitted '{assignment.title}'"
            CommunicationManager.send_email_report(
                assignment.assigned_by.email,
                f"New Submission: {assignment.title}",
                message
            )
        else:
            # Notify students about new assignment
            for student in assignment.assigned_to_class.students.all():
                message = f"New assignment '{assignment.title}' is due on {assignment.due_date}"
                if hasattr(student, 'profile') and student.profile.phone_number:
                    CommunicationManager.send_whatsapp_message(
                        student.profile.phone_number,
                        message
                    )
    
    @staticmethod
    def send_certificate_notification(certificate):
        """
        Send notification when certificate is generated
        """
        from api.communication import CommunicationManager
        
        message = f"Congratulations! You have earned a certificate for completing {certificate.get_tier_display()} tier!"
        
        CommunicationManager.send_email_report(
            certificate.user.email,
            f"Certificate Awarded: {certificate.get_tier_display()} Tier",
            message
        )
        
        if hasattr(certificate.user, 'profile') and certificate.user.profile.phone_number:
            CommunicationManager.send_whatsapp_message(
                certificate.user.profile.phone_number,
                message
            )


class ReportService:
    """Service for generating reports"""
    
    @staticmethod
    def generate_student_report(user, format='json'):
        """
        Generate comprehensive student report
        """
        from api.report_utils import ReportGenerator
        
        progress = StudentProgress.objects.filter(user=user)
        tier_progress = TierProgress.objects.filter(user=user)
        
        data = {
            'user': {
                'name': user.get_full_name(),
                'email': user.email,
                'joined': user.date_joined
            },
            'overall': {
                'total_lessons': Lesson.objects.filter(is_published=True).count(),
                'mastered_lessons': progress.filter(
                    mastery_score__gte=F('lesson__required_mastery_score')
                ).count(),
                'average_score': progress.aggregate(avg=Avg('mastery_score'))['avg'] or 0,
                'total_time': progress.aggregate(total=Sum('time_spent_seconds'))['total'] or 0,
            },
            'tiers': [
                {
                    'name': tp.get_tier_display(),
                    'mastery': tp.mastery_percentage,
                    'completed': tp.is_completed
                }
                for tp in tier_progress
            ]
        }
        
        generator = ReportGenerator(user, data)
        
        if format == 'pdf':
            return generator.generate_pdf_report()
        elif format == 'csv':
            return generator.generate_csv_report()
        else:
            return data