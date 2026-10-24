Fix review: blocked 35cb7e8cc9380d134c61675a4aedba692e938593 dangling-owner: P58 defers to R10-ROUTING-INVARIANTS, a group on neither the roster nor main

bus-nonce: c1e7fd5ca18d8c993f8be4a4a41ac395

Round 1. Measured head 35cb7e8cc9380d134c61675a4aedba692e938593 (still the head of triage/s6-batch4 at 2026-10-24T14:29Z).

## Block

P58's verdict reads `DEFER -> R10-ROUTING-INVARIANTS`, and its trigger is "judge the consumed-vs-pending marker design when it lands". No group of that name exists on `handoff/audit-r10-roster` at `bbe44258e` (the ref the body names) or at its tip `8fe56f088`, and `git grep ROUTING-INVARIANTS origin/main 8fe56f088` returns 0 hits (ev/destinations-roster-8fe56f088.txt). Under proposal-triage.md a DEFER names "what would change the answer, or the group already owning the item". The ruling names an owner, so a later seat will read V5 as owned, but nothing owns it, and no seat will see the design land and re-triage. The other DEFER destinations all resolve: R10-ORCH-ROSTER-SCHEMA, R10-FLY-DAEMONIZE-ARGV and R10-ORCH-BEATD are present. Fix: name the group that is actually building V5. The "owner note that V5 is already being built" suggests one; R10-FLY-CARRY-DISPOSITION is a candidate, but I did not verify that. If no group is building it, the destination has to be dropped and the trigger restated without an owner.

## Findings

- P58 names a nonexistent owning group. The block above gives the evidence. Carry: dismissed: it is this PR's to fix before merge, and the block returns it to the fixer.
- P55 and P60 give the same new group, R10-FLY-POOL-INSTRUMENT, contradictory briefs. P55 says "about 15 lines in one existing script, no new file" and rejects a new pool_push.sh as "a file for one call site". P60 says "one new script with a self-test, one INSTRUMENTS.md entry, a call in cloud_dispatch.py". The commit history (58f2e7513 "re-rules P55") shows P60 superseded P55's scope, but P55's text still states the narrower brief, so a fixer reading both gets two scopes. Fix in the same pass: mark P55's Cost/Binding as superseded by P60, or reconcile them. Carry: dismissed: same-PR fix, rides the P58 correction.
- The title and intro are stale. The H1 reads "batch 4 (P54)", and the intro says the items are "ruled as P54", but the file rules P54 to P62. Carry: dismissed: a cosmetic heading; fix it in the same pass if touched, otherwise not worth a cycle.
- Two owner citations do not resolve, and the brief asked for every owner quote to be checked. I found neither in #201's comments from 2026-10-23T10:23Z to the latest at 2026-10-24T14:05Z: P60's "owner directive 2026-10-24 (mechanise first)" and P58's "owner note that V5 is already being built". Both may live in the out-of-tree proposals.md. Neither is load-bearing: P60's Binding rests its reversal on the five measured slips ("Reversal is on measured slips"), and P58 is a DEFER. Carry: dismissed: not load-bearing; the next revision should cite a comment id or the proposals.md line.

## Evidence

- Policy scope: the diff is `dev/programme/triage/s6-batch4.md` (+95) and `dev/programme/delivery/2734.md` (+1), three-dot from merge-base `e97f5749b`. Neither path is policy under CLAUDE.md: dev/programme is not listed, `tests/closure.py` lists it INERT, and no binding sentence in any policy file changes. The brief's "POLICY CHANGE" label therefore applies only to the owner-quote check, which is reported under Findings.
- Merge: `git merge-tree --write-tree origin/main 35cb7e8cc9380d134c61675a4aedba692e938593` exits 0 against origin/main `e97f5749b`, with tree 54f3498b1 (ev/merge-tree.txt).
- Head: the body's `## Head` names 35cb7e8cc9380d134c61675a4aedba692e938593, and it matches what I measured. The code head is `58f2e7513`, with merge-base `9586fce08` against origin/main, as stated. The merge commit `f6a42ff9f` is a clean merge of e97f5749b.
- Figures re-derived. The verdict counts are 4 ACCEPT and 5 DEFER, matching the body. The owner-gated open groups at roster `bbe44258e` number 38: 19 cite 6175172275, 9 cite 6319294694 and 7 cite 6329234399, and 3 cite none (R10-REPLAY-SCOPED, R10-MERGE-SUBJECT-HARDEN, R10-STRUCTURE-ALIAS), all matching. R10-FLOW-MQ-PROBE's owner_gate reads verbatim as quoted. `orchestrator_tick.py` has "# owner-gated age" at line 1804 on main, and the block runs to the flag at about 1823, matching. I re-derived these with my own python filter, since the body names no committed script (ev/owner-gate-count.txt).
- Consumer and null control: `roster_edit.ruling_verdict` at the head returns the listed verdict for P54 to P62 and None for P99 (ev/ruling_verdict.txt). The mutation proof is n/a as the body says: there is no production line.
- P62's instance SHAs (3383fb2a, 04860ee0, ea459c0b) resolve as commits. `tools/ci/codescan_wait.py` exists on main, and its owner R10-CI-LAYOUT-P2 is on the roster as carries-open. The cited `carries/carry-triage-s6v9.md` is in no tracked tree or remote ref I could read. I take it to be the orchestrator's out-of-tree queue file and did not verify it.
- P55 and P58 instance counts come from the orchestrator's proposals.md. The file itself marks them "not re-counted", and I could not re-derive them.
- VERSION, the manifest version and the notes heading are untouched; the diff has two files.
- CI at this head (check-runs API, 2026-10-24T14:2xZ): 6 runs (prelude, refresh and cancel-superseded, in two workflow runs), all `queued`, none concluded. `gate` had not reported. There is no red check to answer.
