Fix review: merge dc4e3f13a345d794a0621744b22fef8479140ae9

bus-nonce: 4fd41e3fd74bc78a939d10f39ada12c0

This is round 2. Round 1 was the blocked verdict at ace05371ed47a6a9d378883c9fefbad08315c343. A repair is owed, not a re-cut.

Merge conditions. The orchestrator holds each of these. None of them is a defect in the authored work.
1. `mutation` stays red until R9-CI-1's sharded pin run pins this diff's sites. The brief asked me to judge everything else. Merge waits on that pin run.
2. `closures` is red at this head on `dev/audit/harnesses/r9_ro12_batch_mutants.sh`. That is main's red: `closures` on origin/main 6b91e238 printed the same failure. It is not this PR's.
3. The cancelled `budget-raise-gate` twin needs a re-run. A successful twin exists, and the diff contains no `*_budgets.json`.

Head measured: dc4e3f13a345d794a0621744b22fef8479140ae9. The body's `## Head` names it. At posting, `git ls-remote origin refs/heads/fix/r9-ux-actions` returned the same SHA. The merge base is origin/main 6b91e238f6883af6eedef0fc541bce76b14fc46c, so `git merge-tree` against main is trivially clean. `git diff $(git merge-base origin/main HEAD)...origin/main -- tools/audit/briefs/` was empty. Worktree: /Users/timmalmstrom/hpo-seats/review-2010/wt, detached.

## Round-1 blocking points

- **typing.** At this head, CI `typing` (job 113163961692) printed `ok errors did not grow`, `ok type_ignores did not grow` and `ALL 9 typing-ruler checks PASSED`. Commit 5cb01b65 makes the fix. `_fold_away` now takes `away_mode.AwayState` and `Mapping[str, object]` and returns a new `AwayFold(AwayView, total=False)` TypedDict. It narrows `state.as_dict()` with `cast`; it adds no `type: ignore`. Fixed.
- **mutation unmeasured and unnamed.** The body now names `mutation` and `mutation-autofix` under `## Red checks` and lists every site under `## Unpinned sites`. At this head, CI `mutation` (job 113163961812) printed `MUTATION TABLE REFUSED -- 4706 unpinned site(s) against 4670 ..., 37 of them added by this diff` and `nothing was measured: 0 mutant(s) timed out, 37 not started for --budget-minutes`. The trigger is answered. The pins wait on R9-CI-1, which is condition 1.
- **advisor screenshot.** Commit 2ada816b regenerates `docs/img/card/advisor-{light,dark}.png` and `plan-why-{light,dark}.png`. I opened advisor-light.png: the row "Hot-water setpoint 55 → 48 °C" now has an Apply button. I opened plan-why-light.png: the tooltip says "Because:", lists two sub-code reasons, and sits inside the chart without clipping, which also meets the UX-1 forward-carry. Fixed.
- **env-matrix unnamed.** At this head, `env-matrix` (job 113163961997) is green. The body names it anyway. Both `pr-contract` runs at this head are green (113163961294, 113164713101). Fixed.

## Delta since round 1

The non-merge commits that are on HEAD but not on origin/main or ace05371 are 5cb01b65, 2ada816b, 4f4e882c, 13fc4a45, c0a3e641 (a net revert of 13fc4a45), c75b7770 (the approved one-pass `idle_codes`) and c79b4bdd (the closures entry).

`git show --remerge-diff` on each merge:
- **3c061213** (main 8d7903e6). The only change in `tests/features.py` is removing the conflict markers. Both blocks are kept, UX-5 first and R9-DBG-1 after. `claimed_drift.txt` keeps the 31 UX-5 claims and drops the stale R9-DIAG-2S note. The `claimnotes` driver printed `MERGE-CLAIM: refused tests/golden/claimed_drift.txt` because both sides rewrote the claim list. The hand resolution keeps main's `config_flow` line byte-identical, and env_drift reports `config_flow is byte-identical`. The usage line in `ux5_idle_codes.py` was moved to `dev/audit/harnesses/`. All of this matches the body's `## Delta`.
- **a5379d67** (main e2a4f7c6). The ledger driver printed `LEDGER-MERGE: resolved tests/closures.json`, merging inert_reads as a set.
- **dc4e3f13** (main 6b91e238). No remerge difference.

The `inert_reads` entry. CI `closures` at 5eaf0982 (job 112899052762) printed `tests/harness_headers.py: tools/audit/harnesses/ux5_idle_codes.py`. The entry the PR adds names the post-move path, `dev/audit/harnesses/ux5_idle_codes.py`. I ran a plant against the merge base: with the entry deleted, `tools/pr/ci_predict.py --base 6b91e238` printed `PREDICT closures INERT READS tests/harness_headers.py: dev/audit/harnesses/ux5_idle_codes.py`. With the entry restored it printed `no closures or fast red predicted`. At this head, CI `closures` (job 113164048164) no longer names the ux5 harness. Its only line is `tests/harness_headers.py: dev/audit/harnesses/r9_ro12_batch_mutants.sh`. origin/main's own `closures` at 6b91e238 (job 113159208937) printed exactly the same line. That red came from #2044 on main. `closures-autofix` printed `skip-manual-repair-owed`. The movement is earned.

