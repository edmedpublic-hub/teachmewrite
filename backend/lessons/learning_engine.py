# backend/lessons/learning_engine.py
import random
import logging
import json
from collections import Counter
from django.utils import timezone

logger = logging.getLogger(__name__)


class AdaptiveLearningEngine:
    
    MAX_PRACTICE_QUESTIONS = 15
    MAX_TEST_QUESTIONS = 10
    DEFAULT_PRACTICE_QUESTIONS = 8
    DEFAULT_TEST_QUESTIONS = 8
    
    def __init__(self, student_progress):
        self.progress = student_progress
        self.student = student_progress.user
        self.lesson_unit = student_progress.lesson_unit
        
        from .models import QuestionBank, StudentProgress
        self.QuestionBank = QuestionBank
        self.StudentProgress = StudentProgress
    
    def get_practice_questions(self, num_questions=None):
        if num_questions is None:
            num_questions = self.DEFAULT_PRACTICE_QUESTIONS
        num_questions = min(num_questions, self.MAX_PRACTICE_QUESTIONS)
        
        weak_concepts = self.progress.weak_concepts or []
        answered_questions = set(self.progress.questions_answered or [])
        
        # Get all active questions
        all_questions = list(self.QuestionBank.objects.filter(
            lesson_unit=self.lesson_unit,
            is_active=True
        ))
        
        if not all_questions:
            return []
        
        # Filter by weak concepts manually (SQLite compatible)
        weak_questions = []
        new_questions = []
        
        for q in all_questions:
            if q.id in answered_questions:
                continue
            q_tags = q.tags if isinstance(q.tags, list) else []
            if weak_concepts and any(tag in weak_concepts for tag in q_tags):
                weak_questions.append(q)
            else:
                new_questions.append(q)
        
        # Select questions
        selected = []
        
        # Priority 1: Weak concepts (50%)
        weak_count = min(len(weak_questions), num_questions // 2)
        selected.extend(random.sample(weak_questions, weak_count) if weak_questions else [])
        
        # Priority 2: New questions
        remaining = num_questions - len(selected)
        new_count = min(len(new_questions), remaining)
        selected.extend(random.sample(new_questions, new_count) if new_questions else [])
        
        # Priority 3: Fill with random review
        if len(selected) < num_questions:
            remaining_needed = num_questions - len(selected)
            all_remaining = [q for q in all_questions if q.id not in [s.id for s in selected]]
            if all_remaining:
                selected.extend(random.sample(all_remaining, min(remaining_needed, len(all_remaining))))
        
        random.shuffle(selected)
        return selected[:num_questions]
    
    def evaluate_practice(self, answers):
        if not answers:
            return self._get_empty_practice_response()
        
        score = 0
        weak_concepts = []
        correct_answers = []
        incorrect_answers = []
        
        for question_id, user_answer in answers.items():
            try:
                question = self.QuestionBank.objects.get(id=question_id)
                is_correct = self._check_answer(question, user_answer)
                
                if is_correct:
                    score += 1
                    correct_answers.append({
                        'question_id': question.id,
                        'question': question.question_text,
                        'your_answer': user_answer,
                        'correct_answer': question.correct_answer,
                        'explanation': question.explanation or "Good job!",
                        'is_correct': True
                    })
                else:
                    incorrect_answers.append({
                        'question_id': question.id,
                        'question': question.question_text,
                        'your_answer': user_answer,
                        'correct_answer': question.correct_answer,
                        'explanation': question.explanation or "Review this concept.",
                        'is_correct': False
                    })
                    if question.tags:
                        q_tags = question.tags if isinstance(question.tags, list) else []
                        weak_concepts.extend(q_tags)
            except self.QuestionBank.DoesNotExist:
                continue
        
        total_questions = len(answers)
        score_percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        
        self.progress.practice_attempts = (self.progress.practice_attempts or 0) + 1
        self.progress.practice_last_score = score_percentage
        self.progress.practice_best_score = max(
            self.progress.practice_best_score or 0,
            score_percentage
        )
        
        if weak_concepts:
            weak_counter = Counter(weak_concepts)
            self.progress.weak_concepts = [tag for tag, count in weak_counter.items() if count >= 2]
        
        answered_ids = [int(qid) for qid in answers.keys()]
        current_answered = set(self.progress.questions_answered or [])
        current_answered.update(answered_ids)
        self.progress.questions_answered = list(current_answered)
        
        can_take_test = (
            score_percentage >= (self.lesson_unit.practice_pass_threshold or 70) or
            (self.progress.practice_attempts or 0) >= (self.lesson_unit.max_practice_attempts or 5)
        )
        
        if can_take_test:
            self.progress.status = 'TEST'
        
        self.progress.save()
        
        feedback = self._get_practice_feedback(score_percentage, self.progress.weak_concepts or [])
        
        return {
            'success': True,
            'score': round(score_percentage, 1),
            'best_score': round(self.progress.practice_best_score or 0, 1),
            'weak_concepts': self.progress.weak_concepts or [],
            'can_take_test': can_take_test,
            'attempts_remaining': max(0, (self.lesson_unit.max_practice_attempts or 5) - (self.progress.practice_attempts or 0)),
            'feedback': feedback,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'next_action': 'take_test' if can_take_test else 'more_practice'
        }
    
    def get_test_questions(self, num_questions=None):
        if num_questions is None:
            num_questions = self.DEFAULT_TEST_QUESTIONS
        num_questions = min(num_questions, self.MAX_TEST_QUESTIONS)
        
        all_questions = list(self.QuestionBank.objects.filter(
            lesson_unit=self.lesson_unit,
            is_active=True
        ))
        
        if not all_questions:
            return []
        
        random.shuffle(all_questions)
        return all_questions[:num_questions]
    
    def evaluate_test(self, answers):
        if not answers:
            return self._get_empty_test_response()
        
        score = 0
        correct_answers = []
        incorrect_answers = []
        
        for question_id, user_answer in answers.items():
            try:
                question = self.QuestionBank.objects.get(id=question_id)
                is_correct = self._check_answer(question, user_answer)
                
                if is_correct:
                    score += 1
                    correct_answers.append({
                        'question_id': question.id,
                        'question': question.question_text,
                        'your_answer': user_answer,
                        'correct_answer': question.correct_answer,
                        'explanation': question.explanation or "Correct!",
                        'is_correct': True
                    })
                else:
                    incorrect_answers.append({
                        'question_id': question.id,
                        'question': question.question_text,
                        'your_answer': user_answer,
                        'correct_answer': question.correct_answer,
                        'explanation': question.explanation or "Review this concept.",
                        'is_correct': False
                    })
            except self.QuestionBank.DoesNotExist:
                continue
        
        total_questions = len(answers)
        score_percentage = (score / total_questions) * 100 if total_questions > 0 else 0
        pass_threshold = self.lesson_unit.test_pass_threshold or 80
        passed = score_percentage >= pass_threshold
        
        self.progress.test_attempts = (self.progress.test_attempts or 0) + 1
        self.progress.test_last_score = score_percentage
        self.progress.test_best_score = max(self.progress.test_best_score or 0, score_percentage)
        
        if passed:
            self.progress.status = 'COMPLETED'
            self.progress.completed_at = timezone.now()
            
            self.StudentProgress.objects.update_or_create(
                user=self.student,
                lesson=self.lesson_unit.lesson,
                defaults={
                    'is_completed': True,
                    'mastery_score': score_percentage,
                    'completed_at': timezone.now()
                }
            )
            next_unlocked = self._unlock_next_lesson()
        else:
            self.progress.status = 'TEACHING'
            self.progress.practice_attempts = 0
            self.progress.weak_concepts = []
            next_unlocked = False
        
        self.progress.save()
        
        feedback = self._get_test_feedback(score_percentage, passed)
        
        return {
            'success': True,
            'score': round(score_percentage, 1),
            'passed': passed,
            'threshold': pass_threshold,
            'needs_review': not passed,
            'feedback': feedback,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'test_attempts': self.progress.test_attempts,
            'best_score': round(self.progress.test_best_score or 0, 1),
            'next_lesson_unlocked': next_unlocked if passed else False,
            'next_action': 'next_lesson' if passed else 'review_teaching'
        }
    
    def _check_answer(self, question, user_answer):
        if not user_answer:
            return False
        correct = str(question.correct_answer).strip().lower()
        user = str(user_answer).strip().lower()
        if question.question_type == 'MCQ' and question.options:
            try:
                idx = int(user)
                if 0 <= idx < len(question.options):
                    user = question.options[idx].strip().lower()
            except (ValueError, TypeError):
                pass
        return correct == user
    
    def _get_practice_feedback(self, score, weak_concepts):
        if score >= 90:
            return {'type': 'excellent', 'title': '🎉 Outstanding!', 'message': f"You scored {score:.0f}%! Exceptional work!", 'advice': "Ready for the test!", 'next': "Take the test now!"}
        elif score >= 70:
            weak_text = ', '.join(weak_concepts[:3]) if weak_concepts else "the tricky areas"
            return {'type': 'great', 'title': '🌟 Great Progress!', 'message': f"You scored {score:.0f}%.", 'advice': f"Review: {weak_text}", 'next': "A bit more practice and you'll be test-ready!"}
        elif score >= 50:
            return {'type': 'good', 'title': '📚 Good Effort!', 'message': f"You scored {score:.0f}%. You're on the right track!", 'advice': "Keep practicing!", 'next': "Try another practice round"}
        else:
            return {'type': 'encouraging', 'title': '💪 Keep Going!', 'message': f"You scored {score:.0f}%. Learning takes time!", 'advice': "Review the material.", 'next': "Don't give up!"}
    
    def _get_test_feedback(self, score, passed):
        if passed:
            if score >= 95:
                return {'type': 'perfect', 'title': '🏆 PERFECT SCORE! 🏆', 'message': f"Incredible! You scored {score:.0f}%!", 'advice': "You've mastered this lesson!", 'next': "Proceed to the next lesson!"}
            else:
                return {'type': 'passed', 'title': '🎉 Test Passed! 🎉', 'message': f"You scored {score:.0f}% and passed!", 'advice': "Great work!", 'next': "Next lesson unlocked!"}
        else:
            return {'type': 'learning', 'title': '📚 Learning Opportunity', 'message': f"You scored {score:.0f}%. Need {self.lesson_unit.test_pass_threshold or 80}% to pass.", 'advice': "Review the material and try again.", 'next': "You have more chances to succeed!"}
    
    def _unlock_next_lesson(self):
        from .models import LessonUnit, StudentLessonProgress
        next_lesson_unit = LessonUnit.objects.filter(unit=self.lesson_unit.unit, order__gt=self.lesson_unit.order).first()
        if next_lesson_unit:
            next_progress, created = StudentLessonProgress.objects.get_or_create(
                user=self.student,
                lesson_unit=next_lesson_unit,
                defaults={'status': 'NOT_STARTED'}
            )
            if next_progress.status == 'LOCKED':
                next_progress.status = 'NOT_STARTED'
                next_progress.save()
                return True
        return False
    
    def _get_empty_practice_response(self):
        return {
            'success': False,
            'score': 0,
            'best_score': self.progress.practice_best_score or 0,
            'weak_concepts': [],
            'can_take_test': False,
            'attempts_remaining': self.lesson_unit.max_practice_attempts or 5,
            'feedback': {'title': 'No Answers', 'message': 'Please answer the questions.', 'advice': 'Take your time.', 'next': 'Try again.'},
            'correct_answers': [],
            'incorrect_answers': [],
            'next_action': 'more_practice'
        }
    
    def _get_empty_test_response(self):
        return {
            'success': False,
            'score': 0,
            'passed': False,
            'threshold': self.lesson_unit.test_pass_threshold or 80,
            'needs_review': True,
            'feedback': {'title': 'No Answers', 'message': 'Please answer all test questions.', 'advice': 'Take your time.', 'next': 'Try again.'},
            'correct_answers': [],
            'incorrect_answers': [],
            'test_attempts': self.progress.test_attempts or 0,
            'best_score': round(self.progress.test_best_score or 0, 1),
            'next_lesson_unlocked': False,
            'next_action': 'review_teaching'
        }
    
    def get_progress_summary(self):
        return {
            'lesson_title': self.lesson_unit.lesson.title,
            'status': self.progress.status,
            'practice': {
                'attempts': self.progress.practice_attempts or 0,
                'best_score': round(self.progress.practice_best_score or 0, 1),
                'last_score': round(self.progress.practice_last_score or 0, 1),
                'max_attempts': self.lesson_unit.max_practice_attempts or 5,
                'pass_threshold': self.lesson_unit.practice_pass_threshold or 70
            },
            'test': {
                'attempts': self.progress.test_attempts or 0,
                'best_score': round(self.progress.test_best_score or 0, 1),
                'last_score': round(self.progress.test_last_score or 0, 1),
                'pass_threshold': self.lesson_unit.test_pass_threshold or 80
            },
            'weak_concepts': self.progress.weak_concepts or [],
            'questions_answered': len(self.progress.questions_answered or []),
            'started_at': self.progress.started_at,
            'completed_at': self.progress.completed_at
        }
    
    def is_test_available(self):
        if self.progress.status == 'TEST':
            return True
        if (self.progress.practice_best_score or 0) >= (self.lesson_unit.practice_pass_threshold or 70):
            return True
        if (self.progress.practice_attempts or 0) >= (self.lesson_unit.max_practice_attempts or 5):
            return True
        return False