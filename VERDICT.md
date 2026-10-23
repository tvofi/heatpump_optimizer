Fix review: merge 5c640992a0c816a726086e34e7f2f1e536b44b34

bus-nonce: 54dfcab55a587fb155f527c888e64315

PR #2671, group R10-ORCH-LEDGER. This is round 3 by the dispatch's count; the body numbers the merge as "round 4". Measured from a detached worktree at 5c640992a0c816a726086e34e7f2f1e536b44b34, whose merge base with origin/main is f046076ad (origin/main's tip). Re-read at post time: still the head. `dev/governance/roles/` is current (`git diff <merge-base>...origin/main -- dev/governance/roles/` is empty).

Prior rounds: no earlier `Fix review:` verdict exists for #2671. The PR has 0 issue comments and 0 reviews, there is no `review/2671` ref on origin, and `$HPO_BUS_STATE/reviews/2671` does not exist. So no prior finding was left to check as cured. The round-3 CI reds that the body names (`wave-script`, `instrument-self-tests`, `pr-contract`) are green at this head.

## Conflict resolution against #2664 (the merge in 041b22d60)

- Diff against main, `tools/audit/seat/cloud_relay.sh`: `relay()` keeps #2664's non-fast-forward loop (3 tries, no force), its tree-matched `review_tip` confirm and `last_line`. The only changes are `ledger_open verdict-unposted` after the push and `owed` -> `unposted` (stderr). `confirm_arm`, `probe_arm`'s retry/refusal level and `tick_loop.sh pass --confirm` are byte-identical to main. No `owed` caller remains.
- #2664's finder harness at head (`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-1..21 tick_loop-3`, slot lease):
  RESULT harness=r10_seat_selftests_mutants killed=21 not_run=1 survivors=1 rc=1
  The only non-kill is `cloud_relay-8 NOT RUN (PATTERN FOUND 0 TIMES)`. This PR rewrote the failed-update line it targets (301515179). I planted the equivalent swap on the head's line: `FAIL a hold outranks a recorded failed update: still HELD`, 238 checks, 1 failed. So the guarantee is still pinned and only the harness pattern is stale (note N1). All of #2664's own plants (12-21, tick_loop-3) were KILLED.
- The one guarantee that moved is persistence of `<why>`. #2664 appended it to the log; here it is printed to stderr only (and to /dev/null under `tick_loop.sh`). It is not lost as an obligation. `confirm_arm`, which is unchanged, re-runs confirm on the next pass and writes `confirm-owed ... tries=n/3: <why>` to the level, and `verdict-unposted` stands in the ledger until a read-back. An unreadable ledger fails safe there: `disposed` returns rc 2, which is read as not disposed, so the ref is owed.
- My own plants on the merge's lines (my_mutants.sh, second head worktree, slot lease):
  RESULT mutant=M1-verdict-unposted-dropped rc=1 fails=3
  RESULT mutant=M2-unposted-silent rc=1 fails=2
  RESULT mutant=M3-review-arm-dropped rc=1 fails=1 (a disposed review is not owed)
  RESULT mutant=M4-kinds-dropped rc=1 fails=1 (ledger census)
  RESULT mutant=M5-confirm-why-dropped rc=1 fails=1
  RESULT null rc=0 cloud_relay self-test: 238 checks, 0 failed
- Import of #2664-shape log lines (`OWED <utc> <pr> <sha|-> <why>`) gives `verdict-unposted` with nothing refused (import-readback-probe.log).

## Self-tests and instruments at head

RESULT cloud_relay=238/0 ledger=56/0 orchestrator_tick=207/0 ref_privacy_selftest=90/0
RESULT r10_ledger_class_reach ledger=present writers=15 events_uncleared=0 level_writers=10 level_unkinded=0
RESULT ref_privacy_check refused=0 selftest_wiring wired=91 unwired=0 carry_audit routed=8 unrouted=0

The body's figures match except `ref_privacy --self-test`, which is 84 in the body and 90 here. The body took that figure at code head 041b22d60. Main f046076ad then changed ref_privacy.py in the head's second merge.

## The entities.py claim

`tests/entities.py` at main f046076ad, run on this host under the exclusive lease with Python 3.13: `5 of 2409 ENTITY CHECKS FAILED`. Four of them are the same four `hb:positive_control` py-spy arms the fixer's head run lists: "survives one hung py-spy sample", "a try whose sample misses the spin ... is retried", "the control rests between tries [two tries took 0.80s against a 1.0s rest]", "survives two hung samples". The fifth ("the coverage job reuses only an entry main's push run saved") is on main only. Apart from that line, the FAIL-line multiset is identical between main and the fixer's head log. The claim holds: the failures are pre-existing and outside the diff.

## Checks (contract steps 4, 5, 7, 10, 11, 13, 14)

- VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched (three-dot diff is empty). `git merge-tree --write-tree origin/main HEAD` exits 0.
- The body's `## Head` names 5c640992a.
- Forward-carry: all six LANDED texts are present on `origin/handoff/audit-r10-roster` at 42e45f420. P33 is on R10-ORCH-LEDGER's own entry.
- CI at head: 42 runs, all concluded, and only `delivery-status` is red. The diff touches `governance.yml`, so that red is this PR's to answer, and `## Red checks` names and answers it. `pr-contract` started at 22:29:40Z, after the red concluded (21:57:51Z), and passed.
- Metrics: `tests/closures.json` gains +3 INERT READS entries from `ci_predict --apply-inert`, and no budget moved.

## Non-blocking

- N1: `dev/audit/harnesses/r10_seat_selftests_mutants.py` `cloud_relay-8` no longer finds its pattern at head (1 occurrence on main, 0 here), so the harness exits 1 (`survivors=1`) where main's tree lets it run. Nothing in CI runs it: it is only an inert read of `tests/harness_headers.py`. The fix is to re-target the plant at the head's line `if [ -f "$f" ] && grep -qxF "$topic $hs" "$f"; then level_line handoff-update ...; continue; fi`. Control: the swap is killed by "a hold outranks a recorded failed update". Carry: R10-ORCH-LEDGER
- N2: a migrated `verdict-unposted` (imported from a log OWED line) cannot be closed by a read-back. Its text is the journal line and its sha is `-`, so `text in readback` never matches and the head-move close is skipped. Measured with `ledger.fold`: imported row, matching read-back -> open=1; native row -> closed read-back=1; imported row with the PR gone -> closed subject-absent=1. It over-owes (fails safe) until the PR closes or `ledger.py close verdict-unposted <pr> -` runs. The body's design list does not disclose it. Carry: R10-ORCH-LEDGER
- N3: `## Red checks`' `delivery-status` line cites `#2639` at 12 commits, from an earlier head. At this head the run prints `DELIVERY STATUS OVERDUE — 40 rowed, 12 pending, 8 overdue (overdue at 12 commits)`. The diff writes only its own row, `dev/programme/delivery/2671.md`. The answer stands; the cited row is stale. Carry: dismissed: main's overdue rows, the orchestrator's drain
