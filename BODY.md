r10-hotfix-packet-approval-owed: the review packet's `required-red` refusal now asks `merge_train.py classify --pr` for its whole verdict, not only "is it APPROVAL-OWED?".

The defect, on #3379 at 71b95e42daf4d32031ce116b01c469b81f2a23a0 (packet rendered 2026-11-10 00:03Z, kept at the bus state's `packets/3379-71b95e42daf4d32031ce116b01c469b81f2a23a0.md`, sha1 6035054592c06e71d257791c77c94d3fdb93ae87). The gate's latest run had concluded failure while `budget-raise-gate / budget-raise-gate` and `arch-score / arch-score` were re-running. `bus.sh dispatch` asked classify and got past its own gate: RED dies there, so the answer was WAIT, which `Train.classify_at` gives a red gate while `_gate_busy` names a running unit (P436's deferral reading). The packet then asked the same classifier, but `approval_owed_line` kept only an rc 4 APPROVAL-OWED line and turned every other answer, WAIT included, into None. So the packet refused `required-red` on a head that bus.sh had just read as reviewable. The raise's approval follows the review, so the review could not be dispatched and the raise could not be approved. That was the deadlock. Once the re-runs concluded, classify read APPROVAL-OWED and the old code rendered too. The defect is the window, and it opens on every head whose gate is red while a unit re-runs.

The fix is at the owning seam. `required_reading(pr, head)` returns classify's verdict word and the rest of its line. `build` refuses `required-red` only on RED, which includes an unreadable classifier, a word that does not match its rc, or a line naming another head (fail closed). APPROVAL-OWED prints the `approval-owed` advisory as before. WAIT and GREEN print `required-wait` / `required-green` advisories. The packet's own latest-run-per-name digest no longer decides alone, so the packet and bus.sh's dispatch gate now read one answer.

## Head

44467af5a04e72a2502d34130066b16fea42068c, on origin/main b8f67a775137a8032d5c71b34ea64165c1d4613a (merge base and tip at 2026-11-10T00:19Z).

## Mutation proof

The failing test came first, at 650cf3b4376636c21e5a7ad6893f85243e999001. It adds #3379's shape: a red gate beside an in-progress `budget-raise-gate / budget-raise-gate`, with classify reading WAIT. It also adds the GREEN arm and the RED null arm. On the unfixed packet `python3 -I tools/audit/seat/review_packet.py --self-test` printed `75 checks, 3 failed`.

Three hand mutants on the fixed predicate were each run with `python3 -I tools/audit/seat/review_packet.py --self-test` and then restored. They were built and killed through `dev/audit/harnesses/r10_seat_selftests_mutants.py` at 1b56d548e4551bdfdc502d62fca4aca650e650f6 (`RESULT survivors=0`). Those harness entries are reverted at the head, because that file is a hot file that #3366 holds with an unboarded merge verdict, and the packet's hot-file refusal would block this handoff:
- review_packet-16 replaces the WAIT/GREEN arm with `elif False:`. KILLED, `76 checks, 2 failed`: `FAIL #3379: a required red that classify --pr reads WAIT renders ...` and `FAIL a required red that classify --pr reads GREEN renders ...`.
- review_packet-17 makes an unreadable classify answer WAIT (fail open). KILLED, `76 checks, 2 failed`: the P345 reader arm and `FAIL #3379: classify's WAIT line at rc 3 is WAIT; a REFUSE at rc 2 (unread) fails closed as RED, naming it`.
- review_packet-18 accepts a line naming any head. KILLED, `76 checks, 1 failed`: the P345 reader arm, whose null control is a line naming another head.

## Null control

A genuine required red still refuses. With classify reading `RED <head> pending: none red: gate`, the self-test arm `null control: a required red that classify --pr reads RED still refuses, naming classify's line` passes at the head. The unchanged `required-red: the required context's latest run concluded failure refuses` arm (no classify answer, so fail closed) also passes, and mutant M3 below (RED moved to the advisory arm) fails both. A green head renders with no refusal, as before (`null control: a clean head dispatches`).

## Figures

- `python3 -I tools/audit/seat/review_packet.py --self-test`: `72 checks, 0 failed` at b8f67a775137a8032d5c71b34ea64165c1d4613a; `75 checks, 3 failed` at 650cf3b4376636c21e5a7ad6893f85243e999001; `76 checks, 0 failed` at the head.
- The four harness mutants review_packet-15 to 18, run at 1b56d548e4551bdfdc502d62fca4aca650e650f6 (review_packet-15 is the existing one, run as the harness's own control): `RESULT survivors=0`.
- M3 was a hand mutant, not in the harness: `elif word in ("WAIT", "GREEN", "RED"):`. The self-test printed `76 checks, 2 failed`, the two required-red refusal arms, and then the file was restored.
- Replaying the 00:03Z packet's 48 digest lines through `merge_train.classify` without the busy re-read returns state `red`, with `budget-raise-gate / budget-raise-gate` and `arch-score / arch-score` pending. The live `classify_cmd` adds `classify_at`'s `_gate_busy` re-read, which read WAIT: bus.sh's own classify gate let the dispatch through to the packet, and that gate dies on RED.
- Live, run before 2026-11-10T00:19Z: `python3 tools/audit/seat/merge_train.py classify 71b95e42daf4d32031ce116b01c469b81f2a23a0 --repo tvofi/heatpump_optimizer --pr 3379` printed `APPROVAL-OWED 71b95e42daf4d32031ce116b01c469b81f2a23a0 2 budget raise(s), first .claude/workflows/policy_budgets.json: files.tools/audit/briefs/fix-review.md: 140 -> 143 ...`, rc 4.
- `python3 tests/closure.py select --diff b8f67a775137a8032d5c71b34ea64165c1d4613a`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Seam enumeration (fixer.md step 8): `dev/audit/rca/r10-gate-defer-read-final.md` section 4 lists the readers that take a gate red as final. This diff closes `review_packet.py` `gate_digest`, the `required-red` refusal. Still open, as R10-HOTFIX-TRAIN-DEFER-WAIT carry 4 (body item bdc1d62a; that group's resume stage reads done, so the orchestrator re-routes it, together with the rca record's packet row this diff closes): `merge_train.py` `policy_refusal`, `orchestrator_tick.py` `one_pr`/`main`, and `merge_pr.sh`. `bus.sh` dispatch was already guarded (#3290).

## Red checks

none

## Unpinned sites

prepr.sh step 6d reports that the diff adds no unpinned mutation site. The self-test arms pin `required_reading` and the `build` arm, and the hand mutants above are killed by them. The three harness entries can land in `dev/audit/harnesses/r10_seat_selftests_mutants.py` once #3366 leaves that hot file. The `gather` call site is gather wiring that needs a live `gh` read, a declared survivor of the same kind as #2962's M6/M8/M9.

## Forward-carry

none

## Friction

none
