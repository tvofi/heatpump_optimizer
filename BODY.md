Roster group R10-ERREXIT-COUNTERMEASURES: the four carries of #2849 (R10-RCA-HOTFIX-BATCH-ERREXIT, handoff-body `e78cd811`), landed as checks, not as one-call barriers. The diff touches `tests/entities.py`, `tests/arch_score.py`, one line of `.github/workflows/gate-sweep.yml`, and three registry entries in `tools/policy/agreement.mjs`. There is no production code in it.

- **(1) Countermeasure A.** `tests/entities.py` scans every errexit `run:` block (default shell, `bash`, `sh`) in `.github/workflows/*.yml` and `.github/actions/*/action.yml` and refuses a `$?` read whose producer is a bare simple command, including a read in an `if`/`while`/`until` test. It replaces `_RAF_BARE_GREEN`, the one-call barrier that let I3 through. The logic is `dev/audit/harnesses/r10_errexit_capture.py` at e1a684789, ported into the check so the gate does not import an INERT evidence file (a harness edit would change the gate with no closure seeing it). The null-control check carries the harness's 15 selftest cases, its shell arm, the empty tree, and a plant that unwraps the live batch gate back to I3's form.
- **(2) gate-sweep.yml, the 4th instance.** `out=$(python3 -I tools/ci/gate.py --sweep ...) || true`, so under `bash -e` the `case` reads the outcome word on a program exit 1. `_gs_step_verdict` now runs the step under `_GHA_RUN` (`bash -e -c`). Failing test first: that switch alone fails U0c on the 3 rc-1 cases (Mutation proof).
- **(3) Countermeasure B.** `_GHA_RUN = ["bash", "-e", "-c"]` is GitHub's default step shell, used by `_gs_step_verdict`, `_train_hold_status`, `_pt_trigger`, `_cov_trust` and `_cov_marker`. `tests/arch_score.py`'s `base_runs_the_gate` runs `bash -e -c`. A new check pins B for later edits: every `["bash"|"sh", ..., "-c", ...]` list literal in a tracked `.py` under `tests/` and `tools/` must carry an errexit flag, or must be listed in `_SHELL_NOT_A_STEP` (keyed by file and enclosing function) as running text that is no `run:` block. Every site has a disposition (Figures).
- **(4) Class proposal:** under Forward-carry, for the judge or orchestrator to mint. This PR mints nothing.

The ported regexes are a grammar now written in two files, so `tools/policy/agreement.mjs` registers the three as `identical:` copies in `SHARED_GRAMMARS`, following the precedent of the job-id scan. Without the entries the lane printed `unregistered=3`; with them it prints `AGREEMENT ok`.

Alternatives not taken. A as an import of the harness: it is INERT, so editing it would change the gate unseen. A promoted under `tools/ci/`: a new gate file and a closure re-derivation, for logic that only one check reads. B as five flag edits with no pin: the next harness written with `bash -c` would repeat I4. A syntactic check for `x=$(cmd)` (the gap A leaves): costed under Figures and not built.

## Head

88b4ddc859ee1ec0592614502e531b830b14d2dd

The entity-suite, mutant, harness and arch_score figures were taken at `867d20f026e7eac87b807329505c3f9e818290a4`. That commit was amended to this head, which adds only the three `SHARED_GRAMMARS` entries in `tools/policy/agreement.mjs` (`git diff 867d20f02 88b4ddc85 --stat` names only that file). No file those figures read changed. The agreement lane and `prepr.sh` were run at this head.

One commit on `origin/main` `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c`, which was main's tip at 2026-10-29T15:48:08Z. Main has not moved since the cut, so it was not merged in.

## Mutation proof

Every run below is `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` (Python 3.13 venv from `tests/requirements-ci.txt`), each mutant in a detached worktree of the head with one edit.

