# TeachMeWrite -- Session Transition Prompt

**Last updated:** Day 111 close (2026-11-23)
**Read this first.** Then open `ARCHITECTURE.md` for depth and the latest
`book/day_NNN.md` for narrative state. `README.md` is the front door.

---

## Identity

TeachMeWrite is a Mastery-Based Learning Management System for Pakistani
students (Matric through CSS/Competitive exams). Built by Muhammad Afzal,
AI/ML engineer with 25+ years of English teaching. Day 110 of a 160-day
engineering capstone: build a competitive AI product, document daily,
prepare for an AI Engineering role.

Three-pillar architecture: Theory, Practice, AI Feedback. Four tiers
(Basic/Intermediate/Advanced/Professional). Multi-tenant (Student/Teacher/
Parent/Institute Admin).

Three services:
- **Backend:** Django 5.2 + DRF, SQLite (local only), port 8000
- **Frontend:** React 19 + Vite + Tailwind, port 5173, base `/teach-me-write/`
- **AI-service:** FastAPI on GCP Cloud Run `asia-south1`, calls Claude Haiku

### Runtime topology

Two tunnels expose the local services for the day's work. One is named
and stable (Django); the other is still a quick tunnel (Vite).

- **Named** tunnel `teachmewrite-django` (UUID `4cdfe145-b46f-4a87-ba1a-
  52105e5d6fbc`) -> :8000 (Django backend). Stable hostname
  `api.teachmewrite.com` via proxied CNAME -> `4cdfe145-...cfargotunnel.com`.
  `DJANGO_API_URL` in `deploy.yml` points at `https://api.teachmewrite.com/
  api/v1/writing/feedback-callback/` (Day 111, commit `83e25e0`).
  Credentials on Drive at `.secrets/cloudflared/`. Does not rotate across
  sessions.
- **Quick** Vite tunnel -> :5173 (serves built frontend via vite preview).
  Browser entry. Still ephemeral; a new URL each session. Not yet named.


---

## Current state (Day 111 close)

- **Pillar 1 (Auth):** WORKING. Django JWT; Navbar shows actual unlocked tier.
- **Pillar 2 (AI Feedback):** WORKING. /studio -> Cloud Run -> Claude -> render.
- **Pillar 3 (Persistence):** WORKING END-TO-END IN PRODUCTION (Day 110).
  - Browser submit -> Cloud Run -> Claude -> BackgroundTask
  - -> public Django tunnel -> callback auth -> WritingFeedback row
  - -> row appears in /essays for the submitting user
  - Browser-verified 2026-11-17: score 42, tier PROFESSIONAL, visible
    - **Day 111: Django tunnel is named and stable.** `api.teachmewrite.com`.
    Per-session `deploy.yml` edit retired. Commit `83e25e0`.
- **"My Essays" UI:** SHIPPED Day 109. /essays route, Navbar link, paginated.
- **Live Cloud Run:** `ad575f3` (Day 110). Deploy of `83e25e0` failed
  golden-set gate 0/20 HTTP 502 (origin not running at gate time).
  Day 112 action: restart origin, confirm Cell 6 401/401, `workflow_dispatch`.
- **GitHub main:** HEAD = Day 110 close commit (run `git log --oneline -1`)
- **Book chapters:** `book/day_100.md` .. `book/day_111.md` (latest)

**Resume gotchas (Days 110-111 findings):**

1. Gitignored `backend/.env` does not arrive in a fresh clone. Before any
   cell tests a reachable callback, write `.env` from the Drive backup:

    /content/drive/MyDrive/teachmewrite-ai/.secrets/internal_api_key

and set `ALLOWED_HOSTS=localhost,127.0.0.1,.trycloudflare.com,
api.teachmewrite.com` + `INTERNAL_API_KEY=<value>`.

2. **Colab Secrets are not `os.environ`.** Use `google.colab.userdata.get`
   and export to `os.environ` in a shim cell before any subprocess that
   expects the variable. `book/day_111.md` section 4, Entry 1.

