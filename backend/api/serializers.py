from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from lessons.models import (
    Lesson, StudentProgress, TierProgress, Profile,
    Institute, UserProfile, Class, Assignment, 
    AssignmentSubmission, Announcement, Certificate, 
    Tier, UserRole,
    # NEW MODELS
    Unit, LessonUnit, QuestionBank, StudentLessonProgress,
    PracticeSession, TestSession
)

# ============================================
# EXISTING SERIALIZERS (Preserved & Enhanced)
# ============================================

class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for authentication"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class ProfileSerializer(serializers.ModelSerializer):
    """Profile model serializer - Enhanced with new fields"""
    education_level_display = serializers.CharField(source='get_education_level_display', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id', 'phone_number', 'date_of_birth', 'city', 'country', 'cnic',
            'education_level', 'education_level_display', 'institution', 'roll_number',
            'target_exam', 'target_tier', 'total_xp', 'streak_days', 'last_active',
            'average_score', 'total_lessons_completed'
        ]
        read_only_fields = ['total_xp', 'streak_days', 'average_score', 'total_lessons_completed', 'last_active']


class UserProfileSerializer(serializers.ModelSerializer):
    """User with profile data (legacy - keep for compatibility)"""
    profile = ProfileSerializer(read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'profile']
    
    def get_profile(self, obj):
        if hasattr(obj, 'profile'):
            return ProfileSerializer(obj.profile).data
        return None


# ============================================
# INSTITUTE MANAGEMENT SERIALIZERS
# ============================================

class InstituteSerializer(serializers.ModelSerializer):
    """Institute serializer for multi-tenant support"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    member_count = serializers.IntegerField(read_only=True)
    is_subscription_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Institute
        fields = [
            'id', 'name', 'type', 'type_display', 'address', 'phone', 'email',
            'website', 'logo', 'subscription_plan', 'subscription_expiry',
            'max_students', 'max_teachers', 'is_active', 'member_count',
            'is_subscription_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'member_count']


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """User profile with role and institute"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    linked_students_count = serializers.IntegerField(read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'user_details', 'role', 'role_display', 'institute', 'institute_name',
            'phone', 'address', 'qualification', 'specialization', 
            'experience_years', 'joining_date', 'linked_students', 
            'linked_students_count', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'linked_students': {'required': False}
        }


class ClassSerializer(serializers.ModelSerializer):
    """Class/Group serializer"""
    institute_name = serializers.CharField(source='institute.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    student_count = serializers.IntegerField(read_only=True)
    student_details = UserSerializer(source='students', many=True, read_only=True)
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'institute', 'institute_name', 'teacher', 'teacher_name',
            'students', 'student_details', 'student_count', 'grade_level', 'academic_year', 'section',
            'schedule', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'student_count']


# ============================================
# LESSON SERIALIZERS
# ============================================

class LessonSerializer(serializers.ModelSerializer):
    """Enhanced lesson serializer with additional fields"""
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    is_locked = serializers.SerializerMethodField()
    prerequisite_title = serializers.CharField(source='prerequisite.title', read_only=True)
    prerequisite_id = serializers.IntegerField(source='prerequisite.id', read_only=True)
    
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'slug', 'description', 'content', 'tier', 'tier_display',
            'order', 'prerequisite', 'prerequisite_title', 'prerequisite_id',
            'required_mastery_score', 'practice_questions', 'test_criteria', 
            'xp_reward', 'estimated_duration_minutes', 'video_url', 'attachments',
            'is_published', 'is_free', 'is_locked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_is_locked(self, obj):
        """Dynamic locking based on user's progress"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if obj.prerequisite:
                try:
                    progress = StudentProgress.objects.get(
                        user=request.user,
                        lesson=obj.prerequisite
                    )
                    return not progress.is_mastered
                except StudentProgress.DoesNotExist:
                    return True
        return False


class LessonListSerializer(serializers.ModelSerializer):
    """Lightweight lesson serializer for list views"""
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'slug', 'tier', 'tier_display', 'order', 'xp_reward', 'estimated_duration_minutes']


# ============================================
# PROGRESS SERIALIZERS
# ============================================

class ProgressSerializer(serializers.ModelSerializer):
    """Enhanced progress serializer"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_tier = serializers.CharField(source='lesson.tier', read_only=True)
    lesson_slug = serializers.CharField(source='lesson.slug', read_only=True)
    mastery_status = serializers.CharField(read_only=True)
    is_mastered = serializers.BooleanField(read_only=True)
    time_spent_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentProgress
        fields = [
            'id', 'lesson', 'lesson_title', 'lesson_slug', 'lesson_tier',
            'is_completed', 'mastery_score', 'attempts', 'practice_attempts',
            'test_attempts', 'last_practice_score', 'last_test_score',
            'mastery_status', 'is_mastered', 'started_at', 'last_attempt_at',
            'completed_at', 'time_spent_seconds', 'time_spent_formatted'
        ]
        read_only_fields = ['id', 'started_at', 'last_attempt_at']
    
    def get_time_spent_formatted(self, obj):
        hours = obj.time_spent_seconds // 3600
        minutes = (obj.time_spent_seconds % 3600) // 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"


