# backend/lessons/signals.py
"""
Django signals for automatic profile creation and data integrity
"""

from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import logging

from .models import Profile, UserProfile, TierProgress, Tier, StudentProgress

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    """
    Create Profile and UserProfile automatically when a new User is created
    """
    if created:
        # Create Profile
        profile, profile_created = Profile.objects.get_or_create(
            user=instance,
            defaults={
                'country': 'Pakistan',
                'total_xp': 0,
                'streak_days': 0,
                'average_score': 0.0,
                'total_lessons_completed': 0
            }
        )
        
        # Create UserProfile with default role
        user_profile, up_created = UserProfile.objects.get_or_create(
            user=instance,
            defaults={
                'role': 'STUDENT',
                'phone': '',
                'address': '',
                'is_verified': False
            }
        )
        
        # Initialize tier progress for all tiers
        TierProgress.initialize_user_tiers(instance)
        
        if profile_created or up_created:
            logger.info(f"Auto-created profiles for new user: {instance.username}")


@receiver(post_save, sender=User)
def save_user_profiles(sender, instance, **kwargs):
    """
    Save Profile and UserProfile when User is saved
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
    if hasattr(instance, 'user_profile'):
        instance.user_profile.save()


@receiver(post_save, sender=StudentProgress)
def update_user_stats_on_mastery(sender, instance, created, **kwargs):
    """
    Update user's average score and total completed lessons when a lesson is mastered
    """
    if instance.is_mastered and (created or not hasattr(instance, '_mastery_processed')):
        # Mark as processed to avoid infinite loops
        instance._mastery_processed = True
        
        # Update user profile stats
        if hasattr(instance.user, 'profile'):
            profile = instance.user.profile
            profile.update_average_score(instance.mastery_score)
            
            if not profile.total_lessons_completed:
                profile.total_lessons_completed = 0
            profile.total_lessons_completed += 1
            profile.save()
            
            logger.debug(f"Updated stats for user {instance.user.username}: +1 mastered lesson")


@receiver(pre_save, sender=UserProfile)
def validate_user_profile(sender, instance, **kwargs):
    """
    Validate UserProfile before saving
    """
    # Teacher-specific validation
    if instance.role == 'TEACHER' and instance.experience_years < 0:
        raise ValidationError("Experience years cannot be negative")
    
    # Parent-specific validation - must have at least one linked student
    if instance.role == 'PARENT' and not instance.pk:
        # During creation, we can't check linked_students yet
        pass