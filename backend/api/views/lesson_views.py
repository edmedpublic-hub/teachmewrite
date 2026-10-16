# backend/api/views/lesson_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F
from django.utils import timezone
from lessons.models import Lesson, StudentProgress, TierProgress, Tier
from ..serializers import LessonSerializer, ProgressSerializer
import logging

logger = logging.getLogger(__name__)


class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing lessons with tier filtering"""
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Lesson.objects.filter(is_published=True).order_by('tier', 'order')
        
        # Get user's unlocked tiers
        unlocked_tiers = TierProgress.objects.filter(
            user=user, 
            is_unlocked=True
        ).values_list('tier', flat=True)
        
        if not unlocked_tiers:
            unlocked_tiers = [Tier.BASIC]
        
        queryset = queryset.filter(tier__in=unlocked_tiers)
        
        tier = self.request.query_params.get('tier')
        if tier and tier.upper() in [t.value for t in Tier]:
            queryset = queryset.filter(tier=tier.upper())
        
        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        serializer = self.get_serializer(lesson)
        data = serializer.data
        
        try:
            progress = StudentProgress.objects.get(user=request.user, lesson=lesson)
            progress_serializer = ProgressSerializer(progress)
            data['user_progress'] = progress_serializer.data
        except StudentProgress.DoesNotExist:
            data['user_progress'] = None
        
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def start_lesson(self, request, pk=None):
        lesson = self.get_object()
        
        if not lesson.can_access(request.user):
            prereq_title = lesson.prerequisite.title if lesson.prerequisite else "Unknown"
            return Response(
                {'error': f'Complete and master "{prereq_title}" first'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        progress, created = StudentProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        if created:
            logger.info(f"User {request.user.username} started lesson {lesson.id}")
        
        return Response({
            'status': 'started',
            'is_resuming': not created,
            'progress': ProgressSerializer(progress).data
        })
    
    @action(detail=True, methods=['post'])
    def submit_practice(self, request, pk=None):
        lesson = self.get_object()
        user_answers = request.data.get('answers', [])
        
        progress, _ = StudentProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        practice_score = self._calculate_practice_score(lesson, user_answers)
        
        progress.practice_attempts += 1
        progress.last_practice_score = practice_score
        
        if progress.mastery_score < practice_score * 0.3:
            progress.mastery_score = min(100, progress.mastery_score + practice_score * 0.3)
        
        progress.save()
        
        tier_progress, _ = TierProgress.objects.get_or_create(
            user=request.user,
            tier=lesson.tier
        )
        tier_progress.update_progress()
        
        return Response({
            'score': practice_score,
            'mastery_score': progress.mastery_score,
            'message': f'Practice score: {practice_score}%'
        })
    
    @action(detail=True, methods=['post'])
    def submit_test(self, request, pk=None):
        lesson = self.get_object()
        test_answers = request.data.get('answers', [])
        
        progress, _ = StudentProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        test_score = self._calculate_test_score(lesson, test_answers)
        
        progress.test_attempts += 1
        progress.last_test_score = test_score
        
        new_mastery = (progress.last_practice_score * 0.3) + (test_score * 0.7)
        progress.mastery_score = new_mastery
        progress.attempts += 1
        
        is_mastered = progress.mastery_score >= lesson.required_mastery_score
        
        if is_mastered and not progress.is_completed:
            progress.is_completed = True
            progress.completed_at = timezone.now()
            
            tier_progress, _ = TierProgress.objects.get_or_create(
                user=request.user,
                tier=lesson.tier
            )
            tier_progress.update_progress()
            
            self._check_next_tier_unlock(request.user, lesson.tier)
        
        progress.save()
        
        return Response({
            'test_score': test_score,
            'mastery_score': progress.mastery_score,
            'is_mastered': is_mastered,
            'required_score': lesson.required_mastery_score,
            'message': f'Test score: {test_score}% - {"Mastered!" if is_mastered else "Keep practicing!"}'
        })
    
    def _calculate_practice_score(self, lesson, user_answers):
        if not lesson.practice_questions:
            return 100
        correct = 0
        for i, ans in enumerate(user_answers):
            if i < len(lesson.practice_questions):
                correct_answer = lesson.practice_questions[i].get('correct_answer')
                if ans == correct_answer:
                    correct += 1
        return (correct / len(lesson.practice_questions)) * 100 if lesson.practice_questions else 100
    
    def _calculate_test_score(self, lesson, test_answers):
        if not test_answers:
            return 0
        return 100
    
    def _check_next_tier_unlock(self, user, current_tier):
        tier_order = [Tier.BASIC, Tier.INTERMEDIATE, Tier.ADVANCED, Tier.PROFESSIONAL]
        current_index = tier_order.index(current_tier)
        
        if current_index < len(tier_order) - 1:
            next_tier = tier_order[current_index + 1]
            try:
                tier_progress = TierProgress.objects.get(user=user, tier=current_tier)
                if tier_progress.is_completed:
                    next_tier_progress, _ = TierProgress.objects.get_or_create(
                        user=user,
                        tier=next_tier
                    )
                    next_tier_progress.is_unlocked = True
                    next_tier_progress.save()
                    logger.info(f"Unlocked {next_tier} for user {user.username}")
            except TierProgress.DoesNotExist:
                pass
            
# ============================================
# UNIT VIEWSET
# ============================================

class UnitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing curriculum units"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from lessons.models import Unit
        return Unit.objects.filter(is_active=True).order_by('tier', 'order')
    
    def list(self, request, *args, **kwargs):
        """Override list to include lessons in each unit"""
        from lessons.models import LessonUnit
        from api.serializers import UnitSerializer, LessonUnitSerializer
        
        queryset = self.get_queryset()
        serializer = UnitSerializer(queryset, many=True, context={'request': request})
        data = serializer.data
        
        # Add lessons to each unit
        for unit_data in data:
            lesson_units = LessonUnit.objects.filter(
                unit_id=unit_data['id'],
                is_active=True
            ).select_related('lesson').order_by('order')
            
            unit_data['lessons'] = LessonUnitSerializer(
                lesson_units, 
                many=True, 
                context={'request': request}
            ).data
        
        # Paginate if needed
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 100
        result_page = paginator.paginate_queryset(data, request)
        if result_page is not None:
            return paginator.get_paginated_response(result_page)
        
        return Response(data)
    
    def retrieve(self, request, *args, **kwargs):
        from lessons.models import LessonUnit
        from api.serializers import UnitDetailSerializer, LessonUnitSerializer
        
        instance = self.get_object()
        serializer = UnitDetailSerializer(instance, context={'request': request})
        data = serializer.data
        
        # Add lessons to unit
        lesson_units = LessonUnit.objects.filter(
            unit=instance,
            is_active=True
        ).select_related('lesson').order_by('order')
        
        data['lessons'] = LessonUnitSerializer(
            lesson_units, 
            many=True, 
            context={'request': request}
        ).data
        
        # Add user progress for each lesson
        from lessons.models import StudentLessonProgress
        for lesson in data['lessons']:
            try:
                progress = StudentLessonProgress.objects.get(
                    user=request.user,
                    lesson_unit_id=lesson['id']
                )
                lesson['user_progress'] = {
                    'status': progress.status,
                    'practice_best_score': progress.practice_best_score,
                    'test_best_score': progress.test_best_score
                }
            except StudentLessonProgress.DoesNotExist:
                lesson['user_progress'] = {'status': 'NOT_STARTED'}
        
        return Response(data)

# ============================================
# LESSON UNIT VIEWSET (for direct access)
# ============================================

class LessonUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing lesson units"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from lessons.models import LessonUnit
        queryset = LessonUnit.objects.filter(is_active=True).select_related('lesson', 'unit')
        
        unit_id = self.request.query_params.get('unit')
        if unit_id:
            queryset = queryset.filter(unit_id=unit_id)
        
        return queryset
    
    def get_serializer_class(self):
        from api.serializers import LessonUnitSerializer
        return LessonUnitSerializer


# ============================================
# QUESTION BANK VIEWSET
# ============================================

class QuestionBankViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing practice/test questions"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from lessons.models import QuestionBank
        queryset = QuestionBank.objects.filter(is_active=True)
        
        lesson_unit_id = self.request.query_params.get('lesson_unit')
        if lesson_unit_id:
            queryset = queryset.filter(lesson_unit_id=lesson_unit_id)
        
        return queryset
    
    def get_serializer_class(self):
        from api.serializers import QuestionBankReadSerializer
        return QuestionBankReadSerializer


# ============================================
# STUDENT LESSON PROGRESS VIEWSET
# ============================================

class StudentLessonProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing student's lesson progress"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        from lessons.models import StudentLessonProgress
        queryset = StudentLessonProgress.objects.filter(user=self.request.user)
        
        lesson_unit_id = self.request.query_params.get('lesson_unit')
        if lesson_unit_id:
            queryset = queryset.filter(lesson_unit_id=lesson_unit_id)
        
        return queryset
    
    def get_serializer_class(self):
        from api.serializers import StudentLessonProgressSerializer
        return StudentLessonProgressSerializer