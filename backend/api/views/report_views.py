# backend/api/views/report_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import models as django_models
from django.db.models import F, Sum, Avg
from django.utils import timezone
from lessons.models import Lesson, StudentProgress, TierProgress, Tier
from ..report_utils import ReportGenerator


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mastery_report(request):
    """Generate comprehensive mastery report for stakeholder sharing"""
    user = request.user
    
    tier_progress = TierProgress.objects.filter(user=user)
    lesson_progress = StudentProgress.objects.filter(user=user)
    
    total_lessons = Lesson.objects.filter(is_published=True).count()
    mastered_lessons = lesson_progress.filter(
        mastery_score__gte=F('lesson__required_mastery_score')
    ).count()
    
    total_time_seconds = lesson_progress.aggregate(total=django_models.Sum('time_spent_seconds'))['total'] or 0
    total_hours = total_time_seconds / 3600
    
    tier_breakdown = []
    for tier in Tier:
        tier_lessons = Lesson.objects.filter(tier=tier.value, is_published=True)
        tier_mastered = lesson_progress.filter(
            lesson__tier=tier.value,
            mastery_score__gte=F('lesson__required_mastery_score')
        ).count()
        
        tier_breakdown.append({
            'tier': tier.label,
            'tier_code': tier.value,
            'total_lessons': tier_lessons.count(),
            'mastered_lessons': tier_mastered,
            'completion_percentage': (tier_mastered / tier_lessons.count() * 100) if tier_lessons.count() > 0 else 0
        })
    
    profile_info = {}
    if hasattr(user, 'profile'):
        profile_info = {
            'education_level': user.profile.get_education_level_display() if user.profile.education_level else None,
            'target_tier': user.profile.get_target_tier_display() if user.profile.target_tier else None,
            'streak_days': user.profile.streak_days,
            'total_xp': user.profile.total_xp
        }
    
    report = {
        'student': {
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'email': user.email,
            'member_since': user.date_joined.date().isoformat(),
            **profile_info
        },
        'summary': {
            'overall_mastery': (mastered_lessons / total_lessons * 100) if total_lessons > 0 else 0,
            'total_lessons_mastered': mastered_lessons,
            'total_lessons': total_lessons,
            'total_attempts': lesson_progress.aggregate(total=django_models.Sum('attempts'))['total'] or 0,
            'average_mastery_score': lesson_progress.aggregate(avg=django_models.Avg('mastery_score'))['avg'] or 0,
            'total_time_spent_hours': round(total_hours, 1)
        },
        'tier_breakdown': tier_breakdown,
        'recent_activity': list(lesson_progress.order_by('-last_attempt_at')[:5].values(
            'lesson__title', 'mastery_score', 'last_attempt_at'
        )),
        'generated_at': timezone.now().isoformat()
    }
    
    shareable_text = f"""
📊 MASTERY REPORT - {report['student']['name']}
{'=' * 40}

🎯 OVERALL MASTERY: {report['summary']['overall_mastery']:.1f}%
✅ Lessons Mastered: {report['summary']['total_lessons_mastered']}/{report['summary']['total_lessons']}
⏱️  Total Time: {report['summary']['total_time_spent_hours']} hours

📚 TIER BREAKDOWN:
{chr(10).join([f"  • {t['tier']}: {t['mastered_lessons']}/{t['total_lessons']} ({t['completion_percentage']:.0f}%)" for t in tier_breakdown])}

📅 Generated: {report['generated_at'][:10]}
    """
    
    return Response({
        'report': report,
        'shareable_text': shareable_text,
        'shareable_html': shareable_text.replace('\n', '<br>')
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_report(request):
    """Export mastery report as PDF or CSV"""
    format_type = request.query_params.get('format', 'pdf')
    
    user = request.user
    tier_progress = TierProgress.objects.filter(user=user)
    lesson_progress = StudentProgress.objects.filter(user=user)
    
    total_lessons = Lesson.objects.filter(is_published=True).count()
    mastered_lessons = lesson_progress.filter(
        mastery_score__gte=F('lesson__required_mastery_score')
    ).count()
    
    report_data = {
        'overall_mastery': (mastered_lessons / total_lessons * 100) if total_lessons > 0 else 0,
        'mastered_lessons': mastered_lessons,
        'total_lessons': total_lessons,
        'tier_breakdown': [
            {
                'tier': tp.tier,
                'mastery': tp.mastery_percentage,
                'completed': tp.is_completed
            } for tp in tier_progress
        ]
    }
    
    generator = ReportGenerator(user, report_data)
    
    if format_type == 'pdf':
        pdf_file = generator.generate_pdf_report()
        return Response(pdf_file, content_type='application/pdf')
    elif format_type == 'csv':
        csv_file = generator.generate_csv_report()
        return Response(csv_file, content_type='text/csv')
    else:
        return Response({'error': 'Invalid format'}, status=400)