The ledger triage `survivor_triage/notifier.py/_comfort_cause.RETURN_DEL.da9e8e97.json` (4f4e882c) marks the trailing `return None` of `_comfort_cause` as equivalent. That is correct: deleting it falls off the end of the function, which also returns None.

## Mutation proof (my own probe, from this tree)

`evidence/ux5_block.py` executes the UX-5 block of `tests/features.py` one statement at a time with a stub `R`. It skipped 9 statements that need names from earlier blocks. Each mutant was applied in place and restored with `git checkout`.

RESULT baseline checks_run=38 failed=0 skipped=9
RESULT del-other checks_run=38 failed=2 skipped=9
RESULT del-fuse checks_run=38 failed=2 skipped=9
RESULT del-dearer checks_run=38 failed=1 skipped=9
RESULT del-solar checks_run=38 failed=3 skipped=9
RESULT coast-0.10 checks_run=38 failed=1 skipped=9
RESULT cause-none checks_run=38 failed=1 skipped=9
RESULT del-fold-equal checks_run=38 failed=1 skipped=9

The body names two mutants: the deleted fuse line and the deleted `_fold_away` equal-floor return. Both are among the mutants above, and both fail named checks. The null is the baseline row: 0 checks failed. The suite as a whole is CI's: `fast (3.14)` (job 113163961690) is green at this head.

## Claims and goldens (three-dot, against 6b91e238)

- `claims-for: 6.7.16` in both claim files equals `VERSION` 6.7.16. `pr-contract` printed `no version edit: origin/main...dc4e3f13 moves none of VERSION, the manifest version or a notes heading`.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 6b91e238` exited 0. It printed `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`, with 31 CLAIMED, 19 MAY-DRIFT and 6 byte-identical (`config_flow` and the five `coord_*`).
- I wrote my own leaf classifier, `evidence/leaves.py`. It captures HEAD's scenarios and diffs their leaves against env_drift's cached capture of the merge base. Result: `RESULT leaves scenarios_moved=50 reasons_leaves=6050 other_leaves=0`. Every moved leaf in all 50 moved scenarios, may-drift ones included, is `space_reasons` or `dhw_reasons`. No claimed value moved.
- `node tests/card_drift.mjs 6b91e238` (after `tests/plan_view.py`) printed `2 state(s) moved and claimed, 38 identical`. The two states are `tooltip_hover` and `shared_steps_hover`, which are the claim file's two UX-5 annotations.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. The diff contains no `*_budgets.json`.

## Red checks at this head (check-runs API, read at 06:2xZ)

- `mutation` and `mutation-autofix` are named in the body and wait on R9-CI-1 (condition 1).
- `closures` and `closures-autofix` are main's (see above). The body's `closures` paragraph explains the red at 5eaf0982, which this head repairs. It does not explain the new red, which is main's. It should get a one-line update when the body is next re-taken. I am not blocking on it: the check is named, and the red is not this diff's (`defect-root-cause.md`).
- `delivery-status` printed `DELIVERY STATUS UNCHECKED — 69 rowed, 1 pending` for #2029 on main. It is not this PR's.
- `budget-raise-gate` was cancelled; its twin succeeded (condition 3).
- All other checks are green: `fast (3.14)`, `coverage`, `coverage-ratchet`, `browser`, `typing`, `env-matrix`, `pr-contract` x2, `instrument-self-tests`, `hassfest`, `closure-scope`, CodeQL.

## Unpinned-site list: an instrument finding

CI's NOT RUN set and the body's `## Unpinned sites` list (from `ci_predict.py`) agree on 34 of their 35 distinct sites. They differ on one site:
- CI names `optimizer.py:1028 RETURN_DEL`. That is the new `return out` in `_padded`.
- ci_predict and the body name `optimizer.py:4035 RETURN_DEL` instead. That is an old, identical `return out` in `_seed_pinned_guess`, which the diff does not touch.

CI also lists `optimizer.py:1079 CMP_BOUND` three times, because that line has three comparisons. That is why CI counts 37 sites and the body 35. The predictor has a line-attribution fault: it puts an added line on an earlier line with the same text. The body should list 1028 instead of 4035 when it is next re-taken. I did not fix the predictor. This needs carrying to whoever owns `tools/pr/ci_predict.py` (orchestrator).

## Forward-carry and class

The body says `none`. I checked each carry in the brief and found it in the diff:
- UX-1: the tooltip fits.
- UX-4: the comfort event's `cause`, plus the blueprint and `docs/automations.md`. The `cause-none` mutant above pins it.
- EG-B1: the what-if prices the active setback, and the payload publishes the floor the plan used beside the configured one. The `del-fold-equal` mutant and the null controls pin it.

The EG-A4 arch-score carry does not apply: there is no `arch-score` check-run at this head. This is a feature, so there is no class to open.

Evidence: /Users/timmalmstrom/hpo-seats/review-2010/evidence
