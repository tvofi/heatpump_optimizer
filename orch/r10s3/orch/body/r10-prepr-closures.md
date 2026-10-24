prepr's `closures` step (6b) recorded the scoped closures on every platform, including a Darwin seat. CI's
required `closures` context and `closures-autofix` already own that check: the context re-records on
ubuntu and runs `python -u tests/closure.py check --in-dir <recordings> --partial`, and the autofix
commits the recording when the committed table under-approximates. Off Linux the local recording buys
only the round trip that bot commit then costs -- a `GITHUB_TOKEN` head runs no `pull_request` event, so
the required contexts stay absent and the train recarries it -- and it is the dominant cost of a handoff.

This change makes 6b default-skip off Linux. The skip line names CI's `closures` context and
`closures-autofix` as the owners and `PREPR_RECORD_CLOSURES=1` as the opt-in for a lane that needs a
first-green head. Linux is unchanged: every decision the step made before the predicate stands, and a
diff whose recordings are all left to CI still owes no recorder interpreter. `full` and `skip` cases are
untouched and their printed lines are pinned byte-identical by the self-test.

A second arm, same function: the recorder now dies with the prepr. A stopped prepr left
`derive_closures.sh` reparented to launchd, running to completion; the orchestrator reports two such
orphans at 20 and 38 minutes, and they fed the box's load. The recorder runs in its own process group, a
TERM/INT trap reaps that group, and a watchdog reaps it when the top-level prepr is gone -- the case a
command substitution's own trap never sees.

## Head

`e32513490631475ce7e2307183786c0c1c808e7b`. The branch's own prepr was run with `PREPR_SKIP_CLOSURES=1`,
per the owner's wave ruling of 2026-10-20. `tests/entities.py` and `tests/run.sh`'s `run_always` scripts
ran at this head; their rcs are under `## Figures`.

## Mutation proof

Failing first, the step's own `bash tools/pr/prepr.sh --self-test` before the platform guard existed:
313 checks, 310 passed, 3 failed, and the three failures are the new off-Linux arms:

    FAIL 6b leaves a scoped diff's recordings to CI off Linux by default, owing no recorder interpreter (got 1, wanted 3)
    FAIL and the skip line names the CI context and the autofix job that own them (got 1, wanted 0)
    FAIL and names the opt-in that records locally instead (got 1, wanted 0)

After both arms of the fix the same self-test is 315 passed, 0 failed.

M1, delete the off-Linux predicate (the `return 1` in `closures_records_here`): 312 passed, 3 failed,
the three arms above, and the named one is `FAIL 6b leaves a scoped diff's recordings to CI off Linux by
default, owing no recorder interpreter (got 1, wanted 3)` -- the step records, the arm's bad
`HPO_RECORDER_PYTHON` then refuses.

M2, delete the opt-in override: 304 passed, 11 failed. The named check is `FAIL 6b's opt-in records off
Linux for a lane that needs a first-green head (got 3, wanted 0)`; the other ten are the recording arms,
which name the opt-in by design because they drive the recorder.

M3, delete the reap and restore the single-line recorder launch: 314 passed, 1 failed, and it is the
named check: `FAIL a TERM to the prepr leaves no recorder running behind it (the orphan this closes)
(got 1, wanted 0)`.

Failing first for the reap: that same arm, on the tree before the reap landed, printed exactly that line
(the run was stopped after the arm, so it has no run total); it passes on the fixed tree.

## Null control

The unchanged local path still records and still refuses. On a real under-scoped diff (`tests/wood_advisor.py`
reading a file its committed closure does not list): with the opt-in set the step returns rc 1
`UNDER-SCOPED`; the self-test's Linux arm returns rc 1 on an uncovered recording as well. The new
default on that diff returns rc 3 and calls the recorder 0 times.

CI's own arm, driven offline: over the recording the Linux re-record would produce for that diff,
`python -u tests/closure.py check --in-dir <recordings> --partial` returns rc 1 and names the same file;
over a recording without the planted read it returns rc 0.

What I could not show offline, and what it costs the claim: the `closures` job itself running on GitHub
at this head, and a live `derive_closures.sh` capture. A one-script recording on this box sat in
`gate_lock.py slot-take` for 32 min without acquiring a slot and was killed. So the CI evidence is the
job's exact command against a constructed recording (the committed closure plus the planted read), and
the claim that CI catches the under-scope rests on that command and the ruleset's required `closures`
context, not on an end-to-end run of this diff.

## Figures

- Step outcomes across this box's prepr logs. Rule: every `*.log` under `~/hpo-seats`, `~/hpo-orch` and
  `~/.local/state/hpo` holding a line matching `^  (ok|REFUSE|skip) +closures `; 301 files hold 301 such
  lines. `grep -hE '^  (ok|REFUSE|skip) +closures ' $(grep -rlE '^  (ok|REFUSE|skip) +closures ' ~/hpo-seats ~/hpo-orch ~/.local/state/hpo --include='*.log') | sed -E 's/^  (ok|REFUSE|skip) +closures .*/\1/' | sort | uniq -c`
  prints `34 ok`, `15 REFUSE`, `252 skip`. All 34 `ok` lines read `scoped recordings are covered`: no
  local recording found an uncovered closure. The 15 refusals are 11 `failed while being recorded` and 3
  `UNDER-SCOPED` (one line lost its marker to a grep). A pre-study figure of 108 ok / 0 FAIL / 12 skip
  did not reproduce under this rule.
- The self-test totals: `bash tools/pr/prepr.sh --self-test`, before and after the fix.
- Queue wait, at load1 58-150 (`uptime`): `ps -o etime= -p <slot-take>` on a one-script recording printed
  32 min; killed.
- Recorder calls on the under-scoped diff: a stub recorder appends its argv to `$CALLLOG`, and `wc -l` on
  that file printed 0 after the default off-Linux arm.
- Gate at this head: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`
  printed `MODE: SCOPED -- 1 script(s) run` (`tests/entities.py`), and each of `python3 tests/entities.py`,
  `python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)`, `python3 tests/closure.py selftest`,
  `python3 tests/layout.py`, `python3 tests/structure.py` printed rc 0. `tests/harness_headers.py` (the fourth
  `run_always` script) was left to CI: it measures the machine and takes the exclusive lease.

## Red checks

`none`.

## Forward-carry

- A later seat reading how a handoff runs the gate needs the new default without opening `prepr.sh`:
  `dev/governance/rules/gate-scoping.md` now names it and `PREPR_RECORD_CLOSURES=1`.
  Carry: `dev/governance/rules/gate-scoping.md`.

## Friction

none

## Approval

Policy half: `dev/governance/rules/gate-scoping.md` and its generated copies. tvofi, 2026-10-20, asked
whether prepr's `closures` step is needed when CI runs `closures` as a required context, and ruled
"yes, do that": make it default-skip off Linux, keep CI's gate plus `closures-autofix` as the owner, and
leave an opt-in for a lane that specifically needs a first-green head. Ruled under mandate 6175172275;
under decision 0012 this is an edit to an existing rule, never a new file.
