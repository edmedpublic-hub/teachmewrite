# backend/lessons/validators.py
"""
Custom validators for models
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_positive_integer(value):
    """Validate that value is a positive integer"""
    if value < 0:
        raise ValidationError(
            _('Value must be a positive integer'),
            params={'value': value},
        )


def validate_mastery_score(value):
    """Validate mastery score between 0 and 100"""
    if value < 0 or value > 100:
        raise ValidationError(
            _('Mastery score must be between 0 and 100'),
            params={'value': value},
        )


def validate_phone_number(value):
    """Validate phone number format (Pakistan international format)"""
    if not value:
        return
    
    # Pakistan phone number pattern: +92XXXXXXXXXX or 03XXXXXXXXX
    pattern = r'^(\+92|0)?[0-9]{10,13}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Enter a valid phone number (e.g., +923001234567 or 03001234567)'),
            params={'value': value},
        )


def validate_cnic(value):
    """Validate CNIC/B-Form number format"""
    if not value:
        return
    
    # CNIC pattern: 12345-1234567-1 or 1234512345671
    pattern = r'^[0-9]{5}-[0-9]{7}-[0-9]{1}$|^[0-9]{13}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Enter a valid CNIC number (e.g., 12345-1234567-1 or 1234512345671)'),
            params={'value': value},
        )


def validate_certificate_number(value):
    """Validate certificate number format"""
    # Pattern: MAI-TIER-USERID-TIMESTAMP
    # Example: MAI-BASIC-123-20241215143022
    pattern = r'^MAI-[A-Z]+-\d+-\d{14}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Certificate number must follow format: MAI-TIER-USERID-TIMESTAMP'),
            params={'value': value},
        )


def validate_verification_code(value):
    """Validate verification code format"""
    # Pattern: 12 character hex-like string
    pattern = r'^[A-Z0-9]{12}$'
    if not re.match(pattern, value):
        raise ValidationError(
            _('Verification code must be 12 characters of uppercase letters and numbers'),
            params={'value': value},
        )


def validate_lesson_order(value):
    """Validate that lesson order is unique per tier"""
    # This is handled by unique_together constraint in Meta class
    pass


def validate_future_date(value):
    """Validate that date is in the future"""
    from django.utils import timezone
    
    if value and value <= timezone.now().date():
        raise ValidationError(
            _('Date must be in the future'),
            params={'value': value},
        )


def validate_past_date(value):
    """Validate that date is in the past"""
    from django.utils import timezone
    
    if value and value >= timezone.now().date():
        raise ValidationError(
            _('Date must be in the past'),
            params={'value': value},
        )