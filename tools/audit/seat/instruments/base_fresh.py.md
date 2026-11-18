# `base_fresh.py`

- `base_fresh.py` — refuses a tree whose policy, instruments or workflows
  are not origin/main's (`dev/audit/rca/R11-RCA-PLAN-OBJECTIVE-MISSING.md`).
  The paths it judges are its `POLICY` list: `CLAUDE.md`, `AGENTS.md`,
  `dev/governance`, `dev/programme/RULINGS.md`, `.claude/workflows`, `.claude/rules`,
  `.claude/skills`, `.claude/hooks`, `tools/audit`, `tools/policy`, `tools/pr`
  and `tools/plan`. It fetches origin/main first (`--no-fetch` straight after
  a fetch of your own).
  - `tree [--dir D]` judges a checkout. A file whose blob differs from main's
    is `STALE` when main changed it after the merge base, and the branch's
    own when only the branch changed it, which is allowed. An uncommitted
    edit to a tracked policy file and an untracked file under a policy path
    are `STALE` too. Last line `BASE-FRESH PASS` or `BASE-FRESH FAIL`, with
    `(stale N, own M)`; each refusal prints its repair.
  - `tree --rev R` judges a commit, with no uncommitted state.
  - `tree --handoff` is the check before a head freezes: an uncommitted edit
    refuses; files main moved since the base are `LISTED` and do not refuse,
    because a head behind main is not merged for that (`fixer.md` step 6).
  - `ensure [--dir D]` is what a checkout that carries no work runs before
    use: `tree`, and when that refuses, `reset`, then `tree` again. Last line
    `BASE-FRESH PASS`, `BASE-RESET <old> -> <new>` (restart whatever already
    read the old tree) or `BASE-FRESH FAIL` with `not reset: <why>`.
  - `reset [--dir D]` moves a checkout to origin/main: on its branch when it
    has one, detached otherwise. One holding a commit origin/main lacks, or a
    tracked edit, is never moved: `BASE-RESET REFUSED: <why>`, exit 1.
    `tick_loop.sh`'s restart calls it.
  - `overlay --file F --of <tracked path> --patch P` judges a local copy of
    a tracked file: it must be main's current file with that patch applied.

  Exit 0 fresh, reset or a `--handoff` listing; 1 a refusal; 2
  `BASE-FRESH UNREAD` (no checkout, no origin/main, a failed fetch, a shallow
  clone), which callers treat as a refusal. When: at a seat's start (the
  `base fresh:` line of `.claude/hooks/session-start.sh`; a cloud prompt's
  first step), before a dispatch or a Workflow launch from a checkout, before
  a `scriptPath` launch of a copy (`overlay`), and by hand on a `BASE-STALE`
  line. Wired into: `hooks/liveness.py` (`BASE-STALE`, `BASE-RESET`),
  `cloud_dispatch.py`'s prompts, `review_packet.py`'s `## Policy base`
  section, `body_push.sh` (`REFUSED BASE-STALE`), `handoff_push.sh`,
  `tick_loop.sh`, `wt_sync.sh` and the first seat of every
  `.claude/workflows/*.js`; its self-test refuses a seat-start path that
  stops naming it.
