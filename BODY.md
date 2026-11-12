Repair of the handoff blocked at `4b91c2f9f705b76db9e041e1c88ad12bb79147f8` (class-open). open_pr.sh closed a freshly opened pull request when its row push was refused by a red that was the host's (PR 3508). Whether a refusal is the host's is now measured: `pr_host_refusal` (`tools/audit/seat/pr_args.sh`) runs prepr's self-test on the refused head and on a pristine `origin/main` tree, each a detached throwaway worktree run the same way, and the refusal is the host's only when both give the same exit status and the same set of `FAIL` rows. The path guard on `prepr.sh` is deleted. Main's answer is kept per `origin/main` sha in `$HPO_STATE_DIR/pr/selftest-main/<sha>.sig`.

The log is still read, for one thing only: which step refused. prepr's self-test is the one step with a form that runs on a tree alone; a row naming any other step reads the head's body, so it is the head's and closes. Everything unmeasured closes: no worktree at a sha, no self-test in a tree, no cache directory, a refusal the re-run does not reproduce, and a p2 log left by an earlier run of the topic (`OP_REFUSED` is set only by this run's own refused row push).

Alternatives that lost: widening the path guard to the list `selftest_inputs` returns (a copy of a derived list, and still a proxy: `fixer.md` step 17's enumerated-cases shape); comparing the head's `FAIL` rows as printed in the p2 log (prepr prints the first three only, so the set is truncated); a subset rule, head's rows within main's (a head run that stops short with no rows would pass it).

Design choices a reviewer may read as bugs: equality, not subset, so a head that fixes one of several host failures is closed as before; a host fault that stops the self-test before it reads the tree (exit 3 on both) is the host's even if the head also broke an input, because the refused run was masked the same way and CI's governance job still runs the self-test on the open PR; a cached pass for a main sha outlives a host that breaks later, which closes as before until main moves or the file is removed.

Cost on the refusal path only: the self-test once on the head at every such refusal and once per `origin/main` sha, outside prepr's heavy slot, under the branch lock.

prepr.sh ran with PREPR_SKIP_CLOSURES=1 (the cloud environment trap the brief names).

## Head

19c3f4f85cad138f99c63309ac1717ae8d601439

Merges origin/main `005eed2573da9e946fa4838de147401d0ff36cc1` into the blocked handoff head and repairs on top; figures taken 2026-11-12 UTC at that main.

## Mutation proof

`bash tools/audit/seat/pr_args.sh --self-test` at the head: 235 checks, 0 failed. Each production line of the classifier has its own in-suite mutant, run by that command:

- line deleted: `mut:hostother` (direct and through open_pr.sh), `mut:hostrows`, `mut:hostcache`, `mut:hostfails`, `mut:hostsame` (direct and through open_pr.sh), `mut:hoststale`; each arm asserts the wrong verdict the mutant gives.
- `|| return 1` turned into `|| return 0`, the shape of the review's surviving mutdiffread: `ret:hostdir`, `ret:hosthead`, `ret:hostmain`, `ret:sigtree`, `ret:signone`; each arm asserts the unmutated line answers the head's and the mutant answers the host's. The line mutdiffread mutated (the diff read) no longer exists; these five are every `return 1` on an unmeasured path that replaced it.

## Null control

The blocked head's production under this head's arms (open_pr.sh from `4b91c2f9`, `pr_host_refusal` and `pr_step_sig` removed from pr_args.sh): 235 checks, 19 failed, among them "a self-test refusal the head's own commit causes still closes the PR, under the host fault", which is the block: the old classifier leaves that PR open because the head's commit touches a file other than prepr.sh.

In the suite: a head-caused refusal closes (through open_pr.sh, and directly for each path `selftest_inputs` returns); a body-contract row closes; a mixed log closes; a refusal that passes on re-run closes; the same `FAIL` rows under another exit status close.

## Figures

- Seam rule (step 8), the inputs of the refused step: prepr's own `selftest_inputs`, evaluated from its text by the self-test (`eval "$(sed -n '/^SELFTEST_FIXTURES=/,/^}/p' tools/pr/prepr.sh)" && selftest_inputs`). At this head it returns 60 entries; the arm "a head breaking any one path prepr's own selftest_inputs returns" builds one head per entry and reads 60 of 60 as the head's under a host fault that fails main alike. Disposition of every entry: closed in this diff, by comparison of the two trees rather than by name. Had one been unguarded the arm would print fewer heads than entries and fail.
- Seam rule, the sites that decide a close: `git grep -n -E "gh pr close" -- tools .github .claude` returns two lines: `tools/audit/seat/open_pr.sh` in `op_close_unrowed` (closed in this diff: its one exemption is `op_host_refusal`), and a string in `tools/audit/seat/gh_calls.py`'s test table (not a call). `git grep -n host_refusal -- tools .github tests dev/governance .claude` shows one caller of the classifier, that function.
- Main measured once: the arm "origin/main was measured once across all of those refusals" counts the stand-in self-test's runs per sha, 1 for main over 61 refusals; `mut:hostcache` makes it 2 over 2.
- Real trees, not the stand-in (this cloud host, `pr_host_refusal` sourced from the head, `origin/main` 005eed25): a head one scratch commit above this one that makes `tools/policy/policy_lint.mjs` accept every body (`process.exit(0)` as its second line; the review's instance) reads as the head's: main's signature is `rc=0` with no `FAIL` row, the head's is `rc=2` with `FAIL` rows beginning `a body that does not name its red check is refused (got 0, wanted 1)`; the two measurements took 664 s. Its control: this head unbroken under an induced host fault (`PREPR_SELFTEST_FLOOR_KB=99999999999999`, the self-test's own ENVIRONMENT exit) reads as the host's, both signatures `rc=3` with no `FAIL` row. The log handed in both times held one `REFUSE   self-test` row and app_push's summary.
- `PYTHONPATH=tests/hastub bash tools/pr/prepr.sh --self-test` on a pristine worktree of `origin/main` 005eed25 on this host: 542 passed, 0 failed, 346 s. That is the price of one measurement.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED` naming `tests/doc_claims.py`, which passes; `python3 tests/structure.py` passes.

The finding has no committed finder's harness (the review's verdict says so); the probe the reviewer built is superseded by the arms above, which land in the instrument's own self-test.

## Red checks

none

## Forward-carry

none

## Friction

none
