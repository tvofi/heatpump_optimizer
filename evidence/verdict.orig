Fix review: blocked b9f201f90efbb39422319426a7839c036b7b46af carry-missing: the body's ## Forward-carry item and both ## Friction items name no destination, so carry_audit.py (pr-contract's last step) refuses it: CARRY-AUDIT 3 unrouted

bus-nonce: c1b189dc22279cb77bebed3a0761e7de

Round 1. Head measured: b9f201f90efbb39422319426a7839c036b7b46af (ev/HEAD), still the branch tip when this was written. Contract: fix-review.md at main; `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so it is current.

## The block

`python3 -I tools/audit/carry_audit.py check --body <live body>` at this head (the same file as main's) exits 1 (ev/carry_audit_head.txt):

- `UNROUTED body item e6ba36a9 (## Forward-carry)`: the INSTRUMENTS.md entry.
- `UNROUTED body item d64636a3 (## Friction)`: the `fixer.md` cost item.
- `UNROUTED body item c5afd07f (## Friction)`: the `tests/harness_headers.py` cost item.
- Result line: `CARRY-AUDIT: 3 finding item(s): 0 routed, 3 unrouted`.

pr-contract has not refused this yet only because both of its runs on this head died on the rate limit before writing /tmp/pr-body.md. Once it reads the body, it goes red on this step.

The fix is a body edit with no code change. Give each item a `Carry:` marker (`Carry: dismissed: <reason>` or a live group). Alternatively, write `none` under `## Forward-carry`, because the item there is a pointer to the INSTRUMENTS.md entry, not a carried finding.

## What holds (RESULT lines)

- RESULT self-tests: `head_note self-test: 6 checks, 0 failed` and `app_push self-test: 135 checks, 0 failed`. Both match the body.
- RESULT harness (the fixer's own, dev/audit/harnesses/r10_recarry_head.py), from ev/head_figures.txt:
  - Head: `writers: 6`, every row `plain=named quoted=named fenced=named crlf=named`.
  - Base (`git archive origin/main`): every row `fenced=unnamed`, with the other cells named.
  - Both match the body.
- RESULT mutants (ev/mutants_M1_M3.txt). All three match the body.
  - M1: head_note `6 checks, 5 failed`, app_push `135 checks, 4 failed`, 6 harness rows unnamed.
  - M2: `1 failed` and `1 failed`, 6 rows unnamed.
  - M3: `5 failed` and `4 failed`, 6 rows unnamed.
- RESULT reviewer mutants. Both are caught.
  - M4: app_push's head_note call replaced by `true`. `app_push self-test: 135 checks, 13 failed`, including all the R10-RECARRY-HEAD arms (ev/mutant_M4_app_push_callsite.txt).
  - M5: update_pr.sh's call site reverted to `s.index('## Head\n\n')`. The harness turns only that row red: `update_pr.sh:51 ... fenced=unnamed` (ev/mutant_M5_update_pr_revert.txt).
- RESULT finder-shape measurement, built by me (ev/finder/r2400_shape.py). No finder harness is committed for this group: the roster brief names only a control. The script rebuilds #2400's pre-recarry body from its merged body (the two misplaced notes and the hand-written fd0f5d9 line removed). It applies the edc4484 and fd0f5d9 recarries and reads each result with policy_lint `--pr-body --head`:
  - `base recarry1@edc4484=unnamed recarry2@fd0f5d9=unnamed`. This reproduces the two pr-contract refusals the body cites.
  - `head recarry1=named recarry2=named`.
  - Null control: the rebuilt body read at its own head ca96324 is `named`.
- RESULT class: the body's rule, run by me (ev/class_grep.txt). Base gives 7 lines (app_push.sh:344; open_pr.sh 39 and 52; update_pr.sh:53; handoff_push.sh 69, 89 and 105). Head gives 2, both in head_note.py and neither a locator. A wider grep for `'## Head'` in tools/tests/.claude/.github finds only fixtures, record_row.py's body generator and push.sh's line-based awk reader, which the body dispositions as alternative 2. No open seam.
- RESULT merge: `git merge-tree --write-tree origin/main(c3530277) <head>` gives rc=0 with tree cb670a9e (ev/merge_tree.txt).
- RESULT untouched: VERSION, manifest, RELEASE_NOTES.md, tests/golden and the budgets have an empty three-dot diff.
- RESULT cheap checks (ev/cheap_checks.txt): `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, `STRUCTURE RATCHET PASSED`, and tmp_paths `0 refused`.
  - agreement: `divergent=0 unregistered=0 dead=0 refused=4`, identical at main.
  - entities: `1 of 2349 ENTITY CHECKS FAILED` (graders-head-copy) at both head and main, so it is not this diff's (ev/entities_head_then_base.txt).
- RESULT CI on the head (check-runs API, ev/checkruns.tsv): 45 runs. 22 success, 13 skipped, 1 neutral, 7 failure, 2 in progress (closures, Analyze).
  - Six of the reds are the installation rate limit, from ev/logs: pr-contract x2, arch-score x2 (`gh: API rate limit exceeded for installation`), validate-hacs (`GitHubRatelimitException`) and nightly-status (`HTTP 403 ... rate limit exhausted`).
  - env-matrix's one FAIL is `required-contexts ... the GitHub API is unreachable`, in the same 08:00-08:01Z window.
  - None is a test failure of this diff. Step 11's root-cause-unanswered is not posted: the workflows have not all concluded, and no pr-contract run has read the body. The rate-limited checks need a re-run.

## Notes

- Not re-derived: `harness_headers.py` and `env_drift.py --all`. Neither was run here, and the body claims neither.
- head_note.py takes the first `## Head` heading outside a fence. `sections()` in policy_lint.mjs keeps the last one, because `Map.set` overwrites a repeated title. The two diverge only on a body with two real `## Head` headings, a shape no writer produces. Carry: dismissed: no writer emits two Head headings
- The body does not say that r10_recarry_head.py and the app_push arms are the fixer's own instruments, given that the finding had no committed harness (step 9). Carry: R10-RECARRY-HEAD
