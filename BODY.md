This is the root-cause seat for R10-RCA-ROSTER-DRAIN-REPLAY, run beside R10-HOTFIX-ROSTER-DRAIN-REPLAY and never inside it. It names the cause, process state **(d)**, the cost test, and a countermeasure built here. The analysis is `dev/audit/rca/r10-rca-roster-drain-replay.md`, and its `_rca` entry is in `dev/audit/config/bugclasses.json`. `beat_jobs.py` and `beatd.jobs.json` are untouched; they belong to the hotfix.

**Cause:**
- The beat's drain runs each queue line at least once. A pass killed at `timeout_s` 900 had pushed its ops but never written `roster-done.json`, so the next pass re-ran them.
- `drop-carry <group> <index>` resolves its index again on every run. Each replay therefore deleted whatever entry had shifted into that index.

**Why the index form exists:** `9969e3ca8` (2026-10-18, #2513) added it for a caller that runs an op once. That caller is a human who has just read `jq '.carry[N]'`. Nothing ran a queue automatically until #3197 on 2026-11-05.

**Countermeasure:** `roster_queue.replay_unsafe` refuses `drop-carry` and `mark-carry` without `--match` on both run paths, before the editor runs. The report line says `refused rc=2 ... key it --match TEXT`, and the queue line is marked `#refused`. A hand run of `roster_edit.py` keeps the index form.

## Head

`f4fecc828bca91b403cf9395f2b00fa28a713c03`, on `origin/main` `5d09dedf69eb9fe9bcab6bd9e5ddbde04a387ecb` (2026-11-10). The roster history was read on `origin/handoff/audit-r10-roster` at `c444a6995`.

## Mutation proof

`python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py mutants` plants each mutant in a copy of `tools/` and runs `roster_queue.py --self-test` there. The baseline copy passes. Each mutant fails the checks listed:

- M1, the predicate never refuses: `run: drop-carry and mark-carry by index are refused and marked, never pushed` and `run --batch: drop-carry by index is refused before the batch, and marked`.
- M2, the single-op path skips the check: `run: drop-carry and mark-carry by index are refused and marked, never pushed`.
- M3, the batch path skips the check: `run --batch: drop-carry by index is refused before the batch, and marked`.
- M4, `mark-carry` is left out of the predicate: `run: drop-carry and mark-carry by index are refused and marked, never pushed`.

## Unpinned sites

`replay_unsafe`'s predicate and its two call sites in `tools/audit/seat/roster_queue.py` are pinned by the in-tree mutant harness `dev/audit/harnesses/r10_rca_roster_drain_replay.py mutants`, which kills all 4. `mutation-autofix` mutates `custom_components/` only, so it does not reach these sites.

## Null control

- **The unmodified op replays destructively.** `replay` applies `drop-carry G 1` twice to a five-entry fixture through `roster_edit.apply_op`. Both runs apply, and two entries are removed.
- **The `--match` form is the control.** Run twice, it removes one entry, and the replay refuses with `no carry entry matches`.
- **The check does not fire on replay-safe lines.** The `--match` forms of `drop-carry` and `mark-carry` print `runs`. The self-test's `drop-carry G --match one` line is pushed.
- **The census rule is checked independently.** The orchestrator's hand restorations are the control: they restored 14 of the 18 rule-replays and none of the 14 first drops (`firsts_restored=0`).

## Figures

- `python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py replay`: index form `removed=2`, `--match` form `removed=1`. Both index lines are refused by the check, and both `--match` lines run.
- `python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py census 43495fb61 c444a6995`: `drops=32 replays=18 replays_restored=14 replays_unrestored=4 firsts=14 firsts_restored=0`.
  - The rule: a drop is a replay when an earlier drop in the window removed an entry at the same (group, index).
  - The 4 unrestored drops are in R10-HOTFIX-GATE-BUSY-DEFER: `6027d13ff`, `76d95c36a`, `c7c424169`, `dfbc636b9`.
  - Pair replays fall 13 to 15 minutes apart (the `PAIR` lines).
  - 8 of the 14 first index drops were replayed at least once: 8 is the count of `PAIR` lines, 14 is `firsts`.
- `python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py contained c444a6995`: `entries=1690 contained_in_a_sibling=23`.
  - These are entries whose full text also sits inside a sibling entry of the same group. `--match` cannot name them, so only a hand run by index can.
  - The same arm at `5d09dedf6` prints `entries=1337 contained_in_a_sibling=24`.
- `python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py cost`: the check's per-line cost in µs, over 100000 calls. It reads below one microsecond.
- `python3 -I dev/audit/harnesses/r10_rca_roster_drain_replay.py mutants`: `mutants=4 killed=4`.
- `python3 tools/audit/seat/roster_queue.py --self-test`: `65 checks, 0 failed`. Three of those checks are new.
- Cost test, from section 5 of the RCA doc:
  - The defect costs at least 600 s per occurrence. That is the restoration commits `54f325471` (09:35) to `e4ab4a9f8` (09:45), and it leaves out the 4 losses nobody noticed.
  - The countermeasure costs under 1 µs per line, plus at most one 120 s `interval_s` requeue per index line written.
  - It breaks even once P(an index line is replayed) exceeds 0.2. In this incident that rate was 8/14. **Passes.**
- Class search: `Grep` for `(drop|mark)-carry +<group> +<index>` over the tree, JSON excluded.
  - Outside this diff it returns only the usage lines of `roster_edit.py` and `instruments/roster_edit.py.md`.
  - Each other runner that applies first and records afterwards is dispositioned in the RCA doc, section 4: closed here, already guarded, or the hotfix's.
- Scope: `python3 tests/closure.py select --diff 5d09dedf69eb9fe9bcab6bd9e5ddbde04a387ecb` prints `MODE: SCOPED -- 0 script(s) run`.
- Ratchet: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

- **Restore four lost carries.** R10-HOTFIX-GATE-BUSY-DEFER (stage `done`) lost four carries to replays that nobody restored: `6027d13ff`, `76d95c36a`, `c7c424169`, `dfbc636b9`. `76d95c36a` removed the item-453f6578 carry that `83ba995b6` had marked implemented. They are recovered from each commit's parent with `git show <sha>^:dev/programme/rosters/wave-r10-groups.json`, and re-appended with `roster_edit.py append-carry`. Carry: R10-TICK-RESIDUE
- **Correct carry[11]'s premise.** R10-TICK-RESIDUE carry[11] judged the drain's replay harmless because "the ops come back as refusals". That premise is false for `drop-carry` and `mark-carry` by index: the census above counts 18 destructive replays. A queue now refuses those forms, so a carry, brief or orchestrator note that writes a queued carry op must key it `--match TEXT`, and an entry inside a sibling's text (the `contained` arm) is edited by hand, once. Carry: R10-TICK-RESIDUE

## Friction

none
