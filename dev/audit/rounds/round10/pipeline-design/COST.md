# Appendix C: candidates and cost tests, revision 1 (R11-PRE-PARALLEL-PIPELINE)

Revision 1 replaces the first cost test. The design review (verdict
ea028c98ec on `design-verdict/R11-PRE-PARALLEL-PIPELINE`) found the first
replay deleted authored work, used a null that could not fail, and bisected
at a parallelism the job cap does not allow. `REVISE-1.md` answers each point.
The first replay's script and output stay in harness/ and out/
(`replay_pipeline.py`, `out/replay_pipeline*.txt`) as the record of what was
withdrawn; no figure below comes from it.

## The two replays

- **R-pipe2**: `harness/replay_v2.py [proof wall in minutes ...]`. One event
  loop, five rule sets, over the recorded 215 merges. Inputs it keeps from the
  record: each pull request's merge verdicts; the pull-request head each
  verdict judged and the commits after it by kind (`collect_heads.py`,
  `data/heads.json`); the `gate` check-run at the judged heads
  (`data/gate_heads.json`); main's recorded reds (`data/main_gate.json`); the
  direct pushes to main (`main_moves.py`). Output: `out/replay_v2.txt`.
- **R-prog**: `harness/replay_programme.py`, `tools/plan/replan.py` over round
  10's whole roster (495 groups reset to not-started, 20 slots, fixed start),
  a candidate applied as hours taken off every size's first-round hours.
  Output: `out/replay_programme_r1b.txt` (lower bound),
  `out/replay_programme_r1c.txt` (upper bound).

## Rules of R-pipe2

- A pull request lands at its FIRST approved head only when nothing but
  mechanical commits followed it. Fifteen took fixer-authored commits after
  the first approval and thirteen a blocked verdict: those 28 land at their
  LAST merge verdict's head.
- Ready is the later of that verdict and `gate` green at that head. 167 heads
  have the green check-run; 30 were superseded before the gate concluded and
  are imputed as head time plus that day's mean push-to-green; 18 are red on
  their own gate (or unmapped) and keep today's recorded clock.
- Only a head made by a merge of main is removed by a candidate. A delivery-row
  or bot head after approval keeps its cycle (34 such heads).
- Merge latency, 0.45 h, is measured: gate green to main for the heads that
  never moved (n = 58).
- One proof at a time. A direct push to main (11 stamps, 9 ledger App pushes
  in the window) restarts the proof in flight. A recorded red of one red then
  green is transient and costs half a wall; the others are culprits, found by
  prefix bisection with ONE proof at a time, or by cloud seats in one seat
  wall (1.1 h, an estimate) where the rule set says so.
- **Upper bound** (`OWN_RED=cycle ROW=early`): a head red on its own gate is
  cured by one more cycle at the same head, and the delivery row is on the
  head before review. It is the reading nearest the reviewer's own.

## Figures

