record: RCA for the orphaned-handoff class (N-orphaned-handoff)

Class `N-orphaned-handoff`, round 10. One root-cause record, `dev/audit/rca/N-orphaned-handoff.md`, and its citation in `dev/audit/config/bugclasses.json`: the class's `rca` list now names it beside `R9-ORPHAN-HANDOFF`, with an `_rca` entry of level `class`, status `proposed`, as `defect-root-cause.md`'s "Where it is recorded" requires and as the round's earlier RCA records landed (`3f172871c`). No code, policy or roster change.

The record carries `root-cause.md`'s four products:

- **Named cause** (§1): the relay's `handoff-no-pr` level is replayed as append-only history — `orchestrator_tick.py`'s `relay_owed` keys an OWED row on `f[2]`, the kind token, while a POSTED row keys on a PR number, so nothing clears it; a detector arm read its own finding (`bus.sh orphans` exit 1) as unavailability; and an obligation had no age and no closer.
- **Process state** (§3): (c), with the `orchestrator.md` §5b duty quoted and `SEATS.md` lines showing it was read and queued and two openers dispatched and killed; residuals (a) for the design-to-build kind and (d) for a brief that grew after its handoff, kept separate.
- **Cost test** (§4): 1.65–2.4 h per round against 5.13 measured seat-hours × P = 1.0.
- **Countermeasure** (§5): a barrier, not a refusal. The class is an audit class — `bugclasses.json` records 7 instances in R9, and the record counts 11 genuine in R10 — so `defect-root-cause.md` says it owes a class-eliminating barrier and the cost test only picks its form. The form is the obligations ledger's `handoff-no-pr` kind, derived each pass, aged, with an opener-attempt record, a content-covered close and a `design-build` kind. Its build and its red/green demonstration belong to `R10-ORCH-MACHINERY`, whose roster brief already carries it.

This pass re-measured the record at current main (new §2a) and corrected one figure: the median age of the four genuine aged refs is 45.9 h, not 47.5 h (the median of four is the mean of the middle two). The demonstration now says that its prototype is not in the tree. §7 names where each part lands.

The opener was refused by prepr's pr-body check because `## Forward-carry` named the design file, which is not in the tree. Re-run at the merged head, the same check also refused the stale `## Head`. Both are answered here.

## Head

81514b55c9f3127c1916c7684c5dd6c840371ac0 (origin/main 0cc148b2f80fe224ffe2c504b29fd4f0908183df merged in at 70643e3d1; figures re-taken 2026-10-21T08:54Z)

## Mutation proof

n/a: no production line or check changes. The diff is one record and one register citation. `fold_ledger.py check` is the register's reader, and it reads the new entry: its rca-entry count went from 113 at the merge base to 114 at the head, with 0 violations at both.

## Null control

The re-measurement's null control is §2a. `gh api 'repos/tvofi/heatpump_optimizer/pulls?state=all&head=tvofi:fix/<topic>'` returns `[]` for the three refs still stranded. The same command returns PR #2521 for `r10-i5-docs` and PR #2513 for `r10-roster-ops`, so the empty answers are not the query failing. `bus.sh orphans` no longer lists `r10-i5-docs` now that a fix head carries it. `git cherry` prints `-` (equivalent) for earlycutoff's one commit, and a ref with no equivalent on main prints `+`.

## Figures

All at origin/main `0cc148b2f`, 2026-10-21T08:54Z, unless the record dates them. The record's §2 and §4 figures read the orchestrator host's `tick.txt`, `tick.log`, `cloud-relay.log` and `SEATS.md`. None of those exists in this container, so they stand as that seat measured them at 18:00–18:18Z on 2026-10-20 and were not re-taken here.

