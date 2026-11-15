Fix review: blocked 7caa9f561c3f9407b060b579c7a2c512d223bc8d mutation-vacuous: m6-dr-fetch-unreadable m25-dr-timeread-unreadable m12-ud-cp m24-dr-cp m22-ledger-arm m23-ud-wipseat m16-op-stuck3

bus-nonce: 96fc18b257add4f1f71d1b9c2591b72d

Round 1 (first review of #3635, head 7caa9f561c3f9407b060b579c7a2c512d223bc8d = 441f741b9f plus a clean merge of main 31117b1029 plus the delivery row).

## Block

Each mutant below changes a production line this PR adds. `orchestrator_tick.py --self-test` stays at 356 checks, 0 failed for all of them, and so do `ledger.py --self-test` and `owed_unactioned.py --self-test` where those apply. The driver is `ev/mutant_driver.py` and its output is in `ev/mut*.txt`. Each one needs a pin that turns red:

- m6-dr-fetch-unreadable and m25-dr-timeread-unreadable (`Tick.design_reviews_owed`): carry 4 (1) requires that "a failed read is UNREADABLE, never an empty list". m6 deletes the fetch-failure UNREADABLE return. m25 replaces the commit-time-failure UNREADABLE return with `continue`, so the tick would then raise a KeyError. No arm exercises either UNREADABLE path.
- m24-dr-cp (`ledger.design_reviews_owed`) and m12-ud-cp (`Tick.undispatched`): carry 4 says "Use the CP mark as DESIGN OWED does", and carry 3 (a) says "CP-marked the way designs_owed marks". Both mutants remove the ` CP` mark and survive. The UNDISPATCHED arm accepts either `UNDISPATCHED: CP R10-OI` or `UNDISPATCHED: R10-OI`, and no DESIGN-REVIEW OWED fixture is on the critical path.
- m22-ledger-arm (`ledger.ARMS` loses `("refs/heads/design/", "design-review")`): design choice (1) in the body says this ARMS entry is what makes a design-tip disposition recordable. The disposition arm writes `dispositions.tsv` directly and never goes through `ledger.py dispose`, so the arm still passes after the entry is removed.
- m23-ud-wipseat (`SEAT_REFS` loses `refs/heads/handoff/*`, and the next entry after it): the `ls-remote` stub matches on argv containing `refs/heads/dispatch/fixer-*` and returns the planted refs whatever patterns are passed. That leaves the seat-ref set used by UNDISPATCHED and OUTSIDE-CHAIN-IDLE unpinned. Once the mutant drops `handoff/*`, a group whose only seat is a handoff ref would be reported as seatless.
- m16-op-stuck3 (`_opener_last`'s `n >= 3` changed to `n >= 1`): the arm "below three failures, no STUCK" uses a topic (`r10-live-1`) with no `fails.json` entry at all. It never plants n=1 or n=2, so the threshold is unpinned.

## Findings

- Follow-up: OUTSIDE-CHAIN-IDLE is in `beat_jobs.FAMILY` (the board's actionable set) but not in `owed_unactioned.FAMILY`, so `owed_unactioned.py` never counts an unactioned outside-chain line, and the repair-discharges census, which reads only `owed_unactioned.FAMILY`, cannot see it. The same holds for the flagged `OPENER ABSENT` line, which is in neither family. Design choice (5) in the body sets the census population to `owed_unactioned.FAMILY` and does not mention these two flagged kinds. The owner's directive that outside work never slips points to OUTSIDE-CHAIN-IDLE being an owed obligation. Carry: R11-PRE-ACK-COMPLETION

## Evidence

- CI: `merge_train.py classify 7caa9f561c3f9407b060b579c7a2c512d223bc8d --pr 3635` gave `GREEN 7caa9f561c3f9407b060b579c7a2c512d223bc8d pending: none red: none` (rc 0, 2026-11-15T23:00:25Z; `ev/classify.log`).
- Merge: `git merge-tree --write-tree origin/main 7caa9f561c` exits 0 at origin/main 31117b1029 (tree 61b91caff2) and again at 5825e1346c, so there is no conflict. The PR head was still 7caa9f561c at verdict time.
- Role contracts: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract at the head is current.
- The body's named mutants, re-run at the head, are all killed: the dispatch-time clause (m1), the stage gate (m2), `SEATLESS_STAGES = UNBLOCKABLE_STAGES` (m7), and dropping `DESIGN-REVIEW OWED:` from owed_unactioned.FAMILY (m20, which turns the census red). My extra mutants are also killed: m3 (disposition), m4 (verdict at tip), m5 (call dropped), m8 (after-clear `all`→`any`), m9 (start-after), m10 (ref age), m11 (ls-remote UNREADABLE), m13 (seat window), m14 (gates filter), m15 (outside filter), m17 (newest log line), m18 (OPENER ABSENT only when stranded), m19 and m26 (owed_unactioned keys), and m21 (beat_jobs FAMILY entry, killed by `beat_jobs.py --self-test`).
- Figures re-derived at the head (`ev/selftests.txt`): orchestrator_tick 356/0 matches; owed_unactioned 60/0 matches; ledger 104/0 matches; the base 98847b99d7 orchestrator_tick 319/0 matches, and the base has none of the four new literals (0 grep hits); `tests/structure.py` prints STRUCTURE RATCHET PASSED; the census command lists 13 kinds, split 4 armed and 9 debt as the body says.
- Note: figure: the body's `python3 tools/audit/seat/beat_jobs_selftest.py: exit 0` is vacuous. That file has no `__main__` and runs nothing. The real entry is `python3 tools/audit/seat/beat_jobs.py --self-test`, which reports 251 checks, 0 failed at the head.
- Versions and claims: `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files are untouched in the three-dot diff, and the diff includes no golden fixture.
- Finder's harness: none is committed. The body says the measured replay (2026-11-11T05:06Z ref state) cannot be reproduced and stands the self-test fixture in for it. I could not re-derive the replay's three-group figure either.
- Red checks: none at the head, so no answer is owed.
- Head: the body's `## Head` names 441f741b9f and states that 7caa9f561c is the head with its code unchanged. `git diff 441f741b9f 7caa9f561c` touches only main's merged files and the delivery row.
