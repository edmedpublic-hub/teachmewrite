# backend/lessons/views.py
"""
Internal views for lessons app (not API views)
Note: For API endpoints, use api/views.py instead
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import Lesson, StudentProgress, TierProgress

# This file is intentionally minimal since API is handled by api/views.py
# Add any internal (non-API) views here if needed (e.g., for testing, admin extensions)


@login_required
@require_http_methods(['GET'])
def lesson_preview(request, lesson_id):
    """
    Internal view for lesson preview (non-API)
    This could be used for rendering lesson content in a custom admin panel
    """
    try:
        lesson = Lesson.objects.get(id=lesson_id, is_published=True)
        context = {
            'lesson': lesson,
            'progress': StudentProgress.objects.filter(
                user=request.user, 
                lesson=lesson
            ).first()
        }
        return render(request, 'lessons/preview.html', context)
    except Lesson.DoesNotExist:
        return render(request, '404.html', status=404)