- 11 stranded, 1 superseded; three of §2's five aged refs still stranded (`r10-earlycutoff-coverage`, `r10-merge-pr-mandate`, `r10-rca-harness-friction`) and this record's own ref listed: `bash tools/audit/seat/bus.sh orphans --min-age-h 0`
- no pull request at `fix/<topic>` or `fix/<topic>-pr` for those three; #2521 and #2513 for the other two: `gh api 'repos/tvofi/heatpump_optimizer/pulls?state=all&head=tvofi:fix/<topic>'`
- earlycutoff's one commit is equivalent on main: `git cherry origin/main origin/handoff/r10-earlycutoff-coverage`
- #2397 closed (merged) 2026-10-18T13:53:10Z from `fix/r10-test-orphans`: `gh api repos/tvofi/heatpump_optimizer/pulls/2397`
- `relay_owed` keys OWED on `f[2]` and POSTED on the PR number; the relay writes `OWED <utc> handoff-no-pr <ref> <sha>`: `grep -n 'def relay_owed' -A25 tools/audit/seat/orchestrator_tick.py` and `grep -n 'handoff-no-pr' tools/audit/seat/cloud_relay.sh`
- `content_superseded`'s M arm compares blob ids, so a hunk re-applied into a changed file reads stranded: `grep -n 'content_superseded()' -A12 tools/audit/seat/bus.sh`
- 5.13 seat-hours: `grep -n '5\.13' dev/audit/rca/R9-ORPHAN-HANDOFF.md`
- R9 per-round count 7, barrier null: `python3 -c "import json;e=json.load(open('dev/audit/config/bugclasses.json'))['N-orphaned-handoff'];print(e['per_round'],e['barrier'])"`
- 45.9 h median, 2.4 h and 1.65 h per round, 1,327 lines of growth: arithmetic on the record's own figures, `python3 -c "a=sorted([41.9,44.3,47.5,48.9]);print((a[1]+a[2])/2, 5*12*144/3600, 5*8.25*144/3600, 31303-29976)"`
- register: 0 violations, 114 rca entries (113 at the merge base): `python3 tools/audit/fold_ledger.py check`
- gate: `MODE: SCOPED -- 0 script(s) run`: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`; run_always green (`env_drift.py --claims-only`, `closure.py selftest`, `layout.py`, `harness_headers.py`); `tests/entities.py` (under `env -u BASH_ENV`) and `tests/structure.py` pass

## Red checks

`nightly-status`: main's, not this branch's. The diff touches nothing it reads. Its red is the replay lane's `loop_cpu_ratio` over its budget in `tests/replay.py`'s cost budgets, which roster group R10-REPLAY-CAP owns. No other check has run on a commit of this branch.

## Forward-carry

- The ledger extension in §5.1–§5.4 and §5.6 (age and escalation, the opener-attempt record, the content-covered close, the availability contract) and §5.5's `design-build` kind are already in `R10-ORCH-MACHINERY`'s brief ("Ledger extension owed") in `dev/programme/rosters/wave-r10-groups.json` at `handoff/audit-r10-roster` `a691012e5`. That build owes the barrier's red/green demonstration, which the record's scratch prototype cannot give. Carry: R10-ORCH-MACHINERY
- §3's (d) observation is that a brief grew 41 h after its handoff. The countermeasure is to pin the brief at handoff and compare it on a later pass, which is the §6.4 roster-sync step. It is not yet in `R10-ROSTER-OPS`'s brief in `dev/programme/rosters/wave-r10-groups.json` at `a691012e5`, and the roster is the orchestrator's to write. Carry: R10-ROSTER-OPS
- §1's first cause, the board replaying level lines as history, is the live defect `R10-TICK-OWED-LEVEL`'s brief in `dev/programme/rosters/wave-r10-groups.json` states. Its grammar must agree with the ledger's when that lands. Carry: R10-TICK-OWED-LEVEL

## Friction

- `tools/audit/seat/cloud-setup.sh`: cost: the payload said the venv was on PATH, but this harness's shell sources no login profile. `python3` was 3.11, `tests/entities.py` failed with an f-string `SyntaxError`, and the run passed only under `/opt/hpo/venv-ci/bin/python` from `/etc/profile.d/hpo-toolchain.sh`. Carry: dismissed: one rerun, the profile already names the interpreter

🤖 Generated with [Claude Code](https://claude.com/claude-code) https://claude.ai/code/session_01EA1pBSuvaFQrFWtfyz96Y4
