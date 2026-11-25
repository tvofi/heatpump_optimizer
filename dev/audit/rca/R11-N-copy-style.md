# RCA: copy that breaks its siblings' style rule

Seat: round-11 root-cause, class `N-copy-style` (production). Instances R11 6, 6 in all, which meets the per-round, cross-round trigger. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

Six English config-page titles on the first-run path are in Title Case, while the other
35 are in sentence case. Swedish has three such titles. In German, 27 quoted spans use straight
quotes beside 95 that use the German quote marks. A blueprint writes `1.5 C` where every other
string uses the degree sign. The English and Swedish translations mix quote styles too (61
straight against 3 typographic, and 62 against 1). The style rules live only in the strings that
keep them. Nothing written states them, so a new string copies whichever neighbour it was written
beside.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D4-s3-06` (verified, low): planted copy: en_title_case_titles=6 of 41, sv 3; perturb -> 0; perturbation: --perturb=sentence_titles: every en/sv page title sentence-cased in memory, acronyms and the product's proper names kept.
- `R11 D4-s3-07` (verified, low): planted copy: de_straight_spans=27 vs 95 typographic, en degree without sign 2; --perturb de_quotes -> 2; perturbation: 2.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D4/s3/m3_text.py` took 0.2 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-copy-style.json`) lists 9 seams. The ledger carries 4 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/sweep_n_copy_style.py`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

The rules are unwritten. The nearest step, D4's typography consistency across card states
(`dev/governance/dimensions/D4.md:33-34`), covers spacing and colour tokens, not copy. No test reads
the strings for case, quote marks or the degree sign. A check needs a written rule to
check against, and there is none.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 6 instances over the 148 releases they accumulated in, 0.041 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.041 x 15660 s | 635 s/release |
| form | a text lint over `strings.json`, `translations/*.json` and the card's STRINGS for title case, per-language quote marks and the degree sign, once the style rule is written |
| catch share q | 0.9: the lint reads every user-facing string; the residue is a rule the lint does not state |
| expected benefit, q x cost | 571 s/release |
| arm time | 0.2 s (`dev/audit/rounds/round11/D4/s3/m3_text.py`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 3.3 s/release |
| verdict | passes by 175.5x |

### Countermeasure (a class barrier, proposed; not built by this seat)

The lint is proposed behind a policy step: the owner writes the house style (sentence case,
per-language quotes, degree sign) into `D4-criteria.md`, which is owner policy, so this seat
proposes it and does not land it. The lint must then show the 6 + 3 + 27 + 2 counts on this
baseline and 0 after the copy fix. The fix PR owns the lint.
