from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from django.db.models import Count, Q, F
from django.core.exceptions import ValidationError
import uuid
import hashlib
from .managers import LessonManager, StudentProgressManager

# ============================================
# ENUMS & CHOICES
# ============================================

class Tier(models.TextChoices):
    """4-Tier mastery levels for Pakistani educational system"""
    BASIC = 'BASIC', 'Basic (Matric/Grades 9-10)'
    INTERMEDIATE = 'INTERMEDIATE', 'Intermediate (Grades 11-12/FSc)'
    ADVANCED = 'ADVANCED', 'Advanced (Graduation/Bachelors)'
    PROFESSIONAL = 'PROFESSIONAL', 'Professional (CSS/Competitive Exams)'
    
    @classmethod
    def get_next_tier(cls, current_tier):
        """Get the next tier in progression"""
        tier_order = [cls.BASIC, cls.INTERMEDIATE, cls.ADVANCED, cls.PROFESSIONAL]
        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                return tier_order[current_index + 1]
        except ValueError:
            pass
        return None

class UserRole(models.TextChoices):
    """User roles for multi-tenant support"""
    STUDENT = 'STUDENT', 'Student'
    TEACHER = 'TEACHER', 'Teacher'
    PARENT = 'PARENT', 'Parent'
    INSTITUTE_ADMIN = 'INSTITUTE_ADMIN', 'Institute Admin'
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'

class InstituteType(models.TextChoices):
    """Types of educational institutions"""
    SCHOOL = 'SCHOOL', 'School'
    COLLEGE = 'COLLEGE', 'College'
    UNIVERSITY = 'UNIVERSITY', 'University'
    ACADEMY = 'ACADEMY', 'Academy'
    CSS_CENTER = 'CSS_CENTER', 'CSS Preparation Center'
    TUTION_CENTER = 'TUTION_CENTER', 'Tuition Center'

class AnnouncementAudience(models.TextChoices):
    """Target audience for announcements"""
    ALL = 'ALL', 'All Users'
    STUDENTS = 'STUDENTS', 'Students Only'
    TEACHERS = 'TEACHERS', 'Teachers Only'
    PARENTS = 'PARENTS', 'Parents Only'
    INSTITUTE = 'INSTITUTE', 'Institute Specific'
    CLASS = 'CLASS', 'Class Specific'

# ============================================
# PROFILE MODELS (Existing - Enhanced)
# ============================================