class TierProgressSerializer(serializers.ModelSerializer):
    """Enhanced tier progress serializer"""
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    mastery_percentage = serializers.FloatField(read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = TierProgress
        fields = [
            'id', 'tier', 'tier_display', 'total_lessons', 'mastered_lessons',
            'completed_lessons', 'is_unlocked', 'is_completed', 'mastery_percentage',
            'progress_percentage', 'completed_at', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']
    
    def get_progress_percentage(self, obj):
        if obj.total_lessons == 0:
            return 0
        return (obj.completed_lessons / obj.total_lessons) * 100


# ============================================
# ASSIGNMENT SERIALIZERS
# ============================================

class AssignmentSerializer(serializers.ModelSerializer):
    """Assignment serializer for teachers"""
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    class_name = serializers.CharField(source='assigned_to_class.name', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    submission_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'title', 'description', 'lesson', 'lesson_title',
            'assigned_by', 'assigned_by_name', 'assigned_to_class', 'class_name',
            'total_points', 'due_date', 'allowed_attempts', 'instructions',
            'resources', 'is_active', 'is_overdue', 'submission_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_overdue', 'submission_count']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """Assignment submission serializer"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    graded_by_name = serializers.CharField(source='graded_by.get_full_name', read_only=True)
    grading_status = serializers.SerializerMethodField()
    
    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'assignment', 'assignment_title', 'student', 'student_name',
            'content', 'attachments', 'score', 'feedback', 'graded_by',
            'graded_by_name', 'graded_at', 'submitted_at', 'updated_at', 'is_late',
            'grading_status'
        ]
        read_only_fields = ['id', 'submitted_at', 'updated_at', 'is_late', 'grading_status']
        extra_kwargs = {
            'content': {'required': True}
        }
    
    def get_grading_status(self, obj):
        if obj.score is not None:
            return 'graded'
        return 'pending'


# ============================================
# ANNOUNCEMENT SERIALIZERS
# ============================================

class AnnouncementSerializer(serializers.ModelSerializer):
    """Announcement serializer"""
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    target_display = serializers.CharField(source='get_target_audience_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    priority_color = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'target_audience', 'target_display', 'institute', 'class_target',
            'priority', 'priority_display', 'priority_color', 'expires_at',
            'is_active', 'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired']
    
    def get_priority_color(self, obj):
        colors = {
            'LOW': '#6c757d',
            'MEDIUM': '#007bff',
            'HIGH': '#fd7e14',
            'URGENT': '#dc3545'
        }
        return colors.get(obj.priority, '#6c757d')


# ============================================
# CERTIFICATE SERIALIZERS
# ============================================

class CertificateSerializer(serializers.ModelSerializer):
    """Certificate serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    verification_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'user', 'user_name', 'tier', 'tier_display',
            'certificate_number', 'verification_code', 'issue_date',
            'expiry_date', 'pdf_file', 'shareable_link', 'verification_url',
            'is_verified'
        ]
        read_only_fields = [
            'id', 'certificate_number', 'verification_code', 'issue_date',
            'shareable_link', 'verification_url'
        ]
    
    def get_verification_url(self, obj):
        request = self.context.get('request')
        if request and obj.verification_code:
            return request.build_absolute_uri(f'/api/v1/certificates/verify/{obj.verification_code}/')
        return None


# ============================================
# DASHBOARD & REPORT SERIALIZERS
# ============================================

class StudentDashboardSerializer(serializers.Serializer):
    """Comprehensive student dashboard data"""
    profile = ProfileSerializer()
    tier_progress = TierProgressSerializer(many=True)
    recent_lessons = ProgressSerializer(many=True)
    upcoming_assignments = AssignmentSerializer(many=True)
    recent_announcements = AnnouncementSerializer(many=True)
    certificates = CertificateSerializer(many=True)
    statistics = serializers.DictField()


class TeacherDashboardSerializer(serializers.Serializer):
    """Comprehensive teacher dashboard data"""
    profile = UserProfileDetailSerializer(source='user_profile', read_only=True)
    classes = ClassSerializer(many=True)
    pending_assignments = AssignmentSerializer(many=True)
    pending_submissions = AssignmentSubmissionSerializer(many=True)
    recent_announcements = AnnouncementSerializer(many=True)
    statistics = serializers.DictField()


class InstituteDashboardSerializer(serializers.Serializer):
    """Institute admin dashboard data"""
    institute = InstituteSerializer()
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_classes = serializers.IntegerField()
    active_submissions = serializers.IntegerField()
    completion_rate = serializers.FloatField()
    tier_breakdown = serializers.DictField()
    recent_activity = serializers.ListField()


# ============================================
# AUTHENTICATION SERIALIZERS
# ============================================

class RegisterSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=UserRole.choices, default=UserRole.STUDENT)
    phone = serializers.CharField(required=False, allow_blank=True)
    education_level = serializers.ChoiceField(choices=Profile.EDUCATION_LEVELS, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 
                  'last_name', 'role', 'phone', 'education_level']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username already exists"})
        
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
        
        return data
    
    def create(self, validated_data):
        role = validated_data.pop('role', UserRole.STUDENT)
        phone = validated_data.pop('phone', '')
        education_level = validated_data.pop('education_level', None)
        
        # Remove confirm_password
        validated_data.pop('confirm_password')
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Create user profile with role
        UserProfile.objects.create(
            user=user,
            role=role,
            phone=phone
        )
        
        # Create profile with education info
        Profile.objects.create(
            user=user,
            education_level=education_level,
            country='Pakistan'
        )
        
        # Initialize tier progress
        TierProgress.initialize_user_tiers(user)
        
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        return data


