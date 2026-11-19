# RCA: one rule kept as several agreeing copies

Seat: round-11 root-cause, class `N-duplicated-rule` (production). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`P2`) as one (`fold_ledger.py` `_group_counts`): `N-duplicated-rule`, `N-entry-data-placement`, `N-inverted-aggregate`, `N-mode-coupled-write`, `N-wrong-law`, 8 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

Eight rules are written two or three times in the package, among them the note, availability,
step, day, reader, Jacobian, entry and notice rules. Each copy agrees with the others today. A
later fix to one copy forks the rule without a test failing. Each can take one owner in a
behaviour-preserving edit that the architecture score reads as an improvement (9 of 18 clone
copies go, dS +8.27). The verifier judged it an improvement opportunity, not a defect the score
hides.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D7-s1-05` (weakened, low): planted copy: duplication_copies -> 9 with the ten prototypes, dS +9.2671 (verifier +8.2671); fold alone 17; perturbation: +0.0000.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_prototypes.py --score --only note,avail,step,day,reader,layer,fdjac,entry,notice,curr --combined` took 25 s and exited 1. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.
 The harness did not complete on this tree, so its time is not a standing cost; the judge's reproduction above stands as the evidence.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-duplicated-rule.json`) lists 8 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D7/s1/m7_sites.py | grep '^SITE duplication_copies'`. That program is in the tree.

### Process state: (c) followed and did not produce the intended result

`tools/audit/archscore/` reads `duplication_copies` and saw all 18. It is a score a seat
reads, not a gate, and the structural ratchet holds other metrics. The instrument worked as
designed. A copy that comes in raises a number, and nothing refuses the PR that adds it.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | a new barrier refusing duplicated rules |
| catch share q | 0.5: archscore already detects the shape; the question is only whether to gate on it |
| expected benefit, q x cost | 53 s/release |
| arm time | not measured (`dev/audit/rounds/round11/D7/s1/m7_prototypes.py --score ...`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | not computable |
| verdict | not computable: the form's harness did not complete on this tree (see the re-run line) |

### Decision not to build a class barrier

Decision: no new barrier from this seat. Detection exists: `duplication_copies` is an
archscore metric. Making it a ratchet key would be a `*_budgets.json` change, and that is the
owner's call (0013), so this record names the option and does not propose it as a gate. The
architect-planner's move plan (round 11's P3) is where the eight one-owner edits belong. Re-open if
the planner does not take them.
