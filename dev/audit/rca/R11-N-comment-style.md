# RCA: comment and doc sentences over the 40-word ceiling

Seat: round-11 root-cause, class `N-comment-style` (instrument). Instances R11 101, 101 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`I5`) as one (`fold_ledger.py` `_group_counts`): `N-comment-style`, `N-orphan-doc`, `N-table-value`, 103 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`D5-criteria.md` C5 caps a sentence at 40 words. Comments, docstrings and governance prose
exceed it in every seat's cells. The class holds 101 instances this round, 11 of them judged
findings that each aggregate many sentences, for example 339 in one cell set, 363 units in a-i of the package and 558 of 3367 units in
j-z. The criterion is applied only at audit time. Authors write long WHY blocks, and the one
existing reader of C5 (`tools/audit/text_ledger.py`) is an audit instrument. That instrument
mislocated 1175 of 1899 JavaScript units at this baseline (`N-instrument-locator`).

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D5-s10-07` (weakened, low): planted copy: long_sentences=339 across the seat's cell files; perturbation: 275.
- `R11 D5-s2-06` (weakened, low): planted copy: long_sentences=8 in the cell set incl 2 in make_card_weekly_figure.mjs (51, 55 words); perturb -> 0; perturbation: long_sentences 8 -> 0.
- `R11 D5-s3-03` (weakened, low): planted copy: long_units=363; perturb -> 343; perturbation: 343.
- `R11 D5-s4-01` (verified, low): planted copy: long_units=558 of 3367 units; perturbation: pump_mode.py long_units 3 -> 2.
- `R11 D5-s5-07` (verified, low): planted copy: long_sentences_strict=483 in 60 files (raw 743); perturbation: 14 (the --file tools/pr/push.sh arm, from 15).
- `R11 D5-s6-08` (verified, low): planted copy: C5-len=404 over 3781 units; perturbation: 372.
- `R11 D5-s7-01` (verified, low): planted copy: tests/features.py c5_fail=450, c2_fail=3, plus 1 C1 = 454; perturb c2 3 -> 2; perturbation: fix-path: c2_fail 3->2, false_rows 454->453; c2-define: total c2_fail 3->0; c5-split: total false_rows 471->4; c1 --perturb: between-run per solve 3..34 -> 4..41, solves reading eight 2->0.
- `R11 D5-s7-02` (verified, low): planted copy: tests/finite_boundary.py c5_fail=14 of 143 units; perturb -> 0; perturbation: finite_boundary c5_fail 14->0 (total false_rows 471->4).
- `R11 D5-s7-03` (weakened, low): the record carries no metric line.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s10/m4_ledger.py --repo . --ref 92d38ecb640bd462f2e19c0814d0f0b7df1ee692 --adjudicate dev/audit/rounds/round11/D5/s10/m4_adjudicate.tsv` took 1.7 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-comment-style.json`) lists 94 seams. The ledger carries 90 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/N-comment-style/enumerate.py .`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

C5 is a finder criterion, not an authoring rule. No lint, hook or pre-PR check reads sentence
length, so every new comment is written without it. The audit finds the backlog each round.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 101 instances over the 148 releases they accumulated in, 0.682 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.682 x 15660 s | 10687 s/release |
| form | a one-sided ratchet in the D5 lane: the count of over-40-word sentences in D5 units may only fall, measured by `text_ledger.py` once its locator is fixed |
| catch share q | 1.0: the ratchet counts every unit the ledger reads; a hard per-sentence gate is refused because the backlog would fail every PR |
| expected benefit, q x cost | 10687 s/release |
| arm time | 1.7 s (`dev/audit/rounds/round11/D5/s10/m4_ledger.py`, re-timed by this seat on one cell set; a whole-tree count is a few times that) |
| standing cost, arm x 16.3 PRs | 28 s/release |
| verdict | passes by 386.2x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The proposal is a ratchet, not a gate on each sentence: the backlog runs to thousands, and a
hard gate would refuse every PR that touches a long comment. A new budget metric is a
`*_budgets.json` key, which merges only on the owner's approving review (0013), so this seat
records the proposal and builds nothing. The ratchet depends on `N-instrument-locator`'s fix,
because a count of mislocated units cannot name the sentence to split.

The cost side here is soft. The 4.35 h per-finding figure is a behaviour-fix cost, and a C5
instance is a style finding of info or low severity, so the expected cost below overstates the
defect by an unknown factor. The ratchet still passes at 1/50 of that figure.
