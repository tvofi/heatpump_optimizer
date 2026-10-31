Shards the nightly ledger drain four ways (triage s6-batch16 P85), and settles the four carries on the group: mutation-autofix reddens on a survivor, the `ci-autofix.md` contradiction, the #2840 measure-first item, and R10-PIN-DRIVE-INCONCLUSIVE.

**Owner approval owed:** `dev/governance/rules/ci-autofix.md` (and its generated `.claude/`, `.cursor/` copies) changes what a seat does on a red `mutation-autofix`; it is policy.

## Head

`d1afdcf872cb24b059c000e9c16d7f550324cc61` (origin/main 7539d1675 merged in; no later main at 2026-10-31T16:30:31Z).

## Mutation proof

Each mutant run with `PYTHONPATH=tests/hastub python3 tests/entities.py` in its own worktree:
- `drain_pool`: `cap *= shard[1]` deleted -> red: "--drain --shard K/N: the shards are disjoint whole-anchor slices whose union is the unsharded slice ...".
- `merge_pin_shards`: the survivor union replaced by the last shard's list -> red: that check and "the survivors are written by each pin shard, merged as a union ...".
- `closure.autofix_survivors_owed`: graded statuses emptied -> red: "mutation-autofix is red on an applied measurement that left a site alive, naming each ...".
Not mutated: the PIN-DRIVE-INCONCLUSIVE wiring check (below).

## Null control

Shards: `drain_pool` unsharded at the same total cap is the control; the union of the three shards equals it site for site, no anchor is in two shards, and seed 8 draws a different slice. Autofix: `changed` with no survivors and `skip-head-moved` with survivors stay green (`0`), per the carry's acceptance; `skip-not-allowed` stays quiet too.

## Figures

- Entities run on this tree before the merge: `1 of 2497 ENTITY CHECKS FAILED`, the one failure "the template arm turns the acceptance red ... the real template -> rc=1", a check outside this diff; the mutant runs show the same failure besides their own. `PYTHONPATH=tests/hastub python3 tests/entities.py`. Not re-measured at origin/main.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/policy_lint.mjs --budgets`: ci-autofix.md 91 lines, 1466 tokens, cap 96 / 1469.
- `tools/pr/prepr.sh` at d1afdcf87: `PRE-PR: ... rc=0`. Gate mode: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (workflow files change the gate), so CI runs the suite.
- Nothing about the sharded night itself is measured here; the cron fires after merge.

## Red checks

none

## Forward-carry

The controls the brief sets for the first sharded scheduled night stay open and are the orchestrator's to read from that run: its `created_at`; each shard's drawn and evaluated counts, minutes per mutant, timed-out count and partial flag; the merged kill and survivor counts; the push's landing time; all against run 40054585693 (40 in 146 min, `--jobs 3`, created 02:32:21Z). Step rules: shards clip -> `--max 70`; timeouts above baseline or a CPU-bounded harness refused -> `--jobs 3 --max 65`; kills under a quarter of the draw three nights running -> one shard. They are in this group's roster brief, `dev/programme/rosters/wave-r10-groups.json` R10-FLY-LEDGER-SAMPLE. Carry: R10-FLY-LEDGER-SAMPLE

## Friction

R10-PIN-DRIVE-INCONCLUSIVE: stale: not reproduced at head. A scratch worktree at origin/main with `tests/doc_claims.py` forced red and a probe site added ran `mutation_table.py --pin-killed --base HEAD~1 --scripts tests/doc_claims.py,tests/typing_ruler.py --jobs 2`: it printed `MUTATION TABLE INCONCLUSIVE`, rc=0, and no `PIN KILLED:` summary or `lives` line, because main() returns `verdicts.stop` before `pin_results` (since 5b633a7a2, 2026-10-01). The #2712 report of "5 survived" after INCONCLUSIVE is not explained by this code; a check now pins the order and that `LazyBaselines` scores a post-stop red run as no kill. Carry: R10-FLY-LEDGER-SAMPLE
R10-RCA-MUTATION-SURVIVOR: contradiction: ci-autofix.md said to act when mutation-autofix went red while `AUTOFIX_QUIET` kept it green on every survivor path; fixed here. Carry: R10-FLY-LEDGER-SAMPLE

## #2840 measure-first carry

The key counts four PRs (`dev/audit/rca/R10-RCA-MUTATION-SURVIVOR.md` section 1, re-derived from `policy_lint.mjs --stats --since v7.0.4`): #2579 (`tools/audit/seat/review_strength.py` hand mutants), #2820 (`tools/policy/friction_issues.mjs`), #2817 (`coordinator.py:6303`, `6331 GUARD_OFF`), #2912 (`config_flow.py:3490 RETURN_DEL`, equivalent). #2817 and #2912 share one cause, in the autofix status vocabulary (green on a survivor), not `--pin-killed`: fixed here. #2579 and #2820 are `tools/` hand mutants outside `--pin-killed`'s reach with no shared cause: recorded refusal, no tooling built (ci-autofix.md forbids automating survivor triage).

## Alternatives

Encoding survivors in the status string was refused: the push step keys on `changed`, and an unknown status prints "the repair did not happen". The report reads `AUTOFIX_SURVIVORS` from the environment rather than a flag because the job runs the base's `closure.py`. Reddening on every "left unpinned" was refused: budget-cut sites are a later run's.

## Approval

Owed, not given. `dev/governance/rules/ci-autofix.md` changes what a seat does on a red `mutation-autofix`; it needs `@tvofi`'s approving review at the head before merge (CLAUDE.md, 0009 step 6). The brief carries it as countermeasure C of R10-RCA-MUTATION-SURVIVOR, section 7, but no approval has been recorded for this text.

## Carries

Carry 1: R10-PIN-DRIVE-INCONCLUSIVE: not reproduced at head; ordering pinned by a new entities check (see Friction).
Carry 2: #2840 measure-first: four PRs named, #2817/#2912 share the status-vocabulary cause and are fixed; #2579/#2820 refused with evidence (see the #2840 section).
Carry 3: mutation-autofix reddens on an applied measurement that left an added site alive, naming each; acceptance checked in tests/entities.py (red on 2 left alive, green on none, quiet on skip-head-moved).
Carry 4: the roster carry landed on handoff/audit-r10-roster at edd149d14 before this work; this PR delivers what it records.
Carry 5: `.claude/rules/ci-autofix.md` (generated from dev/governance/rules/ci-autofix.md) now states the survivor path as red; the contradiction is gone.
