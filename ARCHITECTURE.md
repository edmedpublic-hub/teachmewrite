# TeachMeWrite -- System Architecture Map

**Last updated:** Day 109 (2026-11-16)
**Scope:** Current state of the running system. What exists, how it connects,
what is wired vs. built-not-wired.

This file is the deep reference. For the front door, see `README.md`. For
session bootstrap, see `TRANSITION_PROMPT.md`. For narrative state with
debugging context, see `book/day_NNN.md`.

---

## 1. What Exists

### 1.1 Backend (Django 5.2 + DRF)

**Role:** Auth, curriculum, progress, user roles, tier state, certificate
issuance. Source of truth for anything that is not AI-generated.

**Apps:**

| App | Models | Purpose |
|-----|--------|---------|
| `lessons` | 18 models | Curriculum (Lesson, Unit, LessonUnit, QuestionBank), progress (StudentProgress, StudentLessonProgress, TierProgress), tier state, students, schools, assignments, certificates, WritingFeedback |
| `api` | (views only) | All REST endpoints; views organized by concern (9 modules) |
| `auth` (Django built-in) | User, Group | Foundation user model (username, email, password, is_active) |

**Key models** (in `backend/lessons/models.py`):

- `Profile` -- one-to-one with User. Learning preferences, XP, streak, average score, `target_tier` (aspirational).
- `UserProfile` -- one-to-one with User. Role (STUDENT/TEACHER/PARENT/INSTITUTE_ADMIN/SUPER_ADMIN), institute membership, teacher metadata, parent-student links.
- `TierProgress` -- one-to-one-per-user-per-tier. `is_unlocked` gatekeeper, `is_completed` graduation signal, `mastery_percentage` property. **The changeable-tier model** (Day 106 finding, closed).
- `Lesson` -- curriculum unit with tier, order, prerequisite, mastery requirements.
- `StudentProgress` -- per-lesson mastery for the legacy adaptive flow.
- `StudentLessonProgress` -- per-lesson-unit mastery for the newer adaptive flow.
- `WritingFeedback` (Day 107) -- persisted AI feedback from `/studio`. Unique on `session_id` (idempotency). Stores `tier_at_submission` (futuristic artifact).
- `Certificate`, `Announcement`, `Assignment`, `AssignmentSubmission`, `Institute`, `Class` -- multi-tenant features (partly wired, partly built-not-wired).

**URL structure:**

| Path | Purpose |
|------|---------|
| `/admin/` | Django admin (superuser only) |
| `/api/auth/token/` | JWT obtain (username + password) |
| `/api/auth/token/refresh/` | JWT refresh |
| `/api/v1/` | Main API (router registered viewsets + function views) |
| `/api/v1/users/me/` | Current user + `current_tier` + `tier_progress` (Day 106) |
| `/api/v1/writing/feedback-callback/` | FastAPI background-task target (Day 107) |
| `/api/v1/auth/register/`, `/auth/change-password/` | Account management |
| `/api/v1/adaptive/*` | Adaptive learning endpoints |
| `/api/v1/diagnose-tier/` | Tier recommendation from writing sample |
| `/api/v1/mastery-report/`, `/api/v1/export-report/` | Reporting |

**Settings essentials** (`backend/writing_mastery_project/settings.py`):

- DB: SQLite at `backend/db.sqlite3` (Postgres migration is Phase 3 work)
- Auth: `rest_framework_simplejwt` (access 60min, refresh 7d, rotate + blacklist)
- CORS: allow localhost:5173, 127.0.0.1:5173, localhost:3000
- Timezone: Asia/Karachi
- `SECRET_KEY`: defaults to `django-insecure-dev-only-change-in-production` (Secret Manager migration Phase 3)
- `GEMINI_API_KEY`: placeholder (unused today; AI feedback is Claude via FastAPI)

**Known backend quirks:**

- `db.sqlite3` is gitignored but a 0-byte placeholder was committed. Migrations must run on every fresh session (Cell 6 of resume).
- `seed_learning_data.py` had a `models` import bug until Day 105 (`090622c`).
- `updateProfile` frontend call is mocked; real `/users/profile/` exists but is not called (Day 106 finding).

---

### 1.2 Frontend (React 19 + Vite + Tailwind)

**Role:** All user-facing UI. SPA under `/teach-me-write/`.

**Components** (`frontend/src/components/`, 20 total):

