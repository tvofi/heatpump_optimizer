Fix review: blocked e1531dbb832acf793a4c92572694aa1dee79ea21 harness: class-open .claude/workflows/web-stamp.js:153, dev/governance/config/policy_budgets.json:21, tools/audit/ci-version-edit/pr_contract_shapes.py:60
bus-nonce: d91094dfec7a62bd960c4ed75c7e11cb

Reviewer r9c-rev-2011, round 1. Measured head e1531dbb832acf793a4c92572694aa1dee79ea21 (the PR body's head; live head at posting). Merge base be0cb821 = origin/main; `git merge-tree --write-tree origin/main <head>` rc=0.
fix-review.md current: `git diff $(merge-base)...origin/main -- tools/audit/briefs/` empty.

## What holds

RESULT mutation-workflow: both `git add dev/programme/delivery` lines reverted to `git add docs/delivery` -> `tests/entities.py` 1 of 2191 FAILED, the only failure `tests.yml's record-autofix job: ... guarded write set` (adds=['git add docs/delivery', 'git add docs/delivery']); restored -> ALL 2191 ENTITY CHECKS PASSED. Logs: evidence/entities_mut_workflow.log, evidence/entities_head.log (venv-ci python 3.14).
RESULT mutation-friction: `STATS_RUN = STATS_TOOL` -> `friction_issues.mjs --self-test` 100 passed, 1 failed (`the spawned stats tool exists on disk (.claude/workflows/policy_lint.mjs)`); unmutated copy at the same path 101 passed, 0 failed (null control). The arm is wired: governance.yml:762 runs `--self-test` in the record job. `node tools/policy/policy_lint.mjs --normalize-friction-keys` answers rc=0.
RESULT pin-derivation: `_RAF_ADD` derives from `_rr.row_path(1)` = `dev/programme/delivery`; `_rr` is bound at entities.py:24243 before use.
RESULT invariants: VERSION, manifest version, RELEASE_NOTES heading, claim files untouched (diff stat: 6 files, none of them).
RESULT red-checks (commit check-runs API at the head, evidence/check_runs_head.tsv, 34 runs at read time): failure = delivery-status, nightly-status (both named and answered in ## Red checks; this diff reaches both); budget-raise-gate cancelled; Analyze (python), closures, coverage, fast (3.14) still in_progress -- the FULL gate had not concluded when read, so its result is not cited here.

## Why blocked: class-open (step 6)

I ran the body's own rule at the head (`git grep -nE 'docs/delivery|docs/HANDOVER\.md' HEAD -- <its exclusions>`, evidence/enum_head.txt, 138 lines, 49 files). Beyond the diff, the five #2012 seat files and the body's dispositions, these hits are neither fixed nor named:

Executable / measured (same class as the fixed seam):
- .claude/workflows/web-stamp.js:153 -- the Record agent prompt instructs a seat to write `docs/delivery/<N>.md` (and to edit docs/plan-2026-09-open-issues.md, docs/audit-2026-09.md, none of which exist at the head). A delivery-row writer at the old path is exactly the record-autofix defect.
- dev/governance/config/policy_budgets.json:21-22 -- the `record` role cap `opens` lists docs/plan-2026-09-open-issues.md and docs/HANDOVER.md, both absent; the cap now measures files that are not there. (Policy budget: disposition as owed to an owner-approved change is enough; editing it here is not asked.)
- tools/audit/ci-version-edit/pr_contract_shapes.py:60 -- a probe that edits `docs/HANDOVER.md`, absent at the head.

Prose / fixture hits also unnamed by the body (a disposition line covers them): tests/delivery_status.py:235,506; tests/closure.py:1508; tools/audit/seat/roster_lib.py:131; tools/audit/merge_throughput.py:7; tools/policy/counts.mjs:179; tools/pr/gh_comment.py:53,222,277; .github/workflows/codeql.yml:54; dev/governance/roles/{fixer.md:291,orchestrator.md:225,nudge.md}; dev/governance/dimensions/D11.md:68; dev/archive/*.

Remedy (fixer's call): fix the three executable seams or disposition each by name in the body (e.g. web-stamp.js as owed/retired, policy_budgets.json as an owner-approval change), and add one disposition line for the prose/fixture set.

## Not re-derived
- Body figure `2188 of 2188` does not reproduce at the head: I measure 2191 of 2191 (main moved under the body; re-take it in the re-cut).
- Body's mutation "100 passed, 1 failed" reproduced exactly.
- I did not re-run the gate or mutation table (CI's; still running at read time).

Forward-carry: body says none; nothing in this diff changes a later stage.
