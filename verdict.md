Fix review: blocked 09ad7e4f750bfee78b18221d68eae0580fef3d3a carry-missing: pr-contract red on carry_audit, Friction item e9ceb9fc routed to a file path and Forward-carry 'none: <reason>' not an allowed none; body says Red checks none

Round 1. Measured at 09ad7e4f750bfee78b18221d68eae0580fef3d3a (ev/HEAD.txt). Role file current (roles/ diff vs origin/main empty).
Group brief R10-TICK-RELAY-DECOUPLE (handoff/audit-r10-roster) names no committed finder harness; it prescribes the tick_loop.sh --self-test arm, so that arm plus the committed r10_seat_selftests_mutants.py is what I ran. No finder harness exists separately (step 9: noted).

## Blocking
- pr-contract is red at this head in both runs (jobs 119179639837 and 119179813053). The cause is `tools/audit/carry_audit.py check`: `CARRY-AUDIT: 2 finding item(s): 0 routed, 2 unrouted`.
  - `## Forward-carry` reads `none: <reason>`. NONE_ITEM accepts only a bare `none` or `n/a: <reason>`.
  - The `## Friction` seat_venv item carries `Carry: tools/audit/seat/cloud-setup.sh`, which is a path. It must be a GROUP, #issue, O-brief or `dismissed: <reason>`.
  - Reproduced locally with main's carry_audit.py (ev/carry_audit_main.txt, rc=1).
- `## Red checks` says none while pr-contract is red. The fix is a body edit only: use `n/a: <reason>` or bare `none` under Forward-carry, and give the friction item a real destination. No code change is needed.

## Verified
- Mutation proof (step 1): `r10_seat_selftests_mutants.py S26 S31 S32 S33 S34` gives every mutant KILLED, with failure counts 3/4/3/1/4 as the body says, and `RESULT survivors=0` (ev/mutants_head.txt). S34 restores the base's serial relay and fails the brief's arm, so the arm fails on the old loop and passes on the fix.
- Null control: `tick_loop.sh --self-test` gives `8 checks, 0 failed` (ev/selftest_head.txt).
- Merge (step 13): `git merge-tree --write-tree origin/main` exits 0 with no conflict (ev/merge_tree.txt).
- VERSION, manifest and notes are untouched: pr-contract's own `no version edit` line.
- No claim, golden or budget file is in the diff (step 4/14 n/a).
- Seams (step 6): the body's git-grep rule. The only executing relay call site is tick_loop.sh tick_pass, and it is in the diff.
- CI at this head: everything except pr-contract is green or skipped. nightly-status is red, but it grades main and the diff does not reach it. coverage and CodeQL python were still in progress when read.

RESULT mutants=5 killed=5 survivors=0
RESULT selftest=8 failed=0
RESULT merge_tree_exit=0
RESULT carry_audit unrouted=2

bus-nonce: ce9a722a1ecbc50d6fb84a715cc84566