- **Auth:** `Login`, `Register`
- **Learning:** `LandingPage`, `Dashboard`, `UnitBrowser`, `LessonList`, `LessonDetail`, `LessonTeachingView`, `PracticeView`, `TestView`, `WritingPad`
- **AI:** `WritingStudio` (the /studio page, Day 105), `MyEssays` (the /essays page, Day 109)
- **Progress:** `MasteryReport`, `ProgressCircle`, `Certificates`, `CertificateVerify`
- **Account:** `Profile`, `TeacherDashboard`
- **Shared:** `Navbar`

**Routes** (`frontend/src/App.jsx`):

| Path | Component | Auth required |
|------|-----------|---------------|
| `/` | LandingPage | No |
| `/login`, `/register` | Login, Register | No (redirect if logged in) |
| `/dashboard` | Dashboard | Yes |
| `/essays` | MyEssays | Yes (Day 109) |
| `/learn` | UnitBrowser | Yes |
| `/learn/lesson/:id` | LessonTeachingView | Yes |
| `/practice/:id` | PracticeView | Yes |
| `/test/:id` | TestView | Yes |
| `/studio` | WritingStudio | Yes (Day 105) |
| `/profile` | Profile | Yes |
| `/certificates` | Certificates | Yes |
| `/teacher` | TeacherDashboard | Yes (role check partial) |

**Services:**

- `frontend/src/services/api.js` -- axios, baseURL `/teach-me-write/api`. Attaches JWT from localStorage; 401 interceptor refreshes on expiry.
- `frontend/src/services/aiService.js` -- fetch to `https://teachmewrite-ai-195673983724.asia-south1.run.app`. Passes user's JWT as `Authorization: Bearer <jwt>`. Calls `POST /feedback`.

**State:**

- `AuthContext.jsx` -- user object, `login()`, `logout()`, `updateProfile()` (mocked). On mount: optimistic cache render from localStorage, then `_fetchCurrentUser()` (Day 106 fix). `isAuthenticated` reads localStorage token presence.

**Config** (`vite.config.js`):

- `base: "/teach-me-write/"` (all URLs must include this prefix)
- `server.proxy` and `preview.proxy`: forwards `/teach-me-write/api` -> `http://127.0.0.1:8000`, strips prefix
- `preview.allowedHosts: [".trycloudflare.com"]` (Day 105 fix `2df70b2`)

**Known frontend quirks:**

- `updateProfile` is a mock (Day 106 finding).
- `localStorage.getItem('user_tier')` was hardcoded to `'BASIC'` before Day 106 -- now fetched from `/me/`.
- Navbar reads `user?.tier` -- `AuthContext` now populates it from `current_tier`.

---

### 1.3 AI-service (FastAPI + Anthropic Claude)

**Role:** The AI feedback pillar. Stateless HTTP service on Cloud Run.
Calls Claude Haiku. Posts feedback back to Django via BackgroundTasks.

**Endpoints:**

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/feedback` | JWT Bearer OR X-API-Key | Generate feedback; fire BackgroundTask |
| GET | `/health` | None | Liveness |
| GET | `/metrics` | Basic auth (METRICS_USER/METRICS_PASS) | Prometheus metrics |

**Middleware stack** (in order):

1. `CORSMiddleware` -- allow origins from `CORS_ALLOWED_ORIGINS` env (default localhost:5173) + `CORS_ORIGIN_REGEX` (default `https://[a-z0-9-]+\.(loca\.lt|trycloudflare\.com)`)
2. `request_context` -- attaches `X-Request-ID` (uuid4.hex), `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`. Rejects payloads > 20000 bytes with 413.

