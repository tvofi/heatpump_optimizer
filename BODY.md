Why this change, and what it measures: `Analyze (python)` is a required
context, and the `analyze` job's 30-minute cap sits inside the leg's observed
runtime spread — three cancellations at the cap on 2026-10-20 (30:19, 30:09,
30:07; the first during query evaluation, the other two during upload) and a
rerun of the same head that finished in 21:31. This raises the cap
to 45 and adds a check that refuses a lower value. It is headroom against
runner-load variance, not a claim that the leg now needs more than 30 minutes
every run.

## Head

7b64805231166191ff3f29e2ed3f618edf2cbf70

prepr was run at this head with `PREPR_SKIP_CLOSURES=1`: the closures
recording step passed green at `fccae47c4` in the preceding full run, and the
only changes since are comment text in `codeql.yml` and `tests/entities.py`
(blob-identical author files across the recarry to `55b74733`). The skip prints
`closures: PREPR_SKIP_CLOSURES is set -- closures-autofix is the only check left`.

## Approval

`.github/workflows/codeql.yml` is code-owned: `.github/CODEOWNERS`'s
`/.github/workflows/` rule names `@tvofi`, so this merge needs tvofi's
approving review. `policy_lint`'s `POLICY_GLOBS` does not match
`.github/workflows/`, so the diff owes no policy `## Approval`; the code-owner
review above is the one that binds.

## Mutation proof

The production line is `.github/workflows/codeql.yml`'s
`analyze.timeout-minutes`. The head `7b6480523` was checked out detached into a
scratch worktree and the value set to 30 there, never committed:

    sed -i '' 's/^    timeout-minutes: 45$/    timeout-minutes: 30/' .github/workflows/codeql.yml
    cd <scratch worktree> && PYTHONPATH=tests/hastub python tests/entities.py

Mutant: rc=1, `1 of 2360 ENTITY CHECKS FAILED`, the failing check being
`codeql.yml's analyze cap clears the python leg's measured worst case`
`[analyze timeout-minutes=30; the python leg was cancelled at 30:19 before the
cap rose (2bd5e90f, 2026-10-20)]`.

Restored at the same head (the value back to 45, no other difference): rc=0,
`ALL 2360 ENTITY CHECKS PASSED`.

The check reads the value it asserts (`_CODEQL_JOBS.get("analyze")` then
`.get("timeout-minutes")`) and prints the value it read in its failure detail,
so the mutation moves the predicate and not a tail.

## Null control

- The unmodified head `7b6480523` passes the same command: rc=0, `ALL 2360 ENTITY CHECKS PASSED`.
- Every other job's cap is unchanged at both ends:

      for r in origin/main HEAD; do git show $r:.github/workflows/codeql.yml | \
        python -c "import sys,yaml; d=yaml.safe_load(sys.stdin); print({k:v.get('timeout-minutes') for k,v in d['jobs'].items()})"; done

  prints `origin/main: {'cancel-superseded': 2, 'scope': 5, 'analyze': 30}` and
  `HEAD: {'cancel-superseded': 2, 'scope': 5, 'analyze': 45}`.
- The comparison is guarded by `isinstance(_analyze_cap, int)`, so a missing
  `analyze` job or key yields `None` and fails rather than reading as a pass.

## Figures

- Scoped gate: `python tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`
  → `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, `RUN tests/entities.py`
  and `RUN tests/harness_headers.py` (both read `codeql.yml`; both run).
- Structure ratchet: `python tests/structure.py` → `STRUCTURE RATCHET PASSED`, rc=0.
- Harness headers: `python tests/harness_headers.py` → `ALL 109 HARNESS HEADER CHECKS PASSED`, rc=0.
- Architecture score: `python tools/audit/archscore/score.py --diff origin/main`
  → `Architecture score: dS +0.0000 NULL`, rc=0.
- The four `Analyze (python)` intervals, from the Actions API (read-only):
  `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id> --jq '{name,conclusion,started_at,completed_at,run_id,head_sha}'`
  and `gh api "repos/tvofi/heatpump_optimizer/actions/runs/<run>/jobs?per_page=100"`:
  - `2bd5e90f` run 39436564344 job 118675172846: 14:09:00Z → 14:39:19Z, cancelled 30:19 (query evaluation started 14:27:57; cancelled 11 min in, then the cancelled handler uploaded the failed-run SARIF).
  - `4e5801eb` run 39437802530 attempt 1 job 118679535262: 14:17:24Z → 14:47:33Z, cancelled 30:09 while uploading results (upload began 14:46:11).
  - `916431ae` run 39434809989 attempt 2 job 118688693484: 14:34:41Z → 15:04:48Z, cancelled 30:07 while uploading results (upload began 15:02:38).
  - `4e5801eb` run 39437802530 attempt 2 job 118701134345: 14:58:02Z → 15:19:33Z, success, 21:31.
- Headroom in the code comment: `python -c "s=45*60-(30*60+19); print(f'{s//60}:{s%60:02d}')"` → `14:41`.
- Parsed caps at the head: `git show HEAD:.github/workflows/codeql.yml | python -c "import sys,yaml; d=yaml.safe_load(sys.stdin); print(d['jobs']['analyze']['timeout-minutes'])"` → `45`.

## Red checks

`Analyze (python)` (required context, ruleset `main-protect-checks` 23698884)
went red on three heads by cancellation at the cap. Answering the trigger:

- For the edit class (a later commit shrinking the cap), the cheaper detector
  is the pin added here: `tests/entities.py` is in `codeql.yml`'s recorded
  closure, so any change to the workflow selects it in the scoped gate, and it
  reads the YAML in seconds instead of after a 30-minute job. Standing cost:
  one YAML load inside an already-selected script.
- For the runtime-variance class, no cheaper detector exists: a runner's
  elapsed time is only known after the job runs, so the cheapest detector that
  would have surfaced it is the `Analyze (python)` run itself. Recorded, not
  built.

## Forward-carry

none

## Friction

- brief-timeout-frame: stale: the brief said the python leg needs 31–34 minutes; the rerun of the same head finished in 21:31 (job 118701134345), so the fix is headroom against variance, not a raised floor. Carry: dismissed: corrected from the orchestrator's measurement.
- codeql-extraction-quiet: unclear: the cancelled log's nine-minute quiet stretch after extraction (14:19–14:28 on `4e5801eb`) is not established as pathological — no file or extractor setting is named, and no local probe can time CodeQL's extractor; the same head succeeded in 21:31. Carry: dismissed: no measured pathology, the spread is runner load.
