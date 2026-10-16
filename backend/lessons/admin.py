from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import (
    Lesson, StudentProgress, TierProgress, Profile,
    Institute, UserProfile, Class, Assignment, 
    AssignmentSubmission, Announcement, Certificate,
    Unit, LessonUnit, QuestionBank, StudentLessonProgress,
    PracticeSession, TestSession
)

# ============================================
# INLINE ADMIN CLASSES
# ============================================

class ProfileInline(admin.StackedInline):
    """Inline profile editing in User admin"""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Personal Information', {
            'fields': ('phone_number', 'date_of_birth', 'cnic', 'city', 'country')
        }),
        ('Educational Information', {
            'fields': ('education_level', 'institution', 'roll_number')
        }),
        ('Learning Preferences', {
            'fields': ('target_exam', 'target_tier')
        }),
        ('Statistics', {
            'fields': ('total_xp', 'streak_days', 'average_score', 'total_lessons_completed'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('total_xp', 'streak_days', 'average_score', 'total_lessons_completed')

class UserProfileInline(admin.StackedInline):
    """Inline user profile editing in User admin"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Role & Institute'
    fieldsets = (
        ('Role & Institute', {
            'fields': ('role', 'institute', 'is_verified')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Teacher Information', {
            'fields': ('qualification', 'specialization', 'experience_years', 'joining_date'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login_ip')

class StudentInline(admin.TabularInline):
    """Inline students in Class admin"""
    model = Class.students.through
    verbose_name = "Student"
    verbose_name_plural = "Students"
    extra = 1
    raw_id_fields = ('user',)

# ============================================
# CUSTOM USER ADMIN (ONLY ONE DEFINITION)
# ============================================

# Unregister the default User admin first
admin.site.unregister(User)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User admin with profile and role integration"""
    inlines = [ProfileInline, UserProfileInline]
    list_display = (
        'username', 'email', 'first_name', 'last_name', 
        'get_role', 'get_institute', 'get_total_xp', 'is_staff'
    )
    list_filter = (
        'is_staff', 'is_superuser', 'is_active', 'groups',
        'user_profile__role', 'user_profile__institute'
    )
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__phone_number')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': (),
            'classes': ('collapse',)
        }),
    )
    
    def get_role(self, obj):
        if hasattr(obj, 'user_profile'):
            return obj.user_profile.get_role_display()
        return 'Student'
    get_role.short_description = 'Role'
    get_role.admin_order_field = 'user_profile__role'
    
    def get_institute(self, obj):
        if hasattr(obj, 'user_profile') and obj.user_profile.institute:
            return obj.user_profile.institute.name
        return '-'
    get_institute.short_description = 'Institute'
    get_institute.admin_order_field = 'user_profile__institute'
    
    def get_total_xp(self, obj):
        if hasattr(obj, 'profile'):
            return format_html('<b>{}</b>', obj.profile.total_xp)
        return 0
    get_total_xp.short_description = 'Total XP'
    get_total_xp.admin_order_field = 'profile__total_xp'

