# backend/api/views/adaptive_views.py
"""
Adaptive Learning Views for TeachMeWrite
Handles practice and test endpoints using the AdaptiveLearningEngine
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from lessons.models import LessonUnit, StudentLessonProgress, QuestionBank
from lessons.learning_engine import AdaptiveLearningEngine


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lesson_unit(request, unit_id, lesson_id):
    """
    Get lesson unit details with teaching content and user progress.
    
    URL: /api/adaptive/units/<unit_id>/lessons/<lesson_id>/
    Method: GET
    """
    try:
        lesson_unit = LessonUnit.objects.get(unit_id=unit_id, lesson_id=lesson_id)
        progress, _ = StudentLessonProgress.objects.get_or_create(
            user=request.user,
            lesson_unit=lesson_unit
        )
        
        return Response({
            'id': lesson_unit.id,
            'unit_id': lesson_unit.unit.id,
            'lesson_id': lesson_unit.lesson.id,
            'title': lesson_unit.lesson.title,
            'description': lesson_unit.lesson.description,
            'teaching_content': lesson_unit.teaching_content,
            'examples': lesson_unit.examples,
            'status': progress.status,
            'practice_threshold': lesson_unit.practice_pass_threshold,
            'test_threshold': lesson_unit.test_pass_threshold,
            'max_practice_attempts': lesson_unit.max_practice_attempts,
            'progress': {
                'practice_attempts': progress.practice_attempts or 0,
                'practice_best_score': progress.practice_best_score or 0,
                'practice_last_score': progress.practice_last_score or 0,
                'test_attempts': progress.test_attempts or 0,
                'test_best_score': progress.test_best_score or 0,
                'test_last_score': progress.test_last_score or 0,
                'weak_concepts': progress.weak_concepts or []
            }
        })
    except LessonUnit.DoesNotExist:
        return Response(
            {'error': 'Lesson unit not found', 'detail': f'No lesson found for unit {unit_id} and lesson {lesson_id}'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_practice_questions(request, lesson_unit_id):
    """
    Get adaptive practice questions for a lesson unit.
    
    URL: /api/adaptive/practice/<lesson_unit_id>/questions/
    Method: GET
    Query Params: num_questions (optional, default 5, max 15)
    """
    try:
        lesson_unit = LessonUnit.objects.get(id=lesson_unit_id)
        progress, _ = StudentLessonProgress.objects.get_or_create(
            user=request.user,
            lesson_unit=lesson_unit
        )
        
        # Get number of questions from query param
        num_questions = request.query_params.get('num_questions', 5)
        try:
            num_questions = int(num_questions)
        except ValueError:
            num_questions = 5
        
        engine = AdaptiveLearningEngine(progress)
        questions = engine.get_practice_questions(num_questions=num_questions)
        
        # Format questions for frontend (exclude correct_answer)
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                'id': q.id,
                'type': q.question_type,
                'question': q.question_text,
                'options': q.options,
                'difficulty': q.difficulty,
                'tags': q.tags
            })
        
        return Response({
            'success': True,
            'questions': formatted_questions,
            'attempt_number': (progress.practice_attempts or 0) + 1,
            'max_attempts': lesson_unit.max_practice_attempts,
            'weak_concepts': progress.weak_concepts or [],
            'practice_best_score': progress.practice_best_score or 0
        })
    except LessonUnit.DoesNotExist:
        return Response(
            {'error': 'Lesson unit not found', 'detail': f'No lesson unit found with id {lesson_unit_id}'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_practice(request, lesson_unit_id):
    """
    Submit practice answers and get evaluation.
    
    URL: /api/adaptive/practice/<lesson_unit_id>/submit/
    Method: POST
    Body: {
        "answers": {
            "question_id": "user_answer",
            ...
        },
        "time_spent": 120 (optional)
    }
    """
    try:
        lesson_unit = LessonUnit.objects.get(id=lesson_unit_id)
        progress, _ = StudentLessonProgress.objects.get_or_create(
            user=request.user,
            lesson_unit=lesson_unit
        )
        
        answers = request.data.get('answers', {})
        if not answers:
            return Response(
                {'error': 'No answers provided', 'detail': 'Please provide answers for the practice questions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Optional: track time spent
        time_spent = request.data.get('time_spent', 0)
        
        engine = AdaptiveLearningEngine(progress)
        result = engine.evaluate_practice(answers)
        
        # Add time_spent to response if needed for tracking
        result['time_spent'] = time_spent
        
        return Response(result)
    except LessonUnit.DoesNotExist:
        return Response(
            {'error': 'Lesson unit not found', 'detail': f'No lesson unit found with id {lesson_unit_id}'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_test_questions(request, lesson_unit_id):
    """
    Get test questions for a lesson unit.
    
    URL: /api/adaptive/test/<lesson_unit_id>/questions/
    Method: GET
    Query Params: num_questions (optional, default 8, max 10)
    """
    try:
        lesson_unit = LessonUnit.objects.get(id=lesson_unit_id)
        progress, _ = StudentLessonProgress.objects.get_or_create(
            user=request.user,
            lesson_unit=lesson_unit
        )
        
        # Check if student is ready for test
        is_ready = (
            progress.status == 'TEST' or 
            (progress.practice_best_score or 0) >= (lesson_unit.practice_pass_threshold or 70) or
            (progress.practice_attempts or 0) >= (lesson_unit.max_practice_attempts or 5)
        )
        
        if not is_ready:
            return Response({
                'error': 'Complete more practice before taking the test',
                'practice_score': progress.practice_best_score or 0,
                'required_score': lesson_unit.practice_pass_threshold,
                'attempts_remaining': max(0, (lesson_unit.max_practice_attempts or 5) - (progress.practice_attempts or 0))
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get number of questions from query param
        num_questions = request.query_params.get('num_questions', 8)
        try:
            num_questions = int(num_questions)
        except ValueError:
            num_questions = 8
        
        engine = AdaptiveLearningEngine(progress)
        questions = engine.get_test_questions(num_questions=num_questions)
        
        # Format questions for frontend (exclude correct_answer)
        formatted_questions = []
        for q in questions:
            formatted_questions.append({
                'id': q.id,
                'type': q.question_type,
                'question': q.question_text,
                'options': q.options,
                'difficulty': q.difficulty,
                'tags': q.tags
            })
        
        return Response({
            'success': True,
            'questions': formatted_questions,
            'test_number': (progress.test_attempts or 0) + 1,
            'passing_score': lesson_unit.test_pass_threshold,
            'max_questions': len(formatted_questions)
        })
    except LessonUnit.DoesNotExist:
        return Response(
            {'error': 'Lesson unit not found', 'detail': f'No lesson unit found with id {lesson_unit_id}'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_test(request, lesson_unit_id):
    """
    Submit test answers and get evaluation.
    
    URL: /api/adaptive/test/<lesson_unit_id>/submit/
    Method: POST
    Body: {
        "answers": {
            "question_id": "user_answer",
            ...
        },
        "time_spent": 300 (optional)
    }
    """
    try:
        lesson_unit = LessonUnit.objects.get(id=lesson_unit_id)
        progress, _ = StudentLessonProgress.objects.get_or_create(
            user=request.user,
            lesson_unit=lesson_unit
        )
        
        answers = request.data.get('answers', {})
        if not answers:
            return Response(
                {'error': 'No answers provided', 'detail': 'Please provide answers for the test questions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Optional: track time spent
        time_spent = request.data.get('time_spent', 0)
        
        engine = AdaptiveLearningEngine(progress)
        result = engine.evaluate_test(answers)
        
        # Add time_spent to response if needed for tracking
        result['time_spent'] = time_spent
        
        return Response(result)
    except LessonUnit.DoesNotExist:
        return Response(
            {'error': 'Lesson unit not found', 'detail': f'No lesson unit found with id {lesson_unit_id}'},
            status=status.HTTP_404_NOT_FOUND
        )