# ============================================
# UTILITY SERIALIZERS
# ============================================

class ErrorSerializer(serializers.Serializer):
    """Standard error response serializer"""
    error = serializers.CharField()
    detail = serializers.CharField(required=False)
    code = serializers.IntegerField(required=False)


class SuccessSerializer(serializers.Serializer):
    """Standard success response serializer"""
    success = serializers.BooleanField()
    message = serializers.CharField()
    data = serializers.DictField(required=False)


# ============================================
# NEW ADAPTIVE LEARNING SERIALIZERS
# ============================================

class UnitSerializer(serializers.ModelSerializer):
    """Serializer for Unit model - groups lessons into curriculum units"""
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    lesson_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = [
            'id', 'title', 'description', 'tier', 'tier_display',
            'order', 'is_active', 'lesson_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_lesson_count(self, obj):
        return obj.lesson_links.filter(is_active=True).count()


class UnitDetailSerializer(UnitSerializer):
    """Detailed Unit serializer with embedded lessons"""
    lessons = serializers.SerializerMethodField()
    
    class Meta(UnitSerializer.Meta):
        fields = UnitSerializer.Meta.fields + ['lessons']
    
    def get_lessons(self, obj):
        lesson_units = obj.lesson_links.filter(is_active=True).order_by('order')
        return LessonUnitSerializer(lesson_units, many=True, context=self.context).data


class LessonUnitSerializer(serializers.ModelSerializer):
    """Serializer for LessonUnit - links lessons to units with teaching content"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_description = serializers.CharField(source='lesson.description', read_only=True)
    lesson_slug = serializers.CharField(source='lesson.slug', read_only=True)
    question_count = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = LessonUnit
        fields = [
            'id', 'unit', 'lesson', 'lesson_title', 'lesson_description', 'lesson_slug',
            'order', 'teaching_content', 'examples', 'practice_pass_threshold',
            'test_pass_threshold', 'max_practice_attempts', 'prerequisites',
            'is_active', 'question_count', 'is_locked', 'user_progress',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_question_count(self, obj):
        return obj.questions.filter(is_active=True).count()
    
    def get_is_locked(self, obj):
        """Check if lesson is locked based on prerequisites"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return True
        
        # Check if user has completed prerequisites
        for prereq in obj.prerequisites.all():
            try:
                progress = StudentLessonProgress.objects.get(
                    user=request.user,
                    lesson_unit=prereq
                )
                if progress.status != 'COMPLETED':
                    return True
            except StudentLessonProgress.DoesNotExist:
                return True
        return False
    
    def get_user_progress(self, obj):
        """Get current user's progress for this lesson"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = StudentLessonProgress.objects.get(
                    user=request.user,
                    lesson_unit=obj
                )
                return StudentLessonProgressSerializer(progress).data
            except StudentLessonProgress.DoesNotExist:
                return {'status': 'NOT_STARTED', 'practice_attempts': 0}
        return None


class QuestionBankSerializer(serializers.ModelSerializer):
    """Serializer for QuestionBank - practice and test questions"""
    question_type_display = serializers.CharField(source='get_question_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    
    class Meta:
        model = QuestionBank
        fields = [
            'id', 'lesson_unit', 'question_type', 'question_type_display',
            'difficulty', 'difficulty_display', 'question_text', 'correct_answer',
            'options', 'explanation', 'tags', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'correct_answer': {'write_only': True},  # Don't send correct answer to frontend
        }


class QuestionBankReadSerializer(QuestionBankSerializer):
    """Read-only serializer for questions (excludes correct_answer)"""
    class Meta(QuestionBankSerializer.Meta):
        fields = [f for f in QuestionBankSerializer.Meta.fields if f != 'correct_answer']


class StudentLessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for StudentLessonProgress - tracks individual student progress"""
    lesson_title = serializers.CharField(source='lesson_unit.lesson.title', read_only=True)
    unit_title = serializers.CharField(source='lesson_unit.unit.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    mastery_percentage = serializers.SerializerMethodField()
    can_take_test = serializers.SerializerMethodField()
    
    class Meta:
        model = StudentLessonProgress
        fields = [
            'id', 'user', 'lesson_unit', 'lesson_title', 'unit_title',
            'status', 'status_display', 'practice_attempts', 'practice_best_score',
            'practice_last_score', 'test_attempts', 'test_best_score', 'test_last_score',
            'questions_answered', 'mastered_concepts', 'weak_concepts',
            'mastery_percentage', 'can_take_test', 'started_at', 'completed_at', 'last_activity'
        ]
        read_only_fields = ['id', 'started_at', 'last_activity']
    
    def get_mastery_percentage(self, obj):
        """Calculate overall mastery percentage"""
        if obj.test_best_score > 0:
            return obj.test_best_score
        return obj.practice_best_score
    
    def get_can_take_test(self, obj):
        """Check if student is ready to take the test"""
        from lessons.learning_engine import AdaptiveLearningEngine
        engine = AdaptiveLearningEngine(obj)
        return engine.is_test_available()


class PracticeSessionSerializer(serializers.ModelSerializer):
    """Serializer for PracticeSession - records practice attempts"""
    lesson_title = serializers.CharField(source='student_progress.lesson_unit.lesson.title', read_only=True)
    formatted_time = serializers.SerializerMethodField()
    
    class Meta:
        model = PracticeSession
        fields = [
            'id', 'student_progress', 'lesson_title', 'questions_asked',
            'answers_given', 'score', 'time_spent', 'formatted_time', 'completed_at'
        ]
        read_only_fields = ['id', 'completed_at']
    
    def get_formatted_time(self, obj):
        minutes = obj.time_spent // 60
        seconds = obj.time_spent % 60
        return f"{minutes}m {seconds}s"


class TestSessionSerializer(serializers.ModelSerializer):
    """Serializer for TestSession - records test attempts"""
    lesson_title = serializers.CharField(source='student_progress.lesson_unit.lesson.title', read_only=True)
    passed_display = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    
    class Meta:
        model = TestSession
        fields = [
            'id', 'student_progress', 'lesson_title', 'questions_asked',
            'answers_given', 'score', 'passed', 'passed_display',
            'time_spent', 'formatted_time', 'completed_at'
        ]
        read_only_fields = ['id', 'completed_at']
    
    def get_passed_display(self, obj):
        return "Passed" if obj.passed else "Failed"
    
    def get_formatted_time(self, obj):
        minutes = obj.time_spent // 60
        seconds = obj.time_spent % 60
        return f"{minutes}m {seconds}s"


class PracticeSubmissionSerializer(serializers.Serializer):
    """Serializer for practice submission request"""
    answers = serializers.DictField(child=serializers.CharField(), required=True)
    time_spent = serializers.IntegerField(required=False, default=0)


class TestSubmissionSerializer(serializers.Serializer):
    """Serializer for test submission request"""
    answers = serializers.DictField(child=serializers.CharField(), required=True)
    time_spent = serializers.IntegerField(required=False, default=0)


class PracticeResultSerializer(serializers.Serializer):
    """Serializer for practice evaluation response"""
    success = serializers.BooleanField()
    score = serializers.FloatField()
    best_score = serializers.FloatField()
    weak_concepts = serializers.ListField(child=serializers.CharField())
    can_take_test = serializers.BooleanField()
    attempts_remaining = serializers.IntegerField()
    feedback = serializers.DictField()
    correct_answers = serializers.ListField()
    incorrect_answers = serializers.ListField()
    next_action = serializers.CharField()


class TestResultSerializer(serializers.Serializer):
    """Serializer for test evaluation response"""
    success = serializers.BooleanField()
    score = serializers.FloatField()
    passed = serializers.BooleanField()
    threshold = serializers.IntegerField()
    needs_review = serializers.BooleanField()
    feedback = serializers.DictField()
    correct_answers = serializers.ListField()
    incorrect_answers = serializers.ListField()
    test_attempts = serializers.IntegerField()
    best_score = serializers.FloatField()
    next_lesson_unlocked = serializers.BooleanField()
    next_action = serializers.CharField()