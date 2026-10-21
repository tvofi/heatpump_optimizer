prepr's `closures` step (6b) recorded the scoped closures on every platform, including a Darwin seat.
CI's required `closures` context and `closures-autofix` already own that check: the context re-records
on ubuntu, and the autofix commits the recording when the committed table under-approximates. Off Linux
a local recording buys only the round trip that bot commit then costs. So 6b now default-skips off Linux.
The skip line names the CI context and the autofix job as the owners, and `PREPR_RECORD_CLOSURES=1` as
the opt-in for a lane that needs a first-green head. Linux is unchanged. The `full` and `skip` cases are
untouched, and the self-test pins their printed lines byte-identical.

Second arm, same step: the recorder dies with the prepr. A stopped prepr used to leave
`derive_closures.sh` reparented and running to completion. Two such orphans ran 20 and 38 minutes on
2026-10-20.

Round 2 fixes the review's block (vacuous-test). The reap arm drove `closures_line` outside a command
substitution and without prepr's top-level TERM trap, so it reproduced no production case. The review
also measured that at the previous head, a TERM to the prepr alone was deferred by the prepr's own trap
until the recorder finished. That is the command-substitution rule: bash runs a trap only once the
substitution's reader returns. So the head now changes the production route as well as the test:

- `closures_step` runs `closures_line` as a job the prepr `wait`s on, never inside `$(...)`. A trapped
  signal ends a `wait` at once. The line is read back from a file once the job ends. Step 6b calls
  `closures_step "$BASE"`.
