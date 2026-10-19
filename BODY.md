Part of #201

No CI workflow ran the orchestrator tick's self-test, `tools/audit/seat/orchestrator_tick.py --self-test`. #2406 removed `roster_lib.DEFAULT_ROSTER_REF`. A tick that still read it crashed in its carry sweep with `AttributeError`, and the first place anyone saw it was review on #2422. The directory is INERT in `tests/closure.py`, so the scoped gate never selects the tick, and nothing in CI ran it.

- `.github/workflows/governance.yml`: one step in `instrument-self-tests`, "Show the orchestrator tick deciding its own fixtures". It sits next to the sweep renderer's step and follows the same pattern: `set -o pipefail`, `python3 -I ... --self-test | tee "$RUNNER_TEMP/ot-self-test.txt"`, then a grep that requires the line `orchestrator_tick self-test: N checks, 0 failed` with N >= 1. A crash prints no tally line and exits non-zero, so the step fails either way. The step needs no file-presence fallback. The tick has a single path on `main`, and this step's siblings only use a fallback where an instrument moved during the reorganisation (R9-RO-2).
- CI can run it with no change to the tick. The self-test stubs gh, git, pgrep and bus through injected runners, and under a spy it makes 0 subprocess calls and 0 socket connects (figures below). It loads `roster_lib.py` and `budget_raise_gate.py` from the tree by path through `_module`. That loading is why it catches the #2406 class: if a symbol the tick reads goes missing from either module, the self-test fails. It also passes under Python 3.12, the runner's default `python3`, as well as the seat's 3.14.

**Interaction with #2422** (`fix/r10-openpr-silent-pr`). #2422 adds arms to the same self-test and keeps both the entry point (`--self-test`) and the tally format. This step calls the self-test exactly as a seat does, so #2422's arms run here once both PRs land, whichever merges first. At #2422's head c12b0562da080854e16e52448b7cdb4f1f242883, a `git archive` copy run under the same spy printed `orchestrator_tick self-test: 150 checks, 0 failed`, with 0 subprocess calls. #2422 also adds `tools/audit/seat/pr_cap.py` and `tools/audit/seat/tick_loop.sh`, each with its own `--self-test`. Neither is on `main`, so this diff does not wire them. They belong to the class below.

Alternatives not taken: (a) A step that finds and runs every `tools/audit/seat/*` self-test. It would close the whole class in one step, but 23 of those self-tests have never run outside a seat. Some, such as `handoff_push.sh`, `merge_pr.sh` and `update_pr.sh`, drive push and merge paths. Wiring them without checking each one is offline would put an unverified program in CI. (b) Running the self-test from `tests/`. The tick is INERT by design (`tools/audit/` prefix), and putting it in a closure would make every tick edit trigger a gate script. `instrument-self-tests` is the job for programs whose verdict grades nothing (`HPO_JOB_GRADES: nothing`). (c) Exit status alone, without the tally grep. Mutant M3 below shows what that misses: a self-test that counts a failure and still exits 0.

Caps: the diff adds 12 lines to `.github/workflows/governance.yml`. That file is not a `POLICY_GLOBS` path, and no `*_budgets.json` or `policy_budgets.json` cap is keyed on it. `node tools/policy/policy_lint.mjs --budgets` exits 0 and `python3 tests/structure.py` passes. No constraint binds, and nothing is raised.

## Head

c13ed69e6d609d90e05cf3d018cd3bda349023d1 (origin/main 913ce1ff5, the merge base, at 2026-10-19T05:37:19Z). `main`'s delta since the fork point 2d843030a is record-only (`dev/programme/delivery/`).

## Mutation proof

Each mutant edits one line in the committed tree. The step's `run:` text is taken from `governance.yml` with `yaml.safe_load` and run under `bash -e` with `RUNNER_TEMP` set and every `__pycache__` removed before each run. Each mutant is then restored with `git checkout -- <file>`, and `git status --short` shows only the step's own file. All three mutants are killed.

- M1, the #2406 shape, in the tick: `rl.default_roster_ref(self.git)` becomes `(rl.DEFAULT_ROSTER_REF, "")`, so the tick reads the symbol #2406 removed. The step exits 1 and its last line is `AttributeError: module 'roster_lib_tick' has no attribute 'DEFAULT_ROSTER_REF'`.
- M2, the same class from the library side: `roster_lib.py`'s `def default_roster_ref(` is renamed, so the tick's reader loses its symbol. The step exits 1: `AttributeError: module 'roster_lib_tick' has no attribute 'default_roster_ref'`.
- M3, the grep arm: `self_test()` returns 0 and its tally counts one more failure. The step exits 1, last line `orchestrator_tick self-test: 104 checks, 1 failed`. Here the grep is the only thing that refuses, because the Python exit status is 0.

