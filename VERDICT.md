Fix review: merge 35cb7e8cc9380d134c61675a4aedba692e938593

bus-nonce: e8bf3d86436d0e9b5d67d1b3a2ea935e

## Round

Round 2: a re-dispatch at the same head. The earlier block (a dangling owner) is answered: R10-ROUTING-INVARIANTS is on the roster at 50c690758, which is an ancestor of origin/handoff/audit-r10-roster. Its brief carries the consumed-vs-pending design (`mark-carry`, STRANDED), which is the design P58 defers to.

## Scope

The dispatch frames this PR as a policy change. The diff is not one. It adds two files, `dev/programme/triage/s6-batch4.md` and `dev/programme/delivery/2734.md`, both under `dev/programme/`. No path in CLAUDE.md's policy set, `.claude/rules`, `dev/governance` or any brief is touched, so there is no owner policy wording to check line by line. The owner's words matter in one place, P60, which cites the "mechanise first" directive (2026-10-24) as the reason for reversing P50. That reversal is argued from 5 measured slips, not from the directive alone.

## Evidence

- Head measured: 35cb7e8cc9380d134c61675a4aedba692e938593. It is still the head of triage/s6-batch4, and it is the head the PR body names.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 (tree 84908aa09). There is no conflict and neither claim file is touched.
- Mutation proof: n/a, because the diff has no production line. I mutated the consumer instead: with P55's `Verdict:` line removed, `ruling_verdict` returns `unreadable` and `triage_refusal` refuses a cite of `#P55`. Unmutated, it returns None, so no refusal.
- Null control: `ruling_verdict(P99)` returns None, as the body claims.
- Figures:
  - Verdict counts re-derive: 4 ACCEPT, 5 DEFER.
  - P54's count re-derives at bbe44258e: 38 open owner-gated groups, 35 of them citing a mandate id (19, 9 and 7 per id), plus the three named groups that cite none. I used my own python filter, following the body's stated rule (truthy `owner_gate`, stage not done).
  - The same filter on the current roster (50c690758) gives 43 and 39. That is a later snapshot; the body names its ref.
  - `orchestrator_tick.py` lines 1804-1823 are the owner-gated block, as cited.
  - R10-FLOW-MQ-PROBE's `owner_gate` text is quoted verbatim and correctly.
- Not re-derived: P55, P57, P58, P61 and P62 instance counts. The file itself marks them as the orchestrator's account and not re-counted. P62's three run SHAs were not checked.
- Owners: every DEFER/ACCEPT owner group exists at 50c690758. The two new groups P55, P60 and P61 create (R10-FLY-POOL-INSTRUMENT, R10-FLY-RECORD-BEAT) do not exist yet. That is the stated route: `roster_edit.py` refuses them until this ruling is on main, as with batches 1 and 2.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched.
- CI: the head has 52 check runs across runs 40102153485 and 40102154724. All are success or skipped and none is red, so step 11 has nothing to answer; the body's `## Red checks: none` is accurate.

## Findings

- P62's verdict line points at `carries/carry-triage-s6v9.md`, which exists nowhere: not on the head, origin/main, the roster branch, or any remote ref. Repo carries are `dev/programme/carries/carry-<n>.json`. The PR body's `## Forward-carry` says n/a and routes the ACCEPT through roster_edit after the merge. Substantively, R10-CI-LAYOUT-P2 already holds carry (f), which describes the same codescan_wait `no run` fast-fail: make it wait up to WAIT_MAX_S, and run a re-run-before-CodeQL control. The finding therefore has an owner, and only the pointer dangles. The roster op that records V9 should cite `dev/programme/triage/s6-batch4.md#P62` and fold into or reference carry (f), not the missing file. Carry: R10-CI-LAYOUT-P2
