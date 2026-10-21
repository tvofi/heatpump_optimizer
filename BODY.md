prepr's `closures` step (6b) recorded the scoped closures on every platform, including a Darwin seat. CI's
required `closures` context and `closures-autofix` already own that check: the context re-records on
ubuntu and runs `tests/closure.py check --partial` over the recordings, and the autofix commits the
recording when the committed table under-approximates. Off Linux the local recording buys only the round
trip that bot commit then costs, and it is the dominant cost of a handoff.

This change makes 6b default-skip off Linux. The skip line names CI's `closures` context and
`closures-autofix` as the owners and `PREPR_RECORD_CLOSURES=1` as the opt-in for a lane that needs a
first-green head. Linux is unchanged: every decision the step made before the predicate
(`closures_records_here`) stands, and a diff whose recordings are all left to CI still owes no recorder
interpreter. The `full` and `skip` cases are untouched and the self-test pins their printed lines
byte-identical.

Second arm, same function: the recorder now dies with the prepr. A stopped prepr used to leave
`derive_closures.sh` reparented and running to completion. Now the recorder runs in its own process
group, a TERM/INT trap reaps that group, and a watchdog reaps it when the top-level prepr is gone. That
last case is the one a command substitution's own trap never sees.

The policy half is `dev/governance/rules/gate-scoping.md` and its two generated copies, which name the
new default and the opt-in.

## Head

Measured at `7eee5b39e6099b67898e18f6a971947381c03621`. That is a merge (never a rebase) of `origin/main`
`03b49e1521a2490335922093c9177aec8f6119d9` (committed 2026-10-21T13:05:09+02:00, read
2026-10-21T11:36Z) into the previous head `a4f01a42154341293aaed52642434c12fab3322b`. The merge base
is now `03b49e152`.

The merge conflicted in `dev/governance/rules/gate-scoping.md`, in the gate-lease paragraph. I resolved
it as the union: main's "Priority, then arrival" (from #2526) replaces "First come, first served", and
this branch's wording of the same sentence stays (`slots;` and `` `$HPO_SLOT_LABEL` names the one it is
inside``). The generated `.claude/rules/gate-scoping.md` and `.cursor/rules/gate-scoping.mdc` were
re-emitted by `node tools/policy/rules_sync.mjs`, not hand-merged. `tools/pr/prepr.sh` auto-merged.

## Mutation proof

Each mutant is a copy of the head's `tools/pr/prepr.sh` with one edit, run as
`bash <copy> --self-test` from the head's worktree under the seat toolchain
(`/etc/profile.d/hpo-toolchain.sh`, Python 3.14). The fixed tree gives 321 passed, 0 failed.

- **M0, null: unmodified copy.** 320 passed, 1 failed: `FAIL a change to prepr.sh owes the self-test
  (got 1, wanted 0)`. The copy lives outside the tree, so this failure belongs to the runner. It appears
  in every mutant below and is not counted as a kill.
- **M1: delete `return 1` in `closures_records_here`.** That is the off-Linux predicate. 317 passed, 4
  failed: the M0 line plus
  `FAIL 6b leaves a scoped diff's recordings to CI off Linux by default, owing no recorder interpreter (got 1, wanted 3)`,
  `FAIL and the skip line names the CI context and the autofix job that own them (got 1, wanted 0)` and
  `FAIL and names the opt-in that records locally instead (got 1, wanted 0)`.
- **M2: delete the `PREPR_RECORD_CLOSURES` override line.** 318 passed, 3 failed: the M0 line plus
  `FAIL 6b's opt-in records off Linux for a lane that needs a first-green head (got 3, wanted 0)` and
  `FAIL and the opt-in still refuses a closure its recording does not cover (null control) (got 3, wanted 1)`.
  The other recording arms that name the opt-in stay green under M2. On this Linux runner `uname` still
  admits them; they would fail only on a Darwin seat.
- **M3: delete the reap block and restore the single-line foreground recorder launch.** 319 passed, 2
  failed: the M0 line plus
  `FAIL a TERM to the prepr leaves no recorder running behind it (the orphan this closes) (got 1, wanted 0)`.

## Null control

M0 above is the runner's null: an unmodified copy fails exactly one check, the same one in every mutant,
so every other failure belongs to its mutant.

The unchanged Linux path still records and still refuses. The self-test arm
`6b on Linux still records and still refuses an uncovered closure (null control)` passes at the head,
and so does the opt-in arm `and the opt-in still refuses a closure its recording does not cover (null control)`.
`M2` turns the opt-in arm red, which shows it is not vacuous.

