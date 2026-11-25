# TeachMeWrite -- Working Rules and Conventions

**This is the sole home of working rules.** `TRANSITION_PROMPT.md`,
`README.md`, `ARCHITECTURE.md`, and every `book/day_NNN.md` chapter are
content; they do not duplicate rules. When a rule is added or changed, it
is added or changed here, and here only.

Read this file before the first cell of any session.

---

## Part 1 -- Working conventions

1. **One concern per cell.** Even when the next three steps are visible.
   Especially then. If the first step fails, the next two are wasted.
2. **First line of every cell is `# === CELL <id>`.** Enables copy-paste
   discipline and makes failed cells identifiable in transcripts.
3. **`ast.parse` every code block before delivery.** Catch syntax errors
   before they reach a runtime.
4. **`assert` before `DONE`.** Never print DONE after a conditional that
   could fail. Failures in this pattern have cost multiple days.
5. **Derive expected values from `git` / ORM / API, never from memory.**
   When the actual value differs from what you remembered, the actual
   value wins.
6. **`.startswith()` for SHA comparisons, never slice.**
7. **ORM for DB verification.** Raw `sqlite3` bypasses type conversion
   (UUID `.hex`). Exception: reading `sqlite_master.name` for table-presence
   checks is safe.
8. **No secret values in chat.** Never paste back. Rotate if exposed.
   Drive links to credential files are access-granting and are treated
   the same way.
9. **Diagnose before edit.** Fetch the actual error from logs. Do not
   guess.
10. **Byte-based size thresholds, not line-based.** Line counts are
    fragile for prose (bash fences, blank-line conventions, trailing
    newline ambiguity).
11. **Book chapter at day's end** with 5 sections (Milestone, Architecture,
    Implementation, Debugging Diary, Key Takeaways). Update README,
    ARCHITECTURE, TRANSITION_PROMPT at milestones. **Rules live in
    `RULES.md`, not in these updates.**
12. **Expected-output blocks are prose, not code.** Never paste them as
    code. If a cell fails with `SyntaxError` on a line starting with `[`
    or `---`, the wrong block was pasted.
13. **Commit per fix, not per session.** A milestone close, a rule
    extraction, a code fix, and a docs update are separate commits.
    Mixing them makes both harder to review and harder to revert.
14. **Colab Secrets are `userdata.get`, not `os.environ`.** On a fresh
    session, `os.environ.get('GITHUB_TOKEN')` is `None` even when the
    secret is present in the UI. Read via `google.colab.userdata.get`,
    assert non-empty, then export to `os.environ` for subprocesses that
    expect it. See `book/day_111.md` section 4, Entry 1.
15. **One cell per turn, no lookahead.** A cell that edits or replaces
    must first **probe**: read the exact byte-context of every target
    string and print it. Write cells derive their `old` values from
    probe output, never from memory. Do not write cell N+1 until cell
    N's output is pasted and its effect is stated. This rule closes the
    failure class seen on Day 111, where a write cell ran against a
    directory that was not a git checkout because a prior cell did not
    probe.

## Part 2 -- What not to do

- Do not push to `main` without a dry-run first.
- Do not commit `backend/.env` or `backend/db.sqlite3` or any file under
  `.secrets/`.
- Do not skip the `assert` before DONE.
- Do not run `gcloud auth login` in Colab (EOF on stdin) -- use Cloud
  Shell.
- Do not pre-decide a fix before seeing the actual log error.
- Do not push through when the end is visible -- stop at clean
  boundaries.
- Do not paste expected-output blocks as code -- check that the first
  line starts with `# ===`.
- Do not write cell N+1 before cell N's output is in hand.

## Part 3 -- Session bootstrap (run once per session, before any other cell)

Three things must hold before any session's first non-bootstrap cell.
The bootstrap cell (`Cell 0` in each notebook) should do all three and
DONE only after all pass.

1. **Colab Secrets exported.** Read `GITHUB_TOKEN` and `ANTHROPIC_API_KEY`
   via `userdata.get`, assert non-empty, export to `os.environ`.
2. **Git identity set.** `git config --global user.name` and `user.email`.
   Without this, `git commit` fails with exit 128 in a fresh runtime.
3. **Repo is a git checkout at a known HEAD.** If `/content/teachmewrite`
   exists but is not a git repo (e.g. an empty directory created by a
   prior write cell), remove it and clone fresh. Report HEAD and status.

## Part 4 -- Pre-push probe

Before any push that triggers `.github/workflows/deploy.yml`, the Django
origin behind `api.teachmewrite.com` must be running. Verify with two
specific 401s (not `in (...)` sets):

- `GET  https://api.teachmewrite.com/api/v1/users/me/` -> 401
- `POST https://api.teachmewrite.com/api/v1/writing/feedback-callback/`
  (no `X-Internal-Key`) -> 401

Include an explicit `User-Agent` header (`urllib`'s default triggers
Cloudflare Browser Integrity Check, error 1010). See
`book/day_111.md` section 4, Entries 2 and 3.

---

*Rules extracted 2026-11-23 (Day 112 opening) from `TRANSITION_PROMPT.md`
conventions 1-13, plus Day 111 findings folded in as conventions 14-15
and pre-session requirements. Append new rules here; do not duplicate
them in other files.*
