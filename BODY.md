R10-FRICTION-FIXER-MD: the root-cause seat for #2895, the third filing of the friction key `tools/audit/briefs/fixer.md`. The record is `dev/audit/rca/R10-RCA-FIXER-MD-KEY.md`.

The key is the whole fixer contract under its canonical OLD spelling: `canon()` maps `dev/governance/roles/fixer.md` back to it, and `#N` is stripped. It is not a stale alias of a retired file. Correcting the brief: `fixer-step-N`, `fixer-env`, `fixer-handoff` and `fixer-instrument` stay verbatim keys, because `policyKeyIndex` claims no role contract's bare name. `fixer.md-step17` does fold.

Grouped by the step each entry names, only one cause recurs: step 5, `python3` on PATH is the system 3.11 and not the seat venv (#2671, #2683 x2, plus #2631 and #2937 under verbatim keys). #2709 found the mechanism, which is that only environment variables reach a seat's shell, and added `cloud-setup.sh --check`. Nothing runs that check, though, and the dispatch prompt kept saying the toolchain is on PATH. The cause was reproduced in this seat five days after #2709. **Process state (d).** Every other group is a single body, or is already repaired (step 2, by #2704), or is environment cost cited as `fixer.md` because that is a fixer's default id.

The countermeasure targets (d) by making the process notice its own precondition:
- `.claude/hooks/session-start.sh` prints a `toolchain:` line. Where `cloud-setup.sh --check` refuses, it appends its own `--env-lines` to the harness's `CLAUDE_ENV_FILE`, which is sourced before each Bash call, and re-checks under that file. `--env-lines` is `cloud-setup.sh --variables`, with each line exported and `%q`-quoted. `--variables` is the interface main already has.
- `cloud_dispatch.py`'s prompt points at that line instead of asserting the toolchain. Its per-call remedy is `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`.
- `stop-selfcheck.sh`'s contract case names the contract's current path.
- `tools/audit/seat/cloud-setup.sh` differs from main only by a comment pointing at the hook.

Refused, with numbers in the record: keying friction by step (the bare-`fixer.md` bucket alone is at threshold) and a policy edit to `fixer.md` (that would be a (b) answer to a (d) state).

One step is outside the tree and is the owner's: set the environment variables that `bash tools/audit/seat/cloud-setup.sh --variables` prints, and re-paste the current setup script. The installed profile predates #2709. The hook's `toolchain: OK` line is how a seat will see that done (record, section 5).

Refs #2895. The roster lists #2895 under this group's `issues` with `fixes` empty, so the body does not close it; the disposition is the orchestrator's.

## Head

`b0392fd138fbc275342f8f09c6ed7543119fb1c7`, on merge base `279578074a17cb2c7f527f5e28da0de4e2006db0` (origin/main at 2026-10-29 16:45Z, read at 2026-10-29T16:45Z). Code is on `handoff/r10-friction-fixer-md`. The head is one commit on top of PR head `381cab4c6`, so it fast-forwards from the previous handoff, `31459ff7c`.

## Mutation proof

Each mutant was applied to `.claude/hooks/session-start.sh` at the head. `bash .claude/hooks/session-start.sh --self-test` was run, then the file was restored. Unmutated, the self-test gives 16 passed, 0 failed.
- M1, `env_lines >> "$CLAUDE_ENV_FILE"` replaced by `true >> …`: `FAIL no variables with a CLAUDE_ENV_FILE exports into it`, `FAIL a shell sourcing the exported file gets venv-ci's python3`, `FAIL a PATH entry holding a space survives the exported file`.
- M2, the `cloud-setup.sh --check` predicate in `toolchain()` forced `true`: `FAIL no variables and no CLAUDE_ENV_FILE refuses, naming the per-call remedy`, plus the three above.
- M3, `%q` replaced by `%s` in `env_lines()`: `FAIL a PATH entry holding a space survives the exported file`.
- M4, the hook's `--env-lines` arm emptied (`env_lines; exit 0` became `exit 0`): `FAIL the REFUSE line's remedy, eval of this hook's --env-lines, gets venv-ci's python3`.

## Unpinned sites

`n/a: the diff adds no production or tools/ Python predicate. The new shell arms are pinned by session-start.sh's self-test, each with a killed mutant above.`

## Null control

- At the merge base, `.claude/hooks/session-start.sh` prints no `toolchain:` line: `bash <base copy> | grep -c '^toolchain:'` reads 0.
- In a healthy environment the head prints `toolchain: OK`, and the `CLAUDE_ENV_FILE` it was handed stays at 0 bytes. The environment was made healthy in this seat with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Under `env -i` with the same file, the head prints `EXPORTED` and the file grows to 133 bytes. A shell sourcing it reads `Python 3.14.7`, and `cloud-setup.sh --check` gives `OK`.
- With no venv-ci under the prefix, the self-test reads `n/a`.
- The red check's own control is below, under `## Red checks`: the old head fails under CI's base restore and this head passes.
- The dispatch prompt at the merge base reads "The toolchain (venv python, node, gh) is on PATH from the environment."; at the head it points at the `toolchain:` line.

## Figures

- The key's count. Instrument: `node tools/policy/policy_lint.mjs --stats --since v7.0.4`, run at `88c6ad5bb` (the earlier base), which printed `friction rule id at 8 in this window ... (11 entries in all)`. `--since v7.0.5` printed `at 3 ... (4 entries in all)`. Re-derived per entry by the rule at the top of the record: 8 PRs and 11 entries; 3 PRs and 4 entries (#2873, #2903, #2947). This is a record measured at that SHA, not re-taken at `279578074`: `--stats` did not finish within 100 s here.
- Merged PRs per window: `git log --first-parent --format=%s v7.0.4..origin/main | grep -c '^Merge pull request #'` gives 286 at `279578074` (285 at `88c6ad5bb`).
- The defect is live in this seat: `bash tools/audit/seat/cloud-setup.sh --check` gave `REFUSE python3 is /usr/local/bin/python3, HPO_TYPING_PYTHON is unset, OPENBLAS_CORETYPE is unset`. After `eval "$(bash .claude/hooks/session-start.sh --env-lines)"` it gave `OK python3 is /opt/hpo/venv-ci/bin/python3`.
- Standing cost: five `date +%s%N` runs of `bash .claude/hooks/session-start.sh` gave 34-37 ms at the head and 27-39 ms at the merge base.
- Class seams: `git grep -n "on PATH from the environment"` returned one site at the earlier base (`cloud_dispatch.py` `_prompt`), closed in this diff, and returns none at the head. `git grep -n -- "--env-lines"` at the head returns only `session-start.sh` (definition, remedy, self-test), `cloud_dispatch.py` (the remedy, naming the hook) and the record. No reader calls `cloud-setup.sh --env-lines`. The venv-build seam (#2947, uv offers no cpython 3.14.7) is a distinct cause, carried below.
- Gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` gave `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. The `run_always` set passed with `PYTHONPATH=tests/hastub`: `env_drift.py --claims-only 279578074…` (`ok`), `closure.py selftest` (`ALL 117 closure shrink pins PASSED`), `layout.py` (`ok`), `harness_headers.py` (`ALL 112 HARNESS HEADER CHECKS PASSED`). `tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Self-tests at the head:
  - `session-start.sh --self-test`: 16 passed, 0 failed.
  - `stop-selfcheck.sh --self-test`: 29 passed, 0 failed.
  - `pre-edit.sh --self-test`: 22 passed, 0 failed.
  - `cloud-setup.sh --self-test`: 13 checks, 0 failed (main's arms; the `--env-lines` arm left with the flag).
  - `cloud_dispatch.py --self-test`: 87 checks, 0 failed.
  - `node tools/policy/policy_lint.mjs --hooks`: `HOOKS ok`.

## Red checks

- `governance / policy-docs`: **this diff caused it**, and it is fixed at this head.
  - The job's restore step (`check source restored from PINNED`) checks out main's copy of the pathspec `tools/audit/*.sh`. Git's pathspec `*` crosses `/`, so `tools/audit/seat/cloud-setup.sh` was restored too (the log reads `1 file(s) differ`). `policy_lint.mjs --hooks` then ran the PR's `session-start.sh --self-test` against main's `cloud-setup.sh`, which has no `--env-lines`. Result: `SELF-TEST FAILED SessionStart … 12 passed, 2 failed`.
  - Reproduced by running that step's exact pathspec list and `git checkout "$PINNED"`, then `node tools/policy/policy_lint.mjs --hooks`. At `381cab4c6` (control) it gives `12 passed, 2 failed` / `HOOKS REFUSED`, the failing arms being `no variables with a CLAUDE_ENV_FILE exports into it` and `a shell sourcing the exported file gets venv-ci's python3`. At this head it gives `16 passed, 0 failed` / `HOOKS ok`.
  - The fix is the shape above: the hook depends only on `cloud-setup.sh --variables`, which main has.
  - Cheaper detector: running `--hooks` locally after the same base restore. It costs one `git checkout` and about 2 s per run. None runs today: `prepr.sh` and `ci_predict.py` do not apply the base restore before predicting `policy-docs`. A plain local `--hooks` passed at the old head and missed this.
  - Not built here, because it is outside this group's scope. It is carried below, to the stage that owns the restore list.
- `tests / nightly-status`: grades main's nightly run, not this pull request. This diff touches none of what it reads: no workflow, no nightly job, no suite script.

## Forward-carry

- `seat_venv.sh` pins cpython 3.14.7, which this container's uv index does not offer (#2947). Carry: R10-FLY-SUITE-ENV-FLAKES
- `governance.yml` policy-docs' base-restore pathspec `tools/audit/*.sh` also restores `tools/audit/seat/*.sh` (git pathspec `*` crosses `/`). So an unpinned caller, such as a hook, that uses a new interface its own PR adds to a file under `tools/audit/` goes red on a PR and green after merge. `prepr.sh`/`ci_predict.py` do not emulate the restore before predicting that job. Carry: R10-PREPR-CAP

## Friction

- `cloud-fixer-prompt: stale`: the original seat's prompt said the toolchain is on PATH from the environment. `python3` was 3.11 and `cloud-setup.sh --check` refused. This seat ran its checks after `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`, the remedy this PR adds. Carry: dismissed: the generator is fixed in this pull request
- `roster-issues: contradiction`: the brief says this group shuts issue 2895 on delivery, but the roster group lists it under `issues` with `fixes` empty, so pr-contract's intended list refuses a closing keyword for it; the body says `Refs`. Carry: dismissed: the orchestrator disposes the issue against its own roster
