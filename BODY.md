Triage batch 69 rules item 4 of batch 68's owed list (orchestrator s8, 2026-10-30): P63's seat generation token was left on R10-ORCH-BEATD, which is `done` on the roster branch (#2916, arm (a) only). It also rules the orchestrator's queue lines 15 and 16 (2026-10-30T09:49Z, 09:54Z). It is the next rolling batch under V182, after batch 68 (#2985). It holds three rulings and three held roster ops.

- **P301: DEFER, recorded as a drop from R10-ORCH-BEATD.** P63 (`seat_gen.py bump|check`) is not re-routed.
  - The harm P63 guards is a superseded seat writing through a tracked writer: roster apply, `bus.sh` dispatch or the train queue. It has not recurred since 2026-10-24. Over `seat-ledger.md` lines 1100-2471, the one duplicate seat is the 2026-10-27 plain HOLD triage writer (P204). It read no brief, so a token would not have bound it.
  - Three things cover the class now: P97(a)'s TaskStop-first restart step, `seat-launch.sh --dup` (clean for merge and triage since the 2026-10-30 stop lines), and R10-FLY-SEAT-ALIVE-ID's `DUPLICATE`/`FOREIGN` arms (P299).
  - The re-route would cost an S group across two hot files (`bus.sh`, `merge_train.py`), plus a bump at every restart. Against zero instances, the trade is worse than even.
  - What would change the answer: one instance, after R10-FLY-SEAT-ALIVE-ID lands, of a superseded seat writing through a tracked writer.
- **P302: ACCEPT narrowed. Retire the orchestrator's session-local sweep** (`s7/orch_sweep.sh` and three sibling scripts, about 460 untracked lines) onto the rendered `sweep_template.md`.
  - `orch-sweep.log` holds 21 `rc=1` boards out of 31, and the local sweep printed P299's false `ok`.
  - The one check the template lacks, standing-seat liveness, is R10-FLY-SEAT-ALIVE-ID. One carry there widens step (1b) to every standing seat the overlay names.
  - Rejected as already owned: a main-CI arm (the tick's main-red lane is the one owner) and in-tree transcript selection (the template already takes `{{transcript}}`).
  - Owed now, out of tree: stop `sweep_mech.sh`'s `pgrep -f`-then-kill restart and `refresh-orch-wt.sh`'s hard-coded `kill -9` of six PIDs.
- **P303: ACCEPT, new S fly-in R10-FLY-BUS-BASH32.** `bus.sh orphans` dies on macOS bash 3.2 (`arms[@]: unbound variable`, reproduced on `/bin/bash` 3.2.57, rc 127), so `pulse.py`'s opener arm has been UNREADABLE for about 46 h, since `d0f6de273`.
  - The fix is the guarded expansion, plus a static class check: CI's bash 5 passes the defect at run time.
  - The rule it breaks is written in `bus.sh:134`, `body_push.sh:11` and `seat_venv.sh:41`. The fixer classifies the other `"${x[@]}"` sites.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`f5c63d5ffcc5ec90def72e4dc424892f2e7f97c2`; the file is the whole diff against `b646e8306`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P301 as `DEFER`. A carry citing `triage: dev/programme/triage/s6-batch69.md#P301` is refused: `dev/programme/triage/s6-batch69.md#P301 is not an ACCEPT ruling (DEFER)`. No roster op cites it.
- `ruling_verdict` reads P302 and P303 as `ACCEPT`. `triage_refusal` passes the R10-FLY-BUS-BASH32 group brief and the P302 carry: each returns None.
- With P303's `Verdict: ACCEPT` changed to `Verdict: REJECT`, the group brief is refused: `dev/programme/triage/s6-batch69.md#P303 is not an ACCEPT ruling (REJECT)`.

## Null control

- With the file absent, the P303 citation does not resolve: `the triage ruling dev/programme/triage/s6-batch69.md is not on the roster branch or origin/main`.
- `seat-launch.sh --dup merge` and `--dup triage` each print `ok: 1 live launch(es)`, the clean state the ruling cites. Before the stop lines, on 2026-10-30, both printed `DUPLICATE: 2 live launches`.

## Figures

- The grep `duplicate|double|two writers|second writer` (case-insensitive) over `seat-ledger.md` lines 1100-2471 finds one duplicate-seat instance, `:1372` and `:1376` (2026-10-27).
- `git grep -l seat_gen b646e8306` finds only `dev/programme/rosters/wave-r10-groups.json` and `dev/programme/triage/s6-batch5.md`, so the token was never built.
- `orch-sweep.log` (last written 2026-10-28) holds 31 `board rc=` lines: 21 `rc=1` and 10 `rc=0`.
- `wc -l`: `orch_sweep.sh` 256, `sweep_mech.sh` 46, `refresh-orch-wt.sh` 67, `wt-reap.sh` 94.
- `/bin/bash -c 'set -u; f(){ local arms; arms=(); echo x "${arms[@]}" y; }; f'` prints `arms[@]: unbound variable`, rc 127, on `GNU bash, version 3.2.57(1)-release`. With `${arms[@]+"${arms[@]}"}` it prints `x y`.
- `git log -S'arms+=(--no-ancestry)' origin/main -- tools/audit/seat/bus.sh` names `d0f6de273` (2026-10-28T11:57:27Z).
- `pulse.py:245` runs `bash bus.sh orphans --min-age-h 0`, with neither flag.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
