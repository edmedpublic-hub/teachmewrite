#!/usr/bin/env python
"""Seed data for TeachMeWrite Learning System - MATCHING EXISTING LESSONS"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_mastery_project.settings')
django.setup()

from lessons.models import Unit, Lesson, LessonUnit, QuestionBank

print("🌱 Seeding TeachMeWrite Learning Data...")
print("=" * 50)

# ============================================
# GET OR CREATE UNIT
# ============================================

unit, created = Unit.objects.get_or_create(
    title="Simple Sentence Structure",
    defaults={
        'tier': "BASIC",
        'description': """Master the art of writing simple sentences. 
This unit teaches you the fundamental building blocks of English sentences.""",
        'order': 1,
        'is_active': True
    }
)

if created:
    print(f"✅ Created Unit: {unit.title}")
else:
    print(f"📚 Unit exists: {unit.title}")

# ============================================
# GET OR CREATE LESSONS WITH CORRECT TITLES
# ============================================

# First, let's see what lessons already exist
existing_lessons = Lesson.objects.filter(tier="BASIC").order_by('order')
print(f"\n📚 Existing BASIC tier lessons:")
for lesson in existing_lessons:
    print(f"   - {lesson.title} (order: {lesson.order})")

print("\n" + "=" * 50)

# Define lessons with their correct titles (matching your existing ones)
lessons_to_create = [
    {
        'title': "Basic Sentence Structure",  # This already exists
        'new_title': "What is a Subject?",  # We'll update this
        'description': "Learn to identify the subject of a sentence - who or what the sentence is about.",
        'teaching_content': """
<h2>Understanding the Subject of a Sentence</h2>
<p>The <strong>subject</strong> is the person, place, thing, or idea that is doing or being something in a sentence.</p>

<h3>Key Points:</h3>
<ul>
    <li>The subject tells us WHO or WHAT the sentence is about</li>
    <li>The subject usually comes at the beginning of the sentence</li>
    <li>The subject can be a single noun or a noun phrase</li>
</ul>

<h3>Examples:</h3>
<ul>
    <li><strong>Ali</strong> writes stories. (Who writes? Ali)</li>
    <li><strong>The cat</strong> sleeps. (What sleeps? The cat)</li>
    <li><strong>Education</strong> is important. (What is important? Education)</li>
</ul>
""",
        'order': 1
    },
    {
        'title': "Parts of Speech",  # This already exists
        'new_title': "Understanding the Predicate",
        'description': "Learn about the predicate - what the subject does or is.",
        'teaching_content': """
<h2>Understanding the Predicate</h2>
<p>The <strong>predicate</strong> tells us what the subject does or is. It contains the verb and everything that follows.</p>

<h3>Key Points:</h3>
<ul>
    <li>The predicate explains the action or state of the subject</li>
    <li>Every complete sentence must have a predicate</li>
    <li>The predicate always includes the verb</li>
</ul>

<h3>Examples:</h3>
<ul>
    <li>Ali <strong>writes stories</strong>. (What does Ali do? Writes stories)</li>
    <li>The cat <strong>sleeps on the sofa</strong>. (What does the cat do? Sleeps on the sofa)</li>
    <li>She <strong>is a teacher</strong>. (What is she? A teacher)</li>
</ul>
""",
        'order': 2
    },
    {
        'title': "Punctuation Basics",  # This already exists
        'new_title': "Subject + Verb Pattern",
        'description': "Learn the simplest sentence pattern using intransitive verbs.",
        'teaching_content': """