3. **Pre-push probe.** Before any push that triggers `deploy.yml`,
   `api.teachmewrite.com` must answer 401 on `/api/v1/users/me/` and 401
   on `/api/v1/writing/feedback-callback/` (no `X-Internal-Key`). The
   golden-set gate calls ai-service synchronously and fails closed when
   the origin is down. `book/day_111.md` section 4, Entry 3.

---

## Day 112 opening task (60-90 minutes)

**Primary: deploy `83e25e0` green, then browser E2E on the stable host.**
The URL change landed 2026-11-22 (commit `83e25e0`); the deploy failed
golden-set gate 0/20 with HTTP 502 because the Colab origin was not running
at gate time. Fix is origin restart + `workflow_dispatch`, not a code
change. See `book/day_111.md` section 4, Entry 3.

1. **Restart origin.** Cells 2.5 through 4.8 of the resume pattern
   (Colab Secrets shim, clone, `.env`, pip, migrate, runserver).
2. **Bring up the named tunnel.** Cell 5. Expect three
   `Registered tunnel connection` lines.
3. **Pre-push probe.** Cell 6. Two specific 401s at
   `https://api.teachmewrite.com`. `User-Agent` header required
   (`book/day_111.md` section 4, Entry 2).
4. **`workflow_dispatch` `83e25e0`.** Watch the Actions run reach green.
5. **Browser E2E.** Vite preview + Vite tunnel, log in as `student_css`,
   submit an essay at `/studio`, verify the row appears in `/essays`,
   confirm in devtools that the callback URL is `api.teachmewrite.com`,
   not `*.trycloudflare.com`.

**Then (same day or next):**

1. Extract `RULES.md` as the sole home of working conventions; reduce
   `TRANSITION_PROMPT.md` and `README.md` to one-line pointers.
   Commit as a separate change (convention 13).
2. `TierProgress.update_progress()` auto-unlock on tier completion
   (Day 106 finding 1; 15 lines + a test).
3. `fastapi.log` append mode (Day 107 defect; one-line fix).
4. Capture browser E2E screenshot to Drive.
5. Begin Phase 2 UI polish (Days 112-114 scope).


---

## Resume pattern (fresh Colab session)

Open today's notebook from Drive (`day_108.ipynb`), then run Cells 1-14
of Day 108's plan. Each cell is one concern.

| Cell | Purpose |
|------|---------|
| 1 | Environment sanity (Python 3.13, Node 22, GITHUB_TOKEN, ANTHROPIC_API_KEY) |
| 2 | Drive mount with stale-state cleanup |
| 3 | Clone repo, verify required commits in ancestry + content markers |
| 4 | pip install backend + ai-service |
| 5 | Django up on :8000 (`--noreload`) |
| 6 | migrate |
| 7a | seed learning data |
| 7b | create 4 demo users |
| 7c | apply tier policy |
| 8 | npm install frontend |
| 9 | npm build (dist/) |
| 10 | vite preview :5173 |
| 11 | cloudflared tunnel + DNS backoff |
| 12 | verify live Cloud Run allows this trycloudflare host |

Credentials: `student_basic/intermediate/advanced/css`, password
`testpass123` for all four.

---

## Working conventions and prohibitions

All working conventions, the "What not to do" list, the session
bootstrap, and the pre-push probe requirements live in `RULES.md`.
Read `RULES.md` before the first cell of any session. This file does
not duplicate them.

## Roadmap to Day 160

**Outcome by Day 160:** TeachMeWrite ships as a Mastery-Based LMS where:

- A student writes, gets tier-calibrated feedback, sees their own
  progression over time, and receives a next-step recommendation --
  for any of the 4 tiers.
- A teacher sees their students' progression and can assign targeted
  practice.
- A parent sees a read-only view of their child's progress and recent
  submissions.
- The product runs on production infrastructure (Postgres, Secret Manager,
  named URL) with monitoring and incident response.

If we are not there by Day 160, the date moves; the outcome does not.

