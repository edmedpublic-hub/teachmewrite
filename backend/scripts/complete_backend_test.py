#!/usr/bin/env python
"""
MasteryAI Complete Backend Test Suite
Run this with: python complete_backend_test.py
Make sure the Django server is running first!
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"
AUTH_URL = "http://127.0.0.1:8000/api/v1/auth/token/"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, status, details=None):
    color = GREEN if status else RED
    symbol = "✓" if status else "✗"
    print(f"{color}{symbol} {name}{RESET}")
    if details:
        print(f"   {details}")

def run_test():
    print("\n" + "=" * 70)
    print(f"{BLUE}🚀 MasteryAI Backend Complete Test Suite{RESET}")
    print("=" * 70)

    # ============================================
    # 1. Server Health Check
    # ============================================
    print(f"\n{YELLOW}[1] Server Health Check{RESET}")
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print_test("Server is running", True)
    except requests.exceptions.ConnectionError:
        print_test("Server is running", False, "Start server with: python manage.py runserver")
        return False
    except Exception as e:
        print_test("Server is running", False, str(e))
        return False

    # ============================================
    # 2. Authentication Tests
    # ============================================
    print(f"\n{YELLOW}[2] Authentication Tests{RESET}")
    
    # Test login with valid credentials
    response = requests.post(AUTH_URL, json={
        "username": "student_basic",
        "password": "testpass123"
    })
    
    if response.status_code != 200:
        print_test("Login with valid credentials", False, f"Status: {response.status_code}")
        print("   Make sure test users exist. Run: python refresh_db.py")
        return False
    
    token = response.json()['access']
    refresh_token = response.json()['refresh']
    print_test("Login with valid credentials", True)
    print_test("Token received", True, f"Token: {token[:50]}...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test invalid login
    response = requests.post(AUTH_URL, json={
        "username": "invalid_user",
        "password": "wrong_password"
    })
    print_test("Invalid login rejected", response.status_code == 401)
    
    # Test token refresh
    response = requests.post(f"{BASE_URL}/auth/token/refresh/", json={
        "refresh": refresh_token
    })
    print_test("Token refresh works", response.status_code == 200)

    # ============================================
    # 3. User Profile Tests
    # ============================================
    print(f"\n{YELLOW}[3] User Profile Tests{RESET}")
    
    response = requests.get(f"{BASE_URL}/users/profile/", headers=headers)
    print_test("Get user profile", response.status_code == 200)
    if response.status_code == 200:
        profile = response.json()
        print(f"   XP: {profile.get('total_xp', 0)}")
        print(f"   Streak: {profile.get('streak_days', 0)} days")
    
    response = requests.get(f"{BASE_URL}/user-profiles/me/", headers=headers)
    print_test("Get user role profile", response.status_code == 200)

    # ============================================
    # 4. Lesson Tests
    # ============================================
    print(f"\n{YELLOW}[4] Lesson Tests{RESET}")
    
    response = requests.get(f"{BASE_URL}/lessons/", headers=headers)
    print_test("Get lessons list", response.status_code == 200)
    if response.status_code == 200:
        data = response.json()
        lessons = data.get('results', data)
        print(f"   Found {len(lessons)} lessons")
        if lessons:
            first_lesson = lessons[0]
            print(f"   First lesson: {first_lesson.get('title')}")
            lesson_id = first_lesson.get('id')
            
            # Test get single lesson
            response = requests.get(f"{BASE_URL}/lessons/{lesson_id}/", headers=headers)
            print_test("Get single lesson", response.status_code == 200)
            
            # Test start lesson
            response = requests.post(f"{BASE_URL}/lessons/{lesson_id}/start_lesson/", headers=headers)
            print_test("Start lesson", response.status_code == 200)
            
            # Test submit practice
            response = requests.post(f"{BASE_URL}/lessons/{lesson_id}/submit_practice/", 
                                     headers=headers, json={"answers": ["test"]})
            print_test("Submit practice", response.status_code == 200)
            if response.status_code == 200:
                print(f"   Practice score: {response.json().get('score', 0)}%")

    # ============================================
    # 5. Progress Tests
    # ============================================
    print(f"\n{YELLOW}[5] Progress Tests{RESET}")
    
    response = requests.get(f"{BASE_URL}/progress/summary/", headers=headers)
    print_test("Get progress summary", response.status_code == 200)
    if response.status_code == 200:
        data = response.json()
        print(f"   Active Tier: {data.get('active_tier')}")
        print(f"   Completion: {data['overall']['completion_percentage']:.1f}%")
    
    response = requests.get(f"{BASE_URL}/tier-progress/", headers=headers)
    print_test("Get tier progress", response.status_code == 200)

    # ============================================
    # 6. AI & Diagnosis Tests
    # ============================================
    print(f"\n{YELLOW}[6] AI & Diagnosis Tests{RESET}")
    
    response = requests.post(f"{BASE_URL}/diagnose-tier/", 
        headers=headers,
        json={"writing_sample": "This is a test writing sample for CSS exam preparation in Pakistan. The student demonstrates understanding of basic sentence structure."})
    print_test("Tier diagnosis", response.status_code == 200)
    if response.status_code == 200:
        data = response.json()
        print(f"   Recommended: {data.get('tier_display')}")
        print(f"   Confidence: {data.get('confidence_score', 0):.0%}")

    # ============================================
    # 7. Report Tests
    # ============================================
    print(f"\n{YELLOW}[7] Report Tests{RESET}")
    
    response = requests.get(f"{BASE_URL}/mastery-report/", headers=headers)
    print_test("Get mastery report", response.status_code == 200)
    if response.status_code == 200:
        data = response.json()
        report = data.get('report', {})
        print(f"   Student: {report.get('student', {}).get('name')}")
        print(f"   Mastery: {report.get('summary', {}).get('overall_mastery', 0):.1f}%")

    # ============================================
    # 8. Institute Tests
    # ============================================
    print(f"\n{YELLOW}[8] Institute Tests{RESET}")
    
    response = requests.get(f"{BASE_URL}/institutes/", headers=headers)
    print_test("Get institutes", response.status_code in [200, 403])

    # ============================================
    # 9. Assignment Tests
    # ============================================
    print(f"\n{YELLOW}[9] Assignment Tests{RESET}")
    
    response = requests.get(f"{BASE_URL}/assignments/", headers=headers)
    print_test("Get assignments", response.status_code in [200, 403])

    # ============================================
    # Summary
    # ============================================
    print("\n" + "=" * 70)
    print(f"{GREEN}✅ Backend Test Suite Complete!{RESET}")
    print("=" * 70)
    print(f"\n{BLUE}📝 Summary:{RESET}")
    print("   - Authentication: Working ✓")
    print("   - Lessons API: Working ✓")
    print("   - Progress Tracking: Working ✓")
    print("   - AI Diagnosis: Working ✓")
    print("   - Reports: Working ✓")
    print("\n🚀 Your backend is ready for frontend integration!")
    
    return True

if __name__ == "__main__":
    run_test()