<h2>Subject + Verb Pattern</h2>
<p>The simplest sentence pattern in English is Subject + Verb. This pattern uses <strong>intransitive verbs</strong> (verbs that don't need an object).</p>

<h3>Structure:</h3>
<p><strong>Subject + Verb</strong></p>

<h3>Examples:</h3>
<ul>
    <li><strong>Birds</strong> <strong>fly</strong>.</li>
    <li><strong>The baby</strong> <strong>cries</strong>.</li>
    <li><strong>Time</strong> <strong>passes</strong>.</li>
</ul>
""",
        'order': 3
    }
]

# Update or create lessons
lesson_objects = []

for lesson_data in lessons_to_create:
    # Try to get existing lesson by title
    lesson = Lesson.objects.filter(title=lesson_data['title']).first()
    
    if lesson:
        # Update existing lesson with new content
        lesson.description = lesson_data['description']
        lesson.content = lesson_data['teaching_content']
        lesson.save()
        print(f"✅ Updated Lesson: {lesson.title} → New content added")
        lesson_objects.append(lesson)
    else:
        # Create new lesson if doesn't exist
        # Find highest order number
        max_order = Lesson.objects.filter(tier="BASIC").aggregate(max_order=models.Max('order'))['max_order'] or 0
        lesson = Lesson.objects.create(
            title=lesson_data['title'],
            tier="BASIC",
            description=lesson_data['description'],
            content=lesson_data['teaching_content'],
            order=max_order + 1,
            is_published=True,
            xp_reward=10,
            estimated_duration_minutes=15,
            required_mastery_score=100
        )
        print(f"✅ Created New Lesson: {lesson.title}")
        lesson_objects.append(lesson)

# Create additional new lessons for S+V+O and S+V+C
additional_lessons = [
    {
        'title': "Subject + Verb + Object",
        'description': "Learn to use transitive verbs with direct objects.",
        'teaching_content': """
<h2>Subject + Verb + Object Pattern</h2>
<p>This pattern uses <strong>transitive verbs</strong> - verbs that need an object to complete their meaning.</p>

<h3>Structure:</h3>
<p><strong>Subject + Verb + Object</strong> (The object receives the action)</p>

<h3>Examples:</h3>
<ul>
    <li><strong>Ali</strong> <strong>eats</strong> <strong>an apple</strong>.</li>
    <li><strong>The teacher</strong> <strong>explains</strong> <strong>the lesson</strong>.</li>
    <li><strong>She</strong> <strong>writes</strong> <strong>a letter</strong>.</li>
</ul>
""",
        'order': 4
    },
    {
        'title': "Subject + Verb + Complement",
        'description': "Learn to use linking verbs with subject complements.",
        'teaching_content': """
<h2>Subject + Verb + Complement Pattern</h2>
<p>This pattern uses <strong>linking verbs</strong> (like 'is', 'are', 'was', 'become') that connect the subject to a complement that describes or identifies it.</p>

<h3>Structure:</h3>
<p><strong>Subject + Linking Verb + Complement</strong></p>

<h3>Examples:</h3>
<ul>
    <li><strong>She</strong> <strong>is</strong> <strong>a doctor</strong>.</li>
    <li><strong>The sky</strong> <strong>looks</strong> <strong>beautiful</strong>.</li>
    <li><strong>He</strong> <strong>became</strong> <strong>famous</strong>.</li>
</ul>
""",
        'order': 5
    }
]

for lesson_data in additional_lessons:
    existing = Lesson.objects.filter(title=lesson_data['title']).first()
    if not existing:
        lesson = Lesson.objects.create(
            title=lesson_data['title'],
            tier="BASIC",
            description=lesson_data['description'],
            content=lesson_data['teaching_content'],
            order=lesson_data['order'],
            is_published=True,
            xp_reward=10,
            estimated_duration_minutes=15,
            required_mastery_score=100
        )
        print(f"✅ Created New Lesson: {lesson.title}")
        lesson_objects.append(lesson)
    else:
        print(f"📚 Lesson already exists: {existing.title}")
        lesson_objects.append(existing)

# ============================================
# CREATE LESSON UNITS
# ============================================

print("\n" + "=" * 50)
print("📚 Creating/Updating LessonUnits...")

for i, lesson in enumerate(lesson_objects, 1):
    lesson_unit, created = LessonUnit.objects.get_or_create(
        unit=unit,
        lesson=lesson,
        defaults={
            'order': i,
            'teaching_content': lesson.content,
            'examples': '["Example sentence 1", "Example sentence 2"]',
            'practice_pass_threshold': 70,
            'test_pass_threshold': 80,
            'max_practice_attempts': 5
        }
    )
    if created:
        print(f"  ✅ Created LessonUnit: {lesson.title}")
    else:
        print(f"  📚 LessonUnit exists: {lesson.title}")

# ============================================
# CREATE QUESTIONS FOR EACH LESSON
# ============================================

print("\n" + "=" * 50)
print("📝 Creating Questions...")

# Questions mapped to lesson titles
questions_by_lesson = {
    'Basic Sentence Structure': [
        {
            'type': 'MCQ',
            'difficulty': 1,
            'question': 'What is the subject in this sentence? "The beautiful flowers bloom in spring."',
            'options': ['beautiful', 'flowers', 'bloom', 'spring'],
            'correct': 'flowers',
            'tags': ['subject', 'identification'],
            'explanation': 'The subject is "flowers" because it tells us what the sentence is about.'
        },
        {
            'type': 'MCQ',
            'difficulty': 2,
            'question': 'Which sentence has a compound subject?',
            'options': ['Ali runs fast.', 'Ali and Sara study together.', 'The dog barks loudly.', 'She sings beautifully.'],
            'correct': 'Ali and Sara study together.',
            'tags': ['subject', 'compound'],
            'explanation': 'A compound subject has two or more subjects joined by "and".'
        },
        {
            'type': 'IDENTIFY',
            'difficulty': 1,
            'question': 'Identify the subject in this sentence: "My brother loves cricket."',
            'options': None,
            'correct': 'My brother',
            'tags': ['subject', 'identification'],
            'explanation': '"My brother" is the complete subject.'
        }
    ],
    'Parts of Speech': [
        {
            'type': 'MCQ',
            'difficulty': 1,
            'question': 'What is the predicate in "The children play happily"?',
            'options': ['The children', 'play happily', 'children play', 'happily'],
            'correct': 'play happily',
            'tags': ['predicate', 'identification'],
            'explanation': 'The predicate tells what the subject does.'
        },
        {
            'type': 'MCQ',
            'difficulty': 2,
            'question': 'Which sentence has a compound predicate?',
            'options': ['She sings.', 'She sings and dances.', 'She is singing.', 'She sings beautifully.'],
            'correct': 'She sings and dances.',
            'tags': ['predicate', 'compound'],
            'explanation': 'A compound predicate has two or more verbs.'
        }
    ],
    'Punctuation Basics': [
        {
            'type': 'MCQ',
            'difficulty': 1,
            'question': 'Which sentence follows the Subject + Verb pattern?',
            'options': ['She reads books.', 'The sun rises.', 'He is a teacher.', 'They play cricket.'],
            'correct': 'The sun rises.',
            'tags': ['S+V', 'pattern'],
            'explanation': '"The sun rises" is Subject + Verb pattern.'
        },
        {
            'type': 'JUMBLE',
            'difficulty': 2,
            'question': 'Rearrange: "birds / fly / south / in winter"',
            'options': None,
            'correct': 'Birds fly south in winter.',
            'tags': ['S+V', 'jumble'],
            'explanation': 'Subject (Birds) + Verb (fly) + additional info.'
        }
    ],
    'Subject + Verb + Object': [
        {
            'type': 'MCQ',
            'difficulty': 1,
            'question': 'Identify the object in: "She reads a book"',
            'options': ['She', 'reads', 'a book', 'book'],
            'correct': 'a book',
            'tags': ['object', 'transitive'],
            'explanation': 'The object receives the action of the verb.'
        },
        {
            'type': 'COMPLETION',
            'difficulty': 2,
            'question': 'Complete: "The chef ___________ a delicious meal"',
            'options': None,
            'correct': 'cooks',
            'tags': ['verb', 'object'],
            'explanation': 'Add a transitive verb like cooks, prepares, makes.'
        }
    ],
    'Subject + Verb + Complement': [
        {
            'type': 'MCQ',
            'difficulty': 1,
            'question': 'Identify the complement in: "She is a doctor"',
            'options': ['She', 'is', 'a doctor', 'doctor'],
            'correct': 'a doctor',
            'tags': ['complement', 'linking verb'],
            'explanation': 'The complement renames or describes the subject.'
        },
        {
            'type': 'IDENTIFY',
            'difficulty': 2,
            'question': 'What type of complement is in: "The food tastes delicious"',
            'options': None,
            'correct': 'predicate adjective',
            'tags': ['complement', 'adjective'],
            'explanation': '"Delicious" is a predicate adjective describing the food.'
        }
    ]
}

total_questions = 0

for lesson_title, questions in questions_by_lesson.items():
    # Find the lesson
    lesson = Lesson.objects.filter(title=lesson_title).first()
    if not lesson:
        print(f"  ⚠️ Lesson not found: {lesson_title}")
        continue
    
    # Get the LessonUnit
    lesson_unit = LessonUnit.objects.filter(lesson=lesson, unit=unit).first()
    if not lesson_unit:
        print(f"  ⚠️ LessonUnit not found for: {lesson_title}")
        continue
    
    print(f"\n  📖 Adding questions for: {lesson_title}")
    
    # Create questions
    for q_data in questions:
        question, created = QuestionBank.objects.get_or_create(
            lesson_unit=lesson_unit,
            question_text=q_data['question'],
            defaults={
                'question_type': q_data['type'],
                'difficulty': q_data['difficulty'],
                'correct_answer': q_data['correct'],
                'options': q_data.get('options'),
                'explanation': q_data['explanation'],
                'tags': q_data['tags'],
                'is_active': True
            }
        )
        if created:
            total_questions += 1
            print(f"    ✅ Created: {q_data['type']} - {q_data['question'][:40]}...")
        else:
            print(f"    📚 Exists: {q_data['type']} - {q_data['question'][:40]}...")

print("\n" + "=" * 50)
print("✅ SEEDING COMPLETE!")
print("=" * 50)

# Final Summary
print(f"\n📊 Final Database Status:")
print(f"   Units: {Unit.objects.count()}")
print(f"   Lessons (BASIC tier): {Lesson.objects.filter(tier='BASIC').count()}")
print(f"   LessonUnits: {LessonUnit.objects.count()}")
print(f"   Questions: {QuestionBank.objects.count()}")
print(f"   New questions created: {total_questions}")

# List all lessons with their question counts
print("\n📚 Lessons Summary:")
for lesson in Lesson.objects.filter(tier='BASIC').order_by('order'):
    lesson_unit = LessonUnit.objects.filter(lesson=lesson, unit=unit).first()
    if lesson_unit:
        q_count = QuestionBank.objects.filter(lesson_unit=lesson_unit).count()
        print(f"   • {lesson.title}: {q_count} questions")