| id | figure | literal (lower bound; upper bound in brackets) | enumerator |
|---|---|---|---|
| N1 | NULL: today's rules through the loop against the measured mean; tolerance 20 % | 7.88 h against 7.60 h, +3.7 % [8.21 h, +8.0 %]; per class U 2.51 / 2.42, M 7.80 / 7.30, A 14.74 / 14.60, B 30.07 / 30.44 | R-pipe2, lines NULL and class |
| N1b | the same with the median cycle in place of the mean | 6.49 h, -14.6 % | `CYCLE=median` R-pipe2 |
| N2 | R-prog null: unedited; an unread term edited | 714.05 h; 714.05 h | R-prog |
| S-a | saving a change, slot freed: day 1's first pull request alone (no clean absorb; the train still recarries) | 0.79 h [1.63] | R-pipe2, day1a |
| S-1 | the same, day 1 complete, proof wall 45 / 60 / 75 / 105 min | 1.78 / 1.53 / 1.31 / 0.32 h [2.83 / 2.55 / 2.26 / 1.17] | R-pipe2, day1 |
| S-1p | the same, every entry behind a proof before GitHub merges it | 1.30 / 0.70 / -0.98 / -4.15 h [2.32 / 1.67 / -0.12 / -3.24] | R-pipe2, day1+ |
| S-i | the same, integration branch, successors at landing | 2.47 / 2.44 / 2.37 / 2.21 h [3.61 / 3.59 / 3.51 / 3.35] | R-pipe2, integ |
| S-ig | the same, successors after a seat's green gate | 1.62 / 1.49 / 1.39 / 1.23 h [2.66 / 2.53 / 2.44 / 2.28] | R-pipe2, integ |
| S-im | the same, successors at promotion (FULL-proof bisection) | 1.44 / 0.73 / -1.20 / -4.91 h [2.47 / 1.74 / -0.23 / -4.01] | R-pipe2, integ |
| T-f | main trails a landing, mean and max, FULL-proof bisection | 1.16 and 2.91 / 1.93 and 7.20 / 4.02 and 19.04 / 8.01 and 34.34 h | R-pipe2, integ |
| T-s | the same with seat search | 1.17 and 3.26 / 1.87 and 6.20 / 2.55 and 7.63 / 4.66 and 15.77 h | R-pipe2, integ seat search |
| E | integration's edge over day 1 at landing (S-i less S-1) | 0.69 / 0.91 / 1.06 / 1.89 h [0.78 / 1.04 / 1.25 / 2.18] | derived from S-i and S-1 |
| Pf | proofs a week, day 1 / every entry / integration, at 45 and 60 min | 104 and 99 / 140 and 120 / 140 and 121 | R-pipe2 |
| G-a | programme wall clock, day 1's first pull request alone | -2.9 % | R-prog r1b |
| G-1 | programme wall clock, day 1 complete, 45 / 60 / 105 min | -6.0 / -5.2 / -0.9 % | R-prog r1b |
| G-i | programme wall clock, integration: successors at landing / after a seat gate / at promotion (60 min) | -7.7 / -5.1 / -2.7 % | R-prog r1b |
| G-u | the upper bounds: day 1's first pull request alone; day 1 at 45 / 60 / 105 min; integration, successors at landing / after a seat gate | -5.6 %; -9.0 / -8.1 / -4.0 %; -11.5 / -8.0 % | R-prog r1c |
| K1 | `ci.yml` run wall at heads made by a driver-free clean merge of main after PR open | 703 runs, 258 h of 1540 h, 16.7 %: the train's recarry 10.1 %, other instruments 6.6 % | `absorb_heads.py` |
| K1n | its null: the same script with those heads relabelled ordinary | 0 h | `absorb_heads.py --null` |
| K2 | runs cancelled when such a head arrived (burned; not counted as saved, the run would otherwise complete) | 102 runs, 111 h, 7.2 % | `absorb_heads.py` |
| K3 | mean wall of a concluded push run; of a successful long dispatch run | 0.94 h; 0.98 h | `absorb_heads.py`, last line |

## The cost test

| | day 1 complete | integration branch (the switch, not approved) |
|---|---|---|
| hours a change, slot freed | S-1 | S-i if successors start on unproved landings; S-ig behind a seat gate; S-im at promotion |
| to main | as S-1 | later than day 1 at every proof wall of 60 min or more (S-im against S-1) |
| programme wall clock | G-1 | G-i |
| CI run wall | K1 less the batch proofs it adds (Pf times K3): about -10 % | K1 less about 1 % (proofs plus one push run a promotion against today's push runs): about -17 %; about -26 % if the push run at a proved sha is skipped (probe U6) |
| main red starts (24 in the window) | unchanged for unproved lone entries; a batch entry cannot redden main once its proof is judged as a push | at least 2 remain (the two stamps); 4 if record pull requests stay on the direct path |
| review turns | the 56 re-issued merge verdicts of B7 lose their cause | the same |
| tokens | not measured: no ledger exists (R11-PRE-TOKEN-LEDGER) | the same |
| build | three groups, S, M and S | three more, L, M and S, plus the probes and a decision on D1 |

## Against the bar (over 20 % on a measured baseline with a null control)

No candidate clears the bar on any of the four measures.

- Programme wall clock: day 1 is G-1 (G-u at the upper bound), the
  integration branch at best G-i's first term (G-u's -11.5 %). The first note's 16.0 to 19.8 % is withdrawn: it rested on a
  landing figure of 2.50 h that R-pipe2 puts at 5.41 to 5.68 h from first
  approval (4.60 to 4.86 h at the upper bound).
- CI: day 1 about -10 % of run wall; the integration branch about -17 %, or
  -26 % with a push-run skip that rests on an unprobed GitHub behaviour and a
  change to `CLAUDE.md` rule 1. The first note's -33 % is withdrawn: it had no
  enumerator and counted K2 and the gating run as saved.
- Right-first-time and tokens: not measured.

Day 1 is nonetheless not a new proposal under the bar's rule: it enforces the
owner's ruling of 2026-11-07 and his direction of 2026-11-14 on
`remerge_main.sh`.

**The weakest inputs.** (1) The proof wall: R-pipe2 takes it as an input, and
S-1 falls from 1.78 to 0.32 h as it goes from 45 to 105 min, because two
thirds of entries wait for a proof under day 1. (2) The 18 heads red on their
own gate: the lower bound keeps their whole recorded clock, the upper bound
cures them in one cycle; the truth is per head and was not read. (3) N1 passes
at +3.7 % with the mean cycle and at -14.6 % with the median: the loop is
sensitive to how one more head is priced, and every saving is stated against
the loop's own today, never against the measured 7.60 h.
