# TeachMeWrite

A Mastery-Based Learning Management System (LMS) for Pakistani students --
Matric through CSS/Competitive exams. Three-pillar architecture: Theory,
Practice, AI Feedback. Four tiers (Basic / Intermediate / Advanced /
Professional). Multi-tenant (Students / Teachers / Parents / Institute Admins).

Built by an educator with 25+ years of English teaching experience, as a
150-day engineering capstone: build a competitive AI product, document the
journey daily, prepare for an AI Engineering role.

---

## Status (as of Day 113, 2026-11-26)

**Phase 2 (Frontend & UI) -- Day 9 of 50.**

- Pillar 1 (Auth): Django JWT, working. Navbar shows actual unlocked tier via `/me/`.
- Pillar 2 (AI Feedback): FastAPI on Cloud Run, working end-to-end via /studio.
- Pillar 3 (Persistence): **WORKING END-TO-END IN PRODUCTION** as of Day 110.
  - Browser /studio submission -> Cloud Run /feedback -> Claude
  - BackgroundTask POST -> public Django tunnel -> callback auth -> row
  - Row appears in /essays for the submitting user
  - Browser-verified 2026-11-17: score 42, tier PROFESSIONAL, visible in list
  - **Day 111: Django tunnel is now named and stable.** Named cloudflared
    tunnel at `api.teachmewrite.com` (UUID `4cdfe145-...`). DNS CNAME is
    proxied and persistent; credentials on Drive at `.secrets/cloudflared/`.
    The Day 110 per-session `deploy.yml` edit is retired.
  - **Deploy of `83e25e0` shipped on Day 113** (run `45877905216`, revision
    `teachmewrite-ai-00103-ruz`, gate 20/20, promoted to 100% traffic).
    The gate failures between Days 111 and 113 were three independent
    causes: a stale Anthropic key in Secret Manager, a second stale copy
    in GitHub Actions secrets, and a genuine prompt ambiguity for golden
    case `g13`. See `book/day_113.md`.
- Tier linkage: closed Day 106. `/me/` exposes `current_tier` + `tier_progress`.
- "My Essays" UI: shipped Day 109. `/essays` route, Navbar link, paginated
  list with per-card expand/collapse.

Day-by-day chapters in `book/day_NNN.md`. The latest chapter is the most
current picture of state.

---

## Repository layout
teachmewrite/
backend/ Django + DRF (auth, curriculum, progress)
frontend/ React (Vite) + Tailwind CSS
ai-service/ FastAPI (Cloud Run, calls Claude Haiku)
.github/workflows/ CI/CD (build, gate, deploy)
book/ Daily chapters, day_100.md .. day_113.md
notebooks/ Older Colab notebooks (Days 85-95)
ARCHITECTURE.md System map (current as of Day 108)
TRANSITION_PROMPT.md Bootstrap doc for a fresh chat session
README.md This file

text

Three deployment targets:

- **Django backend**: runs on Colab :8000 during development. Not yet on Cloud Run.
- **React frontend**: built with Vite, served via `vite preview` + cloudflared tunnel during dev.
- **FastAPI ai-service**: deployed to Cloud Run `teachmewrite-ai` in `asia-south1`.

At runtime, **two** cloudflared tunnels are active per session:

- **Vite tunnel** (:5173) -- browser-facing app entry point.
- **Django tunnel** (:8000) -- FastAPI's background-task POST target
  (DJANGO_API_URL). URL rotates each session; deploy.yml must be edited
  until the sustainable fix lands.


---

## Quick start (fresh Colab session)

The 11-cell resume pattern. Each cell is one concern.

1. **Cell 1**: env sanity (Python 3.13, Node 22, GITHUB_TOKEN, ANTHROPIC_API_KEY)
2. **Cell 2**: Drive mount with stale-state cleanup
3. **Cell 3**: clone repo, verify Day 107 commits in ancestry
4. **Cell 4**: pip install backend + ai-service
5. **Cell 5**: Django up on :8000 (`--noreload`)
6. **Cell 6**: migrate
7. **Cell 7a**: seed learning data
8. **Cell 7b**: create 4 demo users
9. **Cell 7c**: apply tier policy
10. **Cell 8**: npm install frontend
11. **Cell 9**: npm build
12. **Cell 10**: vite preview :5173
13. **Cell 11**: cloudflared tunnel (DNS backoff up to 53s -- Day 107 lesson)
14. **Cell 12**: verify live Cloud Run allows this trycloudflare host

All cells are idempotent. Re-running a cell is safe. A failed cell names the
specific step that broke.

---

## Deploying ai-service changes

Any commit under `ai-service/**` or `.github/workflows/**` triggers the
deploy pipeline:

