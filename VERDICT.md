Fix review: merge fdab889cedf99332ce48b86347eb271d1bea4787

bus-nonce: 3627190069bbeff46b3a0557d3566914

Round 2 delta review of bd93b563..fdab889c (resume: probe/revt-r10-hotfix-replay-class-cut-ae4ddd06@ae4ddd06f2f5, round 1 merge, not redone).

## Evidence

- No pull request and no CI exist yet, so no review packet or CI state was available.
- Delta is one file, dev/audit/rca/R10-RCA-REPLAY-CLASS-RERECORD.md (+39); no code, no goldens, no claim files (ev/delta-stat.txt).
- `git merge-tree --write-tree origin/main fdab889c` is clean (tree 0b39f04c).
- Body Head section names fdab889cedf99332ce48b86347eb271d1bea4787; its Forward-carry carry is `dismissed:` (built in this PR), so nothing for the roster.
- RCA shape: named cause (re-record unit is the drawn class; level shift on undrawn classes), process state (c), countermeasure level_shift_offenders, demonstration table. Re-ran `replay_draws.py shift` at the head: d08ed31049 table with --no-cuts red (ref31/38/40/53 shown in the tail; doc lists ref23/28 too); 6715d97332 and 078780e687 green, 7 classes examined; head green with 7 classes; head --no-cuts red. Matches the doc and body.
- Red checks: body claims none owned; owed-reds printed main-wide names (coverage-ratchet, fast 3.14, mutation, typing, validate-hacs) that I did not tie to this diff, which touches only a markdown file.

## Findings

- Follow-up: the RCA's Cost section gives only the countermeasure's cost ("one pass over a 7-class TSV, no extra CI job") and no cost(defect) x P(recurrence) figure, and there is no explicit class-reach search, though the demonstration shows six classes affected. root-cause.md section 4 asks for numbers; the countermeasure is a few lines in an existing test, so it passes any plausible test and the omission does not change the outcome. Carry: dismissed: countermeasure cost is negligible and already built; documentation gap only
