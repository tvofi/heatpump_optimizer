Round 10, s6, merge record 2026-10-24 (main at e8a08cf9e).

Merged since the last record:
- #2690: main ci-ratchet hotfix (run-title keying, repo-wide artifacts listing). Review deferred per the owner's hotfix ruling, done after merge.
- #2683: R10-INPUT-STALENESS, critical path. Closes #2234. The train ran without --pre-flight under mandate 6329234399, because carry_audit read a review heading as a findings section (4 false-positive items). Carried to R10-FLY-CARRY-DISPOSITION.
- #2693: proposal-triage rulings, s6 batch 3. P53 carried to R10-FLY-OPENPR-ATOMIC.
- #2687, #2694, #2695, #2699: delivery-row records.

Roster: R10-CLOSEOUT-CLEANUP added as the last group. R10-ARCH-DOCS is ordered after every non-done group, and R10-ROUND-PLAYBOOK after ARCH-DOCS.
Fourteen handoff/r10-ci-layout-p2-* refs (27 code and body branches) were archived as archive/* tags. Twelve units had landed in #2673; two were probes.
Production triage (D15, the owner's 7.0.4 bundle) gave three carries:
- R10-SAV-COMFORT: savings volume mismatch.
- R10-COP-GATE: observed-COP latch on a pump-initiated hot-water interval.
- R10-DIAG-REPLAY: incomplete redaction in the bundle.
