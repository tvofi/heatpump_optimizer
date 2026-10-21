Fix review: merge baa75f58ae7f9c00334d92da24d3285e1b047277
bus-nonce: 62e80093323cb8e7517825ba8e2aaca0

Measured head baa75f58ae7f9c00334d92da24d3285e1b047277 (authored code head
31529479, plus the origin/main 3b941800c merge and the delivery-row commit).
Every number below was re-taken at that head; load1 2.9-7.8.

RESULT | precedence and fail-to-0 | PASS. `$HPO_GATE_PRIORITY` > `.gate-priority` >
derived > 0. Live: a listed group answers 1; this branch (unmapped), an unlisted
group, a ref without the file, a nonexistent ref, and a throwaway repo with an
empty list / non-list / non-string item / non-JSON / no `critical` key all answer
0, no crash. A malformed override is skipped to the next channel (documented) --
it never yields a silent 1 from unreadable input.

RESULT | derivation reads the ref | PASS. `_roster_ref` fetches
`origin/handoff/audit-r<N>-roster` at call time and both `show_roster` and
`critical_path_groups` read that ref; a listed group 1, unlisted 0.

RESULT | aging cannot starve | PASS. 69 < 600 < 1800 (SLOT_MIN_SECONDS,
PRIORITY_AGING_SECONDS, LEASE_SECONDS). An aged normal waiter overtakes a younger
urgent one at the window and is FIFO-by-priority one second short (null control);
the normal waiter still takes after the urgent one, not starved.

RESULT | slot lifetime | PASS. A live holder past its lease keeps its slot (fifth
blocked); a dead holder is reclaimed at once, including before its lease expiry;
a no-pid expired slot is freed while a no-pid fresh one is respected;
`slot-status` `past-lease=N` and `unleased=N` both driven and the marker
round-trips and prunes a dead pid.

RESULT | mutants | PASS. Re-ran all nine at this head: each rc=1 on its named arm,
none crashed (a ordering, b rewrite, c aging, d malformed, e derived-always-1,
f derived-always-0, g live-holder expiry, h names_pid=False, i witnesses).

RESULT | rollout boundary | PASS. The body states plainly that a peer running
main's `gate_lock.py` can still steal an expired slot, observed live, and that the
guarantee starts when every seat runs this tree.

RESULT | acceptance and base harness | PASS. `gate_lock.py --accept` 29/29;
`r10_gate_priority_base.py origin/main` shows 8 of 12 red with the four named
green at both ends; `gate_priority.py --self-test` 12/12; `roster_lib.py
--self-test` 24/24.

RESULT | policy, budgets, architecture | PASS. `gate-scoping.md` measures 61 lines
and 792 tokens against caps 61/794 (recorded caps untouched); `rules_sync --check`
ok; `structure.py` PASSED; archscore dS +0.0000 NULL.

RESULT | body checks | PASS. `prepr.sh` with PREPR_SKIP_CLOSURES=1: no REFUSE,
`PRE-PR: baa75f58...`; `carry_audit pr 2526` 1 routed / 0 unrouted; `figure_lint`
8 resolved / 0 refused; `## Head` names the measured head and records the closures
skip; `## Red checks` answers the local `harness-headers` red.

RESULT | checks | PASS. Every head check-run is green except `nightly-status`,
which reports main's scheduled `slow` job (run 39387919507, head 0c298f6,
"slow failed last night") -- exempt per defect-root-cause.md, not this PR's.

NOT ESTABLISHED. (1) A stale-but-present `critical-path.json` keeps granting 1:
the fetch refreshes the local mirror, but `at` is never read, so a set published
weeks ago still decides priority; the body states only the missing/malformed
direction. The 600 s aging bounds the harm done to a waiting normal ticket, but
not the wrong default itself. (2) No #201 comment carries the forward-carry:
`gh api repos/tvofi/heatpump_optimizer/issues/201/comments` returns 0 comments
mentioning `critical-path.json`, "critical path set" or #2526, though the body's
`Carry: #201` marker routes it and `gate_priority.py`'s docstring states the
republish duty. (3) A reused pid would hold a pool slot past its lease with
`past-lease` the only witness -- acknowledged conservative in `_orphaned`'s
docstring.

POLICY. `dev/governance/rules/gate-scoping.md` and its generated copies are policy;
`@tvofi` approves this under mandate 6175172275.

HEAD RE-READ at post time: baa75f58ae7f9c00334d92da24d3285e1b047277 (unchanged).