# ============================================
# PROFILE ADMIN
# ============================================

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'education_level', 'target_tier', 'total_xp', 
        'streak_days', 'average_score', 'get_phone'
    ]
    list_filter = ['education_level', 'target_tier', 'country', 'created_at']
    search_fields = ['user__username', 'user__email', 'city', 'institution', 'cnic']
    readonly_fields = ['total_xp', 'streak_days', 'average_score', 'total_lessons_completed', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Personal Information', {
            'fields': ('phone_number', 'date_of_birth', 'cnic', 'city', 'country')
        }),
        ('Educational Background', {
            'fields': ('education_level', 'institution', 'roll_number')
        }),
        ('Learning Goals', {
            'fields': ('target_exam', 'target_tier')
        }),
        ('Performance Statistics', {
            'fields': ('total_xp', 'streak_days', 'average_score', 'total_lessons_completed', 'last_active'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_phone(self, obj):
        return obj.phone_number or '-'
    get_phone.short_description = 'Phone Number'

# ============================================
# INSTITUTE ADMIN
# ============================================

@admin.register(Institute)
class InstituteAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'type', 'phone', 'email', 'subscription_plan', 
        'is_active', 'member_count', 'subscription_status'
    ]
    list_filter = ['type', 'subscription_plan', 'is_active', 'created_at']
    search_fields = ['name', 'email', 'phone', 'address']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'type', 'address', 'phone', 'email', 'website', 'logo')
        }),
        ('Subscription Details', {
            'fields': ('subscription_plan', 'subscription_expiry', 'max_students', 'max_teachers')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def member_count(self, obj):
        count = UserProfile.objects.filter(institute=obj).count()
        return format_html('<b>{}</b>', count)
    member_count.short_description = 'Members'
    
    def subscription_status(self, obj):
        if obj.is_subscription_valid:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Expired</span>')
    subscription_status.short_description = 'Subscription'

# ============================================
# USER PROFILE ADMIN
# ============================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'role', 'institute', 'is_verified', 'get_linked_students'
    ]
    list_filter = ['role', 'is_verified', 'institute', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone', 'qualification']
    readonly_fields = ['created_at', 'updated_at', 'last_login_ip']
    raw_id_fields = ['user', 'institute', 'linked_students']
    
    fieldsets = (
        ('User & Role', {
            'fields': ('user', 'role', 'institute', 'is_verified')
        }),
        ('Contact Information', {
            'fields': ('phone', 'address')
        }),
        ('Teacher Information', {
            'fields': ('qualification', 'specialization', 'experience_years', 'joining_date'),
            'classes': ('collapse',)
        }),
        ('Parent Information', {
            'fields': ('linked_students',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('last_login_ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_linked_students(self, obj):
        count = obj.linked_students.count()
        if count > 0:
            return format_html('<b>{}</b> students', count)
        return '-'
    get_linked_students.short_description = 'Linked Students'

# ============================================
# CLASS ADMIN
# ============================================

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'institute', 'teacher', 'grade_level', 
        'academic_year', 'student_count', 'is_active'
    ]
    list_filter = ['institute', 'grade_level', 'academic_year', 'is_active', 'created_at']
    search_fields = ['name', 'teacher__username', 'teacher__email', 'section']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['teacher', 'students']
    inlines = [StudentInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'institute', 'teacher', 'grade_level', 'academic_year', 'section')
        }),
        ('Schedule & Status', {
            'fields': ('schedule', 'is_active')
        }),
        ('Students', {
            'fields': ('students',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def student_count(self, obj):
        count = obj.students.count()
        return format_html('<b>{}</b>', count)
    student_count.short_description = 'Students'

# ============================================
# LESSON ADMIN
# ============================================

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'tier', 'order', 'required_mastery_score', 
        'xp_reward', 'is_published', 'lesson_preview'
    ]
    list_filter = ['tier', 'is_published', 'created_at', 'is_free']
    search_fields = ['title', 'description', 'slug']
    ordering = ['tier', 'order']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['prerequisite', 'created_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'content', 'tier', 'order')
        }),
        ('Prerequisites', {
            'fields': ('prerequisite',)
        }),
        ('Mastery Settings', {
            'fields': ('required_mastery_score', 'xp_reward', 'estimated_duration_minutes')
        }),
        ('Media & Resources', {
            'fields': ('video_url', 'attachments'),
            'classes': ('collapse',)
        }),
        ('Assessment Content', {
            'fields': ('practice_questions', 'test_criteria'),
            'classes': ('collapse',)
        }),
        ('Publication', {
            'fields': ('is_published', 'is_free', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def lesson_preview(self, obj):
        if obj.video_url:
            return format_html('<a href="{}" target="_blank">🎥 Watch</a>', obj.video_url)
        return '-'
    lesson_preview.short_description = 'Preview'

# ============================================
# STUDENT PROGRESS ADMIN
# ============================================

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'lesson', 'mastery_score', 'mastery_badge', 
        'attempts', 'started_at', 'time_spent'
    ]
    list_filter = [
        'is_completed', 'lesson__tier', 'started_at', 'completed_at'
    ]
    search_fields = ['user__username', 'user__email', 'lesson__title']
    readonly_fields = [
        'started_at', 'last_attempt_at', 'completed_at', 'time_spent_seconds'
    ]
    date_hierarchy = 'started_at'
    raw_id_fields = ['user', 'lesson']
    
    fieldsets = (
        ('Student & Lesson', {
            'fields': ('user', 'lesson')
        }),
        ('Mastery Tracking', {
            'fields': ('mastery_score', 'is_completed', 'attempts')
        }),
        ('Detailed Scores', {
            'fields': ('practice_attempts', 'test_attempts', 'last_practice_score', 'last_test_score'),
            'classes': ('collapse',)
        }),
        ('Time Tracking', {
            'fields': ('time_spent_seconds', 'started_at', 'last_attempt_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def mastery_badge(self, obj):
        if obj.is_mastered:
            return format_html('<span style="color: green; font-size: 16px;">✓ Mastered</span>')
        elif obj.mastery_score > 0:
            return format_html('<span style="color: orange;">⟳ In Progress</span>')
        return format_html('<span style="color: gray;">○ Not Started</span>')
    mastery_badge.short_description = 'Status'
    
    def time_spent(self, obj):
        if obj.time_spent_seconds > 0:
            hours = obj.time_spent_seconds // 3600
            minutes = (obj.time_spent_seconds % 3600) // 60
            return f"{hours}h {minutes}m"
        return '-'
    time_spent.short_description = 'Time Spent'

# ============================================
# TIER PROGRESS ADMIN
# ============================================

@admin.register(TierProgress)
class TierProgressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'tier', 'mastery_progress_bar', 'mastered_lessons', 
        'total_lessons', 'is_completed', 'is_unlocked'
    ]
    list_filter = ['tier', 'is_completed', 'is_unlocked', 'last_updated']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['mastery_percentage', 'last_updated']
    raw_id_fields = ['user']
    date_hierarchy = 'last_updated'
    
    fieldsets = (
        ('User & Tier', {
            'fields': ('user', 'tier')
        }),
        ('Progress Statistics', {
            'fields': ('mastered_lessons', 'completed_lessons', 'total_lessons')
        }),
        ('Status', {
            'fields': ('is_unlocked', 'is_completed', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    def mastery_progress_bar(self, obj):
        percentage = obj.mastery_percentage
        color = 'green' if percentage >= 80 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<div style="background: #f0f0f0; border-radius: 10px; overflow: hidden; width: 100px;">'
            '<div style="background: {}; width: {}%; text-align: center; color: white; font-size: 10px;">{:.0f}%</div></div>',
            color, percentage, percentage
        )
    mastery_progress_bar.short_description = 'Progress'
    
    def mastery_percentage(self, obj):
        return f"{obj.mastery_percentage:.1f}%"
    mastery_percentage.short_description = 'Mastery %'

# ============================================
# ASSIGNMENT ADMIN
# ============================================

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'assigned_to_class', 'assigned_by', 'due_date', 
        'submission_count', 'is_overdue'
    ]
    list_filter = ['assigned_to_class__institute', 'due_date', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'assigned_by__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'due_date'
    raw_id_fields = ['lesson', 'assigned_by', 'assigned_to_class']
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('title', 'description', 'lesson', 'assigned_by', 'assigned_to_class')
        }),
        ('Grading & Timeline', {
            'fields': ('total_points', 'due_date', 'allowed_attempts')
        }),
        ('Instructions & Resources', {
            'fields': ('instructions', 'resources'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">⚠ Overdue</span>')
        return format_html('<span style="color: green;">✓ On Time</span>')
    is_overdue.short_description = 'Status'
    
    def submission_count(self, obj):
        return obj.submission_count
    submission_count.short_description = 'Submissions'

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = [
        'assignment', 'student', 'score', 'submitted_at', 
        'is_late', 'grading_status'
    ]
    list_filter = ['assignment__assigned_to_class', 'is_late', 'graded_at']
    search_fields = ['student__username', 'assignment__title', 'feedback']
    readonly_fields = ['submitted_at', 'updated_at']
    raw_id_fields = ['assignment', 'student', 'graded_by']
    date_hierarchy = 'submitted_at'
    
    fieldsets = (
        ('Submission Details', {
            'fields': ('assignment', 'student')
        }),
        ('Content', {
            'fields': ('content', 'attachments')
        }),
        ('Grading', {
            'fields': ('score', 'feedback', 'graded_by', 'graded_at')
        }),
        ('Status', {
            'fields': ('is_late',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def grading_status(self, obj):
        if obj.score is not None:
            return format_html('<span style="color: green;">✓ Graded ({:.0f}%)</span>', obj.score)
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    grading_status.short_description = 'Grading'

# ============================================
# ANNOUNCEMENT ADMIN
# ============================================

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'target_audience', 'priority_badge', 
        'created_at', 'is_active', 'is_expired_status'
    ]
    list_filter = ['target_audience', 'priority', 'is_active', 'institute', 'created_at']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    raw_id_fields = ['author', 'institute', 'class_target']
    
    fieldsets = (
        ('Announcement Content', {
            'fields': ('title', 'content', 'author')
        }),
        ('Target Audience', {
            'fields': ('target_audience', 'institute', 'class_target')
        }),
        ('Priority & Expiry', {
            'fields': ('priority', 'expires_at')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def priority_badge(self, obj):
        colors = {
            'LOW': 'gray',
            'MEDIUM': 'blue',
            'HIGH': 'orange',
            'URGENT': 'red'
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.priority, 'gray'), obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def is_expired_status(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    is_expired_status.short_description = 'Expiry'

# ============================================
# CERTIFICATE ADMIN
# ============================================

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = [
        'certificate_number', 'user', 'tier', 'issue_date', 
        'expiry_date', 'verification_badge', 'share_link'
    ]
    list_filter = ['tier', 'issue_date', 'is_verified']
    search_fields = ['certificate_number', 'verification_code', 'user__username', 'user__email']
    readonly_fields = [
        'certificate_number', 'verification_code', 'shareable_link', 
        'issue_date', 'pdf_file'
    ]
    raw_id_fields = ['user']
    date_hierarchy = 'issue_date'
    
    fieldsets = (
        ('Certificate Information', {
            'fields': ('user', 'tier', 'certificate_number', 'verification_code')
        }),
        ('Dates', {
            'fields': ('issue_date', 'expiry_date')
        }),
        ('Files & Links', {
            'fields': ('pdf_file', 'shareable_link')
        }),
        ('Verification', {
            'fields': ('is_verified',)
        }),
    )
    
    def verification_badge(self, obj):
        if obj.is_verified:
            return format_html('<span style="color: green;">✓ Verified</span>')
        return format_html('<span style="color: orange;">⚠ Pending</span>')
    verification_badge.short_description = 'Verification'
    
    def share_link(self, obj):
        if obj.shareable_link:
            return format_html(
                '<a href="{}" target="_blank">🔗 Share</a>',
                obj.shareable_link
            )
        return '-'
    share_link.short_description = 'Share Link'
    
# ============================================
# NEW ADAPTIVE LEARNING ADMIN CLASSES
# ============================================

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin for Unit - curriculum units"""
    list_display = ['title', 'tier', 'order', 'is_active', 'lesson_count', 'created_at']
    list_filter = ['tier', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['tier', 'order']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'tier', 'order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def lesson_count(self, obj):
        count = obj.lesson_links.filter(is_active=True).count()
        return format_html('<b>{}</b> lessons', count)
    lesson_count.short_description = 'Lessons'


@admin.register(LessonUnit)
class LessonUnitAdmin(admin.ModelAdmin):
    """Admin for LessonUnit - links lessons to units"""
    list_display = [
        'get_lesson_title', 'get_unit_title', 'order', 'practice_pass_threshold',
        'test_pass_threshold', 'max_practice_attempts', 'question_count', 'is_active'
    ]
    list_filter = ['unit__tier', 'is_active', 'unit', 'created_at']
    search_fields = ['lesson__title', 'lesson__description', 'unit__title']
    ordering = ['unit', 'order']
    list_editable = ['order', 'practice_pass_threshold', 'test_pass_threshold', 'max_practice_attempts', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['lesson', 'unit']
    filter_horizontal = ['prerequisites']
    
    fieldsets = (
        ('Unit & Lesson', {
            'fields': ('unit', 'lesson', 'order')
        }),
        ('Teaching Content', {
            'fields': ('teaching_content', 'examples')
        }),
        ('Mastery Settings', {
            'fields': ('practice_pass_threshold', 'test_pass_threshold', 'max_practice_attempts')
        }),
        ('Prerequisites', {
            'fields': ('prerequisites',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_lesson_title(self, obj):
        return obj.lesson.title
    get_lesson_title.short_description = 'Lesson'
    get_lesson_title.admin_order_field = 'lesson__title'
    
    def get_unit_title(self, obj):
        return obj.unit.title
    get_unit_title.short_description = 'Unit'
    get_unit_title.admin_order_field = 'unit__title'
    
    def question_count(self, obj):
        count = obj.questions.filter(is_active=True).count()
        color = 'green' if count > 0 else 'red'
        return format_html('<span style="color: {};">{}</span>', color, count)
    question_count.short_description = 'Questions'


@admin.register(QuestionBank)
class QuestionBankAdmin(admin.ModelAdmin):
    """Admin for QuestionBank - practice and test questions"""
    list_display = [
        'short_question', 'lesson_unit', 'question_type', 'difficulty', 
        'tags_preview', 'is_active', 'created_at'
    ]
    list_filter = ['question_type', 'difficulty', 'is_active', 'lesson_unit__unit__tier', 'created_at']
    search_fields = ['question_text', 'correct_answer', 'explanation', 'tags']
    ordering = ['-created_at']
    list_editable = ['difficulty', 'is_active']
    readonly_fields = ['created_at']
    raw_id_fields = ['lesson_unit']
    
    fieldsets = (
        ('Question Details', {
            'fields': ('lesson_unit', 'question_type', 'difficulty', 'question_text', 'correct_answer')
        }),
        ('Options & Explanation', {
            'fields': ('options', 'explanation')
        }),
        ('Metadata', {
            'fields': ('tags', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def short_question(self, obj):
        text = obj.question_text[:60]
        return f"{text}..." if len(obj.question_text) > 60 else text
    short_question.short_description = 'Question'
    
    def tags_preview(self, obj):
        if obj.tags:
            tags = obj.tags[:3]
            display = ', '.join(tags)
            if len(obj.tags) > 3:
                display += f' +{len(obj.tags) - 3}'
            return format_html('<span style="font-size: 11px;">{}</span>', display)
        return '-'
    tags_preview.short_description = 'Tags'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lesson_unit', 'lesson_unit__lesson', 'lesson_unit__unit')


@admin.register(StudentLessonProgress)
class StudentLessonProgressAdmin(admin.ModelAdmin):
    """Admin for StudentLessonProgress - tracks individual student progress"""
    list_display = [
        'user', 'lesson_title', 'status_badge', 'practice_best_score', 
        'test_best_score', 'practice_attempts', 'test_attempts', 'last_activity'
    ]
    list_filter = ['status', 'lesson_unit__unit__tier', 'lesson_unit__lesson', 'completed_at']
    search_fields = ['user__username', 'user__email', 'lesson_unit__lesson__title']
    readonly_fields = ['started_at', 'last_activity', 'completed_at']
    raw_id_fields = ['user', 'lesson_unit']
    date_hierarchy = 'last_activity'
    
    fieldsets = (
        ('Student & Lesson', {
            'fields': ('user', 'lesson_unit')
        }),
        ('Current Status', {
            'fields': ('status',)
        }),
        ('Practice Performance', {
            'fields': ('practice_attempts', 'practice_best_score', 'practice_last_score')
        }),
        ('Test Performance', {
            'fields': ('test_attempts', 'test_best_score', 'test_last_score')
        }),
        ('Concept Mastery', {
            'fields': ('mastered_concepts', 'weak_concepts', 'questions_answered'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('started_at', 'last_activity', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def lesson_title(self, obj):
        return obj.lesson_unit.lesson.title
    lesson_title.short_description = 'Lesson'
    lesson_title.admin_order_field = 'lesson_unit__lesson__title'
    
    def status_badge(self, obj):
        colors = {
            'NOT_STARTED': 'gray',
            'TEACHING': 'blue',
            'PRACTICE': 'orange',
            'TEST': 'purple',
            'COMPLETED': 'green',
            'LOCKED': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'lesson_unit', 'lesson_unit__lesson')


@admin.register(PracticeSession)
class PracticeSessionAdmin(admin.ModelAdmin):
    """Admin for PracticeSession - records practice attempts"""
    list_display = [
        'id', 'student_name', 'lesson_title', 'score_badge', 
        'time_spent_formatted', 'completed_at'
    ]
    list_filter = ['completed_at']
    search_fields = ['student_progress__user__username', 'student_progress__lesson_unit__lesson__title']
    readonly_fields = ['questions_asked', 'answers_given', 'score', 'time_spent', 'completed_at']
    raw_id_fields = ['student_progress']
    date_hierarchy = 'completed_at'
    
    fieldsets = (
        ('Session Info', {
            'fields': ('student_progress',)
        }),
        ('Performance', {
            'fields': ('score', 'time_spent')
        }),
        ('Details', {
            'fields': ('questions_asked', 'answers_given'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('completed_at',),
            'classes': ('collapse',)
        }),
    )
    
    def student_name(self, obj):
        return obj.student_progress.user.username
    student_name.short_description = 'Student'
    student_name.admin_order_field = 'student_progress__user__username'
    
    def lesson_title(self, obj):
        return obj.student_progress.lesson_unit.lesson.title
    lesson_title.short_description = 'Lesson'
    
    def score_badge(self, obj):
        color = 'green' if obj.score >= 70 else 'orange' if obj.score >= 50 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, obj.score)
    score_badge.short_description = 'Score'
    
    def time_spent_formatted(self, obj):
        minutes = obj.time_spent // 60
        seconds = obj.time_spent % 60
        return f"{minutes}m {seconds}s"
    time_spent_formatted.short_description = 'Time Spent'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student_progress', 'student_progress__user', 'student_progress__lesson_unit__lesson')


@admin.register(TestSession)
class TestSessionAdmin(admin.ModelAdmin):
    """Admin for TestSession - records test attempts"""
    list_display = [
        'id', 'student_name', 'lesson_title', 'score_badge', 
        'passed_badge', 'time_spent_formatted', 'completed_at'
    ]
    list_filter = ['passed', 'completed_at']
    search_fields = ['student_progress__user__username', 'student_progress__lesson_unit__lesson__title']
    readonly_fields = ['questions_asked', 'answers_given', 'score', 'passed', 'time_spent', 'completed_at']
    raw_id_fields = ['student_progress']
    date_hierarchy = 'completed_at'
    
    fieldsets = (
        ('Session Info', {
            'fields': ('student_progress',)
        }),
        ('Performance', {
            'fields': ('score', 'passed', 'time_spent')
        }),
        ('Details', {
            'fields': ('questions_asked', 'answers_given'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('completed_at',),
            'classes': ('collapse',)
        }),
    )
    
    def student_name(self, obj):
        return obj.student_progress.user.username
    student_name.short_description = 'Student'
    student_name.admin_order_field = 'student_progress__user__username'
    
    def lesson_title(self, obj):
        return obj.student_progress.lesson_unit.lesson.title
    lesson_title.short_description = 'Lesson'
    
    def score_badge(self, obj):
        color = 'green' if obj.score >= 80 else 'orange' if obj.score >= 60 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{}%</span>', color, obj.score)
    score_badge.short_description = 'Score'
    
    def passed_badge(self, obj):
        if obj.passed:
            return format_html('<span style="color: green;">✓ PASSED</span>')
        return format_html('<span style="color: red;">✗ FAILED</span>')
    passed_badge.short_description = 'Result'
    
    def time_spent_formatted(self, obj):
        minutes = obj.time_spent // 60
        seconds = obj.time_spent % 60
        return f"{minutes}m {seconds}s"
    time_spent_formatted.short_description = 'Time Spent'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('student_progress', 'student_progress__user', 'student_progress__lesson_unit__lesson')

# ============================================
# ADMIN SITE CUSTOMIZATION
# ============================================

admin.site.site_header = 'MasteryAI Administration'
admin.site.site_title = 'MasteryAI Admin Portal'
admin.site.index_title = 'Welcome to MasteryAI Learning Management System'

# Custom admin actions
def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)
make_published.short_description = "Mark selected lessons as published"

def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)
make_unpublished.short_description = "Mark selected lessons as unpublished"

# Add custom actions to Lesson admin
LessonAdmin.actions = [make_published, make_unpublished]

def activate_institutes(modeladmin, request, queryset):
    queryset.update(is_active=True)
activate_institutes.short_description = "Activate selected institutes"

def deactivate_institutes(modeladmin, request, queryset):
    queryset.update(is_active=False)
deactivate_institutes.short_description = "Deactivate selected institutes"

InstituteAdmin.actions = [activate_institutes, deactivate_institutes]