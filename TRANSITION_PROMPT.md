# TeachMeWrite -- Session Transition Prompt

**Last updated:** Day 109 close (2026-11-16)
**Read this first.** Then open `ARCHITECTURE.md` for depth and the latest
`book/day_NNN.md` for narrative state. `README.md` is the front door.

---

## Identity

TeachMeWrite is a Mastery-Based Learning Management System for Pakistani
students (Matric through CSS/Competitive exams). Built by Muhammad Afzal,
AI/ML engineer with 25+ years of English teaching. Day 108 of a 150-day
engineering capstone: build a competitive AI product, document daily,
prepare for an AI Engineering role.

Three-pillar architecture: Theory, Practice, AI Feedback. Four tiers
(Basic/Intermediate/Advanced/Professional). Multi-tenant (Student/Teacher/
Parent/Institute Admin).

Three services:
- **Backend:** Django 5.2 + DRF, SQLite (local only), port 8000
- **Frontend:** React 19 + Vite + Tailwind, port 5173, base `/teach-me-write/`
- **AI-service:** FastAPI on GCP Cloud Run `asia-south1`, calls Claude Haiku

---

## Current state (Day 109 close)

- **Pillar 1 (Auth):** WORKING. Django JWT; Navbar shows actual unlocked tier via `/me/`.
- **Pillar 2 (AI Feedback):** WORKING. `/studio` -> Cloud Run -> Claude -> render.
- **Pillar 3 (Persistence):** DEPLOYED Day 109. Cloud Run serving `0c5305b`.
  - Local E2E proven Day 107 (5/5 callback tests, rows in DB)
  - Secret Manager migration completed Day 109 (3 Cloud Shell commands)
  - Deploy run 43727450414 attempt 2 succeeded; promoted to 100% traffic
  - End-to-end persistence in production still pending Day 110
    (`DJANGO_API_URL` points at loopback)
- **"My Essays" UI:** SHIPPED Day 109. `/essays` route, Navbar link,
  paginated list with per-card expand/collapse. Browser E2E verified.
- **Live Cloud Run:** `0c5305b` (Day 108's fixes, promoted Day 109)
- **GitHub main:** HEAD = Day 109 close commit (run `git log --oneline -1`)
- **Book chapters:** `book/day_100.md` .. `book/day_109.md` (latest)

---

## Day 110 opening task (30 minutes)

**Primary: close end-to-end persistence in production.**

Point `DJANGO_API_URL` at a reachable Django URL so new essays from
`/studio` persist and appear in "My Essays." Today (Day 109) the browser
endpoint works against Cloud Run, but the background task still fails on
loopback (`127.0.0.1:1/disabled`). New essays return feedback but do not
persist.

Two options, decision for Day 110:

- **Option A (fastest):** second cloudflared tunnel for Django :8000,
  capture the URL, edit `deploy.yml` `DJANGO_API_URL` env var, push,
  wait for deploy (~6 min). URL rotates each session; requires a
  redeploy every session. Acceptable to prove the loop once.
- **Option B (sustainable):** named cloudflared tunnel via Cloudflare
  account, stable subdomain. One-time setup (~20 min). No per-session
  redeploy.

Recommendation: A first to prove persistence works end-to-end, then B
if per-session redeploys become a nuisance. Both are Day 110 work.

**Then (same day or next):**

1. `TierProgress.update_progress()` auto-unlock on tier completion
   (Day 106 finding 1; 15 lines + a test)
2. `fastapi.log` append mode (Day 107 defect; one-line fix)
3. Begin Phase 2 UI polish (Days 112-114 scope)

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
