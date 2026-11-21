HOTFIX r11-hotfix-envmatrix-timeout. Since 8fa10e00ce (#3723, merged 2026-11-19T03:20:07Z), `governance / env-matrix` runs past its 10-minute `timeout-minutes` on a large share of runs. GitHub cancels it in "Require each declared environment shape to produce its declared outcome" with no red row: on main, 11 of the 29 push runs since that merge timed out, and 0 of the 270 before it did. On pull requests the same timeout hit #3806 (jobs 136839689039 and 136855442927), #3814, #3824, #3805, #3829 and #3818. A train skips a verdicted PR when this required job is cancelled (P-R11-94).

Cause. The cause is data growth in what the matrix greps, not runner slowness and not a code change. The matrix runs `policy_lint.mjs` in four clones, `policy_lint_mutants.mjs` in three, and the `--record`/`--stats` arms. One local `policy_lint.mjs` run at main spends 89 s of its 111 s in child processes, in 175 `git grep -I -l -w -F <symbol> -- .` calls. These come from `symbolElsewhere` in `tools/policy/policy_lint.mjs`, which greps the whole tree once per cited symbol. Each call costs the tree's tracked bytes. #3723 landed the round-11 audit register under `dev/audit/rounds/round11/` (one file, `D12/s1/out/dump/states.json`, is 35 MB). Tracked bytes went from 140 MB at 54cb721164 to 265 MB at 8fa10e00ce, and are 279 MB at the base. Four first-parent merges since 2026-11-12 touched the matrix's programs: `git log --first-parent --since=2026-11-12 origin/main -- tools/policy/policy_lint.mjs tools/policy/policy_lint_mutants.mjs tools/policy/policy_lint_envmatrix.mjs tools/policy/counts.mjs` lists #3514, #3631, #3668 and #3688. Across the windows between them, the job's success p50 crept from 371 s to 404 s, with no timeout. The step change comes at #3723, which touched no program: 11 of 29 jobs timed out, and the p50 of those that finished is 466 s. That p50 understates the shift, because the slowest jobs were cancelled before they could finish (`windows.py` under Figures). The same check in `policy-docs` grew from a mean of 18.8 s to 27.8 s over the same split, a factor of 1.48. The 10-minute cap had little headroom even before: it was 1.17 times the pre-landing p95 of 513 s.

Fix. `timeout-minutes` goes from 10 to 26. The value comes from this rule: ceil(2 × pre-landing p95 × measured lint-step growth / 60) = ceil(2 × 513 × 1.48 / 60) = 26. A comment above the key states the rule. This PR does not batch or rescope the per-symbol grep. That change belongs in `policy_lint.mjs`, which is pinned from the base and code-owned, and it is a tooling change for the round-end instrument triage (P-R11-94). The cap is what stops the cancellations now.

Interaction: `gate` (ci.yml) re-reads this run's own pending jobs for up to `GATE_WAIT_MAX_S` = 720 s, and `gate-sweep.yml` re-judges at the run's completion. So a matrix that runs longer than the gate's wait is judged at completion rather than failing. That is how a slow job is handled today.

## Head

1ec3ebde083a884035392b11bd095eb14a54030d, one commit on merge base 78d3b4022154b2cc2792df8ebf4a5d7753e8ed7f (origin/main was 42809bec34 at 2026-11-21T13:51Z). The diff is `.github/workflows/governance.yml` only: +6/-1.

- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` and names `tests/entities.py` and `tests/harness_headers.py`, run at the head with `PYTHONPATH=tests/hastub` on this macOS host.
- `tests/entities.py`: `1 of 2735 ENTITY CHECKS FAILED`. The one red is "a measured script's late-writing descendant is waited for, not recorded as nodata". It drives `tools/coverage/coverage_tree.sh` under a stub and reads no workflow file. Run alone from the file's own `_coverage_revalidation` (`late_check.py`, sha1 146d7df9d1090c0f71f17592d61a8c0b9af0a8d6), it fails identically at the merge base 78d3b40221, a detached worktree, with every script reading `nodata`. So it is inherited and specific to this host, not this diff, and CI's Linux run is the authority on it.
- `tests/harness_headers.py`: rc 0, `ALL 115 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- No new tracked file, so no closure or INERT classification is owed.

## Mutation proof

The fix is one value, so its mutant is the base value. With `timeout-minutes: 10` restored, the job is the one cancelled on 11 of 29 main push runs since 8fa10e00ce, every one at 609 to 618 s in the matrix step: for example job 135314988141 (2026-11-19T03:23Z, 610 s), 135369698753 (616 s) and 135389239234 (618 s). With 26 minutes, all 29 measured after-landing durations fit: they are censored at 600 s, and the projected p95 is 760 s. This pull request's own `env-matrix` run is the first uncensored measurement at the new cap. A reviewer reads its duration from `gh api repos/tvofi/heatpump_optimizer/actions/runs/<run>/jobs`, and it should land well under 1560 s.

## Null control

Before the landing, the same job at the same 10-minute cap passed on all 262 main push runs that completed, with none timed out: p50 386 s, max 535 s. For example job 130932618696 (2026-11-12T02:38Z, 285 s) and 130931061266 (365 s). Main's tree then was 133 to 140 MB.

## Figures

The generated scope-line block is left out of this body: update_pr.sh verifies it against its own merge head, which no body can name in advance (R10-HOTFIX-UPDATEPR-FIGURE-REFRESH); the scope line is the gate's own MODE line at the head.

Harnesses are out of the tree, cited by sha1 (fixer.md step 3). They live in the seat's directory `hpo-seats/r11/hotfix-envmatrix/` and are reproduced in the seat report.

- `collect.sh` (sha1 db610435ef11c622e99d73756ba0d82e7b989788) reads, through `GET actions/workflows/ci.yml/runs?event=push&branch=main` (300 runs) and `GET actions/runs/<id>/jobs`, the job and matrix-step duration of every `governance / env-matrix` job: 299 jobs, 2026-11-12T02:27Z to 2026-11-21.
- `collect_lint.sh` (sha1 691c19cc168be911a4f1211e88964b3bc6133f2e) reads the `policy-docs` "Lint the policy corpus" step on every third of those runs: 99 successful steps.
- `derive_cap.py` (sha1 91d168005499beca593d2478dfcc30115fca7b15) splits both at 2026-11-19T03:20:07Z, the merge of 8fa10e00ce, and prints:
  - `main push env-matrix before landing: 262 success, 0 timed out; p50=386s p95=513s max=535s`
  - `main push env-matrix after landing: 29 jobs, 11 timed out at the 600 s cap`
  - `policy-docs lint step mean: before 18.8s (n=89), after 27.8s (n=10), growth x1.48`
  - `projected p95 after = 513 x 1.48 = 760s; cap = ceil(2 x 760 / 60) = 26 min`
  - Cross-check, a censoring-aware bound from the job's own record: `0.38 of after-landing jobs exceed 600 s; the before quantile at 0.62 is 425s, so growth >= x1.41`. Its growth factor agrees with the lint step's.
- `windows.py` (sha1 8aa9330e48e2661385d3d005e2c9089fae0a990e) gives main push env-matrix by window, starting at each merge that touched a matrix program:

  | window from | jobs | timed out | success p50 |
  |---|---|---|---|
  | 2026-11-12 | 123 | 0 | 371 s |
  | #3514 | 48 | 0 | 386 s |
  | #3631 | 41 | 0 | 381 s |
  | #3668 | 40 | 0 | 393 s |
  | #3688 | 18 | 0 | 404 s |
  | #3723 (register) | 29 | 11 | 466 s |
- Pull-request runs: `collect_pr.sh` (sha1 7dd1920b9ad86f67921dff1691ba8523f13adb7a) makes the same reads over every attempt of `event=pull_request` runs. It was stopped after 106 runs, whose jobs started from 2026-11-19T01:17Z to 2026-11-21T13:21Z. `analyse.py` (sha1 48e6399d1f9eb998ff207ca4e11aba9176e91a04) splits them at the landing. After it: 144 env-matrix jobs, 43 timed out at 600 s, 96 succeeded with p50 427 s (the successes include product-only runs, which stand down in about 2 s). Before it: 5 jobs, none timed out.
- Where the matrix's time goes: `prof/spy.cjs` (sha1 8c819acb166f26b0d0f3a11fa2e546f6bd9cea48), preloaded into `node tools/policy/policy_lint.mjs` in a fresh clone at 42809bec34 on this macOS host, logs every synchronous child. The run took 111 s, of which children took 109 s: `git grep -I` 175 calls 89.2 s, `git rev-parse --verify` 129 calls 5.6 s, nested `policy_lint.mjs --record` 4 calls 4.8 s, the rest under 2 s each. Unsampled on the same host, `policy_lint_mutants.mjs` took 621 s and `policy_lint.mjs` 171 s, which puts the mutants arm at about 3.6 lint runs.
- Tree growth: `git ls-tree -r -l <c> | awk '{s+=$4} END{print s}'` gives 133197618 at 6e100ef698 (2026-11-12), 140675332 at 8f39313a44 (2026-11-17), 265 MB at 8fa10e00ce and 279136158 at 42809bec34. Of the growth since 8f39313a44, 136754897 bytes are under `dev/audit/rounds/round11`.

## Red checks

none. The defect reached main through #3723. Under `defect-root-cause.md`, the process state is **no detector existed for the class**: a job's `timeout-minutes` is never compared with its measured durations, and an evidence landing that doubles the grepped tree is not priced against the jobs that scan it. Countermeasure: proposal P-R11-94, for the round-end instrument triage under the tooling freeze. It has two parts. (a) The train's infra-rerun arm treats a job-level timeout with no red step, where the base's same job passed in under half the cap, as one re-run before SKIP. (b) `symbolElsewhere` batches its greps into one `git grep -f` pass, or excludes `dev/audit/rounds/` evidence, so the matrix no longer scales with evidence bytes. A third item goes to the same proposal: re-derive this cap from uncensored durations, by the rule in its comment, once 20 or more post-fix main runs exist.

## Forward-carry

none

## Friction

none
