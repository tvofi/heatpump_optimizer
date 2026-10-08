Fix review: blocked 04b8b4bda2513490de027e0355a46f570109ef31 root-cause-unanswered: delivery-status went red, unanswered; harness: M7 driven-child refusal unpinned; body cites wrong run and misnames shard 2's red check

bus-nonce: f3f157df49e9a5dfdcbdfdecfbf2c68d

PR #2049 (R9-CI-1), round 1 for this reviewer. Measured head 04b8b4bda2513490de027e0355a46f570109ef31; it was still the live head when this was written (pulls API, 2026-10-08 ~03:55Z). Merge base e2a4f7c6 = origin/main, so there is no resolution delta. dev/governance/roles/ shows no difference between the merge base and origin/main, so the contract in the worktree is current.
Evidence: /Users/timmalmstrom/hpo-seats/review-2049/ev

## Blocking

1. **root-cause-unanswered (step 11).** At the head, `delivery-status` is red (check-run 113131807985: `DELIVERY STATUS UNCHECKED — 68 rowed, 0 pending, 0 overdue`). `pr-contract` is red on it three times (113131801566, 113132030985, 113132492257): "check `delivery-status` is red and `## Red checks` does not name it ... this diff touches what it reads (.github/workflows/tests.yml)". The body's `## Red checks` says `none at the head`. The red itself is not this PR's code. I ran `tests/delivery_status.py` locally at the head and its `merge-collection` skip names 9 of main's merge commits that `subject_number` cannot attribute (e.g. 618d014, 0a60e06, f6ac991), and none is on this branch. The body still has to name it and answer it, and `pr-contract` will stay red until it does.

2. **Unpinned safety line (the answer to dispatch question 1).** RESULT M7: in `apply_under_scoped_recordings`, emptying the line that maps a failed driven child to its driver (`failed |= {f"tests/{DRIVEN_BY_OTHERS[...]}" ...}`) leaves `ALL 2209 ENTITY CHECKS PASSED`. That line is the only thing that refuses when `dst_checks.py` fails to record and `features.py`, whose closure folds the child in, is the script named UNDER-SCOPED. Without it, the child's truncated trace is left out, the driver's own trace merges, and the second `check` runs over the clean subset only, so it passes. The bot then pushes a repair of the very closure the truncation affected. The code is correct today, but no test holds it. Add an `_af_case` with a failed `tests/dst_checks.py` record next to a stale `tests/features.py` that expects `skip-failed-recording`.