- The watchdog (`$$` gone, so it reaps the recorder's process group) is now the one reaping mechanism.
  `closures_line`'s own TERM/INT traps and `reap_recorder` are deleted, because nothing they caught is
  left uncaught. Under the new route, a TERM to the prepr's group kills the closures job by its default
  disposition, and the watchdog, which leads its own group under `set -m`, reaps the recorder.
  `## Mutation proof` M3wd shows the watchdog alone carries all three cases.
- `exit_on_signals` is the prepr's `trap 'exit 130' INT; trap 'exit 143' TERM; trap 'exit 129' HUP`,
  which step 1b wrote out twice. It now has one definition, which both arms of step 1b call and which
  the reap arms' driver installs.
- The reap arms now drive the production route. The driver is a separate bash, so its `$$` is the pid
  the watchdog polls. It evals prepr up to `rc=0`, runs `exit_on_signals` and then `closures_step fork`,
  and it leads its own process group. There is one arm per case: KILL to the prepr, TERM to the prepr
  alone, and TERM to its group. Each arm wants the prepr and the recorder both gone 5 s after the signal.
- The review's minor finding: `PREPR_RECORD_CLOSURES` now opts in only at `1`. Before, any non-empty
  value opted in, including `0`. A new arm pins that.

The policy half is `dev/governance/rules/gate-scoping.md` and its two generated copies. They name the
new default and the opt-in, and this round leaves them unchanged.

## Head

Code head `47e0cdd97a3485c9e384c94752a042bc83b7a7e7`, pushed to `handoff/r10-prepr-closures`. It is
the previous head `b18052f664039d36da73ef745a2a8423f82d2c46` plus two merges of `origin/main` (never a
rebase) and the round's commit `8342180c6`. The merges took main at `5d433771a`, then at
`e7c664856776542bf60bd770c98aba1eaadb4041` (read 2026-10-21T15:11:17Z). Both merges were clean. The
second merge brought `tests/requirements-*.txt` and a delivery row, so every figure below was re-taken at
`47e0cdd97` after it. The merge base is `e7c664856`.

## Mutation proof

Rule: each mutant is a detached worktree at `47e0cdd97` with one edit to `tools/pr/prepr.sh`, run as
`bash tools/pr/prepr.sh --self-test` under `/etc/profile.d/hpo-toolchain.sh` (Python 3.14, bash 5.2).
The counts are the totals line, and the names are every line matching `^  FAIL`. The driver is a seat
script (`mutrun.sh`, scratch), and each edit is a literal replace that asserts its match count is 1.

- **Failing test first.** This is the previous head `b18052f66` with this round's reap arms swapped in,
  plus its own production 6b statements named as the two functions the arms call:
  `closures_step() { CLOSURES_LINE=$(closures_line "$1"); }` and its slot-block trap line as
  `exit_on_signals`. Result: 321 passed, 1 failed,
  `FAIL a TERM to the prepr alone ends it and its recorder at once, not when the recording finishes`.
  This is the review's deferral, reproduced by the arm.
- **M0, null: unmodified.** 323 passed, 0 failed. The runner adds no failure of its own.
- **M1: delete `return 1` in `closures_records_here`** (the off-Linux predicate). 319/4:
  `6b leaves a scoped diff's recordings to CI off Linux by default, owing no recorder interpreter`,
  `and the skip line names the CI context and the autofix job that own them`,
  `and names the opt-in that records locally instead`, and
  `and PREPR_RECORD_CLOSURES=0 is no opt-in: the recordings stay CI's`.
- **M2: delete the `PREPR_RECORD_CLOSURES` override line.** 321/2:
  `6b's opt-in records off Linux for a lane that needs a first-green head` and
  `and the opt-in still refuses a closure its recording does not cover (null control)`.
- **M6: the override back to `[ -n "${PREPR_RECORD_CLOSURES:-}" ]`.** 322/1:
  `and PREPR_RECORD_CLOSURES=0 is no opt-in: the recordings stay CI's`.
- **M3wd: watchdog body replaced by `( : ) & wpid=$!`** (the review's M3wd2). 320/3:
  `a KILL to the prepr leaves no recorder running behind it (the orphan the watchdog closes)`,
  `a TERM to the prepr alone ends it and its recorder at once, not when the recording finishes` and
  `a TERM to the prepr's process group ends it and its recorder`.
- **M3setm: delete `set -m`.** 321/2: the KILL arm and the TERM-alone arm. Without its own group, the
  watchdog's `kill -- -$rpid` names no group and the recorder survives. Under the group TERM, the recorder
  then shares the prepr's group and dies by the signal itself, so that arm stays green under this mutant.
- **M4: `closures_step` back to `CLOSURES_LINE=$(closures_line "$1")`** (the previous route). 321/2:
  the TERM-alone arm (deferral) and the group arm. In the group arm, the watchdog holds the substitution's
  pipe open while it waits on `$$`, and `$$` waits on that pipe. That is the review's M3trap hang.
- **M5: `exit_on_signals` emptied to `:`.** 323/0, so it survives. Disposition: an equivalent mutant on
  this interpreter, not a gap this diff opened. `exit_on_signals` is a refactor of two existing,
  identical trap lines with no behaviour change, and no arm before this round pinned them. Bash 5.2 runs
  the EXIT trap and exits 143 on an untrapped TERM too. A probe (`bash -c` script with an EXIT trap
  writing a marker, TERMed in `wait`) printed `none rc=143 mark=ran` and `trap rc=143 mark=ran`. So no
  observable at this interpreter separates the two. An arm I wrote for it (the driver's EXIT trap writes
  a marker) also stayed green under M5, so I removed it rather than ship a vacuous pin.

The review's M3trap (delete `closures_line`'s traps) has no counterpart: this head deletes those traps
as redundant, and M3wd above shows the watchdog alone fails all three arms.

## Null control

M0 above: an unmodified tree passes all 323 checks, so every failure under a mutant is that mutant's.
The failing-first run is the null for the route change. The same arms, run against the previous route,
fail exactly the case the review measured, and pass at this head.

The unchanged Linux path still records and still refuses. The arm
`6b on Linux still records and still refuses an uncovered closure (null control)` passes at the head.

The timing window is 5 s in every reap arm, against a 300 s sleeper. All three arms passed in every run whose
mutant did not target them (M0, M1, M2, M5, M6), and those runs went 9 at a time on a 4-core box. This pass did
not re-take a live `derive_closures.sh` capture or the `closures` job on GitHub. CI runs the second on
push.

## Figures

- Self-test. `bash tools/pr/prepr.sh --self-test` at `47e0cdd97` (M0's run) printed `323 passed, 0 failed`.
  Every mutant's totals and FAIL names are in `## Mutation proof`, under the rule stated there.
- Interpreter probe. `bash probe_exit.sh none|trap <mark>`, TERMed 0.5 s after the start, where the script
  is `[ "$1" = trap ] && trap "exit 143" TERM; trap "echo ran > $2" EXIT; sleep 30 & wait $!`. It printed
  `none rc=143 mark=ran` and `trap rc=143 mark=ran`.
- Rules sync. `node tools/policy/rules_sync.mjs --check` printed
  `RULES-SYNC ok: every generated rule is the generated form of its source`.
- Gate scope. `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`
  printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, and `scope.run` names `tests/entities.py`.
- Scoped and run_always, under the seat toolchain with `PYTHONPATH=tests/hastub`, each rc 0:
  `python3 tests/entities.py` (`ALL 2375 ENTITY CHECKS PASSED`),
  `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)` (`claims hygiene: e7c664856... ok`),
  `python3 tests/closure.py selftest` (`ALL 124 closure shrink pins PASSED`), `python3 tests/layout.py`
  (`layout self-test: ok`), `python3 tests/harness_headers.py` (`ALL 109 HARNESS HEADER CHECKS PASSED`)
  and `python3 tests/structure.py` (`STRUCTURE RATCHET PASSED`).
- Architecture score. `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`
  printed `Architecture score: dS +0.0000 NULL`.
- Class enumeration (fixer.md step 8). Recorder launches:
  `grep -n 'PREPR_RECORD:-' tools/pr/prepr.sh` returns one production line, inside `closures_line`, which is
  closed in this diff. The other `derive_closures.sh` hits are comments and self-test fixture text.
  The sibling class is a heavy child prepr runs in the foreground, which a KILL orphans and a TERM to the
  prepr alone waits behind. The rule is
  `awk -v r=$(grep -n '^rc=0$' tools/pr/prepr.sh | cut -d: -f1) 'NR>r && /(node|python3|bash) [^|]*>\/tmp\/prepr-/' tools/pr/prepr.sh`,
  which returns 18 lines (steps 3 to 3h). Among them are `bash tools/pr/prepr.sh --self-test` (3h,
  minutes), `node ...policy_lint_mutants.mjs` and `node ...field_coverage.mjs`. A probe of that shape
  (`trap 'exit 143' TERM; <child> > /dev/null 2>&1`, with a 300 s child) printed
  `KILL: prepr gone, child alive` and `TERM: prepr alive, child alive` (the TERM sent to the prepr alone). The null control is
  this diff's three reap arms, where the recorder under `closures_step` reads `gone:gone`. Disposition:
  these are open seams of a distinct finding, outside this group's recorder scope. See `## Forward-carry`.
- `nightly-status` (red at the previous head, run 39603139630). It grades main's last concluded scheduled
  `Tests` run, 39563978649 at `c77f89dc6`. Two lanes are red there. `slow`: `tests/replay.py` printed
  `FAIL synthetic-dhw-only.json: cycle_cost  [1 offender(s): loop_cpu_ratio 0.1138 over its budget 0.111]`.
  `mutation-nightly`: `MUTATION TABLE BREACHED`, `10 survivor(s) of 23 evaluated = 39.1%`, cap 30.0%,
  with every survivor under `custom_components/heatpump_optimizer/`.
  `git diff --name-only $(git merge-base origin/main HEAD)...HEAD | grep -E '^(custom_components/|tests/replay|tests/hastub/|tools/replay/|tests/mutation)'`
  prints nothing (rc 1). As a null for the filter, the same filter over
  `git diff --name-only c77f89dc6 e7c664856` counts 22 paths (`grep -c`), from main's own movement.

## Red checks

- `nightly-status`. It grades main's scheduled nightly, not this diff. On run 39563978649 at `c77f89dc6`,
  `slow` failed a machine-measured CPU-ratio budget in `tests/replay.py` (0.1138 against 0.111), and
  `mutation-nightly` breached its survivor cap with survivors only in `custom_components/`. This diff
  changes `tools/pr/prepr.sh`, three copies of one rule and a delivery row, which is nothing either lane
  reads (`## Figures`). So no cheaper detector on this branch could have caught it, and nothing here can
  fix it. The red is main's. It has its owner's instruction in the job log (a fix plus a dispatched run on
  main), which is outside this group.
- Nothing else was red at the previous head `b18052f66`. That is the review's check-runs read, and the
  check-runs API at this writing lists `nightly-status` as the only non-success conclusion.

## Forward-carry

- Sibling seams of the orphaned-recorder class. prepr's foreground heavy steps (the 18 lines the
  `## Figures` rule returns, among them step 3h's `--self-test` and the policy-lint mutants drive) are
  orphaned by a KILL to the prepr and make a TERM to the prepr alone wait behind them. That was measured,
  with this diff's reap arms as the null control. The route that closes it is this diff's `closures_step`
  shape: a job the prepr `wait`s on, with a `$$` watchdog over its own group. This seat can file no issue
  and write no carry file, so the orchestrator owes the new issue that `finding-propagation.md` names
  for a sibling seam. `carry_audit.py check` refuses this route as `BAD-DEST` (`R10-PREPR-CAP is done`),
  and no live roster group or owned issue covers prepr's step lifecycle, so this seat has no valid
  destination to write. I have not substituted a dismissal for it. The orchestrator's new issue is the
  route. Carry: R10-PREPR-CAP
- The review's undispositioned roster note, "force `PREPR_RECORD_CLOSURES=1` on diffs touching
  `tests/closures.json`, `tests/closure.py` or an INERT read": not taken, because it would change nothing.
  `python3 tests/closure.py affected` on a one-file diff of `tests/closures.json`, and on one of
  `tests/closure.py`, printed case `full` for each. 6b skips a `full` diff before the platform predicate
  is read, and a full derive here is forbidden. The arm `6b skips a diff it cannot scope (full),
  recording nothing` pins that skip. Carry: dismissed: a full-case diff never reaches the opt-in

## Friction

none

## Approval

Policy half: `dev/governance/rules/gate-scoping.md` and its generated copies, unchanged this round. On
2026-10-20 tvofi asked whether prepr's `closures` step is needed when CI runs `closures` as a required
context, and ruled "yes, do that": default-skip off Linux, keep CI's gate plus `closures-autofix` as the
owner, and leave an opt-in for a lane that specifically needs a first-green head. The ruling was made
under mandate 6175172275. Under decision 0012 this is an edit to an existing rule, never a new file. It
still owes tvofi's approving review at the head.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_0124zEZpKzzm35P5uJCv7LZJ