**Planning discipline:** 160 calendar days, approximately 15 percent
discovery buffer (Days 108 and 110 were each a full day lost to
infrastructure surprises; assume the rate continues). User testing is a
parallel track, not a phase task -- sourcing testers starts Day 111.

### Phase 2 (Days 111-124, 14 days) -- product feels whole for all personas

- 111: sustainable Django URL (named tunnel or Cloud Run)
- 112: progression visibility -- score trend over time on /essays
- 113: tier-aware /feedback -- tier in schema, prompt calibrates by tier
- 114: recommendation engine v1 -- areas to improve from aggregated issues
- 115: update_progress() auto-unlock + permanent resume .env cell
- 116-117: basic UX polish -- loading, error, empty states
- 118-119: parent view v1 + multi-tenant permissions
- 120-121: adaptive Learning E2E (practice to test to mastery)
- 122: multi-tenant isolation tests
- 123-124: real user testing round 1 (5 students) -- iterate on feedback

### Phase 3 (Days 125-138, 14 days) -- deepen, then widen

- 125-126: long-term memory (revive Day 93 student_notes.json)
- 127-128: RAG for curriculum -- feedback grounded in curriculum content
- 129: individual student model -- tracks struggles, pace, examples that click
- 130: prompt quality pass + eval loop for tier-aware feedback
- 131-132: Teacher Dashboard v1
- 133: Urdu STT (essay dictation)
- 134: GCP TTS (feedback read-aloud)
- 135-136: real user testing round 2 (students + teacher + parent)
- 137: iterate on test feedback
- 138: Phase 3 retrospective

### Phase 4 (Days 139-150, 12 days) -- eval at scale + fine-tune properly

- 139-140: synthetic data generation (4 tiers, 5 levels, error classes)
- 141-142: A/B testing framework for prompt variants
- 143-144: Redis caching (feedback dedupe, tier resolution)
- 145-147: QLoRA fine-tune properly (data prep, training, eval, deploy)
- 148: latency + cost analysis
- 149: load test + scale plan
- 150: Phase 4 retrospective

### Phase 5 (Days 151-160, 10 days) -- launch readiness

- 151: Postgres migration
- 152: Secret Manager complete
- 153: privacy policy + terms of service
- 154: support channel + monitoring dashboard
- 155: rollback plan + runbook
- 156-157: dry-run launch (10 users) -- iterate
- 158: book compilation (Days 100-160)
- 159: resume overhaul + mock interviews
- 160: LAUNCH

### Known risks at 160 days

- User testing rounds slip: 123-124 and 135-136 become iteration days.
- QLoRA underperforms on golden set: 145-147 consumed without shipping a model.
- Parent view requires data model changes: UserProfile.linked_students already
  exists, likely sufficient.
- Postgres migration surfaces latent SQLite assumptions: 151 slips into 152-153.
- Discovery days exceed 15 percent buffer: Phase 5 compresses.

### If 160 also slips -- what to cut, in order

1. Urdu STT/TTS (Days 133-134) -- accessibility, not core learning
2. QLoRA fine-tune (145-147) -- cost optimization, not capability
3. Dry-run launch (156-157) -- risky cut, survivable with careful monitoring

**Not cut:** user testing, parent view, individual student model, launch
readiness (privacy, support, rollback). Those four make the product real
versus built.

### How this changes day-level work

Each day is measured against the outcome statement, not against the day's
task. If a day is complete but does not move toward the outcome, that day
is re-scoped. Days 108 and 110 were infrastructure days -- honest, necessary,
but not outcome days. Expect approximately 20 percent of remaining days to
be infrastructure, not feature.

---

## Reference documents

| File | When to open |
|------|--------------|
| `README.md` | First time on the project; what it is, quick start |
| `ARCHITECTURE.md` | Deep system map: every module, endpoint, model, gap |
| `book/day_NNN.md` | Latest state with debugging context -- most current |
| `backend/API_ENDPOINTS.md` | API reference |
| `ai-service/docs/runbook.md` | Incident response |

**When in doubt, read the latest book chapter.** It is the source of
truth for what works, what is pending, and why.
