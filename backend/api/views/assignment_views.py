# backend/api/views/assignment_views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from lessons.models import Assignment, AssignmentSubmission, UserProfile, UserRole
from ..serializers import AssignmentSerializer, AssignmentSubmissionSerializer
from ..communication import CommunicationManager
import logging

logger = logging.getLogger(__name__)


class AssignmentViewSet(viewsets.ModelViewSet):
    """ViewSet for assignment management"""
    serializer_class = AssignmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'user_profile'):
            if user.user_profile.role == UserRole.TEACHER:
                return Assignment.objects.filter(assigned_by=user)
            elif user.user_profile.role == UserRole.STUDENT:
                return Assignment.objects.filter(assigned_to_class__students=user)
        return Assignment.objects.none()
    
    def perform_create(self, serializer):
        """Create assignment and notify students"""
        assignment = serializer.save(assigned_by=self.request.user)
        
        # Notify students in the class
        class_obj = assignment.assigned_to_class
        for student in class_obj.students.all():
            if hasattr(student, 'profile') and student.profile.phone_number:
                CommunicationManager.send_whatsapp_message(
                    student.profile.phone_number,
                    f"New assignment: {assignment.title}\nDue: {assignment.due_date}"
                )
        
        logger.info(f"Assignment created: {assignment.title} by {self.request.user.username}")
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit an assignment"""
        assignment = self.get_object()
        content = request.data.get('content', '')
        attachments = request.data.get('attachments', [])
        
        if not content:
            return Response({'error': 'Content is required'}, status=400)
        
        # Check if assignment is overdue
        is_late = assignment.due_date < timezone.now()
        
        submission, created = AssignmentSubmission.objects.get_or_create(
            assignment=assignment,
            student=request.user,
            defaults={
                'content': content,
                'attachments': attachments,
                'is_late': is_late
            }
        )
        
        if not created:
            submission.content = content
            submission.attachments = attachments
            submission.submitted_at = timezone.now()
            submission.is_late = is_late
            submission.save()
        
        # Notify teacher
        CommunicationManager.send_email_report(
            assignment.assigned_by.email,
            f"New Submission: {assignment.title}",
            f"Student {request.user.get_full_name()} has submitted '{assignment.title}'\n\n"
            f"Content: {content[:200]}..."
        )
        
        logger.info(f"Assignment submitted: {assignment.title} by {request.user.username}")
        
        return Response({
            'status': 'submitted',
            'submission_id': submission.id,
            'submitted_at': submission.submitted_at,
            'is_late': is_late
        })
    
    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """Grade a submission (teacher only)"""
        if not hasattr(request.user, 'user_profile') or request.user.user_profile.role != UserRole.TEACHER:
            return Response({'error': 'Teachers only'}, status=403)
        
        submission_id = request.data.get('submission_id')
        score = request.data.get('score')
        feedback = request.data.get('feedback', '')
        
        if not submission_id or score is None:
            return Response({'error': 'submission_id and score required'}, status=400)
        
        try:
            submission = AssignmentSubmission.objects.get(id=submission_id, assignment=self.get_object())
            submission.score = score
            submission.feedback = feedback
            submission.graded_by = request.user
            submission.graded_at = timezone.now()
            submission.save()
            
            # Notify student
            CommunicationManager.send_email_report(
                submission.student.email,
                f"Assignment Graded: {submission.assignment.title}",
                f"Your assignment has been graded!\n\n"
                f"Score: {score}%\n"
                f"Feedback: {feedback}"
            )
            
            logger.info(f"Assignment graded: {submission.assignment.title} for student {submission.student.username}")
            
            return Response({
                'status': 'graded',
                'score': score,
                'feedback': feedback
            })
        except AssignmentSubmission.DoesNotExist:
            return Response({'error': 'Submission not found'}, status=404)