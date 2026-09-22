# D11 — Governance mechanisms and policy — audit round 6

Baseline `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9), worktree `/Users/timmalmstrom/audit-r6-D11`. Interpreter system `python3` (3.11.5); Node v20.10.0; `gh` read-only as tvofi. Every number is a count, a fraction of counts, or an exit status — no wall/CPU/RSS, so nothing is provisional.

> Reconstructed by the orchestrator from the finder's inline return (REPORT.md write refused; 4 harnesses on disk).

## Findings

### D11-01 (high, hygiene) — the required-check enforcement surface is outside the code-owner boundary

Of the **37 tracked files** that produce or implement the checks the live ruleset requires, **0** are matched by an owner-carrying `.github/CODEOWNERS` pattern, so `require_code_owner_review` cannot demand the repository owner for a change to the checks themselves, and **9 of the 14** merges whose diff touched that surface in the window were approved by the `hpo-approver` App alone.

The enforcement surface is derived from the tree: 6 `.github/workflows/*.yml` + the 26 scripts their non-comment lines execute + 4 wired `.claude/hooks/*.sh` + `.claude/settings.json` — including `policy_lint.mjs`, `policy_lint_mutants.mjs`, `brief_lint.mjs`, `figure_lint.mjs`, the hooks, and the `tests/*` scripts the jobs run. The record confirms the consequence: **#1357 changed `.claude/workflows/policy_lint.mjs` and merged on `hpo-approver[bot]`'s review alone**; #1284/#1364 changed `.github/workflows/tests.yml` the same way.

- Evidence: `codeowners_gap.py` — `0/37` files matched by an owner-carrying pattern.
- Perturbation: append `/.claude/workflows/  @tvofi` to a **copy** of CODEOWNERS → covered 0→11; one ownerless line naming `policy_lint.mjs` → 11→10 (last-match-wins). Null arm (unmodified) → 0.
- instrumented_symbol: `.github/CODEOWNERS` (armed by ruleset 23698884's `require_code_owner_review`).
- Fix: ~6 lines of CODEOWNERS (`.claude/workflows/`, `.claude/hooks/`, `.claude/settings.json`, `.github/workflows/`, the `tests/*` scripts), or record the refusal in the file's header as it does for `docs/HANDOVER.md`.

### D11-02 (high, bug) — a required check is executed from the change it is checking

A one-line change (`process.exit(errors > 0 || rc ? 1 : 0)` → `process.exit(0)`) to `.claude/workflows/policy_lint.mjs` makes the `policy-docs` required-check command exit **0** on a corpus the same run reports as red, with stdout **byte-identical** to the unmuted run; the lane built to catch a gutted check (`policy_lint_mutants.mjs`) does not notice.

`governance.yml`'s `policy-docs` job runs `actions/checkout` with no `ref:`, so both the corpus and the checker come from the PR's own tree; the job conclusion is `node policy_lint.mjs`'s exit status. `policy_lint_mutants.mjs` exercises `assertAcceptance`, which returns before the mutated exit line.

- Evidence: `check_in_diff.py` — `rc_red_unmodified=1, rc_red_one_line_changed=0, total_errors` identical (1) in both, `stdout_identical_red_arms=1`.
- Perturbation: the one-line change in a scratch clone, corpus made red by renaming one citation target.
- Null control (arm D): the same one-line change on a GREEN corpus → rc 0, TOTAL 0 — the mutation changes no verdict of its own; arm E runs the mutant lane in the mutated tree → verdict unchanged.
- instrumented_symbol: `.claude/workflows/policy_lint.mjs:main`.
- Fix: re-execute the checker from a trusted ref (`git show origin/main:.claude/workflows/policy_lint.mjs` against the diff's corpus), or take D11-01's fix. ~15 lines.

## Non-findings (13, each with its executed number)

Key ones: required contexts green at all 45 merged heads (`required_red_at_head_last=0`); body contract held at every merged head (`refused_at_merged_head=0/45`; one-hex perturbation → 43/45 refused); authorship rule executable (45/45, baseline-checker's 10 refusals were anachronisms); 0 shell interpolations of untrusted text; 0 `pull_request_target`/`workflow_run`; 65/65 SHA-pinned actions; hooks roster pinned by membership; 21 mutant arms 0 SKIP; structure ratchet 12/12 at cap; budgets inside band; brief_lint clean. **Refuted, do not re-file:** the red `record` job on main is the documented batch state (green at the stamp where the window is empty). **Null result:** `strict_required_status_checks_policy=false` showed no separation (change-failure rate is D13's).

## Ranked changes

1. Extend CODEOWNERS to the enforcement surface (~6 lines).
2. Re-execute one checker from a trusted ref (~15 lines).
3. Make enforcement-surface ownership self-measuring (~30 lines).
4. If 1 is refused, record the refusal in CODEOWNERS' header.
5. Optional: raise `strict_required_status_checks_policy` to `true`.

## Exposure

GitHub API read-only: both rulesets (22628467, 23698884) from `/rulesets/{id}`; a 45-merge window (2026-09-13..09-22) of PR bodies/titles/reviews/files + per-head and per-merge-commit check-runs; releases. Git history (`git log -S`, tag objects). Toolkit read as required. **Not opened:** the audit register, HANDOVER, plan, RELEASE_NOTES. Incidental `grep -rn` printed round3/4/5 filenames only — not opened, no finding rests on them.

## Harnesses

`codeowners_gap.py`, `conformance.py`, `contract_replay.py`, `check_in_diff.py` — all run from the worktree with `PYTHONPATH=tests/hastub`; mutation arms run in a scratch clone so the tree under audit is untouched.
