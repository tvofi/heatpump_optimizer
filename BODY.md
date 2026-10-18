Part of #201.

**Policy change: tvofi approves it before merging** (an approving review at the head; `ci-autofix.md` is code-owned policy under `CLAUDE.md`).

`dev/governance/rules/ci-autofix.md` named only the bot's route for an INERT READS — wait for `closures-autofix` — while `prepr.sh` step 6d refuses the push that route needs. #2376 added `python3 tools/pr/ci_predict.py --apply-inert` as the seat's pre-push repair and drafted the rule sentence in `dev/audit/rca/R10-RCA-INERT-PREDICT.md` section 5 ("Not landed, because it is policy and needs tvofi's approval"). This lands that sentence verbatim, at the place the RCA names (after "the bot merges INERT READS from CI recordings too (#1886, R9-CI-1)"):

> One 6d predicts is not the wait: `prepr.sh` refuses it before the push, and `python3 tools/pr/ci_predict.py --apply-inert` writes the entry the Linux recording would — that commit is not a `--single`.

**RCA process state addressed: (d), its preconditions changed underneath it** (`R10-RCA-INERT-PREDICT.md` section 2). #2376 fixed (d) in the instrument; this fixes it in the rule, so the rule's "wait" covers only an INERT READS CI finds that 6d did not predict.

Instrument wording the sentence must match: the flag is `--apply-inert` and the command is `python3 tools/pr/ci_predict.py --apply-inert`, as `ci_predict.py`'s own route line prints it ("an INERT READS entry is written with `python3 tools/pr/ci_predict.py --apply-inert` and committed"), and as 6d's step line names it ("`--apply-inert` repairs them"). The command sits on one line of the rule, so a grep for it finds it.

**Paid for, not raised** (`ratchet-budgets.md` step 1). The file sat 1 token under its `files_tokens` cap; the sentence costs about 50. Four cuts in the same file pay for it:

- "(Linux `strace` recordings are the ones to merge)": a duplicate. The same paragraph's next sentence says Darwin "cannot replace a Linux node recording", and the inert clause says `strace`-only.
- "— the status a clean run also reports —": a duplicate. The "What green means" paragraph already lists `skip-clean` as green.
- "Closing it needs a dry-run classification and a ruling on the guard's contract.": a design note on future work. It tells a seat holding a `skip-not-allowed` nothing to do.
- "; none is closed here" in the heading: scaffolding. A rule file closes nothing.

The generated `.claude/rules/ci-autofix.md` and `.cursor/rules/ci-autofix.mdc` were regenerated with `node tools/policy/rules_sync.mjs`. No `*_budgets.json` is touched.

## Head

107a6e00d3d0360348eb75865fe161dff4f35bfb

## Mutation proof

n/a: a prose change with no production line. The checks it can redden are mechanical. Reverting the generated copies alone makes `node tools/policy/rules_sync.mjs --check` refuse the drift. Without the four cuts, a plain `node tools/policy/policy_lint.mjs` refuses `ci-autofix.md` on `files_tokens` (see Null control).

## Null control

At the merge base, `node tools/policy/policy_lint.mjs --budgets` puts `ci-autofix.md` 1 token under its cap. On a detached `origin/main` worktree with only the sentence added and nothing cut, a plain `node tools/policy/policy_lint.mjs` refuses with `ERROR [budgets] .claude/rules/ci-autofix.md: ... exceeds its cap ... (files_tokens)`. With the four cuts it exits 0. `--budgets` alone only prints the rows; the plain run is the one that refuses.

## Figures

- `node tools/policy/policy_lint.mjs --budgets`: the `ci-autofix.md` row at the head, against its cap, compared exactly.
- `node tools/policy/rules_sync.mjs --check`: RULES-SYNC ok.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: the scoped gate's mode line, `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`. It names `tests/entities.py`. Run under `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`, it ends `ALL 2346 ENTITY CHECKS PASSED`. Run with the seat toolchain's `BASH_ENV` set, it ends `1 of 2346 ENTITY CHECKS FAILED`, on `graders-head-copy's delivery_status step ...`, and a detached `origin/main` worktree ends the same way. So that failure is not this diff's (see Friction).
- `run_always` lines, all exit 0 at the head: `python3 tests/env_drift.py --claims-only <merge-base>`, `python3 tests/closure.py selftest`, `python3 tests/harness_headers.py` and `python3 tests/layout.py`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `env -u BASH_ENV bash tools/pr/prepr.sh <this body>`: rc=0 at the head. With the toolchain's `BASH_ENV` set, its `closures` step refuses on `tests/entities.py (exit 1)` while recording, for the Friction line's cause.

## Red checks

none

## Forward-carry

none

## Friction

entities-bash-env: unenforced: `tests/entities.py`'s `_pt_ds_rc` stubs `git` and `python` by prepending a stub `bin/` to `PATH`, then runs `bash -e -c`. Where `BASH_ENV` points at a profile that prepends its own `PATH`, as `/etc/profile.d/hpo-toolchain.sh` does on this cloud seat, the real `python` wins and every case reads 0. This reproduces on `origin/main`, and `env -u BASH_ENV` clears it. Not touched here.
ci-autofix-draft: unclear: the drafted sentence opens "One 6d predicts", whose antecedent is "an INERT READS" in the sentence before; it was landed verbatim as the RCA drafted it rather than reworded on this seat's judgement.

## Approval

Policy: `dev/governance/rules/ci-autofix.md` and its two generated copies. tvofi approves before merging, by an approving GitHub review at the head. Nothing is merged on this seat's word.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_018qAxaCuvKU3aVvNn8asGdA
