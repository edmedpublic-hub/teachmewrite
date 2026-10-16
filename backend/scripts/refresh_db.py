#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_mastery_project.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import IntegrityError
from lessons.models import Lesson, Tier, StudentProgress, TierProgress, Profile, UserProfile

def clear_database():
    """Clear existing data safely - handles missing tables"""
    print("Clearing existing data...")
    
    # Delete in correct order to avoid foreign key constraints
    try:
        StudentProgress.objects.all().delete()
        print("  - Cleared StudentProgress")
    except:
        pass
    
    try:
        TierProgress.objects.all().delete()
        print("  - Cleared TierProgress")
    except:
        pass
    
    try:
        UserProfile.objects.all().delete()
        print("  - Cleared UserProfile")
    except:
        pass
    
    try:
        Profile.objects.all().delete()
        print("  - Cleared Profile")
    except:
        pass
    
    try:
        Lesson.objects.all().delete()
        print("  - Cleared Lesson")
    except:
        pass
    
    # Delete test users (keep superusers)
    try:
        test_usernames = ['student_basic', 'student_intermediate', 'student_advanced', 'student_css']
        User.objects.filter(username__in=test_usernames).delete()
        print("  - Cleared test users")
    except:
        pass
    
    print("✓ Database cleared successfully")

def create_sample_curriculum():
    """Create sample tiered curriculum"""
    print("\n📚 Creating sample curriculum...")
    
    basic_lessons = [
        {
            'title': 'Basic Sentence Structure',
            'description': 'Learn to form complete, grammatically correct sentences',
            'content': 'A sentence must have a subject and predicate. The subject is who or what the sentence is about, and the predicate tells what the subject does or is.',
            'order': 1,
            'practice_questions': [
                {'question': 'Identify the subject: "The cat sleeps"', 'correct_answer': 'The cat'},
                {'question': 'Complete the sentence: "The dog ___"', 'correct_answer': 'barks'}
            ],
            'test_criteria': {'passing_score': 80, 'time_limit_minutes': 10}
        },
        {
            'title': 'Parts of Speech',
            'description': 'Master nouns, verbs, adjectives, and adverbs',
            'content': 'The eight parts of speech are fundamental to English grammar: nouns, pronouns, verbs, adjectives, adverbs, prepositions, conjunctions, and interjections.',
            'order': 2,
            'prerequisite_title': 'Basic Sentence Structure',
            'practice_questions': [
                {'question': 'What part of speech describes an action?', 'correct_answer': 'verb'},
                {'question': 'Which word is a noun in "The red ball bounced"?', 'correct_answer': 'ball'}
            ]
        },
        {
            'title': 'Punctuation Basics',
            'description': 'Learn periods, commas, question marks, and exclamation points',
            'content': 'Punctuation guides readers through your writing by indicating pauses, stops, and relationships between ideas.',
            'order': 3,
            'prerequisite_title': 'Parts of Speech'
        }
    ]
    
    intermediate_lessons = [
        {
            'title': 'Paragraph Development',
            'description': 'Write coherent, well-structured paragraphs',
            'content': 'A good paragraph has unity (one main idea), coherence (logical flow), and development (adequate support).',
            'order': 1,
            'practice_questions': [
                {'question': 'What is the first sentence of a paragraph typically called?', 'correct_answer': 'topic sentence'}
            ]
        },
        {
            'title': 'Essay Structure',
            'description': 'Master the five-paragraph essay format',
            'content': 'Essays require an introduction with a thesis statement, body paragraphs with supporting evidence, and a conclusion that reinforces the main argument.',
            'order': 2,
            'prerequisite_title': 'Paragraph Development'
        },
        {
            'title': 'Transitional Phrases',
            'description': 'Connect ideas smoothly between sentences and paragraphs',
            'content': 'Transitions guide readers through your arguments using words like "however," "furthermore," "consequently," and "in contrast."',
            'order': 3
        }
    ]
    
    advanced_lessons = [
        {
            'title': 'Argumentative Writing',
            'description': 'Build compelling arguments with evidence',
            'content': 'Strong arguments require clear claims, relevant evidence from credible sources, logical reasoning, and acknowledgment of counterarguments.',
            'order': 1
        },
        {
            'title': 'Research Integration',
            'description': 'Quote, paraphrase, and cite sources effectively',
            'content': 'Proper source integration builds credibility. Learn to introduce, cite, and explain quotations and paraphrased material.',
            'order': 2,
            'prerequisite_title': 'Argumentative Writing'
        },
        {
            'title': 'Style and Tone',
            'description': 'Adapt your writing for different audiences and purposes',
            'content': 'Formal writing for academic/business contexts differs from creative or informal writing. Choose vocabulary and sentence structure appropriately.',
            'order': 3
        }
    ]
    
    professional_lessons = [
        {
            'title': 'CSS Essay Writing',
            'description': 'Master the CSS exam essay format and expectations',
            'content': 'CSS essays require depth, analysis, and precise language. Practice writing within time constraints on diverse topics.',
            'order': 1
        },
        {
            'title': 'Precis Writing',
            'description': 'Summarize complex texts concisely and accurately',
            'content': 'A precis captures essential arguments in about one-third of the original length while maintaining the author\'s tone and logical flow.',
            'order': 2
        },
        {
            'title': 'Comparative Analysis',
            'description': 'Compare and contrast multiple perspectives on issues',
            'content': 'Critical analysis requires examining multiple viewpoints, identifying similarities and differences, and evaluating the strength of each position.',
            'order': 3
        }
    ]
    
    def create_lessons_with_prereqs(lessons_data, tier):
        created_lessons = {}
        for lesson_data in lessons_data:
            prereq_title = lesson_data.pop('prerequisite_title', None)
            
            lesson, created = Lesson.objects.get_or_create(
                title=lesson_data['title'],
                tier=tier,
                defaults={
                    'description': lesson_data['description'],
                    'content': lesson_data['content'],
                    'order': lesson_data['order'],
                    'practice_questions': lesson_data.get('practice_questions', []),
                    'test_criteria': lesson_data.get('test_criteria', {'passing_score': 100}),
                    'xp_reward': 10 + (lesson_data['order'] * 5),
                    'is_published': True
                }
            )
            
            if created:
                if prereq_title and prereq_title in created_lessons:
                    lesson.prerequisite = created_lessons[prereq_title]
                    lesson.save()
                created_lessons[lesson.title] = lesson
                print(f"  ✓ Created: [{tier}] {lesson.title}")
            else:
                print(f"  ⚠ Already exists: [{tier}] {lesson.title}")
    
    create_lessons_with_prereqs(basic_lessons, Tier.BASIC)
    create_lessons_with_prereqs(intermediate_lessons, Tier.INTERMEDIATE)
    create_lessons_with_prereqs(advanced_lessons, Tier.ADVANCED)
    create_lessons_with_prereqs(professional_lessons, Tier.PROFESSIONAL)
    
    print(f"\n✓ Curriculum ready: {Lesson.objects.count()} lessons")

