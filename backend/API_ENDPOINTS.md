# MasteryAI Backend API Endpoints

Base URL: `http://localhost:8000/api/v1/`

## Authentication
- POST `/auth/token/` - Login
- POST `/auth/token/refresh/` - Refresh token
- POST `/auth/register/` - Register new user
- POST `/auth/change-password/` - Change password

## Users
- GET `/users/profile/` - Get user profile
- PUT `/users/profile/` - Update profile
- GET `/users/dashboard/` - User dashboard

## Lessons
- GET `/lessons/` - List lessons (filtered by tier)
- GET `/lessons/{id}/` - Get lesson details
- POST `/lessons/{id}/start_lesson/` - Start lesson
- POST `/lessons/{id}/submit_practice/` - Submit practice
- POST `/lessons/{id}/submit_test/` - Submit test

## Progress
- GET `/progress/summary/` - Progress summary
- GET `/tier-progress/` - Tier progress

## Reports
- GET `/mastery-report/` - Mastery report
- GET `/export-report/?format=pdf` - Export report

## AI
- POST `/diagnose-tier/` - Tier diagnosis

## Test Credentials
- student_basic / testpass123 (BASIC tier)
- student_intermediate / testpass123 (INTERMEDIATE tier)
- student_advanced / testpass123 (ADVANCED tier)
- student_css / testpass123 (PROFESSIONAL tier)