A pitfall for anyone reproducing this: run the mutants with `PYTHONDONTWRITEBYTECODE=1`, or remove `__pycache__` between runs. `roster_lib.py`'s same-length rename, restored within the same second, otherwise leaves a stale `.pyc` that the next run loads. A first pass here did exactly that and read the restored tree as red. A fresh CI checkout has no cache.

## Null control

On the unmodified head the step exits 0, and its last line is `orchestrator_tick self-test: 104 checks, 0 failed`. It printed the same before and after the mutant series. The spy's own null control is a two-line script that calls `subprocess.run(["true"])`: the spy counts 2 calls for it, against 0 for the self-test.

## Figures

- Gate scope: `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`). One changed file: `.github/workflows/governance.yml`. The rule is the mode line, not the count.
- What `scope.run` names, plus `tests/run.sh`'s `run_always` lines, at this head with `PYTHONPATH=tests/hastub`: `env -u BASH_ENV python3 tests/entities.py` printed `ALL 2349 ENTITY CHECKS PASSED`, `python3 tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED`, `python3 tests/layout.py` printed `layout self-test: ok`, `python3 tests/closure.py selftest` printed `ALL 124 closure shrink pins PASSED`, `GOLDEN_MODE=drift python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD)` printed `claims hygiene: 913ce1ff5b02d74fd2913534df99ae3c490323cd ok`, `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`, and `node tools/policy/policy_lint.mjs --budgets` exited 0. Every run exited rc=0, with no mutant applied while any of them ran.
- `python3 -I tools/audit/seat/orchestrator_tick.py --self-test` at this head: `orchestrator_tick self-test: 104 checks, 0 failed`, rc=0. The same command with uv's CPython 3.12.14: `104 checks, 0 failed`, rc=0.
- Offline: a spy wraps `subprocess.run`, `subprocess.Popen.__init__` and `socket.socket.connect` (connect raises), then runs the tick's `__main__` with `--self-test`. It counted `CALLS 0` and exit 0 at this head and at #2422's head. The spy is a one-off probe kept in scratch (`fixer.md` step 18).
- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `uncovered_files=0`. `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`. `python3 -I tools/audit/seat/ref_privacy.py --check`: `0 refused`.
- Seams of the class "a seat instrument's self-test that no CI step runs". The rule: for each file that `git grep -lE -e '--self-test|self-test\)' -- tools/audit/seat/ ':!*.md'` returns, check whether its basename appears under `.github/workflows/`. At the merge base 913ce1ff5 it returns 32 files: 8 wired (`bus.sh`, `merge_train.py`, `policy_reread_check.py`, `record_row.py` in `tests.yml`, `ref_privacy.py`, `sweep_render.py`, `tmp_paths.py`, `train.sh`) and 24 unwired. This diff closes `orchestrator_tick.py`. The other 23 are an open seam, returned to the orchestrator for a group of their own and not closed here: `ci-watch.sh`, `cloud_dispatch.py`, `cloud_relay.sh`, `daemonize.py`, `delivery_row.sh`, `failure_logs.sh`, `features_block.py`, `handoff_push.sh`, `handover_prompt.py`, `merge_pr.sh`, `moved_paths.py`, `open_pr.sh`, `plan_table.py`, `proof_watch.py`, `prune_refs.py`, `queue_pre_flight.py`, `resume_doc.py`, `roster_edit.py`, `roster_lib.py`, `run_twins.py`, `seat_venv.sh`, `state_docs.py`, `update_pr.sh`. A file the gate selects through a closure, as `tests/entities.py` loads `roster_lib.py` and `state_docs.py`, is still unwired by this rule, because the gate runs `entities.py`'s checks and not that file's `--self-test`. The rule's null control is the 8 wired files, which it reports as wired. At this head the same rule prints `wired=10 unwired=22`: `orchestrator_tick.py` is now wired, and `roster_lib.py` is a false positive, matched only because the new step's comment names it. The rule keys on a basename mention, so a comment counts as wiring. Its other blind spot: a self-test whose entry point is spelled neither `--self-test` nor `self-test)`.

## Red checks

none

## Unpinned sites

`prepr.sh` step 6d: no production or tests/ line is added. The mutants above are killed by the new step itself.

## Forward-carry

none. The 23 unwired self-tests (Figures, last line) go to the orchestrator for dispatch as one group, not to a later stage's brief.

## Friction

none

## Approval

The owner's direction, in chat on 2026-10-19, under mandate 6175172275 (#201, scope all): "Close the governance gap under your mandate". The diff touches no `POLICY_GLOBS` path, so `checkPrBody` does not require this section. It is here because the change adds a CI step on the owner's direction. The orchestrator approves under mandate 6175172275.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
