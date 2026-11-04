# TeachMeWrite: Project Transition Prompt
**Last Updated:** Day 103 (Completed)
**Context:** This file serves as the single source of truth for the project's intent, architecture, and current state.

## 1. The Original Intent
A Mastery-Based Learning Management System (LMS) for the Pakistani education system. It handles Theory, Practice, and Assessment across 4 Tiers (Basic/Matric, Intermediate/FSc, Advanced/Bachelors, Professional/CSS). It supports multiple roles (Students, Teachers, Parents, Institute Admins).

## 2. The 3-Tier Architecture
1. **Backend (`backend/`):** Django + PostgreSQL. Handles Auth (JWT), User Roles, Curriculum Theory, and Progress Tracking.
2. **Frontend (`frontend/`):** React + Vite + Tailwind CSS. Handles the UI (UnitBrowser, PracticeView, Dashboards).
3. **AI Microservice (`ai-service/`):** FastAPI on GCP Cloud Run. Handles the AI Writing Feedback. 
   - *Rule:* FastAPI does NOT talk to PostgreSQL directly. It receives the JWT, validates it, calls Claude AI with RAG context, and sends a BackgroundTask POST request to Django to save the progress.

## 3. Current State (As of Day 103)
- **FastAPI:** Secure (JWT + API Key fallback), RAG-enabled (ChromaDB), and saving progress via BackgroundTasks. Live on Cloud Run.
- **React:** Fully intact. Contains `AuthContext`, `PracticeView`, and routing. We are *adding* a `WritingStudio` component without breaking existing routes.
- **CI/CD:** GitHub Actions with LLM-as-a-Judge evaluation gate.

## 4. Next Steps (Day 104)
- Finish integrating the Navbar link for the Writing Studio.
- Run the React app locally in Colab (`npm run dev`) to visually verify the new UI.
- Test end-to-end flow (Login -> Writing Studio -> AI Feedback).

## 5. Working Ethics
- Tiny steps, one purpose per cell.
- Wait for output. Ask A/B before architectural decisions.
- Fix in-cell. Honest over impressive.
- Notebook hygiene (idempotent Cell 1a, asserts).
- Security discipline (no hardcoded secrets).
- Book Protocol: Write `book/day_XXX.md` daily.
