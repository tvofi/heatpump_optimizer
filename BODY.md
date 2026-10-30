Triage batch 69 rules item 4 of batch 68's owed list (orchestrator s8, 2026-10-30): P63's seat generation token was left on R10-ORCH-BEATD, which is `done` on the roster branch (#2916, arm (a) only). It is the next rolling batch under V182, after batch 68 (#2985). It holds one ruling and no roster op.

- **P301: DEFER, recorded as a drop from R10-ORCH-BEATD.** P63 (`seat_gen.py bump|check`) is not re-routed.
  - The harm P63 guards is a superseded seat writing through a tracked writer: roster apply, `bus.sh` dispatch or the train queue. It has not recurred since 2026-10-24. Over `seat-ledger.md` lines 1100-2471, the one duplicate seat is the 2026-10-27 plain HOLD triage writer (P204). It read no brief, so a token would not have bound it.
  - Three things cover the class now: P97(a)'s TaskStop-first restart step, `seat-launch.sh --dup` (clean for merge and triage since the 2026-10-30 stop lines), and R10-FLY-SEAT-ALIVE-ID's `DUPLICATE`/`FOREIGN` arms (P299).
  - The re-route would cost an S group across two hot files (`bus.sh`, `merge_train.py`), plus a bump at every restart. Against zero instances, the trade is worse than even.
  - What would change the answer: one instance, after R10-FLY-SEAT-ALIVE-ID lands, of a superseded seat writing through a tracked writer.

No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`6244554031bbd226532c8a60fc637d80fca79c3d`; the file is the whole diff against `b646e8306`.

## Mutation proof

This file's only consumer is `tools/audit/seat/roster_edit.py`'s triage gate, `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P301 as `DEFER`. A carry citing `triage: dev/programme/triage/s6-batch69.md#P301` is refused: `dev/programme/triage/s6-batch69.md#P301 is not an ACCEPT ruling (DEFER)`. No roster op cites it.

## Null control

- `seat-launch.sh --dup merge` and `--dup triage` each print `ok: 1 live launch(es)`, the clean state the ruling cites. Before the stop lines, on 2026-10-30, both printed `DUPLICATE: 2 live launches`.

## Figures

- The grep `duplicate|double|two writers|second writer` (case-insensitive) over `seat-ledger.md` lines 1100-2471 finds one duplicate-seat instance, `:1372` and `:1376` (2026-10-27).
- `git grep -l seat_gen b646e8306` finds only `dev/programme/rosters/wave-r10-groups.json` and `dev/programme/triage/s6-batch5.md`, so the token was never built.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
