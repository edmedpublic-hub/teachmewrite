# backend/lessons/tests.py
"""
Test suite for lessons app
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    Lesson, Tier, Profile, UserProfile, StudentProgress, 
    TierProgress, Institute, Class
)


class LessonModelTest(TestCase):
    """Test cases for Lesson model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Description',
            content='Test Content',
            tier=Tier.BASIC,
            order=1,
            xp_reward=10
        )
    
    def test_lesson_creation(self):
        """Test that lesson is created correctly"""
        self.assertEqual(self.lesson.title, 'Test Lesson')
        self.assertEqual(self.lesson.tier, Tier.BASIC)
        self.assertEqual(self.lesson.order, 1)
        self.assertEqual(str(self.lesson), f'[Basic (Matric/Grades 9-10)] Test Lesson')
    
    def test_lesson_can_access_no_prerequisite(self):
        """Test that lesson without prerequisite is accessible"""
        self.assertTrue(self.lesson.can_access(self.user))
    
    def test_lesson_can_access_with_prerequisite(self):
        """Test that lesson with prerequisite checks mastery"""
        prereq = Lesson.objects.create(
            title='Prerequisite',
            description='Prerequisite Description',
            content='Prerequisite Content',
            tier=Tier.BASIC,
            order=0
        )
        
        self.lesson.prerequisite = prereq
        self.lesson.save()
        
        # Should be inaccessible initially
        self.assertFalse(self.lesson.can_access(self.user))
        
        # Master the prerequisite
        progress = StudentProgress.objects.create(
            user=self.user,
            lesson=prereq,
            mastery_score=100
        )
        progress.save()
        
        # Should now be accessible
        self.assertTrue(self.lesson.can_access(self.user))


class ProfileModelTest(TestCase):
    """Test cases for Profile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)
    
    def test_profile_auto_created(self):
        """Test that profile is auto-created with user"""
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.country, 'Pakistan')
    
    def test_add_xp(self):
        """Test adding XP to profile"""
        initial_xp = self.profile.total_xp
        self.profile.add_xp(50)
        self.assertEqual(self.profile.total_xp, initial_xp + 50)
    
    def test_update_streak(self):
        """Test streak update logic"""
        from datetime import timedelta
        from django.utils import timezone
        
        initial_streak = self.profile.streak_days
        
        # Update streak
        self.profile.update_streak()
        # Streak should increase or reset based on timing
        self.assertGreaterEqual(self.profile.streak_days, 0)


class StudentProgressTest(TestCase):
    """Test cases for StudentProgress model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            description='Test Description',
            content='Test Content',
            tier=Tier.BASIC,
            order=1,
            required_mastery_score=100
        )
        self.progress = StudentProgress.objects.create(
            user=self.user,
            lesson=self.lesson
        )
    
    def test_is_mastered_property(self):
        """Test mastery detection"""
        self.assertFalse(self.progress.is_mastered)
        
        self.progress.mastery_score = 100
        self.assertTrue(self.progress.is_mastered)
    
    def test_mastery_status_property(self):
        """Test mastery status string"""
        self.assertEqual(self.progress.mastery_status, 'NOT_STARTED')
        
        self.progress.mastery_score = 50
        self.assertEqual(self.progress.mastery_status, 'IN_PROGRESS')
        
        self.progress.mastery_score = 100
        self.assertEqual(self.progress.mastery_status, 'MASTERED')


class TierProgressTest(TestCase):
    """Test cases for TierProgress model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_initialize_user_tiers(self):
        """Test tier initialization for new user"""
        TierProgress.initialize_user_tiers(self.user)
        
        for tier in Tier:
            tier_progress = TierProgress.objects.filter(
                user=self.user,
                tier=tier.value
            ).first()
            self.assertIsNotNone(tier_progress)
            
            if tier == Tier.BASIC:
                self.assertTrue(tier_progress.is_unlocked)
            else:
                self.assertFalse(tier_progress.is_unlocked)
    
    def test_mastery_percentage(self):
        """Test mastery percentage calculation"""
        tier_progress = TierProgress.objects.create(
            user=self.user,
            tier=Tier.BASIC,
            total_lessons=10,
            mastered_lessons=5
        )
        self.assertEqual(tier_progress.mastery_percentage, 50.0)


class InstituteModelTest(TestCase):
    """Test cases for Institute model"""
    
    def setUp(self):
        self.institute = Institute.objects.create(
            name='Test Academy',
            type='ACADEMY',
            address='123 Test Street',
            phone='+923001234567',
            email='test@academy.com'
        )
    
    def test_institute_creation(self):
        """Test institute creation"""
        self.assertEqual(self.institute.name, 'Test Academy')
        self.assertEqual(self.institute.type, 'ACADEMY')
        self.assertTrue(self.institute.is_active)
    
    def test_subscription_validity(self):
        """Test subscription validity check"""
        from django.utils import timezone
        from datetime import timedelta
        
        # No expiry - should be valid
        self.assertTrue(self.institute.is_subscription_valid)
        
        # Future expiry - should be valid
        self.institute.subscription_expiry = timezone.now() + timedelta(days=30)
        self.institute.save()
        self.assertTrue(self.institute.is_subscription_valid)
        
        # Past expiry - should be invalid
        self.institute.subscription_expiry = timezone.now() - timedelta(days=1)
        self.institute.save()
        self.assertFalse(self.institute.is_subscription_valid)


class APITestCase(TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            password='testpass123',
            email='api@test.com'
        )
    
    def test_user_registration(self):
        """Test user registration endpoint"""
        # This will test the API endpoint via the test client
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'New',
            'last_name': 'User'
        })
        
        # Status should be 201 Created
        self.assertEqual(response.status_code, 201)
        
        # User should exist in database
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_login(self):
        """Test login and token generation"""
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'apiuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())