def create_test_users():
    """Create test users for development"""
    print("\n👥 Creating test users...")
    
    users_data = [
        {'username': 'student_basic', 'password': 'testpass123', 'email': 'basic@test.com', 
         'first_name': 'Basic', 'last_name': 'Student', 'education_level': 'MATRIC', 'target_tier': 'BASIC'},
        {'username': 'student_intermediate', 'password': 'testpass123', 'email': 'intermediate@test.com',
         'first_name': 'Intermediate', 'last_name': 'Student', 'education_level': 'INTERMEDIATE', 'target_tier': 'INTERMEDIATE'},
        {'username': 'student_advanced', 'password': 'testpass123', 'email': 'advanced@test.com',
         'first_name': 'Advanced', 'last_name': 'Student', 'education_level': 'BACHELORS', 'target_tier': 'ADVANCED'},
        {'username': 'student_css', 'password': 'testpass123', 'email': 'css@test.com',
         'first_name': 'CSS', 'last_name': 'Candidate', 'education_level': 'CSS', 'target_tier': 'PROFESSIONAL'},
    ]
    
    created_count = 0
    for user_data in users_data:
        education_level = user_data.pop('education_level', None)
        target_tier = user_data.pop('target_tier', None)
        
        # Check if user already exists
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
            created_count += 1
            print(f"  ✓ Created user: {user.username}")
        else:
            print(f"  ✓ User already exists: {user.username}")
        
        # Create or update profile
        try:
            profile, profile_created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'education_level': education_level,
                    'target_tier': target_tier,
                    'city': 'Test City',
                    'country': 'Pakistan'
                }
            )
            if profile_created:
                print(f"    └─ Created profile for: {user.username}")
            else:
                print(f"    └─ Profile exists for: {user.username}")
        except IntegrityError:
            print(f"    └─ Profile already exists for: {user.username}")
        
        # Create or update user profile with role
        try:
            user_profile, up_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'STUDENT',
                    'phone': '',
                    'address': ''
                }
            )
        except IntegrityError:
            pass
        
        # Initialize tier progress
        for tier in Tier:
            TierProgress.objects.get_or_create(
                user=user,
                tier=tier.value,
                defaults={
                    'is_unlocked': tier == Tier.BASIC,
                    'total_lessons': Lesson.objects.filter(tier=tier.value, is_published=True).count()
                }
            )
    
    print(f"\n✓ Test users ready. Passwords: 'testpass123'")
    print(f"  Created {created_count} new users")

def main():
    print("=" * 60)
    print("🎯 MasteryAI Database Refresh Tool")
    print("=" * 60)
    
    # Confirm action
    response = input("\n⚠️  This will DELETE all existing data. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Operation cancelled.")
        return
    
    print("\n🔄 Starting database refresh...\n")
    
    try:
        clear_database()
        create_sample_curriculum()
        create_test_users()
        
        print("\n" + "=" * 60)
        print("✅ DATABASE REFRESH COMPLETE!")
        print("=" * 60)
        print(f"\n📊 Statistics:")
        print(f"   📚 Total lessons: {Lesson.objects.count()}")
        print(f"   👥 Total users: {User.objects.count()}")
        print(f"   👤 Total profiles: {Profile.objects.count()}")
        
        print("\n🔑 Test User Credentials:")
        print("   • student_basic / testpass123 (Matric level)")
        print("   • student_intermediate / testpass123 (Intermediate level)")
        print("   • student_advanced / testpass123 (Graduation level)")
        print("   • student_css / testpass123 (CSS level)")
        
        print("\n🚀 Next steps:")
        print("   1. Start the server: python manage.py runserver")
        print("   2. Visit admin panel: http://127.0.0.1:8000/admin/")
        print("   3. Test API: python quick_test.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure migrations are applied: python manage.py migrate")
        print("2. Check if database file is writable")
        print("3. Try deleting db.sqlite3 and running migrations again")

if __name__ == "__main__":
    main()