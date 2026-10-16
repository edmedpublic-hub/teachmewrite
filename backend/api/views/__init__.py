# backend/api/views/__init__.py
"""API Views Module"""

# Auth views
from .auth_views import (
    UserViewSet, register, change_password
)

# Lesson views
from .lesson_views import (
    LessonViewSet,
    UnitViewSet,
    LessonUnitViewSet,
    QuestionBankViewSet,
    StudentLessonProgressViewSet
)

# Progress views
from .progress_views import ProgressViewSet, TierProgressViewSet

# Institute views
from .institute_views import (
    InstituteViewSet, UserProfileViewSet, ClassViewSet,
    teacher_dashboard, institute_dashboard, parent_dashboard
)

# Assignment views
from .assignment_views import AssignmentViewSet

# Certificate views
from .certificate_views import CertificateViewSet

# Report views
from .report_views import mastery_report, export_report

# AI views
from .ai_views import diagnose_tier

# Adaptive Learning Views
from .adaptive_views import (
    get_lesson_unit,
    get_practice_questions,
    submit_practice,
    get_test_questions,
    submit_test
)

# Legacy compatibility exports
from .auth_views import UserViewSet as UserViewSetLegacy
from .lesson_views import LessonViewSet as LessonViewSetLegacy
from .progress_views import ProgressViewSet as ProgressViewSetLegacy
from .progress_views import TierProgressViewSet as TierProgressViewSetLegacy

__all__ = [
    'UserViewSet', 'register', 'change_password',
    'LessonViewSet', 'UnitViewSet', 'LessonUnitViewSet',
    'QuestionBankViewSet', 'StudentLessonProgressViewSet',
    'ProgressViewSet', 'TierProgressViewSet',
    'InstituteViewSet', 'UserProfileViewSet', 'ClassViewSet',
    'teacher_dashboard', 'institute_dashboard', 'parent_dashboard',
    'AssignmentViewSet',
    'CertificateViewSet',
    'mastery_report', 'export_report',
    'diagnose_tier',
    'get_lesson_unit', 'get_practice_questions', 'submit_practice',
    'get_test_questions', 'submit_test',
    'UserViewSetLegacy', 'LessonViewSetLegacy',
    'ProgressViewSetLegacy', 'TierProgressViewSetLegacy'
]