1. Build Docker image, push to Artifact Registry
2. Deploy to Cloud Run staging tag (`--no-traffic`)
3. Wait for staging health (up to 150s)
4. Golden-set gate (3 runs, 2-of-3 rule, LLM judge, min-helpfulness 3)
5. Promote to 100% traffic (only if gate passed)

Secrets: `ANTHROPIC_API_KEY` and `INTERNAL_API_KEY` are read via
`--set-secrets` from Secret Manager. Each secret needs its own
`roles/secretmanager.secretAccessor` binding on the Cloud Run SA
(`195673983724-compute@developer.gserviceaccount.com`). New secret =>
new binding. This is not automatic (Day 108 finding).

Env vars: `deploy.yml` line 59 holds non-secret configuration.
Notable values today:
  - `JWT_SECRET_KEY=django-insecure-dev-only-change-in-production` -- MUST match Django's SECRET_KEY for JWT decode to work. Rotates to Secret Manager when Django deploys to Cloud Run (Phase 3).
  - `DJANGO_API_URL=http://127.0.0.1:1/disabled` -- background task fail-closed. Points to Django tunnel URL once stable (Day 109+).

---

## Deploying Django or Frontend changes

Neither is deployed yet. Both run locally via Colab. The pipeline paths
filter is `['ai-service/**', '.github/workflows/**']` -- backend and frontend
changes go to GitHub but do not deploy. Migrating Django to Cloud Run is
Phase 3 work (Days 108-110 in the roadmap).

---

## Documents and their roles

| File | Purpose |
|---|---|
| `README.md` | This file. Front door. What the project is, how to resume. |
| `ARCHITECTURE.md` | Full system map: every module, every endpoint, every model. |
| `TRANSITION_PROMPT.md` | Bootstrap doc for opening a fresh chat session. |
| `book/day_NNN.md` | Daily engineering journal. Latest = most current state. |
| `backend/API_ENDPOINTS.md` | Backend endpoint reference (if maintained). |
| `ai-service/docs/runbook.md` | Incident response for the AI service. |
| `ai-service/docs/evaluation.md` | Day 90 golden-set evaluation report. |

**When in doubt about state, read the latest `book/day_NNN.md`.**
The daily chapter is the source of truth for what is working, what is
pending, and why.

---

## Known issues (open as of Day 110)

- **Django tunnel is stable and shipping (Days 111-113).** `api.teachmewrite.com` is a
  named cloudflared tunnel. `deploy.yml` line 59 points at it permanently.
- **Pre-push probe required.** Any commit that triggers `deploy.yml` must be
  pushed while `api.teachmewrite.com` answers 401 on `/api/v1/users/me/` and
  401 on the callback with no `X-Internal-Key`. The golden-set gate calls
  the ai-service synchronously and fails closed when the origin is down.
  See `book/day_111.md` section 4, Entry 3.
- **`urllib` probes need an explicit User-Agent.** Cloudflare Browser
  Integrity Check returns 403 / `error code: 1010` for the default
  `Python-urllib/...` UA. `requests` / `httpx` defaults pass. See
  `book/day_111.md` section 4, Entry 2.
- **Colab Secrets are not `os.environ`.** Use `google.colab.userdata.get()`,
  then export to `os.environ` in a shim cell. See `book/day_111.md` section
  4, Entry 1.
- **`TierProgress.update_progress()` does not auto-unlock next tier** when a tier is completed. Day 106 finding. 15 lines + a test.
- **`fastapi.log` uses write mode `"w"`** in Cell 7, losing prior session's log. One-line fix (append mode).
- **Resume pattern does not write `.env` before starting Django.** New Day 110 finding: gitignored `.env` means fresh clones have no `INTERNAL_API_KEY` or `ALLOWED_HOSTS` for `*.trycloudflare.com`. Cell 5 must be preceded by a cell that writes `.env` from the Drive backup (`/content/drive/MyDrive/teachmewrite-ai/.secrets/internal_api_key`).
- **`essaysAPI` in api.js is appended after `export default api;`** -- ES module valid, stylistically unconventional. Refactor when api.js next changes.
- **No browser E2E screenshots saved to Drive.** Day 109 and Day 110 both have browser evidence only in chat transcript. Screenshot to Drive would survive runtime recycle.
- **Test-harness discipline:** see Day 107 entries 1-5, Day 108 entries 5-6, Day 109 entries 1-5, Day 110 entries 1-3. Rules captured in Day 107 section 5.2, Day 109 section 5.6, Day 110 section 5.2.

---

## Working conventions

Working conventions, prohibitions, the session bootstrap, and the
pre-push probe requirements live in `RULES.md`. Read it before the
first cell of any session.

## License

Private project. Not yet open-sourced.

---

## Links

- GitHub: https://github.com/edmedpublic-hub/teachmewrite
- Cloud Run (ai-service): https://teachmewrite-ai-195673983724.asia-south1.run.app
- GCP project: `teachmewrite-prod` (region `asia-south1`)