class Profile(models.Model):
    """Extended user profile for additional student information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal information
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be in international format")]
    )
    date_of_birth = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Pakistan')
    cnic = models.CharField(max_length=20, blank=True, null=True, help_text="CNIC/B-Form Number")
    
    # Educational information
    EDUCATION_LEVELS = [
        ('MATRIC', 'Matric (9th/10th)'),
        ('INTERMEDIATE', 'Intermediate (11th/12th)'),
        ('BACHELORS', 'Bachelors'),
        ('MASTERS', 'Masters'),
        ('CSS', 'CSS Candidate'),
        ('PHD', 'PhD'),
        ('OTHER', 'Other'),
    ]
    education_level = models.CharField(
        max_length=20,
        choices=EDUCATION_LEVELS,
        blank=True,
        null=True
    )
    institution = models.CharField(max_length=200, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Learning preferences
    target_exam = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="e.g., CSS, NTS, University Admission, IELTS"
    )
    target_tier = models.CharField(
        max_length=20,
        choices=Tier.choices,
        blank=True,
        null=True,
        help_text="Student's target learning tier"
    )
    
    # Statistics
    total_xp = models.IntegerField(default=0)
    streak_days = models.IntegerField(default=0)
    last_active = models.DateTimeField(auto_now=True)
    total_lessons_completed = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['education_level']),
            models.Index(fields=['target_tier']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['cnic']),
        ]
    
    def __str__(self):
        return f"Profile for {self.user.username}"
    
    def update_streak(self):
        """Update daily learning streak"""
        from datetime import timedelta
        
        today = timezone.now().date()
        last_active_date = self.last_active.date()
        
        if last_active_date == today:
            return
        
        if last_active_date == today - timedelta(days=1):
            self.streak_days += 1
        else:
            self.streak_days = 1
        
        self.last_active = timezone.now()
        self.save()
    
    def add_xp(self, amount):
        """Add XP to user profile and check for level up"""
        self.total_xp += amount
        self.save()
        return self.total_xp
    
    def update_average_score(self, new_score):
        """Update average mastery score"""
        if self.total_lessons_completed == 0:
            self.average_score = new_score
        else:
            self.average_score = (self.average_score * self.total_lessons_completed + new_score) / (self.total_lessons_completed + 1)
        self.total_lessons_completed += 1
        self.save()

# ============================================
# INSTITUTE MANAGEMENT MODELS (New)
# ============================================

class Institute(models.Model):
    """Educational institution model for multi-tenant support"""
    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=InstituteType.choices, default=InstituteType.ACADEMY)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='institute_logos/', blank=True, null=True)
    
    # Subscription
    subscription_plan = models.CharField(
        max_length=50, 
        default='BASIC',
        choices=[
            ('BASIC', 'Basic'),
            ('PRO', 'Professional'),
            ('ENTERPRISE', 'Enterprise'),
        ]
    )
    subscription_expiry = models.DateTimeField(null=True, blank=True)
    max_students = models.IntegerField(default=100)
    max_teachers = models.IntegerField(default=10)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['subscription_expiry']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    @property
    def is_subscription_valid(self):
        """Check if subscription is still valid"""
        if not self.subscription_expiry:
            return True
        return self.subscription_expiry > timezone.now()

class UserProfile(models.Model):
    """Extended user profile with role and institute association"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.STUDENT)
    institute = models.ForeignKey(Institute, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    
    # Contact information
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    # For teachers
    qualification = models.CharField(max_length=200, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    experience_years = models.IntegerField(default=0)
    joining_date = models.DateField(null=True, blank=True)
    
    # For parents
    linked_students = models.ManyToManyField(User, related_name='parents', blank=True, limit_choices_to={'user_profile__role': UserRole.STUDENT})
    
    # Metadata
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['institute']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    def has_permission(self, required_role):
        """Check if user has required role or higher"""
        role_hierarchy = {
            UserRole.STUDENT: 0,
            UserRole.PARENT: 1,
            UserRole.TEACHER: 2,
            UserRole.INSTITUTE_ADMIN: 3,
            UserRole.SUPER_ADMIN: 4,
        }
        return role_hierarchy.get(self.role, -1) >= role_hierarchy.get(required_role, -1)

class Class(models.Model):
    """Class/Group model for organizing students"""
    name = models.CharField(max_length=100)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, related_name='classes')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='classes_teaching', limit_choices_to={'user_profile__role': UserRole.TEACHER})
    students = models.ManyToManyField(User, related_name='classes_enrolled', blank=True, limit_choices_to={'user_profile__role': UserRole.STUDENT})
    
    # Academic information
    grade_level = models.CharField(max_length=50, help_text="e.g., 9th, 10th, 11th, 12th, Graduation, CSS")
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    section = models.CharField(max_length=10, blank=True, help_text="e.g., A, B, C")
    
    # Schedule
    schedule = models.JSONField(default=dict, blank=True, help_text="Class schedule JSON")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Classes"
        unique_together = ['institute', 'name', 'academic_year']
        indexes = [
            models.Index(fields=['institute', 'is_active']),
            models.Index(fields=['teacher']),
            models.Index(fields=['grade_level']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.grade_level}) - {self.academic_year}"
    
    @property
    def student_count(self):
        return self.students.count()

# ============================================
# LESSON MODELS (Existing - Enhanced)
# ============================================

