import requests

BASE_URL = "http://127.0.0.1:8000/api/v1/"

print("=" * 50)
print("MasteryAI Quick Test")
print("=" * 50)

# Test 1: Check if server is running
try:
    response = requests.get(f"{BASE_URL}")
    print(f"✓ Server is running (Status: {response.status_code})")
except:
    print("✗ Server is not running. Start with: python manage.py runserver")
    exit()

# Test 2: Test login
print("\nTesting login...")
response = requests.post(f"{BASE_URL}token/", json={
    "username": "student_basic",
    "password": "testpass123"
})

if response.status_code == 200:
    token = response.json()['access']
    headers = {"Authorization": f"Bearer {token}"}
    print("✓ Login successful")
    
    # Test 3: Get lessons
    print("\nFetching lessons...")
    response = requests.get(f"{BASE_URL}lessons/", headers=headers)
    if response.status_code == 200:
        data = response.json()
        lessons = data.get('results', data)
        print(f"✓ Found {len(lessons)} lessons")
    else:
        print(f"✗ Failed: {response.status_code}")
else:
    print("✗ Login failed - Run refresh_db.py first")

print("\n" + "=" * 50)
print("To load sample data, run: python refresh_db.py")
print("=" * 50)