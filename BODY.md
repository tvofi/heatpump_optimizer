R10-FRICTION-FIXER-MD: the root-cause seat for #2895, the third filing of the friction key `tools/audit/briefs/fixer.md`. The record is `dev/audit/rca/R10-RCA-FIXER-MD-KEY.md`.

The key is the whole fixer contract under its canonical OLD spelling: `canon()` maps `dev/governance/roles/fixer.md` back to it, and `#N` is stripped. It is not a stale alias of a retired file. Correcting the brief: `fixer-step-N`, `fixer-env`, `fixer-handoff` and `fixer-instrument` stay verbatim keys, because `policyKeyIndex` claims no role contract's bare name. `fixer.md-step17` does fold.

Grouped by the step each entry names, only one cause recurs: step 5, `python3` on PATH is the system 3.11 and not the seat venv (#2671, #2683 x2, plus #2631 and #2937 under verbatim keys). #2709 found the mechanism, which is that only environment variables reach a seat's shell, and added `cloud-setup.sh --check`. Nothing runs that check, though, and the dispatch prompt kept saying the toolchain is on PATH. The cause was reproduced in this seat five days after #2709. **Process state (d).** Every other group is a single body, or is already repaired (step 2, by #2704), or is environment cost cited as `fixer.md` because that is a fixer's default id.

The countermeasure targets (d) by making the process notice its own precondition:
- `.claude/hooks/session-start.sh` prints a `toolchain:` line. Where `cloud-setup.sh --check` refuses, it appends `cloud-setup.sh --env-lines` to the harness's `CLAUDE_ENV_FILE`, which is sourced before each Bash call, and re-checks under that file.
- `cloud_dispatch.py`'s prompt points at that line instead of asserting the toolchain.
- `stop-selfcheck.sh`'s contract case names the contract's current path.

Refused, with numbers in the record: keying friction by step (the bare-`fixer.md` bucket alone is at threshold) and a policy edit to `fixer.md` (that would be a (b) answer to a (d) state).

One step is outside the tree and is the owner's: set the environment variables that `bash tools/audit/seat/cloud-setup.sh --variables` prints, and re-paste the current setup script. The installed profile predates #2709. The hook's `toolchain: OK` line is how a seat will see that done (record, section 5).

Refs #2895. The roster lists #2895 under this group's `issues` with `fixes` empty, so the body does not close it; the disposition is the orchestrator's.

## Head

`31459ff7ca37e78add2fe941a15f26169a368b7d`, on merge base `88c6ad5bbec69bfe157e04597a74d0c9c3e4775c` (origin/main at 2026-10-29 15:06Z).

## Mutation proof

Each mutant was applied to the head, then `CLAUDE_PROJECT_DIR=$PWD bash .claude/hooks/session-start.sh --self-test` and `bash tools/audit/seat/cloud-setup.sh --self-test` were run, then the file was restored:
- M1, `>> "$CLAUDE_ENV_FILE"` append replaced by `true`: `FAIL no variables with a CLAUDE_ENV_FILE exports into it`, `FAIL a shell sourcing the exported file gets venv-ci's python3` (12 passed, 2 failed).
- M2, the `cloud-setup.sh --check` predicate in `toolchain()` forced `true`: `FAIL no variables and no CLAUDE_ENV_FILE refuses, naming the per-call remedy`, plus the two above (11 passed, 3 failed).
- M3, `--env-lines)` arm deleted from `cloud-setup.sh`: the hook's two EXPORTED arms fail (12 passed, 2 failed), and `cloud-setup.sh --self-test` gives `FAIL check is OK in a shell that sourced --env-lines` (14 checks, 1 failed).

## Unpinned sites

`n/a: the diff adds no production or tools/ Python predicate. The new shell arms are pinned by the two self-tests above, each with a killed mutant.`

## Null control

- At the merge base, `.claude/hooks/session-start.sh` prints no `toolchain:` line: `grep -c '^toolchain:'` reads 0.
- In a healthy environment, the head under `eval "$(bash tools/audit/seat/cloud-setup.sh --env-lines)"` prints `toolchain: OK`, and the `CLAUDE_ENV_FILE` it was handed stays at 0 bytes.
- With no venv-ci under the prefix, the self-test reads `n/a`.
- The dispatch prompt at the merge base reads "The toolchain (venv python, node, gh) is on PATH from the environment."; at the head it points at the `toolchain:` line.

## Figures

- The key's count. Instrument: `node tools/policy/policy_lint.mjs --stats --since v7.0.4` at `88c6ad5bb`, which printed `friction rule id at 8 in this window ... (11 entries in all)`. `--since v7.0.5` printed `at 3 ... (4 entries in all)`. Re-derived per entry by the rule at the top of the record: 8 PRs and 11 entries; 3 PRs and 4 entries (#2873, #2903, #2947).
- Merged PRs per window: `git log --first-parent --format=%s v7.0.4..origin/main` with subjects `Merge pull request #N`, giving 285 and 59 (v7.0.5).
- The defect is live in this seat: `bash tools/audit/seat/cloud-setup.sh --check` gave `REFUSE python3 is /usr/local/bin/python3, HPO_TYPING_PYTHON is unset, OPENBLAS_CORETYPE is unset`, exit 1. Under the variables it prints, it gave `OK`, exit 0.
- Demonstration at the head: with no `CLAUDE_ENV_FILE`, `REFUSE`. With one, `EXPORTED`, and `bash -c '. $file; python3 --version'` gave `Python 3.14.7` with `--check` `OK`.
- Standing cost: for `bash .claude/hooks/session-start.sh`, five `date +%s%N` runs each gave 34-43 ms at the head and 26-29 ms at the merge base, and `cloud-setup.sh --check` took 8-10 ms.
- Class seams: `git grep -n "on PATH from the environment"` returned one site at the merge base (`cloud_dispatch.py` `_prompt`), closed in this diff, and none at the head. `git grep -n "cloud-setup.sh --check" origin/main -- .claude/` returned 0 at the merge base, and the detector is added in this diff. The venv-build seam (#2947, uv offers no cpython 3.14.7) is a distinct cause, carried below.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` gave `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. Every changed file is inert by prefix. The `run_always` set passed: `env_drift.py --claims-only`, `closure.py selftest`, `layout.py`, `harness_headers.py`, and `tests/structure.py` (`STRUCTURE RATCHET PASSED`).
- Self-tests at the head: `session-start.sh --self-test` 14 passed, 0 failed. `stop-selfcheck.sh --self-test` 29 passed, 0 failed. `cloud-setup.sh --self-test` 14 checks, 0 failed. `cloud_dispatch.py --self-test` 87 checks, 0 failed.

## Red checks

none

## Forward-carry

- `seat_venv.sh` pins cpython 3.14.7, which this container's uv index does not offer (#2947). Carry: R10-FLY-SUITE-ENV-FLAKES

## Friction

- `cloud-fixer-prompt: stale`: this seat's prompt said the toolchain is on PATH from the environment. `python3` was 3.11 and `cloud-setup.sh --check` refused. Every run here used `eval "$(bash tools/audit/seat/cloud-setup.sh --env-lines)"`, the remedy this PR adds. Carry: dismissed: the generator is fixed in this pull request
- `roster-issues: contradiction`: the brief says this group shuts issue 2895 on delivery, but the roster group lists it under `issues` with `fixes` empty, so pr-contract's intended list refuses a closing keyword for it; the body says `Refs`. Carry: dismissed: the orchestrator disposes the issue against its own roster