class Lesson(models.Model):
    objects = LessonManager()
    """Main lesson model with tier-based progression"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="URL-friendly version of title")
    description = models.TextField()
    content = models.TextField(help_text="Main lesson content/teaching material")
    
    # Metadata
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.BASIC, db_index=True)
    order = models.IntegerField(default=0, db_index=True)
    prerequisite = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_lessons')
    
    # Mastery requirements
    required_mastery_score = models.FloatField(default=100.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    practice_questions = models.JSONField(default=list, help_text="List of practice exercises")
    test_criteria = models.JSONField(default=dict, help_text="Test passing criteria")
    
    # Gamification
    xp_reward = models.IntegerField(default=10)
    estimated_duration_minutes = models.IntegerField(default=30, help_text="Estimated time to complete lesson")
    
    # Media
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or Vimeo URL")
    attachments = models.JSONField(default=list, blank=True, help_text="List of attachment URLs")
    
    # Status
    is_published = models.BooleanField(default=True)
    is_free = models.BooleanField(default=False, help_text="Free preview lesson")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='lessons_created')
    
    class Meta:
        ordering = ['tier', 'order']
        unique_together = ['tier', 'order']
        indexes = [
            models.Index(fields=['tier', 'order']),
            models.Index(fields=['prerequisite']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"[{self.get_tier_display()}] {self.title}"
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def can_access(self, user):
        """Check if user has completed prerequisite lesson with mastery"""
        if not self.prerequisite:
            return True
        try:
            progress = StudentProgress.objects.get(user=user, lesson=self.prerequisite)
            return progress.is_mastered
        except StudentProgress.DoesNotExist:
            return False

# ============================================
# PROGRESS TRACKING MODELS (Existing)
# ============================================

class StudentProgress(models.Model):
    objects = StudentProgressManager()
    """Track individual lesson progress for students"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    
    # Mastery tracking
    is_completed = models.BooleanField(default=False)
    mastery_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    attempts = models.IntegerField(default=0)
    
    # Detailed tracking
    practice_attempts = models.IntegerField(default=0)
    test_attempts = models.IntegerField(default=0)
    last_practice_score = models.FloatField(default=0.0)
    last_test_score = models.FloatField(default=0.0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    last_attempt_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # For analytics
    time_spent_seconds = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['user', 'lesson']
        indexes = [
            models.Index(fields=['user', 'is_completed']),
            models.Index(fields=['user', 'mastery_score']),
            models.Index(fields=['completed_at']),
        ]
    
    @property
    def is_mastered(self):
        """Check if lesson is mastered (100% required by default)"""
        return self.mastery_score >= self.lesson.required_mastery_score
    
    @property
    def mastery_status(self):
        if self.is_mastered:
            return "MASTERED"
        elif self.mastery_score > 0:
            return "IN_PROGRESS"
        return "NOT_STARTED"
    
    def save(self, *args, **kwargs):
        """Override save to update tier progress and XP when mastered"""
        was_mastered = False
        if self.pk:
            try:
                old = StudentProgress.objects.get(pk=self.pk)
                was_mastered = old.is_mastered
            except StudentProgress.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # If newly mastered, update tier progress and award XP
        if not was_mastered and self.is_mastered:
            # Update tier progress
            tier_progress, created = TierProgress.objects.get_or_create(
                user=self.user,
                tier=self.lesson.tier
            )
            tier_progress.update_progress()
            
            # Award XP
            if hasattr(self.user, 'profile'):
                self.user.profile.add_xp(self.lesson.xp_reward)
                self.user.profile.update_average_score(self.mastery_score)
            
            # Update streak
            if hasattr(self.user, 'profile'):
                self.user.profile.update_streak()

class TierProgress(models.Model):
    """Track overall progress per tier for a user"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tier_progress')
    tier = models.CharField(max_length=20, choices=Tier.choices)
    
    # Statistics
    total_lessons = models.IntegerField(default=0)
    mastered_lessons = models.IntegerField(default=0)
    completed_lessons = models.IntegerField(default=0)
    
    # Mastery requirement for tier completion
    is_unlocked = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'tier']
        indexes = [
            models.Index(fields=['user', 'tier', 'is_completed']),
            models.Index(fields=['is_unlocked']),
        ]
    
    @property
    def mastery_percentage(self):
        if self.total_lessons == 0:
            return 0.0
        return (self.mastered_lessons / self.total_lessons) * 100
    
    def update_progress(self):
        """Recalculate progress from individual lesson progress"""
        lessons = Lesson.objects.filter(tier=self.tier, is_published=True)
        self.total_lessons = lessons.count()
        
        progress_stats = StudentProgress.objects.filter(
            user=self.user,
            lesson__tier=self.tier,
            lesson__is_published=True
        ).aggregate(
            mastered=Count('id', filter=Q(mastery_score__gte=F('lesson__required_mastery_score'))),
            completed=Count('id', filter=Q(is_completed=True))
        )
        
        self.mastered_lessons = progress_stats['mastered'] or 0
        self.completed_lessons = progress_stats['completed'] or 0
        
        # Auto-mark tier as completed if all lessons mastered
        if self.mastered_lessons == self.total_lessons and self.total_lessons > 0:
            self.is_completed = True
            if not self.completed_at:
                self.completed_at = timezone.now()
        
        self.save()
        return self
    
    @classmethod
    def initialize_user_tiers(cls, user):
        """Initialize tier progress for a new user"""
        tiers_created = []
        for tier in Tier:
            tier_progress, created = cls.objects.get_or_create(
                user=user,
                tier=tier.value,
                defaults={
                    'is_unlocked': tier == Tier.BASIC,
                    'total_lessons': Lesson.objects.filter(tier=tier.value, is_published=True).count()
                }
            )
            tiers_created.append(tier_progress)
        return tiers_created

# ============================================
# ASSIGNMENT MODELS (New)
# ============================================

class Assignment(models.Model):
    """Teacher-created assignments for students"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments_created')
    assigned_to_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='assignments')
    
    # Assignment details
    total_points = models.IntegerField(default=100)
    due_date = models.DateTimeField()
    allowed_attempts = models.IntegerField(default=1)
    
    # Instructions and resources
    instructions = models.TextField(blank=True)
    resources = models.JSONField(default=list, blank=True, help_text="Additional resources URLs")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
        indexes = [
            models.Index(fields=['assigned_to_class', 'is_active']),
            models.Index(fields=['due_date']),
            models.Index(fields=['lesson']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to_class.name}"
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now()
    
    @property
    def submission_count(self):
        return self.submissions.count()

class AssignmentSubmission(models.Model):
    """Student submissions for assignments"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    
    # Submission content
    content = models.TextField()
    attachments = models.JSONField(default=list, blank=True, help_text="Uploaded files URLs")
    
    # Grading
    score = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)])
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_late = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['assignment', 'student']
        indexes = [
            models.Index(fields=['assignment', 'student']),
            models.Index(fields=['submitted_at']),
            models.Index(fields=['score']),
        ]
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    
    def save(self, *args, **kwargs):
        """Check if submission is late"""
        if self.assignment.due_date < timezone.now():
            self.is_late = True
        super().save(*args, **kwargs)

# ============================================
# COMMUNICATION MODELS (New)
# ============================================

class Announcement(models.Model):
    """System announcements and notifications"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    
    # Targeting
    target_audience = models.CharField(max_length=20, choices=AnnouncementAudience.choices, default=AnnouncementAudience.ALL)
    institute = models.ForeignKey(Institute, on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
    class_target = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
    
    # Priority and expiry
    priority = models.CharField(max_length=20, choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High'), ('URGENT', 'Urgent')], default='MEDIUM')
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['target_audience', 'is_active']),
            models.Index(fields=['institute']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_priority_display()})"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return self.expires_at < timezone.now()
        return False

class Certificate(models.Model):
    """Completion certificates for tiers"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    tier = models.CharField(max_length=20, choices=Tier.choices)
    certificate_number = models.CharField(max_length=100, unique=True)
    
    # Certificate details
    issue_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='certificates/%Y/%m/', null=True, blank=True)
    shareable_link = models.CharField(max_length=200, unique=True)
    
    # Verification
    verification_code = models.CharField(max_length=50, unique=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['user', 'tier']),
            models.Index(fields=['certificate_number']),
            models.Index(fields=['verification_code']),
        ]
    
    def __str__(self):
        return f"Certificate #{self.certificate_number} - {self.user.username} - {self.get_tier_display()}"
    
    def save(self, *args, **kwargs):
        """Generate certificate number and verification code if not provided"""
        if not self.certificate_number:
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.certificate_number = f"MAI-{self.tier}-{self.user.id}-{timestamp}"
        if not self.verification_code:
            self.verification_code = hashlib.md5(f"{self.certificate_number}{uuid.uuid4()}".encode()).hexdigest()[:12].upper()
        if not self.shareable_link:
            self.shareable_link = f"/certificate/verify/{self.verification_code}"
        super().save(*args, **kwargs)

# ============================================
# HELPER FUNCTIONS
# ============================================

from django.utils.text import slugify

def get_student_summary(user):
    """Get comprehensive summary for a student"""
    from django.db.models import Avg
    
    tier_progress = TierProgress.objects.filter(user=user)
    total_mastery = tier_progress.aggregate(avg_mastery=Avg('mastery_percentage'))['avg_mastery'] or 0
    
    return {
        'total_xp': user.profile.total_xp if hasattr(user, 'profile') else 0,
        'streak_days': user.profile.streak_days if hasattr(user, 'profile') else 0,
        'overall_mastery': total_mastery,
        'tiers': {
            tp.tier: {
                'mastery': tp.mastery_percentage,
                'completed': tp.is_completed,
                'mastered_lessons': tp.mastered_lessons,
                'total_lessons': tp.total_lessons
            } for tp in tier_progress
        }
    }
    
# ============================================
# NEW ADAPTIVE LEARNING MODELS (Add at the end of models.py)
# ============================================

class Unit(models.Model):
    """Major curriculum divisions - Groups lessons into learning units"""
    TIER_CHOICES = [
        ('BASIC', 'Basic'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
        ('PROFESSIONAL', 'Professional'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    tier = models.CharField(max_length=20, choices=TIER_CHOICES)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        ordering = ['tier', 'order']
    
    def __str__(self):
        return f"{self.tier} - {self.title}"

class LessonUnit(models.Model):
    """Link lessons to units with additional metadata"""
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='lesson_links')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='unit_links')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # Teaching phase settings
    teaching_content = models.TextField(blank=True, help_text="Specific teaching content for this lesson in this unit")
    examples = models.JSONField(default=list, blank=True, help_text="Examples in JSON format")
    
    # Mastery settings for this specific lesson
    practice_pass_threshold = models.IntegerField(default=70)
    test_pass_threshold = models.IntegerField(default=80)
    max_practice_attempts = models.IntegerField(default=5)
    
    # Prerequisites
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    class Meta:
        ordering = ['unit', 'order']
        unique_together = ['unit', 'lesson']
    
    def __str__(self):
        return f"{self.unit.title} - {self.lesson.title}"

class QuestionBank(models.Model):
    """Bank of all questions for practice and testing"""
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('JUMBLE', 'Jumbled Sentence'),
        ('COMPLETION', 'Sentence Completion'),
        ('FREE_WRITING', 'Free Writing'),
        ('IDENTIFY', 'Identify Component'),
        ('CORRECT', 'Error Correction'),
    ]
    
    DIFFICULTY_LEVELS = [
        (1, 'Very Easy'),
        (2, 'Easy'),
        (3, 'Medium'),
        (4, 'Hard'),
        (5, 'Very Hard'),
    ]
    
    lesson_unit = models.ForeignKey(LessonUnit, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty = models.IntegerField(choices=DIFFICULTY_LEVELS, default=3)
    
    # Question content
    question_text = models.TextField()
    correct_answer = models.TextField()
    options = models.JSONField(blank=True, null=True, help_text="For MCQ: list of options")
    explanation = models.TextField(blank=True, help_text="Explanation for correct answer")
    
    # Metadata
    tags = models.JSONField(default=list, help_text="Tags for categorization (e.g., ['subject', 'verb', 'object'])")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.lesson_unit.lesson.title} - {self.question_type} (Difficulty: {self.difficulty})"

class StudentLessonProgress(models.Model):
    """Track individual student progress through lesson units"""
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('TEACHING', 'Teaching Phase'),
        ('PRACTICE', 'Practice Phase'),
        ('TEST', 'Test Phase'),
        ('COMPLETED', 'Completed'),
        ('LOCKED', 'Locked'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson_unit = models.ForeignKey(LessonUnit, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    
    # Practice tracking
    practice_attempts = models.IntegerField(default=0)
    practice_best_score = models.IntegerField(default=0)
    practice_last_score = models.IntegerField(default=0)
    
    # Test tracking
    test_attempts = models.IntegerField(default=0)
    test_best_score = models.IntegerField(default=0)
    test_last_score = models.IntegerField(default=0)
    
    # Question tracking
    questions_answered = models.JSONField(default=list, help_text="Track answered question IDs")
    mastered_concepts = models.JSONField(default=list, help_text="Concepts mastered in this lesson")
    weak_concepts = models.JSONField(default=list, help_text="Concepts needing review")
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'lesson_unit']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson_unit.lesson.title} - {self.status}"

class PracticeSession(models.Model):
    """Record each practice session"""
    student_progress = models.ForeignKey(StudentLessonProgress, on_delete=models.CASCADE, related_name='practice_sessions')
    questions_asked = models.JSONField()
    answers_given = models.JSONField()
    score = models.IntegerField()
    time_spent = models.IntegerField(help_text="Time in seconds")
    completed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Practice {self.id} - Score: {self.score}"

class TestSession(models.Model):
    """Record each test attempt"""
    student_progress = models.ForeignKey(StudentLessonProgress, on_delete=models.CASCADE, related_name='test_sessions')
    questions_asked = models.JSONField()
    answers_given = models.JSONField()
    score = models.IntegerField()
    passed = models.BooleanField(default=False)
    time_spent = models.IntegerField(help_text="Time in seconds")
    completed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Test {self.id} - Passed: {self.passed}"