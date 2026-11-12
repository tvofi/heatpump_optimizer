Repair of the handoff blocked a second time at `19c3f4f85cad138f99c63309ac1717ae8d601439` (class-open), on top of that head; not a re-cut. open_pr.sh leaves a freshly opened pull request open when its refused row push is the host's (PR 3508), decided by measurement: `pr_host_refusal` (`tools/audit/seat/pr_args.sh`) runs prepr's self-test on the refused head and on a pristine `origin/main` tree and calls the refusal the host's only when both give one exit status and one set of `FAIL` rows. The block: every measurement built its worktree at one path under the cache all topics share, so two refusals measured at once replaced each other's tree mid-run.

What changed in `pr_step_sig` and the cache write:

- Each measurement owns its tree: `mktemp -d <cache>/tree.XXXXXX`, made for that one call. No run names, removes or reuses another's; the removal of a stale tree before each run, which was the defect, is gone.
- A run that did not end whole is not a measurement: its tree gone or off the measured sha when the self-test returns, or the self-test ended by a signal (a status above the shell's signal base). It is the head's, and it is never kept as main's answer.
- Main's answer is written under the writing process's own name (`<sha>.tmp.<pid>`) and renamed into place, so a reader sees a whole file or none.
- The `tools/audit/prepr.sh` copy path (the review's surviving mutant) is kept, because prepr's own step runs that copy when a tree holds one, and pinned by `mut:sigold`.

Alternatives that lost: one lock around the cache (serialises measurements, minutes each by the figure below, behind every other topic's, during exactly the host fault the hotfix serves, and leaves the stale-tree removal in place); dropping the copy-path line (a tree holding the self-test only at the copy path would then be unmeasured and closed, where prepr itself runs it).

Design choices a reviewer may read as bugs: a self-test a signal ends on both trees closes the PR, as everything unmeasured does, where an exit 3 on both is the host's; an opener killed mid-measurement leaves its `tree.*` directory, because removing a tree this run did not make is the class; two runs that both find no answer kept for main both measure it, and the later rename wins; `rm -f <cache>/*.sig` can drop an answer another run just kept, which costs one more measurement and no verdict.

prepr.sh ran with PREPR_SKIP_CLOSURES=1 (the cloud environment trap the brief names).

## Head

29c904c23278a56900a6087e5b823df1009cdd13

The blocked head `19c3f4f85cad138f99c63309ac1717ae8d601439`, the repair on it, then a merge of the pull request's branch (`origin/fix/r10-hotfix-openpr-host-refusal` at `89d2a2d3df91b007f799af20edbb7c0b99f15205`: the delivery row and its merge of main), which prepr's push-order step asked for because that branch had moved past the handoff. The merge touches none of the three files of the delta. Every figure below was taken at this head on 2026-11-12 UTC; `git merge-tree --write-tree origin/main HEAD` exits 0 at origin/main `870238eb2194c99ae1ad6f1f78e0665e838c70f3`, merge base `43e95474559ca8e2188830f8775c1ddf52df964a`.

## Mutation proof

Full pass over the delta: `python3 tools/audit/seat/mutant_run.py --in-place --spec dev/audit/harnesses/r10_hotfix_openpr_host_refusal_mutants.json --cmd 'bash tools/audit/seat/pr_args.sh --self-test' --report-only` prints `SURVIVED NULL` and `KILLED` for each of the spec's mutants, no `SURVIVED` line among them. The spec covers every production line of `pr_step_sig`, `pr_host_refusal` and open_pr.sh's hook: S01 to S21 the measurement, H01 to H09 the comparison and the cache, O01 to O04 the opener. S06 and S07 mutate the copy-path line beyond `mut:sigold`'s deletion. The default copy tree reads `KILLED NULL` (the suite needs a checkout), hence `--in-place`. It was run as six slices of the spec in six detached worktrees of this head, each with its own null.

In the suite, new with this repair: `ret:sigpriv`, `mut:sigold`, `ret:sigwhole` (two arms), `ret:sigkilled`, and `shared`, which puts the blocked head's one shared tree back into this head's `pr_step_sig`.

Three of the spec's mutants are killed only because the stand-in self-test was made stricter in this repair (written before the pass, so no surviving run of them was observed): it fails when not run with prepr's `PYTHONPATH` (S09), prints the head's break row on stderr (S10), and prints the host's row twice on a tree above main (S21).

Not pinned, by disposition:

- The `.tmp.<pid>` suffix. A shared temporary name changes a result only when two writers interleave inside one `printf`; no arm overlaps at that grain.
- The bound in the signal test, `[ "$rc" -le 128 ]`. A signal's status is that bound plus the signal's number and prepr's self-test exits 0 to 3, so the bound itself is reached by neither side.

## Null control

The blocked head's production under this head's arms (`pr_step_sig` through `pr_host_refusal` taken from `19c3f4f8`, the rest of pr_args.sh from the head): seven arms failed at this head. Six of them also failed in the one earlier run, at the repair commit before the merge (`8521f19bacbaef01d7b8cf58fa9547ef4847a9a7`). Among the six: "two host refusals measured at once, each in a tree of its own, are both the host's, and no tree outlives its run", which is the block, and the three whole-run arms (trees removed under both runs; a main run whose tree was removed keeps no answer; a self-test ended by a signal). The other two, `ret:sigpriv` and `mut:sigold`, fail there because the old text carries neither tag, so they say nothing about the old code.

The seventh is the arm that starts with no answer kept for main (a head's own break beside a host refusal): it failed on the blocked head's code at this head and passed in the earlier run. There the outcome turns on which run replaces the tree during main's measurement, so it is not the arm that shows the defect; the arm above is, and `shared` fails it on every run because the first run is held inside its tree until the second has replaced it.

## Figures

- Seam rule (step 8), every path a measurement writes under the cache: `sed -n '/^pr_step_sig() {/,/^pr_push_failed() {/p' tools/audit/seat/pr_args.sh | grep -o -E '"\$(3|c|w)[^" ]*"|"\$c"/\*\.sig' | sort | uniq -c` names four: `$3/tree.XXXXXX` and everything under `$w` (closed in this diff: one per call); `$c/$4.tmp.$$` (closed in this diff: one per process); `$c/$4.sig` (shared by design: created only by rename of a whole run's answer, read whole); `"$c"/*.sig` (shared by design: the removal of older answers, costing a re-measurement). The checkout's worktree registry is shared too: git names each registration after the tree's own basename, and the overlap arms assert `git worktree list` returns to one line.
- Seam rule, the sites that decide a close: `git grep -n -E "gh pr close" -- tools .github .claude` returns two lines, `tools/audit/seat/open_pr.sh` in `op_close_unrowed` (its one exemption is `op_host_refusal`) and a string in `tools/audit/seat/gh_calls.py`'s test table (not a call).
- Overlap, stand-in self-test: the arm holds the first run inside its tree until the second run is inside its own (the stand-in writes `alone` if no second run arrives within its wait, and the arm fails on it). With main's answer kept: two host refusals both read 0. With none kept: a head's break reads 1, a host refusal 0, the kept answer equals the unraced one, and both heads read the same alone afterwards. Under `shared` the first refusal reads 1: PR 3508's defect.
- Overlap, real trees (this cloud host, functions sourced from the head, `origin/main` 870238eb, one cache; two `tree.*` directories stood in it at once): the signature of a scratch head that makes `tools/policy/policy_lint.mjs` accept every body (`process.exit(0)` as its second line) was taken while a refusal of this head was measured. The scratch head: `rc=2`, 47 `FAIL` rows, the first `a body that does not name its red check is refused (got 0, wanted 1)`. This head: 1, the head's (the self-test passes on both trees, so nothing is reproduced); kept for main: `rc=0`, no row. the three self-test runs took under a quarter of an hour together; no `tree.*` left in the cache. Control, a second cache under an induced host fault (`PREPR_SELFTEST_FLOOR_KB=99999999999999`): this head and its parent measured at once both read 0, the host's, main kept as `rc=3`. The real self-test leaves its tree at the measured sha, or the first run would have read unmeasured.
- Round 1's class, unchanged by this repair: the arm "a head breaking any one path prepr's own selftest_inputs returns" still prints its own count of entries, all read as the head's.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED`, naming `tests/doc_claims.py`, which passes; `python3 tests/structure.py` passes.

- Suite: `bash tools/audit/seat/pr_args.sh --self-test` prints its own tally of checks, 0 failed; it is each slice's `SURVIVED NULL` above.
- `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` prints `ALL` its `ENTITY CHECKS PASSED` and exits 0 (run alone; beside the six mutant slices it had crashed on a killed `git tag` and timing arms, none naming this diff).

The finding has no committed finder's harness; the reviewer's race probe stays in the review's evidence, and the overlap arms above stand in for it inside the instrument's own self-test.

## Red checks

none

## Forward-carry

none

## Friction

none
