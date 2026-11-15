# backend/api/views/writing_views.py
# Day 107 Pillar 3 -- Django callback endpoint for FastAPI BackgroundTasks.
#
# Contract: FastAPI POSTs the /feedback result here after the HTTP response
# has returned to the user. Auth via X-Internal-Key header (service-to-service),
# NOT JWT -- the user's token has already been consumed by /feedback.
#
# Idempotent on session_id (UUID). Retries do not create duplicate rows.
#
# Privacy: student_text is the student's own writing. Never log it.

import logging
import os
import secrets
import uuid

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from lessons.models import TierProgress, WritingFeedback

logger = logging.getLogger(__name__)


def _check_internal_key(request):
    """Returns (ok, error_detail). Fail-closed if INTERNAL_API_KEY not set."""
    expected = os.environ.get("INTERNAL_API_KEY", "").strip()
    if not expected:
        logger.error("INTERNAL_API_KEY not set -- rejecting all callback requests")
        return False, "Service not configured"
    supplied = request.headers.get("X-Internal-Key", "").strip()
    if not supplied:
        return False, "Missing X-Internal-Key header"
    if len(supplied) != len(expected):
        return False, "Invalid internal key"
    if not secrets.compare_digest(supplied, expected):
        return False, "Invalid internal key"
    return True, ""


@api_view(["POST"])
@authentication_classes([])  # no JWT, no session -- service auth only
@permission_classes([AllowAny])
def feedback_callback(request):
    """Idempotent callback: FastAPI BackgroundTask POSTs here after /feedback."""
    ok, err = _check_internal_key(request)
    if not ok:
        return Response({"detail": err}, status=status.HTTP_401_UNAUTHORIZED)

    required = ("user_id", "session_id", "student_text", "level", "feedback")
    missing = [k for k in required if k not in request.data]
    if missing:
        return Response(
            {"detail": "Missing required fields: %s" % missing},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(pk=int(request.data["user_id"]))
    except (User.DoesNotExist, ValueError, TypeError):
        return Response(
            {"detail": "User not found: %s" % request.data.get("user_id")},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        session_uuid = uuid.UUID(str(request.data["session_id"]))
    except (ValueError, TypeError):
        return Response(
            {"detail": "Invalid session_id (must be UUID)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    feedback = request.data["feedback"]
    if not isinstance(feedback, dict):
        return Response(
            {"detail": "feedback must be an object"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        overall_score = int(feedback["overall_score"])
        issues = feedback.get("issues", [])
        rewrite_suggestion = feedback["rewrite_suggestion"]
        level_appropriate = bool(feedback["level_appropriate"])
    except (KeyError, ValueError, TypeError) as e:
        return Response(
            {"detail": "Malformed feedback: %s" % e},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not isinstance(issues, list):
        return Response(
            {"detail": "feedback.issues must be a list"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not (0 <= overall_score <= 100):
        return Response({"detail": "overall_score must be 0-100"}, status=400)

    try:
        level = int(request.data["level"])
    except (ValueError, TypeError):
        return Response({"detail": "level must be an integer"}, status=400)
    if not (1 <= level <= 7):
        return Response({"detail": "level must be 1-7"}, status=400)

    # tier_at_submission via centralized classmethod (Cell 6a)
    tier_at_submission = TierProgress.current_tier_for(user).value

    obj, created = WritingFeedback.objects.get_or_create(
        session_id=session_uuid,
        defaults={
            "user": user,
            "student_text": request.data["student_text"],
            "level": level,
            "tier_at_submission": tier_at_submission,
            "overall_score": overall_score,
            "issues": issues,
            "rewrite_suggestion": rewrite_suggestion,
            "level_appropriate": level_appropriate,
        },
    )

    if created:
        return Response(
            {"id": obj.id, "created": True},
            status=status.HTTP_201_CREATED,
        )
    # Duplicate: return existing row id; flag if content differs
    if obj.user_id != user.id:
        logger.warning(
            "session_id %s reused by different user (%s vs %s)",
            session_uuid, obj.user_id, user.id,
        )
    return Response(
        {"id": obj.id, "created": False, "detail": "already exists"},
        status=status.HTTP_200_OK,
    )
