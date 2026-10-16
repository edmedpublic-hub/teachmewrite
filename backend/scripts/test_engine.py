#!/usr/bin/env python
"""Quick test script for the learning engine - Run with: python test_engine.py"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_mastery_project.settings')
django.setup()

# Now import and test
from lessons.learning_engine import AdaptiveLearningEngine
from lessons.models import Unit, LessonUnit, QuestionBank

print("=" * 50)
print("TEACHMEWRITE LEARNING ENGINE TEST")
print("=" * 50)

# Test 1: Engine constants
print("\n✅ Engine Configuration:")
print(f"   Max practice questions: {AdaptiveLearningEngine.MAX_PRACTICE_QUESTIONS}")
print(f"   Max test questions: {AdaptiveLearningEngine.MAX_TEST_QUESTIONS}")
print(f"   Default practice: {AdaptiveLearningEngine.DEFAULT_PRACTICE_QUESTIONS}")
print(f"   Default test: {AdaptiveLearningEngine.DEFAULT_TEST_QUESTIONS}")

# Test 2: Database status
print("\n📊 Database Status:")
print(f"   Units: {Unit.objects.count()}")
print(f"   LessonUnits: {LessonUnit.objects.count()}")
print(f"   Questions: {QuestionBank.objects.count()}")

if Unit.objects.count() == 0:
    print("\n⚠️ No data found! You need to seed the database.")
    print("   Run: python manage.py shell < seed_data.py")
else:
    print("\n✅ Database has content! Engine is ready.")

print("\n" + "=" * 50)