- Failing test first: main `88c6ad5bb` printed `ALL 2470 ENTITY CHECKS PASSED`. The same tree with only `_gs_step_verdict` switched to `bash -e -c` printed `1 of 2470 ENTITY CHECKS FAILED`: gate-sweep.yml's U0c check, `defects=` naming `SWEEP-DONE run=2 reruns=0` rc 1 (step rc 1, want success), `RATE-LIMITED ...` rc 1 (no `::error title=RATE-LIMITED::`) and `RuntimeError ...` rc 1 (no `::error title=sweep failed::`). The head printed `ALL 2473 ENTITY CHECKS PASSED`.
- M1, gate-sweep.yml's ` || true` deleted: `1 of 2473` failed, U0c, with the same 3 defects.
- M2, A's predicate (`stmt = _EX_TEST_HEAD.sub("", head[cut + 1:].strip())` becomes `stmt = head[cut + 1:].strip()`): `1 of 2473` failed, "and the errexit check reads the shapes, not one call (null controls)", `cases wrong=['if test -ne', 'if test builtin', 'if test quoted', 'same-line if', 'while test']`.
- M3, B reverted (`_GHA_RUN = ["bash", "-c"]`): `1 of 2473` failed, "every `bash -c` / `sh -c` a check runs carries errexit ...", `without errexit=['tests/entities.py:<module>']`. U0c stays green under M3 because the step is fixed. Only the pin sees the revert, which is why the pin exists.
- M4, the tree A reads (nightly.yml's hotfix unwrapped to the bare `--batch-due` call then `batch=$?`): `2 of 2473` failed. A's check printed `hits=['.github/workflows/nightly.yml job=record-autofix step='Write the rows and push the record branch': ...]`, and the existing executed check "nightly.yml's batch gate, run under the runner's `bash -e`" printed `got {0: 'apply', 4: 'died:4', 1: 'died:1', 2: 'died:2'}`.

## Null control

- The finder harness `python3 -I dev/audit/harnesses/r10_errexit_capture.py --root <tree>` (sha1 `03767097bf17a13cae0b52425482dcf6b1c3ebdb`, identical to e1a684789's copy) printed `blocks=265 reads=5 hits=0` (exit 0) at main `88c6ad5bb` and also at this head. **It reads flat at both ends by design**: the instance it measures, I3, was fixed on main by #2848 before this cut, and I4 is a `$(...)` read outside its unit. The positive arm is M4's `.github/` tree, where it printed the one `HIT ... record-autofix ...` line, `hits=1`, exit 1. An empty `.github/` printed `REFUSED`, `blocks=0 reads=0`, exit 2.
- The companion that reads I4 is the tree's own executed check, U0c under `bash -e`: red at the base (Mutation proof, failing test first), green at the head.
- Parity of the ported check with the harness, `_ex_scan` against `--root` on the same tree, as (blocks, reads, hits): main `(265, 5, 0)` EQUAL; head `(265, 5, 0)` EQUAL; M4 `(265, 5, 1)` EQUAL; `git archive d181d014a .github` (I3 live) `(260, 5, 1)` EQUAL, the batch gate; `bc2ad6964^` (I2 live) `(183, 3, 1)` EQUAL, tests.yml's `guard --require-green; rc=$?`; `718c94c84^` (I1 live) `(145, 2, 0)` EQUAL. I1 is a pipeline shape outside the unit, as the RCA's section 6 says. A non-zero `reads` at every tree shows the green verdicts are not skips.
- B's pin is checked against its own controls in-tree. Three plants each yield exactly their own defect: a bare `["bash", "-c", s]` in a new function, `["sh", "-x", "-c", s]`, and a listed function name (`self_test`) in another file, which shows the key includes the file. The pages harness's `["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", s]` yields none. Every listed key is used: `listed and unused=[]`.
- The agreement lane (`python3 -I tools/policy/agreement_py.py --out J` then `node tools/policy/agreement.mjs --py-json J`), before and after the registry entries. Without them it printed `RESULT divergent=0 unregistered=3` and three `UNREGISTERED` lines, one for each ported grammar shared by `tests/entities.py` and the harness. With them it printed `unregistered=0 dead=0`, `AGREEMENT ok`. Main printed `AGREEMENT ok`.
- `tests/arch_score.py`'s `base_runs_the_gate`, called alone with `BASH_ENV` unset: both its checks printed `ok` at main and at the head (`bash -e -c`).

## Figures

- B's enumeration rule is `_shell_c_sites` (an `ast` walk over every `git ls-files -- 'tests/*.py' 'tools/*.py'` for a list literal whose first string is `bash` or `sh` and that contains `-c`). At the head it returns 11 sites, each with a disposition:
  - `tests/entities.py` `<module>` (`_GHA_RUN`, used by `_gs_step_verdict`, `_train_hold_status`, `_pt_trigger`, `_cov_trust`, `_cov_marker`): `-e`, **closed in this diff**
  - `tests/arch_score.py` `run` in `base_runs_the_gate`: `-e`, **closed in this diff**
  - `tests/entities.py` `_pt_ds_rc`: `-e`, already guarded
  - `tests/entities.py` `_raf_batch_outcomes`, `_pg_run` and `_pg_probe_defects`: `-eo pipefail`, already guarded (stricter than the default `bash -e`, so a healthy step can show red but a defect cannot show green)
  - `tests/entities.py` `_cir_once_count`: listed, runs two lines of `tools/coverage/coverage_tree.sh`, not a step
  - `tests/throwaway_git.py` `self_test` (3 literals): listed, sources `tests/throwaway_git.sh`
  - `tools/audit/judge_batch.py` `run`: listed, a judge's own command line

  The RCA's 14 at `908237a8c` are these, with the five entity literals folded into `_GHA_RUN` (14 − 5 + 1) plus `_raf_batch_outcomes`, which #2848 added (11). Outside the rule: `tools/audit/seat/train.sh`'s embedded `bash -c` is a `.sh` file and runs a signal fixture, not a step. Frozen harnesses under `dev/audit/` are evidence, not checks (the RCA's section 5 B).
- The gap A leaves (`x=$(cmd)` read through its output), costed and not built. The rule: in every errexit block (the harness's `run_blocks`/`logical_lines`), count a logical line matching `^(local\s+|export\s+)?\w+=\$\(` that has no `||`/`&&`. Main gives 76, including gate-sweep's `--sweep` line. The head gives 75, without it. A syntactic refusal would need 75 dispositions, almost all of them fail-fast captures where errexit is the intent. The executed checks under `_GHA_RUN` (B) catch the harmful case where a harness drives the step, so this is a recorded decision not to build the wider check.
- Entity counts: the command under Mutation proof, main 2470 → head 2473 (A's two checks and B's pin).
- The scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: FULL -- every test script runs, nothing is scoped out`, reason `.github/workflows/gate-sweep.yml changes the gate itself`. I ran the scripts the diff reaches (`tests/entities.py`, `tests/arch_score.py`'s `base_runs_the_gate`) and `run.sh`'s `run_always` lines, and left the full suite to CI. `tests/closure.py selftest`: `ALL 117 closure shrink pins PASSED`. `tests/layout.py`: `layout self-test: ok`. `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED` (the first run, concurrent with four entity suites, read `sysid_estimator_frontier.py` at `cpu=240.9s against 240s`, a harness this diff does not touch; the re-run on an idle host passed, and main passed under the same load). `tests/env_drift.py --claims-only`: `claims hygiene: 88c6ad5bb ok`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures, fast, wave-script or instrument red predicted`.

## Red checks

none: no check run exists for this head before the push.

## Forward-carry

- **Class proposal (carry 4), for the judge or the orchestrator to mint.** "A workflow step's meaningful nonzero exit ended by errexit before the step reads it." Instances, all as `non_round_instances`: I1 (`718c94c84`, a later step reads a file that a `-e`/`pipefail` pipeline was to finish), I2 (`bc2ad6964`, `guard --require-green; rc=$?`), I3 (#2848, `e0ffb1213`, bare `--batch-due` then `batch=$?`), I4 (gate-sweep's `out=$(...)`, `85d13b859`, fixed here). Seams and their detectors: a `$?` read is refused by A tree-wide; a `$(...)` read through output is caught where a harness executes the step under `_GHA_RUN`, and B's pin keeps those harnesses under errexit; I1's cross-step shape has no detector (RCA section 6). Whether process incidents count toward the audit-class barrier rule is the owner's question, and the RCA left it open. Carry: R10-ERREXIT-COUNTERMEASURES (this group's carry (4) in dev/programme/rosters/wave-r10-groups.json; the class mint itself is the judge's or orchestrator's, in dev/audit/config/bugclasses.json)

## Friction

none
