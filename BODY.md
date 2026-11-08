Root cause fix for the roster drain's "stale-worktree trap" and its "HEAD ... is on no origin ref" cascade (round 10 root-cause seat, 2026-11-08). The sweep runner drain refused roster ops because the lint clone stayed at an older main; each refusal then stranded a local commit in wt-run and refused the next op for that op's fault.

Cause, in tools/audit/seat/roster_queue.py `_run_op`: (1) the lint refresh (fetch, detach) ignored return codes and read the lint clone's own origin/main, a different ref from the edit checkout's origin/main that roster_edit.lint_gate compares; four attempts in a row stayed stale (main-lint's origin/main reflog: no update 11:40 to 14:34 +0100 while the edit checkout saw 4a9d2d5 and bb7dfb9). (2) A refusal other than "not origin/main" left its edit as a local commit in the worktree. Why the clone's fetch did not move is not established; the fix does not depend on it.

Process state (defect-root-cause.md): (c). The check existed (the lint gate, the retry on "not origin/main") but the refresh feeding it was unchecked and read another ref.

Fix: `refresh_lint` detaches the lint clone at the edit checkout's origin/main SHA after a fetch there, verifies HEAD equals it, and refuses by name ("lint clone not refreshed") otherwise; a final refusal removes the worktree. Self-test gains 2 checks (54 checks, 0 failed). Harness committed at dev/audit/harnesses/roster_queue_stale_lint.py.

Cost test: defect about 5 min hand-landing plus about 20 min pass delay per stale refusal, 172 of 1327 drain report lines (13%) were cascade refusals, 3+ instances on 2026-11-08; countermeasure a one-time diff of about 40 lines and about 50 ms per op, no extra network call. cost(countermeasure) < cost(defect) x P(recurrence).

## Head

353e852db5b10772e94f001a86e79af0f263cc95

## Mutation proof

Pre-fix roster_queue.py (git show bb7dfb9bd6:tools/audit/seat/roster_queue.py) under the harness, stale lint clone (its fetch fails), then main moves between ops:

```
roster: set-stage G refused rc=3 LINT GATE REFUSED the push | --lint-cwd is at 14053059bc7f, not origin/main (b1810f0b0dd6): the stale-worktree trap
roster: set-stage G refused rc=2 REFUSED: /tmp/tmpt23p5h0l/wt HEAD d91f2c4d9b3e is on no origin ref
RESULT: FAIL
```

## Null control

The fixed tree on the same harness: the lint clone also lags, and main moves between the two ops (a healthy tree moving on). Both ops push.

```
roster: set-stage G pushed f66ba38cc
roster: set-stage G pushed 7a4f1ccd0
RESULT: PASS
```

## Figures

- 1327 report lines, 786 pushed, 172 no-origin-ref cascade, 2 stale-worktree, 30 lint TOTAL refusals: python3 -I dev/audit/harnesses/roster_queue_stale_lint.py prints the old/new runs; the counts are from the sweep runner's roster-rep.txt (outside the tree).

## Red checks

none

## Forward-carry

none

## Friction

none
