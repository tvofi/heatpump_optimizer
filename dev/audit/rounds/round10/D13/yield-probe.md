# R10-FLOW-YIELD-PROBE: why real-catch blocks per reviewed PR fell

Owner ruling R13 (#201, 2026-10-21) asked two things before any guardrail
relies on review strength. First, explain the fall from 0.52 real-catch blocks
per reviewed pull request (round 10's first six days, 112 PRs) to 0.15 (the
48 h before the flow plan's adoption, 47 PRs). Second, recommend a threshold.
This file is a measurement record. Every figure in it was taken over git from
the `review/*`, `verdict/*` and `probe/*` refs and the `archive/probe/*` tags,
using the tool and windows below. No REST call was made.

Measured 2026-10-21T15:24Z. `origin/main` was at `e7c664856776`, and the roster
was `origin/fix/audit-r10-roster` at `802b38503eb5`. Every window is closed
(it ends at or before 15:15Z). The bus is append-only, so a re-run gives the
same counts unless `prune_refs.py` removes a ref first.

## The instrument and its rule

`tools/audit/seat/review_strength.py` holds the rule in its header.

- A verdict is a `review/<pr>` commit whose subject matches
  `verdict: #N Fix review: merge|blocked <40hex>[ <class>:]`. A commit is read
  once, by committer time.
- A blocked verdict is real when its class is in the study's real-catch list
  (STUDY.md, "Guardrail baselines"). Every other block is bookkeeping.
- **real/PR** is real blocks divided by reviewed PRs. **incidence** is the
  number of PRs with at least one real block, divided by reviewed PRs.
  **first-pass m/n** counts the PRs whose first bus verdict falls in the
  window (n) and those whose first verdict is `merge` (m).
- A verdict's reviewer **kind** is `cloud` when one of these holds:
  - a probe return `probe/rev-<pr>-<nonce[:8]>` (a ref or an archive tag)
    carries its bus nonce;
  - its `bus-confirmed:` id starts with `cloud` or ends with `-cloud`.

  Otherwise the kind is `local`. 306 verdicts were read, and 0 fell outside
  the grammar.

The reproduction command, with the windows used throughout:

```
python3 tools/audit/seat/review_strength.py --fetch \
  --window E=2026-10-15T12:37Z..2026-10-19T14:50Z --window L=2026-10-19T14:50Z..2026-10-21T14:50Z \
  --window P1=2026-10-15T12:37Z..2026-10-18T08:00Z --window P2=2026-10-18T08:00Z..2026-10-19T14:50Z \
  --window L1=2026-10-19T14:50Z..2026-10-21T13:00Z --window S=2026-10-21T13:00Z..2026-10-21T15:15Z \
  --by kind --by prior-merge --by origin --by size --by product --by fixer --by class --by kind+origin \
  --roster origin/fix/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json
```

What each window covers:

- **E**: from the start of the study window to the start of the 48 h window.
- **L**: the 48 h window.
- **P1**: before the first cloud reviewer (the first cloud environment was
  created at 10-18 08:05Z, per the orchestrator ledger
  `wip-sync/orchestrator-scratch:orch/SEATS.md`).
- **P2**: from the first cloud reviewer to L's start.
- **L1**: L, cut at 13:00Z.
- **S**: the orchestrator's sample, from 13:00Z.

## The baselines reproduce, and the 0.15 window holds the sample

| window | reviewed PRs | real/PR | bookkeeping/PR | incidence |
|---|---|---|---|---|
| 10-15 12:37Z → 10-21 11:00Z (the study's 0.52) | 112 | 0.52 (58) | 0.58 (65) | 36/112 |
| L: 10-19 14:50Z → 10-21 14:50Z (the study's 0.15) | 47 | 0.15 (7) | 0.64 (30) | 6/47 |
| P1 | 48 | 0.90 (43) | 0.17 (8) | 25/48 |
| P2 | 39 | 0.36 (14) | 0.92 (36) | 10/39 |
| L1 | 39 | 0.08 (3) | 0.64 (25) | 3/39 |
| S | 14 | 0.36 (5) | 0.36 (5) | 4/14 |

The study's 47 / 0.15 reproduces only as the 48 h ending between 14:45Z and
15:00Z on 10-21 (a 15-minute sweep of the end time). The same 48 h ending at
11:00Z, the study window's own end, holds 35 PRs and 0.06 (2). The 0.15 window
therefore includes the 13:00Z sample, and 5 of its 7 real blocks are the
sample's. The fall ran in two steps: from 0.90 to 0.36 at P1 → P2, then from
0.36 to 0.08 at P2 → L1.

## Each candidate, stratified, with its null control

The rule for each table is the tool's `--by` stratum. A null control is a
stratum whose rate must stay put if the candidate is the cause.

### 1. PR mix: origin, size, product

| stratum | P1 | P2 | L1 |
|---|---|---|---|
| finding-fix group (roster lists issues, findings or fixes) | 1.08 (40/37) | 0.29 (5/17) | 0.08 (1/13) |
| roster group without findings | — (0 PRs) | 0.25 (1/4) | 0.00 (0/6) |
| no roster group | 0.27 (3/11) | 0.44 (8/18) | 0.10 (2/20) |
| size L ≥ 600 lines | 1.10 (22/20) | 0.69 (11/16) | 0.08 (1/13) |
| size M < 600 | 1.31 (17/13) | 0.17 (2/12) | 0.15 (2/13) |
| size S < 150 | 0.27 (4/15) | 0.09 (1/11) | 0.00 (0/13) |
| product (touches `custom_components/` or `blueprints/`) | 1.21 (17/14) | 0.22 (2/9) | 0.14 (1/7) |
| instrument or process | 0.76 (26/34) | 0.40 (12/30) | 0.06 (2/32) |

Null control: if the mix were the cause, the rate inside each stratum would
stay put. Every stratum falls from P1 to L1, so mix is at most a share of the
fall. The share comes from re-weighting: L1's PR counts per stratum, times
P1's per-stratum rate, divided by L1's 39 PRs. A stratum with no P1 PRs is
taken at 0.

- origin: 0.50 (finding-fix PRs made up 37/48 of P1 and 13/39 of L1)
- size: 0.89
- product: 0.85

Against the observed 0.90 → 0.08, the share of finding-fix work accounts for
about half of the fall. Size and product account for almost none of it.

### 2. Reviewer seat: agent kind and model

| kind | P1 | P2 | L1 | S |
|---|---|---|---|---|
| cloud, real/PR | — | 0.19 (6/31) | 0.12 (3/24) | 0.36 (5/14) |
| local, real/PR | 0.90 (43/48) | 0.57 (8/14) | 0.00 (0/20) | — |
| cloud + finding-fix group | — | 0.23 (3/13) | 0.17 (1/6) | — |
| local + finding-fix group | 1.08 (40/37) | 0.25 (2/8) | 0.00 (0/8) | — |

Null control: during P2 both kinds were running. On finding-fix PRs in P2,
cloud reviewers read 0.23 (13 PRs) and local reviewers read 0.25 (8 PRs), so
kind alone does not set the rate. The cloud stratum stays within 0.12–0.36
across P2, L1 and S. The deep trough is L1's local seats, at 0 real blocks in
20 PRs. Those seats were:

- the Sonnet roster-PR reviewers (named `sonnet-rev-*` and `rev-2471-sonnet`
  in their `bus-confirmed:` ids);
- the local seats after the 10-20 session crash (the ledger records that its
  07:10Z–13:20Z entries were lost);
- the next session's seats, named `reviewer`.

**The reviewer's model is not recorded per verdict.** The ledger records it
for 18 verdicts (10 Opus, 8 Sonnet) and ends at 10-20T13:34Z. `nudge.md`'s
rule (a dead Opus seat is replaced on grok-4.7-high) leaves no trace on the
bus. A model stratum could only be taken from the roster's planned
`reviewerModel` (Opus for every group), which measures the plan, not the seat.
It is left unmeasured.

### 3. Fixer quality: first-pass merge share by fixer model

| fixer model (roster) | P1 | P2 | L1 |
|---|---|---|---|
| Opus | 7/22 | 2/14 | 5/7 |
| Sonnet | 5/15 | 0/3 | 3/6 |
| no roster group | 8/11 | 8/18 | 9/23 |
| all | 20/48 | 10/35 | 17/36 |

The real/PR rate by fixer model moves the same way: Opus goes from 1.00
(22/22) to 0.33 (6/18) to 0.10 (1/10), and Sonnet from 1.20 (18/15) to 0.00
(0/3) to 0.00 (0/6).

Null control: if fixer quality is the cause, first-pass share also rises for a
fixed reviewer kind. Cloud reviewers' first-pass share was 8/25 in P2 and 9/20
in L1, so it does rise. The bus cannot separate better fixers from weaker
reviewers. Both raise first-pass share and lower real catches together. Only
a planted defect can separate them (see the recommendation).

### 4. Verdict carries that replace re-reviews

A carry (`app_approve.sh --carry`) replaces the re-review that follows a merge
verdict. The bus stratum for that re-review is `after-a-merge-verdict`:

| window | verdicts | PRs | real |
|---|---|---|---|
| E | 22 | 17 | 0 |
| L | 12 | 8 | 0 |
| the 6-day window | 33 | 22 | 0 |

Every window reads 0. Removing re-reviews that never caught anything real
cannot lower the rate. **Rejected.**

### 5. The real-catch classes themselves

The `harness` class (a finder's harness still reading the defect) went from 25
in P1 to 3 in P2 to 2 in L1. That is 23 of P1's 43 real blocks gone, out of
the 40 lost overall. The blocks are concentrated: in P1, #2320 carries 6 real
blocks and #2283 carries 5. A per-verdict rate counts one PR's six rounds six times.

The list also misses engineering catches. Nine block words outside it name a
defect in the diff or a false claim the gate did not catch:

- regression
- flaky-arm
- claim-false
- control-failed (a surviving mutant)
- claim-refuted
- rule-dropped (a deleted policy rule)
- null-control-false
- red-at-head
- tests-red

These words occur 0 times in P1, 5 in P2 and 5 in L1. Re-run with
`--real-extra` set to those nine words:

| window | real/PR | incidence |
|---|---|---|
| P1 | 0.90 (43/48) | 25/48 |
| P2 | 0.49 (19/39) | 13/39 |
| L1 | 0.21 (8/39) | 7/39 |
| S | 0.36 (5/14) | 4/14 |
| cloud P2 | 0.29 (9/31) | 8/31 |
| cloud L1 | 0.33 (8/24) | 7/24 |
| cloud S | 0.36 (5/14) | 4/14 |
| local L1 | 0.00 (0/20) | 0/20 |

Null control: P1 holds none of the nine words and reads 43 under both lists.
The extension moves only the windows where the words occur.

One class per subject did not hide many catches. Of the bookkeeping-blocked
subjects, the ones that name a real class after `also` number 0 of 8 in P1,
1 of 31 in P2 (#2396: `conflict: … also harness: class-open`), 0 of 20 in L1
and 0 of 5 in S.

## The explanation

1. **Under half of the headline fall is in what was counted.**
   - The 0.15 window includes the 13:00Z sample.
   - The list misses five L1 catches. With them, L1 reads 0.21, not 0.08.
2. **P1 was wave 1 of the round's finding fixes.** In P1, 37 of the 48
   reviewed PRs were finding-fix groups. They drew 40 of the 43 real blocks,
   25 of them `harness`, and a few multi-round PRs dominated. When that wave
   drained, the origin mix alone takes the expected rate from 0.90 to 0.50.
3. **After P1, the cloud reviewers' rate is flat.** Their incidence reads 8/31
   in P2, 7/24 in L1 and 4/14 in S (extended list). This is the stratum where
   one reviewer kind stayed constant, and it does not move.
4. **The remaining trough is L1's local seats, at 0/20.** In the same hours,
   cloud seats on a similar mix found 7/24 (extended list). At the
   post-cloud incidence of 0.28 (24/85, 10-18 08:00Z → 10-21 15:15Z), the
   chance of 0 in 20 is 0.0014. The model behind those seats is unrecorded.
5. **Carries are not the cause.** Bookkeeping blocks rose from 0.17 to 0.92
   per PR at P2, which is when `carry_audit.py` (O11, 10-18) landed:
   `carry-missing` went from 3 to 15. That moved the bookkeeping rate, not the
   real-catch rate.

## The recommended threshold for the review-strength guardrail

- **Measure incidence, not blocks per PR.** Blocks per PR counts one PR's
  repeated rounds.
- **Count the study's list plus the nine words above,** and route any untaught
  word to a row that needs classifying, never to bookkeeping.
- **Use the last 30 reviewed PRs by first verdict,** with baseline
  p0 = 0.28 (24/85, the post-cloud regime).
- **Trip at P(X ≤ k | 30, 0.28) < 0.05**, which means 3 or fewer of the 30
  PRs (P = 0.017). At 4, P = 0.050, so 4 is the line.
- **Add a second arm for each seat family** (cloud or local; the model when
  the dispatch records it): the last 20 PRs that family reviewed, tripping at
  1 or fewer (P = 0.012). Only this arm would have caught L1's local trough.

Back-test of the first arm (`--guardrail 30 --p0 0.28`, with `--real-extra`
set to the nine words, at ten cut points from 10-17 00:00Z to 10-21 15:15Z):

- lowest point: 5/30 at 10-21 06:00Z and 13:00Z (P = 0.116);
- highest point: 19/30 at 10-18 08:00Z.

It would have tripped at no cut point.

A trip means: audit the last N reviews with a planted defect. It does not mean
the reviewers are weak. Incidence is the supply of defects times the review's
detection, and the bus cannot split the two (candidate 3). The calibration
that can split them is a planted defect of a known class in a reviewed head,
caught or missed. It is owed to whoever builds the guardrail
(FUTURE-STATE.md §9). Until the owner adopts a threshold, R13 stands: the
guardrail reports and trips on nothing.

## D13's required outputs, where they apply

- **Output 3** (block classes) is the class table above, taken raw: one row
  per class word, with no bucketing into the `VERDICT_CLASSES` grammar. The
  bus subjects use 46 class words. `VERDICT_CLASSES` teaches 17 of them, and
  the study's real-catch list holds 16.
- **Output 1** (first-pass yield) is taken here on the bus, not on
  `/commits/<sha>/pulls`. It is a different population: bus-reviewed PRs, not
  first-parent merges.
- **Outputs 2, 4, 5 and 6** are outside this probe's question.
