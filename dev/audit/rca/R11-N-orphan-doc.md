# RCA: a reader document no other document links to

Seat: round-11 root-cause, class `N-orphan-doc` (instrument). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`I5`) as one (`fold_ledger.py` `_group_counts`): `N-comment-style`, `N-orphan-doc`, `N-table-value`, 103 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

Of the 8 `docs/*.md` documents, `docs/CONTRIBUTING.md` has no inbound link from README.md
or any other doc. README's Documentation table lists the other seven. The file was added in
`89a88bade` (2026-11-12) without a table row, and nothing requires one.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D5-s2-02` (verified, low): planted copy: orphan_doc=1 (docs/CONTRIBUTING.md, inbound 0); perturbation: orphan_doc 1 -> 0.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s2/structure.py` took 0.2 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-orphan-doc.json`) lists 1 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/orphan_doc.py .`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

D5 asks for orphaned documents (`dev/governance/dimensions/D5.md:25`), and round 10's D5 s2
seat ran that step over README.md and `docs/*.md`. The file landed on 2026-11-12, after round 10,
and between rounds no check runs: the docs checks resolve outbound links, and none asks for an
inbound one. The audit step exists, and nothing applies it before a merge.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | a `tests/` arm requiring every `docs/*.md` to have an inbound link from README.md or another reader doc |
| catch share q | 1.0: the arm reads the whole reader set; the shape is exact |
| expected benefit, q x cost | 106 s/release |
| arm time | 0.1 s (an estimate: a link scan over 9 files) |
| standing cost, arm x 16.3 PRs | 1.6 s/release |
| verdict | passes by 65.0x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The arm must show `docs/CONTRIBUTING.md` red on this baseline and green with the README row.
It costs almost nothing, because it reads nine files. The fix PR owns it.
