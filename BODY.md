The roster-tooling part of R10-TICK-ORCH (findings R10-TICK b and d), pulled forward because every per-merge step depends on it, plus R10-TICK j. Part of R10-TICK-ORCH; the group has no issue number yet, so this body closes none.

The seat tools held the closed round-9 roster as a constant: `roster_edit.py`'s and `roster_lib.py`'s `ROSTER_PATH`, `--roster-ref` defaults of `handoff/audit-r9-fixplan`, and `state_docs.py`'s `handoff/audit-r9-plan` / `handoff/round9/state`. Round 10's roster (`dev/programme/rosters/wave-r10-groups.json`) lands in a tree that still carries round 9's, so `roster_edit.py wire-issue` refused every round-10 group, and `orchestrator_tick.py`'s PLAN listed round-9 groups even when given the round-10 ref. Why the tick did that: it read `git show <ref>:<roster_lib.ROSTER_PATH>`, and the round-10 ref's tree carries the round-9 file, so the read succeeded on the wrong roster instead of failing.

The fix gives "which roster" one owner. `roster_lib.roster_path(repo, ref, override)` returns the newest `wave-r<N>-groups.json` under `dev/programme/rosters/`, compared as an integer because `wave-r10` sorts before `wave-r9` as text. It reads the ref's tree with `git ls-tree`, or the checkout on disk when no ref is given. A `--roster-path` override wins once it exists, and no roster raises `RosterNotFound`. It does not fall back to another round's roster. `show_roster` resolves through it and now runs git in the repository it is given (it used to ignore `repo`, and the generators passed `OWNER/REPO` there). Every tool takes `--roster-path` and asks `roster_lib`: `roster_edit`, `orchestrator_tick` (which keeps its git reads injectable and takes the choice from `roster_lib.newest_roster`), `state_docs`, `plan_table`, `resume_doc`, `handover_prompt` and `record_row`. Reader defaults are `origin/main`. In `roster_edit`, `--roster-ref` defaults to `main` and `--branch` to the round's `handoff/audit-r<N>-roster` (`roster_lib.round_branch`), so a default edit never targets main. `state_docs` derives its state ref, dir and write set from the roster's round (`state_of`), and refuses when it cannot read a round. The legacy `.claude/workflows/wave-r9-groups.json` fallback is removed: its only ref is archived.

`daemonize.py` (R10-TICK j): on Python 3.14 `nargs=REMAINDER` keeps the leading `--` as the command's first word, so the documented `-- CMD` form was refused as an empty command. `parse_cli` now splits at the first `--` itself, keeps a later `--` for the command, and still parses the bare form.

Alternatives: (1) bump each constant to round 10. That repeats the defect at round 11 and keeps seven owners. (2) Read the roster from an environment variable. That adds a second source the tree cannot test. (3) Keep the legacy fallback. That reintroduces a silent other-round read. The design takes one function in the module that already owns the roster schema.

## Head

9b3fd503feb930ac58bf7492d31c99610060d5e0

## Mutation proof

Each mutant was applied in a detached copy at the head and its tool's self-test run, then restored (`git checkout -- .`):
- M1 `newest_roster` compares as text: roster_lib red (`newest is numeric, not textual`, `two rosters at a ref: the newest`, `two rosters on disk: the newest`, `show_roster reads the newest round's groups`, `the round's roster branch`); orchestrator_tick red (`PLAN roster: two rosters: the newest round's group is unblocked`, `... no round-9 group is read`, `... the roster read is named`); roster_edit rc 1.
- M2 override ignored in `roster_path`: roster_lib red (`an override wins over the newest`, `an override wins on disk too`, `an override the ref lacks refuses loudly`, `an override the checkout lacks refuses loudly`); roster_edit red (`--roster-path wins over the newest`, `--roster-path naming a missing file refuses`).
- M3 silent fallback to the round-9 path: roster_lib red (`no roster at a ref refuses loudly`, `no roster on disk refuses loudly`); roster_edit rc 1.
- M4 `state_of` hard-coded to round 9: state_docs red (`round 10's state`). M4b `roster_round_of` returns 9: state_docs red (`two rosters at the ref: round 10`, `no roster refuses, naming the round question`).
- M5 daemonize without the `--` split: daemonize red (`` `-- CMD` parses to CMD, the `--` dropped ``, `options before `--` still parse`, `a later `--` belongs to the command`).
- M6 tick reads a fixed round-9 path: orchestrator_tick red (four `PLAN roster` checks, including `no roster at the ref is UNREADABLE, loudly`). M7 tick ignores `--roster-path`: red (`PLAN roster: --roster-path wins over the newest`).
- M8 roster_edit's default branch is the base ref (main): roster_edit rc 1. The round-10 roster branch is never written.

## Null control

`dev/audit/harnesses/r10_tick_which_roster.py` drives each tool of a tool tree against a throwaway two-ref mirror of `main` and `handoff/audit-r10-roster`. Nothing reaches GitHub. Its `null_r9_main` arm runs `wire-issue` on a round-9 group at `main`, where round 9's is the only roster. That arm is `rc=0` at the merge base and at the head, so with one roster present the fix changes nothing. The perturbation arm is the head run with `--roster-path dev/programme/rosters/wave-r9-groups.json`. It returns `wire_r10_rc=2` and `tick_plan_r9_lines=13` / `tick_plan_r10_lines=0`, the merge-base readings, so the harness tracks the roster choice and not some other difference between base and head.

