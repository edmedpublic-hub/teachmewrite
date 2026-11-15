# TeachMeWrite -- Session Transition Prompt

**Last updated:** Day 108 close (2026-11-15)
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

## Current state (Day 108 close)

- **Pillar 1 (Auth):** WORKING. Django JWT; Navbar shows actual unlocked tier via `/me/`.
- **Pillar 2 (AI Feedback):** WORKING. `/studio` -> Cloud Run -> Claude -> render.
- **Pillar 3 (Persistence):** LOCAL-PROVEN Day 107. NOT WORKING IN PRODUCTION.
  - Django callback tested 5/5 Day 107, rows confirmed in local DB
  - Cloud Run deploy `0c5305b` FAILED at step 07 (Deploy to Cloud Run)
  - Reason: secret `internal-api-key` does not exist in Secret Manager
  - Fix: 3 Cloud Shell commands (Day 109 opening task, see below)
- **Live Cloud Run:** `9cbfd0e` (Day 107 image), fail-closed callback
- **GitHub main:** HEAD is `0c5305b` (Day 108's two commits on top of `9cbfd0e`)
- **Book chapters:** `book/day_100.md` .. `book/day_108.md` (latest)

---

## Day 109 opening task (10 minutes)

Three Cloud Shell commands, then rerun deploy. Full detail in
`book/day_108.md` section 3 and `ARCHITECTURE.md` section 3.1.

1. Open Cloud Shell: https://console.cloud.google.com/cloudshell?project=teachmewrite-prod
2. Run:
read -s -p "Paste key: " KEY; echo
printf '%s' "$KEY" | gcloud secrets create internal-api-key --replication-policy=automatic --data-file=- --project=teachmewrite-prod
gcloud secrets add-iam-policy-binding internal-api-key --member="serviceAccount:195673983724-compute@developer.gserviceaccount.com" --role="roles/secretmanager.secretAccessor" --project=teachmewrite-prod
unset KEY

text
3. The key value is at `backend/.env` line `INTERNAL_API_KEY=...` on Colab
(fingerprint `2c4be7f1`). Also backed up to Drive at
`/content/drive/MyDrive/teachmewrite-ai/.secrets/internal_api_key`.
4. Back in Colab: rerun the failed deploy via GitHub API
(`rerun-failed-jobs` on run `43727450414`) OR the "Re-run failed jobs"
button in the GitHub UI.
5. After promote: verify Cloud Run's callback accepts authenticated POSTs.

Then begin "My Essays" UI (Day 107/108 deferred deliverable).

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