3. **Body evidence (steps 7/8).** Two corrections, both mechanical:
   - The body cites `run 37710478042` for #2048's 10-shard result. That run is #2047's (`proof/r9-ci-1-shards3`, head fe2ad3d931). It runs 4 shards with 200-minute budgets and was still in progress when I read it. #2048's run is **37711053129** (head 894e821cd5). Its figures do re-derive exactly from that run's ten shard logs (shard-extracts.txt): 40 pinned, 8 survived, 2 timed out, shard 2 with 6 sites unmeasured, 56 in total; `count=10`; `shards merged: measured`, `AUTOFIX: changed`; 01:04:24 to 02:56:00.
   - Shard 2 was not refused by `a3:roster`. `mutation_table`'s null-control message joins every `FAIL` line of the red run. entities.py prints dozens of negative-control `FAIL` lines on purpose, and `a3:roster [1 registered ... extra=['sensor.not_ours']]` is simply the first of them. The check that actually went red is the last one: `tools/release/stamp.py's --self-test passes [... OSError: [Errno 39] Directory not empty: '/tmp/tmpa46lxjxy/.git/objects/pack']` (shard2-real-red-check.txt). That is a tempdir-cleanup race in stamp.py's self-test. The body's Forward-carry sends the next seat to the wrong check. Name the real check, and name the attribution defect: on entities.py the null-control refusal names a negative control rather than the red check.

## Dispatch questions

(1) closures-autofix can no longer cover a named under-scope, apart from the unpinned M7 line above. A partial `merge` never shrinks a committed closure (`_keep_committed_files`), so leaving out a failed recording drops no committed read. The only residual case is a failed recording of an unnamed script X whose truncation hides X's own under-scope. Before this PR that case was already green on `skip-clean` whenever nothing else was stale (ci-autofix.md's third "green unrepaired" bullet). Now it can also end green on `changed`, and that bullet still names only `skip-clean`. That is a doc gap, not a new hole. There is also an ordering effect: when INERT READS fires, `check` returns before the UNDER-SCOPED comparison, so a failed script's under-scope can only be named on the follow-up run. Closures proofs: runs 37673851552 and 37674068287 each logged `left out 2 failed recording(s) ... tests/entities.py, tests/stress.py` and then `AUTOFIX: changed` (closures-autofix-proofs.txt). I did not re-read the bot commits' contents.

(2) The shard merge cannot lose or duplicate pins in a way that matters. `pin_shard` is disjoint and covering, with twins kept together; RESULT M1 (an overlapping deal) is killed. A shard with no status file, or a malformed one, is skipped or marked `skip-measure-failed`, and its sites stay unpinned. `mutation` re-derives the unpinned count from scratch on the bot commit, so a refused shard (shard 2's 6 sites) cannot turn into a green `mutation`: the next run refuses again and re-plans for the leftovers. RESULT M2 survives: `merge_pin_shards` writing one head when the shards' heads differ goes unnoticed. Within one run that mix cannot happen, because every shard takes `PR_HEAD` from the same event payload and `apply_pins` compares against the branch tip anyway. So M2 is an observation, not a block. RESULT M3 (merged status = the last shard's) is killed.

(3) Pins come from the base program. `git show "$PR_BASE":tests/mutation_table.py` uses `pull_request.base.sha`, and `--shard`/`--budget-minutes` are passed only when the base program has them. `mutation-autofix` still restores `tests/closure.py` and `tests/mutation_table.py` from `base.sha` before it calls `merge_pin_shards`/`apply_pins`, and that restore step is unchanged. `mutation-pin-plan` runs the head's `pin_shard_count` in a read-only job. A PR can change only how many runners it gets, which can leave fewer sites pinned (mutation stays red) but never add one. As before this PR, the drivers and `measurement()` are head code. That trust model is unchanged and documented in the job comment.

(4) The bot identity and token are untouched. No hunk reaches either autofix job's checkout token, permissions or commit identity. The new `mutation-pin-plan` and `mutation-pins` jobs declare no `permissions`, so they inherit the workflow default `contents: read`, and they reference no secret. The entities check asserts `contents: write` appears in neither `mutation` nor `mutation-pins`.

(5) `record-autofix` is untouched. Every tests.yml hunk ends by new line 2632, and `record-autofix:` sits at line 2853.

(6) ci-autofix.md: `policy_lint.mjs` reports `TOTAL: 0 error(s) across 40 policy file(s)`, `rules_sync.mjs --check` reports ok, and `policy-docs` is green at the head. It does not contradict fixer.md, whose line 21 defers to ci-autofix.md for when `--pin-killed` runs, nor nudge.md line 85. Two small gaps, not blocking: the frontmatter description and the Failure table still list only `UNDER-SCOPED` for closures-autofix, not INERT READS; and the third green-unrepaired bullet still names only `skip-clean` (see (1)).

(7) The shard-2 kill is not this PR's. The check that went red is the stamp.py self-test, not a3:roster (see blocking item 3). Neither stamp.py nor that check is in the diff. The nine other shards drove the same null control and it survived, so this is a flake under load.

## RESULT lines (reviewer's own mutants, harness ev/mutants/run.sh, tests/entities.py with PYTHONPATH=tests/hastub, seat venv-ci python)

- RESULT baseline head: ALL 2209 ENTITY CHECKS PASSED (rc 0, 166 s)
- RESULT M1 pin_shard deals overlapping (`<=`): KILLED, "the pin shards are disjoint..."
- RESULT M2 merge_pin_shards keeps one head when heads differ: SURVIVED (unreachable within one run; observation)
- RESULT M3 merge status = last shard's: KILLED, same check
- RESULT M4 pin_shard_count floor division: KILLED, "the pin shard count scales..." (counts=[1,1,1,9,10])
- RESULT M5 survivor remedy printed whenever left: KILLED, "the pin summary counts budget cuts..."
- RESULT M6 stale_scripts ignores INERT READS entries: KILLED, "an INERT READS under-approximation is merged by the bot..."
- RESULT M7 driven-child to driver mapping emptied: **SURVIVED** (blocking item 2)
- RESULT M8 drive_pin_pool tail-deadline check off: KILLED, "the split admits a mutant on its shared work..."

The fixer's mutants A–H were not re-run one by one. M1/M3–M6/M8 cover the same functions with different operators.

## CI at the head (check-runs API, two reads about 30 min apart)

`mutation` succeeded, so `mutation-pin-plan`, `mutation-pins` and `mutation-autofix` were all skipped at the head. The new sharded jobs did not run on this PR's own diff, and their only evidence is the proof runs. Green: briefs, typing, closure-scope, instrument-self-tests, policy-docs, wave-script, hassfest, validate-hacs, budget-raise-gate, nightly-status, CodeQL analyses (CodeQL itself neutral). Red: pr-contract and delivery-status (item 1). One budget-raise-gate twin was cancelled while the other succeeded. Still in progress at my second read: closures, fast (3.14), coverage. Not re-run locally (heavy-scripts rule).

Local at the head: `STRUCTURE RATCHET PASSED`; policy_lint 0 errors; RULES-SYNC ok; entities 2209/2209. `VERSION`, the manifest version, RELEASE_NOTES.md, both claim files and every `*budgets.json` are untouched (three-dot diff is empty).

## Not verified

- The autofix census figures (116 jobs, 63 statuses read, 53 logs unavailable; 14 manual-repair-owed, all INERT READS; 6 of 9 failed recordings not stale). Re-deriving them takes about 300+ API calls, which the 2026-10-07 pacing directive rules out. I have not confirmed them.
- The ~4069 s first-site estimate. The body itself calls it an estimate.

## Non-blocking observations

- `tools/audit/seat/autofix_statuses.sh` makes one unpaced `gh api` call per run (up to 300) and re-fetches the closures job list for every closures-autofix row. The 2026-10-07 directive asks bulk reads to be paced at least 1 s apart and cached. Add a `sleep 1` and cache the jobs list per run.
- The Forward-carry "follow-up" items live only in the PR body (finding-propagation.md). After correcting item 3, say where the stamp.py self-test flake and the null-control attribution defect are carried.