## Figures

Instrument: `python3 -I dev/audit/harnesses/r10_tick_which_roster.py --tree <tree> --repo <clone>` at the base cfe24f8ef29f (the branch point), at the head and at the head with the perturbation; roster ref `handoff/audit-r10-roster` at db71fe47.
- base: `wire_r10_rc=2` (`REFUSED: no roster group 'R10-TICK-ORCH' (known: 170 groups)`), `wire_r10_touched_r10_file=0`, `null_r9_main_rc=0`, `tick_plan_r9_lines=13`, `tick_plan_r10_lines=0`, `daemonize_dashdash_rc=2`.
- head: `wire_r10_rc=0` (the commit touched `dev/programme/rosters/wave-r10-groups.json` only), `wire_r10_touched_r10_file=1`, `null_r9_main_rc=0`, `tick_plan_r9_lines=0`, `tick_plan_r10_lines=52`, `daemonize_dashdash_rc=0`.
- head with `--roster-path` naming round 9: `wire_r10_rc=2`, `tick_plan_r9_lines=13`, `tick_plan_r10_lines=0`.
Rule for the tick counts: PLAN lines matching `\bR9-[A-Z0-9-]+:` or `\bR10-[A-Z0-9-]+:`. The 52 equals the round-10 roster's group count at db71fe47.

The branch merges origin/main at 93f5970e90d0, a merge that touches none of this change's files. The head readings above and below were re-taken after that merge. Self-tests at the head: `python3 tools/audit/seat/<tool>.py --self-test` for roster_lib (14 checks, 0 failed), roster_edit (45 checks, 0 failed), orchestrator_tick (88 checks, 0 failed), state_docs (all checks passed), plan_table (25 checks, 0 failed), resume_doc (14 checks, 0 failed), handover_prompt (13 checks, 0 failed), record_row (all checks passed) and daemonize (`SELF-TEST PASS`).

Class seams. Rule: `git grep -nE "wave-r[0-9]+-groups|audit-r[0-9]+-(fixplan|plan|roster)|round[0-9]+/state" -- 'tools/audit/seat/*.py' 'tools/audit/seat/*.sh' 'tools/audit/seat/*.mjs'`. At the merge base it hits 9 files. At the head every hit is a self-test fixture, a docstring example, or `prune_refs.py`'s archive-tag example (it names a ref as data and does not choose a roster). No tool chooses a roster anywhere else. Outside the seat tools, the one live hit is a comment in `.github/workflows/tests.yml` (record-autofix) naming `roster_lib.ROSTER_PATH`. This pull request removes that symbol, and the file is code-owned, so the comment is forward-carried (below) and not edited here. The job's behaviour is unchanged: `record_row --roster-ref origin/main` now reads the newest roster at main.

Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (tests/entities.py, tests/harness_headers.py). `tools/pr/ci_predict.py` predicted the `closures` red `INERT READS tests/harness_headers.py` for the new harness. The inert dimension is recorded only on Linux (`ci-autofix.md`), so a Darwin `--single` cannot record it. `tests/closures.json` therefore lists the harness by hand in `inert_reads["tests/harness_headers.py"]`, in sorted order, which is the entry the CI recording would add, and `ci_predict` now prints `no closures or fast red predicted`. At the head, `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/entities.py` (seat venv, Python 3.14) printed `ALL 2319 ENTITY CHECKS PASSED`, including `tools/audit/seat/roster_lib.py --self-test passes: the newest roster, the override, the loud refusal`. `tests/harness_headers.py` printed `ALL 109 HARNESS HEADER CHECKS PASSED` (its first run caught the new harness's depth root, and the harness now uses the canonical `repo_root` walk). `tests/entities.py` now runs `roster_lib`'s self-test beside its existing branch-to-group check. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `dS +0.0000 NULL`. `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`. No golden fixture is in any changed file's closure (`tests/golden.py` scoped out), so GOLDEN_MODE=drift has nothing to measure.

## Red checks

none

## Unpinned sites

Every changed production line in `tools/audit/seat/` is pinned by its tool's self-test, as the mutation proof above records. Those tools sit under the INERT `tools/audit/` prefix, so `roster_lib`, `state_docs` and `record_row` reach CI through `tests/entities.py`, and the others through their self-tests.

## Forward-carry

`.github/workflows/tests.yml` (record-autofix, `ROSTER_REF` comment) names `roster_lib.ROSTER_PATH` and the round-9 path. After this merges the comment should say `roster_lib.roster_path`, the newest roster at the ref. It is code-owned, so the orchestrator owns routing it. The remaining TICK-ORCH items, (a) the absent-versus-waiting context and (c) the SyntaxWarning at `orchestrator_tick.py`'s `#[0-9]\+` grep, are untouched here and stay with R10-TICK-ORCH's roster brief.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
