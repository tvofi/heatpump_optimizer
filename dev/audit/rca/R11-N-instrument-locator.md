# RCA: an audit instrument that reports the wrong line

Seat: round-11 root-cause, class `N-instrument-locator` (instrument). Instances R11 1, 1 in all, which meets the per-round, cross-round trigger. The trigger counts the classes minted in R11 with the same nearest class (`I4`) as one (`fold_ledger.py` `_group_counts`): `N-instrument-locator`, `N-unordered-tiebreak`, `N-untranslated-splice`, 11 instances together. Tree: `handoff/audit-r11-register` at `0a7ea717c`; the round's baseline is `92d38ecb6`. This seat fixes nothing and builds no barrier.

## Root cause

### Cause

`tools/audit/text_ledger.py:scan_c_like` loses one line each time a non-template string
literal stops at a newline (`break` before `line += 1`, then `i = j + 1` consumes the newline). So
the `line` column of 1175 of 1899 JavaScript comment units does not hold the unit's text. Every D5
seat that cites a ledger line cites the wrong site. The scanner was added in `e130ee97a`
(2026-11-13), three days before this round's baseline, and its self-test has no quote at a line
end.

### Evidence

Judged instances, as the round-11 judge reproduced them (`dev/audit/rounds/round11/JUDGE.json`):

- `R11 D5-s8-07` (verified, medium): planted copy: scan_c_like mislocates per file (tests/card.mjs 690, agreement.mjs 49, check-wave-script.mjs 59, ...) over 3099 comment units; verifier total 1175 of 1899 JS units; perturbation: --fixed: in scan_c_like, `line += 1` before the newline `break`, and on an escaped newline.

Re-run by this seat at `0a7ea717c`, single-threaded BLAS: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D5/s8/ledger_lines.py` took 0.9 s and exited 0. The seat ran it to time the standing cost of a gate form. It did not re-grade the judged number, which is the judge's.

### Class search

The R11 sweep (`dev/audit/rounds/round11/sweep-N-instrument-locator.json`) lists 1 seams. The ledger carries 0 of the seams as instances beyond the finding. Its enumerator is cited as `python3 dev/audit/rounds/round11/D14/N-instrument-locator/enumerate.py tools`. That program is not in the tree, and `git log --all` finds no commit that ever touched its path. So the class search cannot be re-run from the tree, and the counts here are the sweep's as recorded. Of the 27 round-11 sweeps this seat read, 26 cite an enumerator that never reached origin.

### Process state: (a) the process did not exist

D5's briefs take their universe from this instrument (`dev/governance/dimensions/D5.md:14-15`),
and no step or check compares the location it reports with the text at that location before seats
cite it. The instrument is three days older than the round's baseline, so no earlier round read
it. Its self-test fixtures never put a string literal at a line end.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`, in wall-clock seconds per release.

Inputs shared by every round-11 record, measured at `92d38ecb6`:

- Releases from `v4.0.0` (2026-08-26) to `v10.0.2`, the baseline's last tag: 148. First-parent PRs in that span: 2409, so 16.3 PRs per release.
- cost(defect): the round-9 per-finding fix cost, 4.35 h (#1718: 21.75 h over 5 findings), the figure round 10's records used. It is a lower bound for a high or critical instance's field cost, and an upper bound for a style finding.
- P(recurrence): the class's 1 instances over the 148 releases they accumulated in, 0.007 per release. This is an estimate, because instances found late are dated by the round, not by their merge.

| term | value |
|---|---|
| expected defect cost, 0.007 x 15660 s | 106 s/release |
| form | a class barrier over instrument locators |
| catch share q | 0.1: locator correctness is per instrument and per lexical state; a generic arm would have to re-lex every language each instrument reads |
| expected benefit, q x cost | 11 s/release |
| arm time | 0.9 s (`dev/audit/rounds/round11/D5/s8/ledger_lines.py`, re-timed by this seat) |
| standing cost, arm x 16.3 PRs | 15 s/release |
| verdict | fails: standing cost is 1.4x the expected benefit |

### Decision not to build a class barrier

Decision: no class barrier. The fix repairs `scan_c_like` and adds the self-test arm (a quote
at a line end, an escaped newline) that asserts the text at each reported line. That arm closes
this instance. The general rule, that an instrument emitting locations asserts the text at one
location per lexical state in its self-test, belongs in the instruments guide
(`tools/audit/seat/INSTRUMENTS.md`). This record proposes the sentence there through the owner and
does not land it.
