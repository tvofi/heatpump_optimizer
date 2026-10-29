Roster group R10-ERREXIT-COUNTERMEASURES: the four carries of #2849 (R10-RCA-HOTFIX-BATCH-ERREXIT, handoff-body `e78cd811`), landed as checks, not as one-call barriers. The diff touches `tests/entities.py`, `tests/closures.json` (the `tests/entities.py` entry, re-recorded), `tests/arch_score.py`, one line of `.github/workflows/gate-sweep.yml`, and one registry entry in `tools/policy/agreement.mjs`. There is no production code in it.

- **(1) Countermeasure A.** `tests/entities.py` scans every errexit `run:` block (default shell, `bash`, `sh`) in `.github/workflows/*.yml` and `.github/actions/*/action.yml` and refuses a `$?` read whose producer is a bare simple command, including a read in an `if`/`while`/`until` test, an arithmetic `(( $? ))` test among them. It replaces `_RAF_BARE_GREEN`, the one-call barrier that let I3 through. The logic is `dev/audit/harnesses/r10_errexit_capture.py` at e1a684789, ported into the check so the gate does not import an INERT evidence file. The arithmetic arm is a deliberate departure from the harness, which misses it (carry 5). The null-control check carries the harness's 15 selftest cases, 3 arithmetic cases, its shell arm, the empty tree, and a plant that unwraps the live batch gate back to I3's form.
- **(2) gate-sweep.yml, the 4th instance.** `out=$(python3 -I tools/ci/gate.py --sweep ...) || true`, so under `bash -e` the `case` reads the outcome word on a program exit 1. `_gs_step_verdict` runs the step under `_GHA_RUN` (`bash -e -c`).
- **(3) Countermeasure B.** `_GHA_RUN = ["bash", "-e", "-c"]` is GitHub's default step shell, used by `_gs_step_verdict`, `_train_hold_status`, `_pt_trigger`, `_cov_trust`, `_cov_marker` and, after the merge, main's `_bash_env_reads` control (#2835). `tests/arch_score.py`'s `base_runs_the_gate` runs `bash -e -c`. A pin keeps it: every `-c` list literal whose shell is `bash` or `sh` by basename, in a tracked non-INERT `.py` under `tests/` and `tools/`, carries an errexit flag or is listed in `_SHELL_NOT_A_STEP` (keyed by file and enclosing function).
- **(4) Class proposal:** under Forward-carry. This PR mints nothing.

### This round: the closures red, fixed at the root

Round 1 was blocked because B's pin opened every tracked `tests/*.py` and `tools/*.py` in-process, the 49 INERT ones included. `closure.py` refuses an INERT file that a gate script reads in-process (#357), so `tests / closures` printed `INERT READS UNDER-APPROXIMATED` and `closures-autofix` could not repair it. The fix narrows what the pin reads to the gate's own files: `_SHELL_DOMAIN` is the tracked list less `_closure.is_inert`. The tree's own classification therefore decides where a check can live. The gate never runs an INERT file in-process, and a file that a check starts running has to leave INERT (the #357 refusal), at which point it enters B's read. Every file read now lands in `tests/entities.py`'s closure, so a branch that adds a bare `bash -c` to any of them selects `tests/entities.py` under `GATE_SCOPE=auto`. The scoped-path blindness the verdict named is closed by construction, and the closure is recorded, not left to the bot (Figures).

The same commit takes the verdict's third finding: a shell is matched by basename, after a leading `env`, so `["/bin/bash", "-c", ...]` and `["/usr/bin/env", "bash", "-c", ...]` are inside the rule. Two plants pin that. The 8 `/bin/bash` literals in `tools/audit/seat/beatd.py` are INERT and so are outside the read. They run beatd's own scripts, not `run:` blocks, and the domain arm of the check names beatd.py as the excluded file.

Alternatives not taken, for the closures red:
- Moving the 49 INERT files to `INERT_EXCEPT`. That reclassifies evidence and seat tools as gate dependencies to fit one pin, and the #357 list exists to record reads, not to manufacture them.
- Excepting the reads in `closure.py`. That would leave a gate read that no closure records, which is exactly the blindness the block names.
- Narrowing to "files that read workflow text", using the closures of the scripts that read `.github/`. That set is 239 files, almost the same as the domain, and it depends on a recorded table that lags a new file by one recording.
- A cheaper `git grep --cached` pre-filter. It reads blobs, not working-tree files, so the recorder would not see the dependency, and that is the same blindness again.

The cost of the narrowing is that `tests/entities.py`'s closure gains the 152 non-INERT `.py` files it did not list, so a script's own edit now also re-derives `tests/entities.py`. Measured over main's last 300 first-parent merges, 116 already selected `tests/entities.py` and 1 more would have (Figures).

### Roster carries

The group's carries, at `origin/handoff/audit-r10-roster`:

- Carry 1: countermeasure A, landed (the first bullet at the top). The control was re-measured: the harness gives `blocks=265 reads=5 hits=0` at main `ce5940c0d` and at this head (Null control).
- Carry 2: gate-sweep.yml fixed, with failing test first (round 1) and M1 at this head.
- Carry 3: countermeasure B, landed, with its pin narrowed this round (M3, M5, M6).
- Carry 4: the class proposal, under Forward-carry.
- Carry 5: the arithmetic `(( $? ))` arm, landed in 9ca68c8c5, with its plant pair and the M7 mutant. The `bash -c` site list was re-derived after the merge, at 6ac7d972e: 11 sites (Figures). `_raf_batch_outcomes` is among them, with `-eo pipefail`.
- Carry 6: each runner main moved to `_stub_path_env` keeps `env=_stub_path_env(...)`. Only the argv moved to `_GHA_RUN`: `_gs_step_verdict`, `_train_hold_status` and `_pt_trigger` were merged that way, and `_pt_ds_rc` already ran `-e`.

## Head

9ca68c8c5f652c5b0f950a2dacd5e088fd3aaa9c

This head is the round-1 head 9d97a52d5 plus: 663b63727 (the narrowed read and the basename match), 000528856 (the re-recorded closure), d93e51afc (a merge of `origin/main` `ce5940c0d1d8f611a818d53e7fffcafb48b356c1`, main's tip at 2026-10-29T18:16:51Z, made because `git merge-tree --write-tree origin/main HEAD` reported a content conflict in `tests/entities.py`), 6ac7d972e (main's new `bash -c` control routed through `_GHA_RUN`, and two scoping pins re-keyed), and 9ca68c8c5 (carry 5's arithmetic arm on A, with the two `SHARED_GRAMMARS` identities it ends removed). I resolved the merge by hand: main's `_stub_path_env` (#2835) and this branch's `_GHA_RUN` both kept, and the three runners main rewrote take main's env helper under `_GHA_RUN`. A figure that names no tree was taken at this head. The B-site census and the closure figures were taken at 6ac7d972e, and 9ca68c8c5 touches neither B nor any file read. Steps 2–8 were re-executed after the merge.

## Mutation proof

Every run is `env -u BASH_ENV PYTHONPATH=tests/hastub /opt/hpo/venv-ci/bin/python3 tests/entities.py` (the Python 3.14 CI venv). The head, 9ca68c8c5, printed `ALL 2474 ENTITY CHECKS PASSED`, rc 0, and so did 6ac7d972e. M1–M6 ran in a detached worktree of 6ac7d972e with one edit, and M7 ran in one of 9ca68c8c5. 9ca68c8c5 changes only A's two grammars, three cases and the registry, so M1 and M3–M6 do not read its delta. M2's line is unchanged by it:

- M1, gate-sweep.yml's ` || true` deleted: `1 of 2474` failed, U0c, `defects=` naming `SWEEP-DONE run=2 reruns=0` rc 1 (step rc 1, want success), the `RATE-LIMITED` case and the `RuntimeError` case.
- M2, A's test-head strip removed (`stmt = head[cut + 1:].strip()`): `1 of 2474` failed, the null-control check, `cases wrong=['if test -ne', 'if test builtin', 'if test quoted', 'same-line if', 'while test']`.
- M3, B reverted (`_GHA_RUN = ["bash", "-c"]`): `1 of 2474` failed, B's pin, `without errexit=['tests/entities.py:<module>']`.
- M4, nightly.yml's batch gate unwrapped back to a bare `--batch-due` call then `batch=$?` (YAML-valid): `2 of 2474` failed: A's tree check (`hits=['.github/workflows/nightly.yml job=record-autofix ...` then `batch=$?`']`) and the executed batch-gate check, `got {0: 'apply', 4: 'died:4', 1: 'died:1', 2: 'died:2'}`.
- M5, this round's fix deleted (`_SHELL_DOMAIN = [f for f in _SHELL_TRACKED]`, which reads INERT files again): `1 of 2474` failed: B's pin printed `read 312 of 312 tracked`, `sites=19`, `without errexit=` the 8 beatd.py sites. The domain arm failed too. Under the recorder, this is the tree that reddened `tests / closures`.
- M6, the basename match deleted (`lits[0] in ("bash", "sh")`): `1 of 2474` failed: B's pin printed `plants missed=['an absolute shell']`. The `env bash` plant still passes under M6, because the `env` strip runs before the shell match.

- M7, carry 5's arithmetic arm dropped from both grammars (`|\(\(` deleted from `_EX_TEST_HEAD` and `_EX_READER`): `1 of 2474` failed, the null-control check, `cases wrong=['arith list', 'if arith']`.

Before the merge, on 663b63727's tree, M5 and M6 had the same results: each failed `1 of 2473` on the same lines.

## Null control

- The finder harness, `python3 -I dev/audit/harnesses/r10_errexit_capture.py --root <tree>` (sha1 `03767097bf17a13cae0b52425482dcf6b1c3ebdb`), printed `blocks=265 reads=5 hits=0` (rc 0) on `git archive origin/main .github` at `ce5940c0d` and on this head. On M4's tree it printed `hits=1` (rc 1). **It reads flat at both ends by design**: I3 was fixed on main by #2848 before the cut, and I4 is a `$(...)` read outside its unit. The companion that reads I4 is the tree's own executed check, U0c under `bash -e`, which M1 turns red.
- B's domain arm: the check asserts that `tests/entities.py` and `tools/audit/judge_batch.py` are read, and that `tools/audit/seat/beatd.py` is tracked and not read. The rule run over every tracked file, INERT included (the M5 tree), returns 19 sites and 8 defects, all in `tools/audit/seat/beatd.py` (`_stubborn`, `case3`, `pair` ×2, `_race`, `_discovery`, `case6_beat` ×2). Over the domain it returns 11 sites and no defects. So the INERT filter is what separates the two, and a defect planted in the domain is still seen (M3).
- B's plants each yield exactly their own defect: a bare `["bash", "-c", s]`, `["sh", "-x", "-c", s]`, a listed function name in another file, `["/bin/bash", "-c", s]` and `["/usr/bin/env", "bash", "-c", s]`. The pages harness's `["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", s]` yields none. `listed and unused=[]`.
- The closure: the re-derivation on the merged tree left `tests/closures.json` byte-identical to the committed one (`git status --short` empty after `--single`). So main's merged changes read nothing the committed entry lacks.

## Figures

- B's read. The rule is `git ls-files -z -- 'tests/*.py' 'tools/*.py'` less `closure.is_inert`, which gives 312 tracked and 263 read. `_shell_c_sites` over the 263 returns 11 sites. I ran the head's own `_shell_c_sites` and `_SHELL_NOT_A_STEP`, extracted by `ast` from this head's `tests/entities.py`. Each site has a disposition:
  - `tests/entities.py` `<module>` (`_GHA_RUN`): `-e`, closed in this diff
  - `tests/arch_score.py` `run`: `-e`, closed in this diff
  - `tests/entities.py` `_pt_ds_rc`: `-e`, already guarded
  - `tests/entities.py` `_raf_batch_outcomes`, `_pg_run` and `_pg_probe_defects`: `-eo pipefail`, already guarded
  - `tests/entities.py` `_cir_once_count`: listed, two lines of `tools/coverage/coverage_tree.sh`, not a step
  - `tests/throwaway_git.py` `self_test` (3 literals): listed, sources `tests/throwaway_git.sh`
  - `tools/audit/judge_batch.py` `run`: listed, a judge's own command line

  Main's `_bash_env_reads` runs `[*_GHA_RUN, "python3"]`, which the `<module>` site covers. The INERT side is the 8 beatd.py defects under Null control, outside the read by design. A gap is measured and left: an INERT tool that a check spawns as a child (`inert_reads`) is unread. The `/bin/bash` literals in beatd.py are of that kind, and they run beatd's own scripts.
- The closure. `./tests/derive_closures.sh --single tests/entities.py` (Linux, CI venv) at 663b63727's tree, on a refreshed index, added 152 files to the `tests/entities.py` entry. All 152 are non-INERT `tests/`/`tools/` `.py` files. It added 0 `inert_reads` entries and changed no other script's entry. The one domain file still absent is `tests/closure.py`, a gate file whose edit forces `full`. The first attempt, on a fresh worktree's stat-dirty index, recorded 368 closure and 2290 `inert_reads` additions: `git` re-hashed the tree under `strace`. I discarded that recording and did not commit it.
- The selection cost. For each of main's last 300 first-parent merges (`git rev-list --first-parent --merges -n 300 origin/main` at `279578074`), `git diff --name-only M^1 M` was intersected with the committed `tests/entities.py` closure and with the 152 added files: 116 already selected `tests/entities.py`, and 1 would newly select it.
- The two re-keyed scoping pins. `_closure.affected(["tests/dst_checks.py"])` is now `['tests/entities.py', 'tests/features.py', 'tests/dst_checks.py']`, still scoped and still not every closure. `affected(["tests/open_meteo.py"])` is now `['tests/entities.py', 'tests/open_meteo.py']`, so the one-entry cost pin takes `tests/typing_budgets.json`, a file only `tests/typing_ruler.py`'s closure lists (`['tests/typing_ruler.py']`). On the merged tree before 6ac7d972e, both pins failed with exactly those lists (`2 of 2474`).
- A's domain (the verdict's second finding). Shape (d), `if (( $? != 0 ))` and `(( $? )) && ...`, is closed here (carry 5). Three cases pin it: `if arith` and `arith list` each yield 1 hit, and `arith after inline capture` (`rc=0; cmd || rc=$?` then `if (( rc != 0 ))`) yields 0. I drove the head's own `_EX_CASES` through its `_ex_hazards` (`probe_a.py`, which execs the head's definitions extracted by `ast`), and it printed `cases 18 wrong []`. `_ex_scan` gave `(265, 5, 0)` at this head and `(265, 5, 1)` on M4's tree, equal to the frozen harness's `blocks=265 reads=5` and its `hits` on both. So the arm moves no live verdict. Agreement lane: after the change it printed `dead=2` for the test-head and reader identities (they no longer span two files), and after their removal `AGREEMENT ok`. The safe-producer identity is still shared and stays. Left as disclosed, with zero live instances per the reviewer's probe at 9d97a52d5: (a) `prep && cmd` then `rc=$?`, which the class rule excludes by wording; (b) `export RC=$?`; (c) `rc=${?}`. These are carried under Forward-carry.
- The scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: FULL -- every test script runs, nothing is scoped out`, reason `.github/workflows/gate-sweep.yml changes the gate itself`. I ran `tests/entities.py` and the `run_always` lines, and left the full suite to CI. Results: `tests/closure.py selftest` printed `ALL 117 closure shrink pins PASSED`; `tests/layout.py` printed `layout self-test: ok`; `tests/harness_headers.py` printed `ALL 112 HARNESS HEADER CHECKS PASSED`; `tests/env_drift.py --claims-only origin/main` printed `claims hygiene: origin/main ok`; `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`. The `run_always` lines were taken at 663b63727, and 6ac7d972e changes only `tests/entities.py` pins on top of a merge.
- Entity counts at this head: 2474 (the arithmetic arm adds cases, not checks), which is main's count at `ce5940c0d` plus A's two checks and B's pin.

## Red checks

- `tests / closures` (job 123591615668) and `tests / closures-autofix` (job 123603236249), red at 9d97a52d5: `INERT READS UNDER-APPROXIMATED`, then `skip-merge-failed`. They were this diff's. The cause was B's pin reading INERT files in-process, and it is fixed above. A cheaper detector existed, `./tests/derive_closures.sh --single tests/entities.py` before the handoff (one script, about 25 minutes on a seat box), and the round-1 body did not run it. `tools/pr/ci_predict.py --base origin/main` predicted no red at 9d97a52d5 and still prints `no closures ... red predicted` here. It is static and does not see an in-process read whose path list is computed (`git ls-files` at run time). That is a predictor miss, for `root-cause.md`'s seat to weigh.
- `tests / nightly-status`, red at 9d97a52d5: it grades main's scheduled Nightly, and this diff reaches none of what it reads. It is not this PR's.

## Forward-carry

- **Class proposal (carry 4), for the judge or the orchestrator to mint.** "A workflow step's meaningful nonzero exit ended by errexit before the step reads it." Instances, all as `non_round_instances`: I1 (`718c94c84`), I2 (`bc2ad6964`, `guard --require-green; rc=$?`), I3 (#2848, `e0ffb1213`, bare `--batch-due` then `batch=$?`), I4 (gate-sweep's `out=$(...)`, `85d13b859`, fixed here). Seams and detectors: a `$?` read is refused by A tree-wide; a `$(...)` read through output is caught where a harness executes the step under `_GHA_RUN`, and B keeps those harnesses under errexit; I1's cross-step shape has no detector. Carry: R10-ERREXIT-COUNTERMEASURES (this group's carry (4) in dev/programme/rosters/wave-r10-groups.json; the class mint is the judge's or orchestrator's, in dev/audit/config/bugclasses.json)
- **A's unguarded domain (round-1 review, finding 2).** `export X=$?` and `${?}` are bare-producer reads that A and its finder harness both skip, and the tree has no live instance of either. The arithmetic form is closed here (carry 5). The finder harness `r10_errexit_capture.py` still misses all three, which the class's next finder should know. Carry: R10-ERREXIT-COUNTERMEASURES (the same carry (4) entry, for whoever mints the class)

## Friction

none
