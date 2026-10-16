# TeachMeWrite

**A mastery-based English writing tutor for Pakistani students — from simple sentences to CSS-level professional writing.**

[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)](https://react.dev/)
[![DRF](https://img.shields.io/badge/DRF-3.18-A30000?logo=django)](https://www.django-rest-framework.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 The Problem

English writing is the single biggest barrier for Pakistani students competing for:

- **CSS/PMS** — Pakistan's highest civil service exams
- **IELTS/TOEFL** — international study and work
- **Academic writing** — university-level essays and theses
- **Professional communication** — business English

Existing tools (Grammarly, ChatGPT) provide **corrections** but no **structured curriculum**. Students can't tell if they've mastered a skill before moving on — so they plateau.

Coaching centers cost **Rs 100,000+ per year** and don't scale. There is no affordable, structured, digital alternative for writing mastery in Pakistan.

---

## 💡 The Solution

TeachMeWrite is a **mastery-based learning platform** with a progressive curriculum. Students cannot advance until they demonstrate competency at each level.

| Level | Skill | Mastery Gate |
|-------|-------|--------------|
| 1 | Simple sentences | Grammar + SVO structure |
| 2 | Compound sentences | Conjunctions + clause boundaries |
| 3 | Complex sentences | Subordination + coherence |
| 4 | Paragraphs | Topic sentences + unity |
| 5 | Essays | Argumentation + evidence |
| 6 | Stories | Narrative arc + voice |
| 7 | Professional (CSS-level) | Examiner-standard rubrics |

Each level has:
- **Teaching content** — concepts explained with examples
- **Practice mode** — adaptive exercises targeting weak concepts
- **Mastery test** — unlocks the next level only on passing
- **Progress tracking** — persistent, per-student

---

## 🏗️ Architecture
┌─────────────────────────────────────────┐
│ Frontend (React + Vite) │
│ • components / hooks / contexts │
│ • services/ for centralized API calls │
│ • JWT auth via localStorage │
└──────────────────┬──────────────────────┘
│ REST API
▼
┌─────────────────────────────────────────┐
│ Backend (Django + DRF) │
│ • JWT authentication │
│ • Mastery engine (progression gates) │
│ • Progress tracking │
│ • Lesson content delivery │
│ • PDF report generation (ReportLab) │
└─────────────────────────────────────────┘

---

## 🛠️ Tech Stack

**Backend:**
- Django 5.2 + Django REST Framework 3.18
- JWT authentication (djangorestframework-simplejwt)
- SQLite (dev) / PostgreSQL-ready (prod)
- ReportLab for PDF reports
- Pandas for progress analytics

**Frontend:**
- React 18 + Vite
- React Router
- Context API for state management
- Axios for HTTP + JWT interceptors

**Deployment Ready:**
- Gunicorn WSGI server
- WhiteNoise for static files
- dj-database-url for production database config

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### Backend

```bash
git clone https://github.com/edmedpublic-hub/teachmewrite.git
cd teachmewrite/backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your values

# Run migrations
python manage.py migrate

# Seed initial curriculum
python seed_learning_data.py

# Start server
python manage.py runserver

Backend runs at http://localhost:8000

Frontend
cd teachmewrite/frontend
npm install
npm run dev

Frontend runs at http://localhost:5173

TeachMeWrite/
├── backend/                      # Django backend
│   ├── api/                      # REST API app
│   │   ├── migrations/
│   │   └── views/                # ViewSets, split by domain
│   ├── lessons/                  # Curriculum + mastery engine
│   │   ├── migrations/
│   │   └── management/
│   │       └── commands/         # Custom Django commands
│   ├── writing_mastery_project/  # Project settings
│   ├── requirements.txt
│   ├── .env.example
│   └── manage.py
├── frontend/                     # React frontend
│   └── src/
│       ├── components/           # Reusable UI
│       ├── contexts/             # Global state (auth, etc.)
│       ├── hooks/                # Custom hooks
│       ├── services/             # API client
│       └── utils/                # Helpers
├── data/                         # Curriculum content (JSON)
├── .gitignore
├── LICENSE
└── README.md

📖 API Documentation
See backend/API_ENDPOINTS.md for the current API surface.

🗺️ Roadmap
Completed:

☑ 7-level curriculum structure
☑ Mastery gate engine
☑ User authentication + registration
☑ Progress tracking with weak-concept identification
☑ Practice and mastery-test modes
☑ PDF report generation
In Progress:

□ AI-powered feedback for Levels 4-7 (paragraphs → essays → CSS)
□ Deployment to Railway
Future:

□ Multi-instructor support
□ Peer review integration
□ Mobile app
🤝 Contributing
This is currently a solo project. If you're interested in collaboration, reach out via the contact below.

📄 License
This project is licensed under the MIT License — see the LICENSE file for details.

👤 Author
Muhammad Afzal

GitHub: @edmedpublic-hub

Project: Building AI-powered learning tools for Pakistani students

Live produ

🙏 Acknowledgments
Built to solve a real problem — English writing mastery is a barrier for millions of Pakistani students. This project is a step toward making high-quality writing education accessible, measurable, and affordable.