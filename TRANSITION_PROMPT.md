# TeachMeWrite -- Session Transition Prompt

**Last updated:** Day 110 close (2026-11-17)
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

Two cloudflared tunnels expose the local services for the day's work:

- Vite tunnel -> :5173 (serves built frontend via vite preview). Browser entry.
- Django tunnel -> :8000 (serves Django backend). FastAPI's DJANGO_API_URL
  points at <django-tunnel>/api/v1/writing/feedback-callback/. URL is
  ephemeral; deploy.yml must be edited every session until the sustainable
  fix lands.


---

## Current state (Day 110 close)

- **Pillar 1 (Auth):** WORKING. Django JWT; Navbar shows actual unlocked tier.
- **Pillar 2 (AI Feedback):** WORKING. /studio -> Cloud Run -> Claude -> render.
- **Pillar 3 (Persistence):** WORKING END-TO-END IN PRODUCTION (Day 110).
  - Browser submit -> Cloud Run -> Claude -> BackgroundTask
  - -> public Django tunnel -> callback auth -> WritingFeedback row
  - -> row appears in /essays for the submitting user
  - Browser-verified 2026-11-17: score 42, tier PROFESSIONAL, visible
  - **Caveat:** Django tunnel URL is ephemeral; `deploy.yml` must be edited
    each session. Day 111: named tunnel or Django on Cloud Run.
- **"My Essays" UI:** SHIPPED Day 109. /essays route, Navbar link, paginated.
- **Live Cloud Run:** `ad575f3` (Day 110's DJANGO_API_URL fix)
- **GitHub main:** HEAD = Day 110 close commit (run `git log --oneline -1`)
- **Book chapters:** `book/day_100.md` .. `book/day_110.md` (latest)

**Resume gotcha (Day 110 finding):** gitignored `backend/.env` does not
arrive in a fresh clone. Before any cell tests a reachable callback,
write `.env` from the Drive backup:

    /content/drive/MyDrive/teachmewrite-ai/.secrets/internal_api_key

and set `ALLOWED_HOSTS=localhost,127.0.0.1,.trycloudflare.com` +
`INTERNAL_API_KEY=<value>`.

---

## Day 111 opening task (60-90 minutes)

**Primary: stable Django URL.** The tunnel URL rotates every session; today
proved the loop closes, but tomorrow's session gets a different URL and
`deploy.yml` must be edited again. Two options, decision for Day 111:

- **Option A -- Named cloudflared tunnel.** Cloudflare account + a domain
  (~20 min setup). Stable subdomain, no per-session redeploy. Fastest
  sustainable fix.
- **Option B -- Django on Cloud Run.** Multi-hour build: Dockerfile,
  Postgres, prod settings, secrets management, migrations at startup.
  Correct long-term answer, Phase 3 scope.

Recommendation: A first. B in Phase 3.

**Also required (from Day 110 debugging):**

- **Resume pattern must write `.env` before starting Django.** New Cell 4.5
  (or extend Cell 5) that reads the Drive key + writes
  `backend/.env` with `ALLOWED_HOSTS` and `INTERNAL_API_KEY`.

**Then (same day or next):**

1. `TierProgress.update_progress()` auto-unlock on tier completion
   (Day 106 finding 1; 15 lines + a test)
2. `fastapi.log` append mode (Day 107 defect; one-line fix)
3. Capture browser E2E screenshot for Day 109/110 retrospective
4. Begin Phase 2 UI polish (Days 112-114 scope)

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

## Working conventions (load-bearing)

Violating these produces the failure classes we spent Days 105-108 debugging.

1. **One concern per cell.** Even when the next three steps are visible.
*Especially* then. If the first step fails, the next two are wasted.
2. **First line of every cell is `# === CELL <id>`.**
3. **`ast.parse` every code block before delivery.**
4. **`assert` before `DONE`.** Never print DONE after a conditional that
could fail. Three failures in one week from this pattern.
5. **Derive expected values from `git status` / ORM / API.** Never from
memory. (Day 107 entry 4.)
6. **`.startswith()` for SHA comparisons.** Never slice. (Day 107 entry 5.)
7. **ORM for DB verification.** Raw sqlite3 bypasses type conversion
(UUID `.hex`). (Day 107 entry 1.)
8. **No secret values in chat.** Never paste back. Rotate if exposed.
(Day 108 entry 2.)
9. **Diagnose before edit.** Fetch actual error from logs. Do not guess.
(Day 108 entry 4.)
10. **Byte-based size thresholds, not line-based.** Line counts are
 fragile for prose (bash fences, blank-line conventions).
 (Day 108 Cell 16.)
11. **Book chapter at day's end** with 5 sections (Milestone, Architecture,
 Implementation, Debugging Diary, Key Takeaways). Update README,
 ARCHITECTURE, TRANSITION_PROMPT at milestones.
12. **Expected-output blocks are prose, not code.** Never paste them as
 code. If a cell fails with `SyntaxError` on a line starting with `[`
 or `---`, the wrong block was pasted.

---

## What not to do

- Do not push to `main` without dry-run first
- Do not commit `backend/.env` or `backend/db.sqlite3`
- Do not skip the `assert` before DONE
- Do not run `gcloud auth login` in Colab (EOF on stdin) -- use Cloud Shell
- Do not pre-decide a fix before seeing the actual log error
- Do not push through when the end is visible -- stop at clean boundaries
- Do not paste expected-output blocks as code -- check that first line starts with `# ===`

---

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
