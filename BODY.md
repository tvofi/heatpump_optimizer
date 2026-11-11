R10-FIXER-MD-SPELLING-CORPUS continuation (p2): the owner's measure-first on making the diff's mutation survivors the fixer's own. Measured at merge base origin/main a7628041 (2026-11-11T05:52:35Z). **Policy change**: `dev/governance/roles/fixer.md` step 2 changes what a fixer must do before the handoff; it needs the owner's approving review (no generated rule copy of fixer.md exists: `git ls-files | grep -i fixer`).

Outcome: **arm (a) landed, arm (b) refused.**
- (b) does not pay: diff mode reproduces 5 of the 36 mutation-vacuous blocks in the window (at most 7 with the two it could not run), fewer than half, so by the coverage term the prepr refusal does not pay whatever the wall time.
- (a) pays on the owner's 10-diff cost test: 1632 s of added diff-mutant time against the reproduced block's repair (3405: 18.66 h block-to-next-verdict, 2.62 h of the fixer's own repair commits).
- Built in this group's seam: prepr step 6d' printed `ok "no survivor"` when `mutant_run.py` measured nothing (rc 3 `BASELINE FAILS`, a killed NULL, rc 2 refusal), so a MUTANT_CMD failing on the unedited tree read as a clean run. In this measurement, 3 of the 5 runnable fixer diffs failed baseline in the default `git archive` copy (3379, 3417, 3405). The step is now `mutants_line`, refuses a run that measured nothing, and `MUTANT_IN_PLACE=1` adds `--in-place` for a self-test needing a checkout. Survivors stay a WARN; MUTANT_CMD unset still skips.

The group's carries, by the review packet's ordinals:
- Carry 1 (the owner's measure-first, arms (a) and (b)): measured. (a) is landed; (b) is refused, with both cost-test numbers under `## Figures`.
- Carry 2 (the coverage term): measured. Reproduced against total, as sets, is under `## Figures`.
- Carry 3 and Carry 7 (R10-ROUND-PLAYBOOK-FINAL's reflection of the fixer.md sentence): not acted on. The playbook file is out of tree, and they stay pending the orchestrator's ruling.
- Carry 4 and Carry 5 (#3397's items c2bbe67f and a629d56d): dismissed on the roster as duplicates of Carry 6 and Carry 7. Not acted on.
- Carry 6 (carries 1 and 2 not measured in #3397): discharged by this pull request's measurement.

## Head

`ecf3c51cd2ab43ca79bf30cb74cda05ade25c14b` (worktree from origin/main a7628041; no merge since).

## Mutation proof

prepr's self-test, which drives `mutants_line` over a throwaway repo, at the head and with each reviewer-style mutant applied (`python3 -I tools/audit/seat/mutant_run.py --spec <spec> --cmd "bash tools/pr/prepr.sh --self-test" --in-place`; the four `{name, file, old, new}` entries are below):

```
SURVIVED NULL
KILLED rc_check_off
KILLED flow_drops_cmd
KILLED in_place_dropped
KILLED survivor_reads_ok
```
(rc 0, 30 min; `tools/pr/prepr.sh` is byte-identical at the head and at the commit measured, `git diff --quiet f06a7376d1d0 HEAD -- tools/pr/prepr.sh` exits 0, the proof run at f06a7376d1d0.)

- `rc_check_off`: `if [ "$r" -ne 0 ]; then` → `if false; then` (the fail-open restored).
- `flow_drops_cmd`: the main flow passes `""` for MUTANT_CMD.
- `in_place_dropped`: `${MUTANT_IN_PLACE:+--in-place}` deleted.
- `survivor_reads_ok`: `if [ "$n" -gt 0 ]` → `if false`.

The same `rc_check_off` edit, applied by hand: `prepr.sh --self-test` goes from `524 passed, 0 failed` to `522 passed, 2 failed` with
`FAIL a MUTANT_CMD failing on the unedited tree is refused, never read as no survivor (got 0, wanted 1)` and `FAIL and the refusal quotes mutant_run's own reason (got 0, wanted 1)`.

## Null control

- prepr: `mutants_line` passes a check killing every mutant (`ok a check killing every mutant of the added lines passes (null control)`). It skips with MUTANT_CMD unset (`ok MUTANT_CMD unset skips`), so a fixer who never sets it sees today's behaviour.
- Coverage term, a merged head with no block: `bash dev/audit/harnesses/r10_mutant_coverage.sh run c620ebba^1 c620ebba^2 "bash -c 'python3 -I tools/audit/seat/orchestrator_tick.py --self-test && python3 -I tools/audit/seat/cloud_dispatch.py --self-test'"` (#3384, merged on its first verdict). It reports 2 survivors, `orchestrator_tick.py:3987` and `:3994` CONST_SWAP. Both are inside `def self_test()` (top-level def at :2726): fixture lines, none a reviewer would name.

## Figures

Instrument: `dev/audit/harnesses/r10_mutant_coverage.sh` (this PR; `fetch` first). Window: `2026-11-04T06:52:35+01:00..2026-11-11T06:52:35+01:00`, the 7 days before the merge base.

**Coverage term (Carry 2).** Rule: a block is a (PR, head) pair with a `Fix review: blocked <sha> mutation-vacuous:` verdict on `review/*` or `verdict/*`. It is **reproduced** when `mutant_run.py --diff <base>...<head>` reports a SURVIVED mutant on a line the verdict names, capped at 40 and run under the group's self-test (the `--self-test` of each file among the first 40 mutants, or the section's `features_block.py` call). `<base>` is `harness base <head> <verdict time>`.
- `harness blocks <window> mutation-vacuous | wc -l` → **36**. `review/*` alone gives 35: `review/3419` no longer holds its block, `verdict/3419` does.
- **Reproduced (5)**: {3248@c8c50b9f ledger.py:296, 3252@69aa9cd3 orchestrator_tick.py:1038, 3260@2fa354bf carry_audit.py:927 and :956, 3337@d0db3e30 roster_queue.py:335, :349 and :376, 3425@779c9432 orchestrator_tick.py:1220} (`harness run <base> <head> "<self-tests>"` per block).
- **Undetermined (2)**: {3184@913e74e8 freq_control.py:228, listed at rank 4, but no features block for it, and the reviewer's own run has GUARD_OFF surviving every suite check; 3232@6e048afc coordinator.py:2038/:2043, ranks 14 and 16, but the section's block needs earlier sections' state (`_g511_coord`), so only `--through` runs it, i.e. most of features.py per mutant}.
- **Not reproduced (29)**:
  - No named survivor on an added `.py` line outside `tests/` and `dev/`, which is diff mode's whole domain (9): {3217 mjs, 3219 tests/replay.py, 3221 prepr.sh/body_push.sh, 3243 tests/gate_lock.py, 3249 bus.sh, 3263 tests/nightly_status.py, 3275@d6482b70 bg_wait shell, 3275@a09ebaeb governance.yml, 3431 tests/harness.py}.
  - Named line where diff mode draws no mutant, `harness rank` → `none` (10): {3193, 3231, 3232@bba5b4d4, 3241, 3246, 3265, 3297, 3341, 3344, 3428}.
  - Listed only past the cap of 40 (5): {3262@48acc104 rank 111, 3262@3189559b 53, 3262@0fd9bc6d 76, 3262@aa5022f6 362, 3419@245ddf78 51}.
  - Listed within the cap, but the group self-test kills it (4): {3262@c95c3b4b, 3264, 3326, 3427}.
  - The group self-test fails its own baseline in this seat, in the archive copy and in place (1): {3301, `ci_predict.py --self-test` 4 failed}.
- **5 reproduced of 36** (at most 7): fewer than half, so (b) is refused.
- MUTANT_CMD set at the handoff: {3326@8f073db7, 3344@1a1da73c}, 2 of 36. Rule: a `handoff-body/<topic>` commit dated at or before the verdict quotes MUTANT_CMD with a value (`git log refs/heads/handoff-body/<topic>`, `git show <c>:BODY.md | grep MUTANT_CMD`). Where no handoff body cites the head (3217, 3219, 3248, 3260, 3425, 3428, 3431), the rule is no hit in `gh api -X GET search/issues -f q='repo:tvofi/heatpump_optimizer is:pr MUTANT_CMD'` or the `"mutant_run.py --diff"` search. Of these, only 3431 hits, and its diff has no mutable line. Neither set head reproduced, so the step being run is no proxy for the survivor being caught.

**Cost test (Carry 1) over the last 10 merged fixer diffs** before the merge base (`git log --first-parent a7628041`, `fix/` merges: #3419, #3379, #3429, #3426, #3389, #3392, #3384, #3405, #3383, #3417). Each is run `harness run <m>^1 <m>^2 "<self-tests>" [in-place]`, cap 40:
- #3419: 192.7 s, copy.
- #3379: 263.5 s, in place; it failed baseline in the copy.
- #3384: 59.1 s.
- #3405: 660.6 s, in place, with the features block and its four preludes; it failed baseline in the copy and without the preludes.
- #3417: 456.1 s, in place, without `ci_predict.py`, which fails its own self-test here.
- #3429, #3426, #3389, #3392, #3383: 0 mutable lines (`--list` empty), 0 s.
- **Added time: 1632 s (0.45 h)**. This is an upper bound: #3405 and #3417 ran beside a prepr self-test on 4 cores.
- Repair: the mutation-vacuous or mutation-survivors blocks on these PRs (`harness blocks <window> 'mutation-vacuous|mutation-survivors'` restricted to the 10):
  - 3419@245ddf78: 15.96 h (`harness repair`). Not reproduced: its `.py` survivor ranks 51, and the other is in governance.yml.
  - 3405@38e3d17e (`tests / mutation` red): 18.66 h. Reproduced: at the blocked head, diff mode reports the reviewer's 260, 276, 922, 926 and 953 among 14 survivors (658 s). 997, 1000 and 1022 rank 50, none and 63.
- **Saving counted (reproduced only): 18.66 h round, or 2.62 h block-to-last-repair-commit** (`git log 38e3d17e..4a927eed`, 05:50:29Z → 08:27:53Z). Both exceed 0.45 h, so (a) pays.
- Window view, for the reviewer: the reproduced blocks' repair hours are 3248 2.10, 3252 4.34, 3260 3.10, 3337 4.59, and 3425 still open at the merge base (`harness repair`). `flow_metrics.py --window 2026-11-04T05:52..2026-11-11T05:52 --roster origin/main:dev/programme/rosters/wave-r10-groups.json --prefix R10-` gives first-pass yield 87/188. `flow_metrics.py` has no per-PR repair-hours output, so repair hours come from the bus.
- Two heavy self-tests show that one diff can cost far more than this sample's mean: 3262@c95c3b4b took 1349 s and 3326@8f073db7 took 2320 s under the cap.
- Policy corpus: `node tools/policy/policy_lint.mjs --budgets` goes from `~68671` to `~68667` tokens, and `tools/audit/briefs/fixer.md` (fixer.md's budget row) from 315 to 314 lines against its cap of 315. role fixer stays at `~6265`, flat. Paid by cutting `Compare three-dot (CLAUDE.md rule 3)` and fixer.md's restatement of `defect-root-cause.md`'s Enforcement (`name each red in owed-reds' set ... none exists`, `You name the trigger; analysing it is root-cause.md's seat`). That rule file loads with fixer.md and states both.
- `bash tools/pr/prepr.sh --self-test`: `524 passed, 0 failed` at the head.
- `bash tools/pr/prepr.sh <this body>`: `PRE-PR: ecf3c51cd2ab43ca79bf30cb74cda05ade25c14b 000000000000000000000000000000 rc=0` against origin/main a7628041 (`date -u`: 2026-11-11). Mode line: the diff touches `tests/closures.json`, so `closures` skips ("CI re-records every closure").

## Approval

Pending: the owner's approving review of `dev/governance/roles/fixer.md` (step 2's new duty, and the three cut restatements). Requested, not yet given.

## Red checks

none

## Unpinned sites

none: the diff adds no Python production line (`prepr.sh`, a harness under `dev/`, markdown).

## Forward-carry

- Diff mode's domain (added `.py` lines outside `tests/` and `dev/`, the first 40 mutants) missed 24 of the 36 blocks. That limit is stated in fixer.md step 2 itself, the destination every fixer reads. Carry: dismissed: landed in this PR's fixer.md sentence.

## Friction

none
