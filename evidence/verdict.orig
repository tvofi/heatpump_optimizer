Fix review: merge 45bb861b75728e7924944741b41a68c8fb5e9f5c

bus-nonce: f45ab9746cdf02dbff07b69e4742adb6

Round 1. Reviewer seat for #2433 (R10-TICK-SELFTEST-CI). I measured head 45bb861b75728e7924944741b41a68c8fb5e9f5c from a detached worktree. The diff is 12 lines in `.github/workflows/governance.yml` and the PR's own delivery row. Roles at main: `git diff merge-base...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.

## Mutation proof, using the step's own text

I took the `run:` text from the head's governance.yml with `yaml.safe_load` (ev/step.sh) and ran it under `bash -e` with RUNNER_TEMP set (ev/RESULTS3, logs ev/*.log):

    RESULT clean rc=0 last=orchestrator_tick self-test: 150 checks, 0 failed
    RESULT M1 rc=1 last=AttributeError: module 'roster_lib_tick' has no attribute 'DEFAULT_ROSTER_REF'   (#2406 shape)
    RESULT M2 rc=1 last=AttributeError: ... no attribute 'default_roster_ref'
    RESULT M3 rc=1 last=orchestrator_tick self-test: 150 checks, 1 failed   (python exits 0; the grep alone refuses)
    RESULT M4_zero_checks_exit0 rc=1 last=orchestrator_tick self-test: 0 checks, 0 failed   (mine: [1-9] refuses an empty tally)
    RESULT clean2 rc=0 last=orchestrator_tick self-test: 150 checks, 0 failed
    RESULT M2_archive rc=1 (M2 again in a pristine git-archive copy)

All mutants are killed and the clean runs pass. After each restore, `git status` was clean.

The body's pitfall note is half wrong: `PYTHONDONTWRITEBYTECODE=1` has no effect under `python3 -I`, because -I ignores PYTHON* environment variables. My first pass (ev/RESULTS) and second pass (ev/RESULTS2) both read a stale roster_lib .pyc and showed a false survivor or a false red. Pass 3 gives each run a unique absolute mtime, and M2 was confirmed again in a fresh archive copy. CI checks out fresh, so the step is not affected. Only the reproduction advice is wrong ("remove __pycache__" holds; the env var does not).

## CI on this head (check-runs API)

Job `instrument-self-tests` (id 117916936202) ran at head_sha 45bb861b and concluded success. Step 25, "Show the orchestrator tick deciding its own fixtures", succeeded. Its log line reads `orchestrator_tick self-test: 150 checks, 0 failed`, so the self-test ran with a nonzero count (ev/instrument-self-tests.log:3257). Across 45 check runs, none is red. At verdict time `closures` and `Analyze (python)` were still in_progress (ev/check-runs-final.tsv). "Red checks: none" holds so far.

## Figures

- Tick self-test: the body says 104. That holds at the authored code head c13ed69e, where I measured 104 checks, 0 failed, rc=0. At 45bb861b it reads 150, because fb6ee66 merged main, and main carries #2422 (7ab3030bb). That is exactly the count the body's #2422 paragraph predicts.
- Gate scope: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` ✓
- entities 2349 ✓, harness_headers 109 ✓, layout ok ✓, closure selftest 124 ✓, structure PASSED ✓, policy_lint --budgets rc=0 ✓, codeowners_gap uncovered_files=0 ✓, tmp_paths 0 refused ✓, ref_privacy 0 refused ✓.
- claims hygiene ok: at 45bb861b the merge base is abb397938, not 913ce1ff5.
- Seam rule, re-run by me (same rule):
  - 913ce1ff5: wired=8 unwired=24 (32) ✓
  - code head c13ed69e: wired=10 unwired=22 ✓
  - 45bb861b: wired=10 unwired=25

  The 3 extra unwired at this head came in from main with #2422: pr_args.sh, pr_cap.py, tick_loop.sh. The body names pr_cap.py and tick_loop.sh as the class's open seam. pr_args.sh is a third newcomer the body does not name. The class stays returned to the orchestrator, so this is not blocking, but the dispatched group should be **26 files at main, not 23**.
- The spy figures (0 subprocess calls, 0 connects) come from the fixer's own scratch probe. I did not re-derive them. The step's own clean run does no network work, and the stubbed runners are visible in the self-test.

## Other checks

- `git merge-tree --write-tree origin/main 45bb861b`: exit 0, tree 9e5a3a1e (ev/merge-tree.txt).
- VERSION, the manifest and RELEASE_NOTES are untouched in the three-dot diff. The diff claims no golden fixture, so there is no drift to compare.
- No budget or metric moves.
- Head is unchanged at post time: 45bb861b.