**Auth** (`authenticate_user`): tries JWT bearer first (verifies with `JWT_SECRET_KEY`, must match Django's `SECRET_KEY`), falls back to X-API-Key. Both must be present in env or the service refuses to start.

**Rate limiting:**

- `RATE_LIMIT_PER_MIN` (default 10; Cloud Run sets 200)
- `DAILY_CALL_CEILING` (default 500)
- `DAILY_TOKEN_CEILING` (default 400,000)

**Background task** (`save_progress_task`, Day 107 rewire):

- Sends `X-Internal-Key` header (from `INTERNAL_API_KEY` env)
- Posts `{user_id, session_id, student_text, level, feedback}` to `DJANGO_API_URL`
- **Fail-closed:** refuses to POST if `INTERNAL_API_KEY` unset
- Idempotent: Django uses `get_or_create(session_id=...)` where `session_id` = request's `X-Request-ID`

**Model:** `claude-haiku-4-5-20251001`, max_tokens 1024.

**Prompt** (in `get_feedback`): level-aware instructions (1-7), evidence-based issue detection, toxic-content + PII firewall post-processing, "praise correct writing" rule.

**Known AI-service quirks:**

- `BackgroundTasks` imported twice (cosmetic, line 29 of main.py).
- `fastapi.log` opened in write mode `"w"` in Cell 7 -- loses prior session's log across restarts.
- `DJANGO_API_URL` default is `http://127.0.0.1:1/disabled` (fail-closed by design); Cloud Run currently uses this default until Day 109.

---

### 1.4 CI/CD (GitHub Actions)

**Workflow:** `.github/workflows/deploy.yml`

**Trigger:** `on.push.branches: [main]` + `paths: ['ai-service/**', '.github/workflows/**']` (paths fix Day 108 `0c5305b`). Plus `workflow_dispatch` for manual runs.

**Pipeline:**

1. Checkout
2. Authenticate to GCP via WIF (keyless) -- SA `github-deployer@teachmewrite-prod.iam.gserviceaccount.com`
3. Login to Artifact Registry
4. Build Docker image, push to `asia-south1-docker.pkg.dev/teachmewrite-prod/teachmewrite-ai/teachmewrite-ai:<sha>`
5. Deploy to Cloud Run staging tag (`--no-traffic --tag staging`)
6. Wait for staging health (curl /health, up to 150s)
7. Golden-set gate: `run_gate.py` with 3 runs, 2-of-3 threshold, LLM judge, min-helpfulness 3
8. Promote staging to 100% traffic (only if gate passed)
9. Upload gate_result.json artifact

**Secrets on Cloud Run** (via `--set-secrets`):
- `ANTHROPIC_API_KEY` = `anthropic-api-key:latest`
- `INTERNAL_API_KEY` = `internal-api-key:latest` (committed `9a3a320`, **deploy FAILED -- secret does not exist in Secret Manager as of Day 108 close**)

**Env vars** (via `--set-env-vars`, line 59):
- `METRICS_USER`, `METRICS_PASS`, `TMW_API_KEYS`, `TMW_RATE_LIMIT_PER_MIN=200`
- `JWT_SECRET_KEY=django-insecure-dev-only-change-in-production` (must match Django's SECRET_KEY)
- `DJANGO_API_URL=http://127.0.0.1:1/disabled` (fail-closed; Day 109 changes to Django tunnel URL)

**Known CI/CD quirks:**

- Paths filter originally `['ai-service/**']` -- workflow could not validate its own definition changes. Fixed Day 108 `0c5305b`.
- Per-secret IAM binding required for each new secret (`roles/secretmanager.secretAccessor` on the SA `195673983724-compute@developer.gserviceaccount.com`). Not automatic -- Day 108 finding.
- Hardcoded `TMW_API_KEYS` and `METRICS_PASS` in plaintext `deploy.yml` line 59 -- flagged Day 105, still open (Phase 3 Secret Manager migration).
- Node.js 20 deprecation warning in GitHub Actions (upstream, not our code).

---

## 2. How It Connects

### 2.1 The Three-Pillar Flow (Student submits essay)

A real user action -- student at `/studio` types an essay and clicks
"Get Feedback" -- traverses every layer. This is the reference flow.
[Browser]
|
| 1. GET https://<trycloudflare>.trycloudflare.com/teach-me-write/studio
v
[cloudflared tunnel]
|
v
[vite preview :5173] -- static dist/ served, /api/* proxied
|
| 2. Request arrives at WritingStudio.jsx (already logged in)
| JWT from localStorage sent to FastAPI
v
[Cloud Run: teachmewrite-ai]
|
| 3. POST /feedback {student_text, level}
| Header: Authorization: Bearer <jwt>
| CORS preflight passes (regex matches *.trycloudflare.com)
v
[FastAPI main.py]
|
| 4. authenticate_user() decodes JWT with JWT_SECRET_KEY
| (must match Django's SECRET_KEY -- configured via deploy.yml line 59)
| Rate limit check (200/min on Cloud Run)
v
[Claude Haiku API]
|
| 5. Prompt includes level (1-7), student_text
| Response: JSON with overall_score, issues[], rewrite_suggestion,
| level_appropriate
v
[FastAPI main.py -- continues]
|
| 6. PII / toxicity filter applied to Claude's output
| 7. BackgroundTask queued: save_progress_task(user_id, session_id, ...)
| 8. HTTP 200 returned to browser with feedback JSON
| Response header: X-Request-ID = <32-hex>
v
[Browser]
|
| 9. WritingStudio renders feedback (score, issues, suggestion)

[BackgroundTask fires, concurrent with user viewing feedback]
|
| 10. save_progress_task POSTs to DJANGO_API_URL
| Header: X-Internal-Key: <secret>
| Body: {user_id, session_id, student_text, level, feedback}
v
[Django callback /api/v1/writing/feedback-callback/]
|
| 11. _check_internal_key() verifies X-Internal-Key matches INTERNAL_API_KEY
| If unset: 401 Service not configured (fail-closed)
| If mismatch: 401 Invalid internal key
| 12. Look up User by user_id; if not found: 404
| 13. TierProgress.current_tier_for(user).value -> tier_at_submission
| 14. WritingFeedback.get_or_create(session_id=..., defaults={...})
| If exists: return existing (idempotent, 200 created: false)
| If new: return 201 created: true
v
[DB: lessons_writingfeedback row]

text

**Current production reachability (Day 108 close):**

| Step | Status | Notes |
|------|--------|-------|
| 1-2. Landing + studio | WORKS | Day 105, Day 106 |
| 3. Browser -> Cloud Run | WORKS | CORS regex allows trycloudflare |
| 4. JWT decode on FastAPI | WORKS | `JWT_SECRET_KEY` synced with Django's SECRET_KEY |
| 5. Claude call | WORKS | Haiku; ~3-8s per request |
| 9. Render feedback | WORKS | Verified Day 105, Day 106, Day 107 |
| 10. Background POST to Django | **DOES NOT WORK IN PRODUCTION** | `DJANGO_API_URL=http://127.0.0.1:1/disabled` (fail-closed by design) |
| 10a. `X-Internal-Key` header | **NOT YET SET IN PRODUCTION** | `internal-api-key` secret does not exist in Secret Manager; deploy `0c5305b` failed at step 07 |
| 11-14. Django callback | **PROVEN LOCALLY ONLY** (Day 107) | 5/5 tests pass; not reachable from Cloud Run |

**What "persistence proven" means precisely:** the Django side works
end-to-end (5-test suite passed Day 107, cells 6b-3). The FastAPI side
works (background task fires, correct payload). What is missing is
network reachability from Cloud Run to Colab's ephemeral Django. Two
paths to fix:
- **A. Point Cloud Run at a Django tunnel URL** (Day 109 work). Per-session
  redeploy cost: ~6 min each time. Not sustainable, but unblocks E2E demo.
- **B. Deploy Django to its own Cloud Run service** (Phase 3). Sustainable.
  Requires Dockerfile, migrations at startup, settings for prod, Postgres.

**Day 109 opens with path A** (fastest to a working demo). Path B is
Day 110+.

### 2.2 Auth flow (independent of /studio)
[Login page] -> POST /teach-me-write/api/auth/token/
(Vite proxy forwards to Django :8000, strips /teach-me-write prefix)
-> simplejwt returns {access, refresh}
-> localStorage.setItem('access_token', ...)
-> AuthContext.login() -> _fetchCurrentUser() -> /api/v1/users/me/
-> /me/ computes current_tier via TierProgress.current_tier_for()
-> AuthContext._cacheUser() stores username + current_tier
-> Navbar reads user?.tier -> shows actual unlocked tier

text

### 2.3 Data flow vs. real-time

There is no WebSocket, no push, no streaming. All interaction is
request/response. The only "async" is the BackgroundTask from FastAPI
to Django, which fires within 1-2 seconds of the HTTP response to the
user. Even that is best-effort: if the POST fails, nothing retries.

**Phase 3 consideration:** if reliability matters, background task
should use a queue (Cloud Tasks or Pub/Sub), not in-process
BackgroundTasks. Not today's concern -- the current design fails closed,
which is honest.

---

## 3. What Is Not Wired

This section is the roadmap. Everything below is genuinely not yet
connected, not "mostly done."

### 3.1 Production persistence

- **Blocker:** `internal-api-key` not created in Secret Manager.
- **Fix (Day 109):** 3 Cloud Shell commands (create secret, add version
  from key, add IAM binding to SA `195673983724-compute@developer.gserviceaccount.com`).
- **Then:** rerun the failed deploy (`rerun-failed-jobs` on run
  `43727450414`).

### 3.2 Cloud Run -> Django reachability

- **Blocker:** `DJANGO_API_URL=http://127.0.0.1:1/disabled` on Cloud Run.
  Loopback fails immediately (by design; Day 105 httpbin fix).
- **Fix (Day 109):** `DJANGO_API_URL` -> stable cloudflared tunnel URL
  pointing at Colab's `:8000`. Requires per-session redeploy (Day 109's
  per-session cost). Long-term fix is Django on Cloud Run (Phase 3).

### 3.3 "My Essays" UI

- **Status:** SHIPPED Day 109 (commit pending Cell 24).
- **Backend:** `GET /api/v1/writing/essays/` (paginated, page_size capped
  at 100). Server-side tenant isolation via `filter(user=request.user)`.
  5 sub-tests PASS (owner sees rows, other user sees zero, anon 401,
  pagination works, page_size cap).
- **Frontend:** `/essays` route (`MyEssays.jsx`, 204 lines), Navbar link.
  Bundle-hash-as-proof: `Sq88cd-i` -> `B8X35t0d` (component) ->
  `Cwqx2DdT` (Navbar).
- **Browser E2E:** `student_css` sees 3 cards (91/82/75, newest first),
  expands one to show issues + rewrite.

### 3.4 Tier auto-unlock on completion

- **Blocker:** `TierProgress.update_progress()` sets `is_completed=True`
  but never flips `is_unlocked` on the next tier.
- **Consequence:** a student who masters all BASIC lessons stays locked
  out of INTERMEDIATE. The futuristic lens (tier evolves) fails at the
  exact moment it matters.
- **Fix:** ~15 lines in `models.py` + a test. Small; scheduled Day 109
  if time, Day 110 otherwise.

### 3.5 Tier-aware AI feedback

- **Current:** `FeedbackRequest` has `student_text` + `level` (1-7). No
  `tier`. A CSS aspirant gets the same level-5 prompt as a Matric student.
- **Designed (Day 106):** add `tier` field; `WritingFeedback.tier_at_submission`
  already captures it.
- **Fix (Phase 3):** prompt reads `tier` to calibrate expectations.
  Requires a `/feedback` schema change + redeploy + quality re-test.

### 3.6 `updateProfile` frontend

- **Current:** `AuthContext.updateProfile()` is a mock, no backend call.
- **Backend ready:** `GET/PUT /api/v1/users/profile/` exists.
- **Fix (Phase 3):** wire the frontend call. Not urgent.

### 3.7 Postgres migration

- **Current:** SQLite at `backend/db.sqlite3`. Fine for local dev, wrong
  for production.
- **Fix (Phase 3, coupled to Django-on-Cloud-Run):** settings.py DB
  switch, data migration script, CI tests against Postgres.

### 3.8 Secret Manager migration (complete)

- **Current:** `JWT_SECRET_KEY`, `TMW_API_KEYS`, `METRICS_PASS` in
  plaintext `deploy.yml` line 59. Ethics rule #8 is not satisfied.
- **Flagged:** Day 105, Day 106, Day 107, Day 108.
- **Fix (Phase 3):** Secret Manager for all three; `deploy.yml` uses
  `--set-secrets` for all. ~30 minutes plus a deploy.
- **Note:** `INTERNAL_API_KEY` is already on `--set-secrets` (Day 108
  `9a3a320`); the three above are not.

### 3.9 Teacher Dashboard, Mastery Report, Certificates

- **Current:** built but not wired to the new API structure. Components
  exist; some call legacy endpoints.
- **Fix (Phase 2 remainder):** audit each dashboard, point at
  `/api/v1/*`, verify with sample data.

### 3.10 Adaptive Learning Flow (practice + test)

- **Current:** backend endpoints exist (`/adaptive/*`). Frontend
  `PracticeView`, `TestView` exist. Not E2E-tested.
- **Fix (Phase 2):** E2E test the practice -> test -> mastery flow like
  we did for `/studio`.

---

## Verification state (day-by-day)

| Day | What proved | Where |
|-----|-------------|-------|
| 105 | E2E browser flow: Django login -> /studio -> Cloud Run -> feedback rendered | `book/day_105.md` section 1 |
| 106 | Tier linkage: /me/ returns current_tier; Navbar shows actual tier | `book/day_106.md` section 1 |
| 107 | Pillar 3 E2E local: /feedback -> BackgroundTask -> Django row | `book/day_107.md` section 1 |
| 108 | Deploy pipeline: built image, diagnosed IAM. Not yet completed. | `book/day_108.md` section 1 |

**The pattern:** each day proves one layer more than the last. Day 105's
"E2E" was Pillars 1+2. Day 107's "E2E" was Pillars 1+2+3, locally. Day
109's target: Pillars 1+2+3 in production.

---

*End of ARCHITECTURE.md*