What this pass did not re-take: the `closures` job running end to end on GitHub at this head, and a
live `derive_closures.sh` capture. CI runs the first on push.

## Figures

- Self-test totals. `bash tools/pr/prepr.sh --self-test` at the head printed `321 passed, 0 failed`,
  rc 0, in 2m57s wall time. Each mutant's totals and FAIL lines come from `bash <mutant copy> --self-test`
  (`## Mutation proof`). The rule is the totals line and every line matching `^ *FAIL`.
- Rules sync. `node tools/policy/rules_sync.mjs --check` printed
  `RULES-SYNC ok: every generated rule is the generated form of its source`.
  `grep -c '<<<<<<<\|>>>>>>>'` on both generated copies printed `0` for each.
- Gate scope. `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`
  printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, and `scope.run` names `tests/entities.py`.
- run_always and the gate, under the seat toolchain with `PYTHONPATH=tests/hastub`. Each of these
  printed rc 0: `python3 tests/entities.py`,
  `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)` (`claims hygiene: ... ok`),
  `python3 tests/closure.py selftest` (`ALL 124 closure shrink pins PASSED`), `python3 tests/layout.py`
  and `python3 tests/structure.py` (`STRUCTURE RATCHET PASSED`). `tests/harness_headers.py` takes the
  exclusive lease and measures the machine, so it is left to CI.
- What `nightly-status` grades. The red is the scheduled `slow` run 39387919507 on main at `0c298f6`.
  Its replay step, `python3 tests/replay.py`, printed
  `FAIL synthetic-dhw-only.json: cycle_cost  [1 offender(s): loop_cpu_ratio 0.1114 over its budget 0.111]`.
  Whether this diff reaches it, by rule:
  `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -E '^(custom_components/|tests/replay|tests/hastub/|tools/replay/)'`
  printed nothing (rc 1). The same filter over `git diff --name-only 0c298f6 c77f89d` (main's own movement)
  printed 15 paths, so the filter is not vacuous. `grep -cE 'prepr|gate-scoping|delivery/' tests/replay.py`
  printed `0`.
- Carry audit. `python3 -I tools/audit/carry_audit.py check --body <this body>` printed 0 unrouted.

## Red checks

- `pr-contract`, on the previous head `a4f01a421`. `carry_audit.py check` refused the body's one
  Forward-carry item as `UNROUTED`, because its `Carry:` named a file path rather than a group, issue,
  O-number or `dismissed:` reason. The item is delivered in this diff, so its route is now
  `Carry: dismissed: delivered in this diff`, and the audit reads 0 unrouted (`## Figures`). The cheaper
  detector already exists: the same `carry_audit.py check` the job runs. It costs seconds locally, and
  this body was run through it before the push. Its standing cost is one command a seat must remember
  to run, which `prepr.sh` already runs for it.
- `nightly-status`. It grades main's last scheduled nightly, not this diff. The `slow` lane failed
  on main at `0c298f6` on a CPU-time budget in `tests/replay.py`'s `cycle_cost`: `loop_cpu_ratio`
  0.1114 against 0.111, a machine-measured ratio over the budget. This diff does not reach what
  that lane reads. It changes `tools/pr/prepr.sh`, three copies of one rule and a delivery row, none
  under the coordinator, the replay fixtures, the HA stub or `tools/replay/`, and `tests/replay.py`
  names none of them (`## Figures`). So nothing in this PR can fix that red or cause it. The red is
  main's and is not this diff's to answer. At the time of reading, run 39563978649 (today's scheduled
  run at `c77f89d`) was still in progress, and `nightly-status` reads whichever scheduled run last
  concluded.

## Forward-carry

- A later seat reading how a handoff runs the gate needs the new off-Linux default and
  `PREPR_RECORD_CLOSURES=1` without opening `prepr.sh`. `dev/governance/rules/gate-scoping.md` names both
  in this diff. Carry: dismissed: delivered in this diff

## Friction

none

## Approval

Policy half: `dev/governance/rules/gate-scoping.md` and its generated copies. On 2026-10-20 tvofi
asked whether prepr's `closures` step is needed when CI runs `closures` as a required context, and ruled
"yes, do that": default-skip off Linux, keep CI's gate plus `closures-autofix` as the owner, and leave an
opt-in for a lane that specifically needs a first-green head. The ruling was made under mandate
6175172275. Under decision 0012 this is an edit to an existing rule, never a new file. The merge-time
resolution adds no wording of its own; it keeps #2526's already-merged sentence and this branch's.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_0169EzsXMGsmrd3gkdF9vHYa
