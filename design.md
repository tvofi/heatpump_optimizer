# R10-HOTFIX-CODEQL-HEADROOM — design note

Base: `origin/main` at 17e1157925908bd69addb58ed824c1ac22bfa82f (no predecessor; roster `after: []`).
Roster read: `handoff/audit-r10-roster` at 387418af42eecc704ae9306b27bfec4a1fa7975c.
Verdict: **do not refuse.** Main does not fit the 45-minute cap, and the job is growing.
Design: a timeout scoped to the python leg, as a **stopgap of about two weeks**. The structural cure needs an owner ruling (section 5).

## 1. Measurement (check-runs/jobs API, every page)

Instrument: `gh api repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?branch=main&event=push&per_page=100&page=N&created=>=2026-10-25`, pages 1–5. The API's `total_count` was 475, and 475 runs were read. Per run, `.../actions/runs/<id>/jobs?filter=all` gives the `codeql / Analyze (*)` jobs. Duration is `completed_at - started_at`. A job cancelled at 44.9 min or more counts as capped; none was dropped. The cap has been 45 for the whole window (`fccae47c4`, 2026-10-20).

| leg | jobs | p50 | p90 | p99 | max | at/over 45 min |
|---|---|---|---|---|---|---|
| python | 480 (467 success, 12 capped, 2 superseded at 37.0/38.2) | 33.8 | 42.5 | 45.1 | 45.2 | **12** |
| javascript-typescript (null) | 480 | 1.6 | 1.8 | 2.3 | 4.0 | 0 |
| actions (null) | 480 | 0.9 | 1.0 | 1.4 | 2.7 | 0 |

The null legs share each run's runners and read about 40× under the cap, so the python figure is not a runner artefact.

The capped figures are censored at 45, so the python p99 is a floor. All 12 caps fall on 2026-11-04 or later. The last 21 python jobs (2026-11-07) read p50 42.7, p90 45.1, 4 capped. The base's own python job (17e11579) was cancelled at 45.1 min.

**The job is growing; it is not only runner noise.** Python p50 by start day:

| day | 10-25 | 10-27 | 10-29 | 10-31 | 11-02 | 11-04 | 11-06 | 11-07 |
|---|---|---|---|---|---|---|---|---|
| p50 (min) | 30.4 | 32.1 | 35.1 | 34.2 | 39.2 | 38.9 | 42.1 | 42.2 |
| capped | 0 | 0 | 0 | 0 | 0 | 3 | 3 | 6 |

Every 12th python job's log was read, plus every capped job's (n=50): `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`, grep `Extracted file .* in Nms`, `Processed N modules in`, `[k/52 eval`.
- **Where the time goes.** Extraction takes 561–1714 s and query evaluation 9m09s–20m26s. Both sit inside "Perform CodeQL Analysis" (2144–2674 s of the job; init takes about 20 s).
- **The extraction critical path is `tests/features.py` alone.** It takes 536–1645 s, against a phase total of 562–1714 s. On the other three threads, all 1976 other modules finish within the first ~90 s, `tests/entities.py` aside (291–872 s). Every other file takes under 9 s. `tools/audit/seat/merge_train.py` (8k lines) is the next-slowest at 15 s.
- **Two causes.** Runner speed is bimodal, read from `tests/closure.py` + `tests/structure.py` extraction (about 2.2 s vs 3.6 s), and accounts for the 2× swing that measurement 2 (recut body 3838ebda) found. Code growth is real on top of it.
  - A regression over the 50 logs gives log(features.py extract) = 0.94·log(runner) + 3.78·log(features.py lines), R² 0.913. A runner-only model reads R² 0.552.
  - Query evaluation fits 3.84·log(features.py lines), R² 0.952.
  - `features.py` grew 68,601 → 78,778 lines over the window, about 780 lines/day, and six live roster groups list it in `files`. Measurement 2's "no growth in the files" is refuted.
  - Collinearity caveat: total python lines grew too (`git ls-tree` at v7.1.0 → v7.1.5: 491k → 532k lines). The regression shows growth drives the job. It does not prove `features.py` is the only driver of evaluation time.
- **Uncensored worst case (estimate).** The slowest capped job (355d9965) was at query 7/52 when cancelled, after 1714 s of extraction. Adding a slow-runner evaluation (≤ 20m26s) plus ~2 min of setup, finalize and upload gives **≈ 51 min**. This is a projection, not a measurement.
- **Growth rate.** Slow-runner jobs went from 30–33 min (10-25) to 43–51 min (11-07), about 2.9 %/day compounded.

## 2. Owning seam

`.github/workflows/codeql.yml`, job `analyze`, owns the cap. `.github/workflows/ci.yml` (the `codeql:` job) only calls it. The cap's one reader is the pin in `tests/entities.py` ("codeql.yml's analyze cap clears the python leg's measured worst case", `_analyze_cap`). No second owner.

## 3. Shape (for the fixer)

Per-leg cap in the matrix, so the job stays one matrix with one job per leg and the step list is not copied three times:

```yaml
    timeout-minutes: ${{ matrix.timeout }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - { language: actions, timeout: 45 }
          - { language: javascript-typescript, timeout: 45 }
          - { language: python, timeout: 75 }
```

The `matrix` context is admitted in `jobs.<id>.timeout-minutes`.
- The three `Analyze (<language>)` context names are unchanged, and so are the categories and the steps.
- **75** = the ≈ 51-min projected worst case + 24 min of margin. At the measured ≈ 2.9 %/day, 24 min is about 13 days of growth (51·1.029^13 ≈ 74).
- The margin is a deliberate stopgap length, not headroom. The cap does not shorten any wait: the merge train still waits the job's full duration (44 min for #3269).
- **Rewrite the header comment's cap paragraph** with section 1's figures and this enumerator, replacing the 2026-10-20 history.

Invariants:
- The actions and javascript-typescript legs read 45 before and after (the null control below).
- The required contexts, categories, the stand-in path and the D-5 step are untouched.

## 4. Alternatives, and why each lost

- **Raise the job-level `timeout-minutes` to 75 for all legs.** It moves two legs whose p99 is ≤ 2.3 min for no reason, and the brief scopes the cap to python.
- **Split `analyze` into three jobs.** It triples the 10-step list and its four pins in `tests/entities.py` read `_CODEQL_JOBS["analyze"]` steps. A matrix entry is already its own job.
- **Refuse on measurement.** Refuted: 12/480 capped, 6 of them on the last day.
- **Timeout alone as the cure.** Lost: at the measured growth rate, any finite cap is reached in days to weeks (section 5).

## 5. The structural cure — owner ruling owed; not this group

The growth is the single-threaded extraction of `tests/features.py` plus an evaluation that grows with it. The candidates, each blocked by a ruling or a budget:
- **(S1) Split `tests/features.py` into scripts of at most ~12k lines.** Per-line extraction is about 0.4–1.1 ms for files ≤ 11.5k lines (`coordinator.py` 4.5 s, `tests/stress.py` 4.0 s), against 14–21 ms for the 42k and 79k files. Separate files also extract in parallel on the extractor's 4 threads.
  - Cost: `tests/ci_budgets.json` `script_runs_per_push` / `script_runs_full_case_pr` rise, which is a budget raise (#3266's alternatives).
  - It is the only candidate that also improves D7 maintainability.
  - Prerequisite: a spike measured by a `ci.yml` dispatch with **inputs empty** (carries 93aad749, e017bcd8). #3266 showed that a predicted extraction gain can reverse.
- **(S2) Give the two giant scripts their own python category.** Their leg still carries `features.py`'s extraction, so the critical path barely moves. It also adds a required context (a settings change), stand-in and D-5 work, and loses flows across the split.
- **(S3) `paths-ignore` the two scripts.** Forbidden by the owner's ruling (#3266 body).
- **(S4) A larger runner.** Billing and settings, the owner's call.

Recommendation to the orchestrator: put S1 to the owner as a new group before this stopgap's margin is spent.

**Reopen trigger for this group:** any python job capped at 75, or a 7-day python p90 over 65 min.

## 6. Sibling sites

`git grep -n "timeout-minutes" .github/workflows/codeql.yml` returns one site. `git grep -n "_analyze_cap" tests/entities.py` returns the one pin.

`tools/pr/codeql_scope.py` and `tools/ci/prelude.py` name `codeql.yml` only as a changed file: a diff touching it analyzes every leg. That is in scope by design, and it gives the fixer a real python analysis on the PR, under the head's 75 cap.

## 7. Evidence plan

- **Failing test first.** `tests/entities.py`'s pin today reads the job-level `timeout-minutes` and requires an int ≥ 45. Against the new shape it reads the string `${{ matrix.timeout }}` and fails. Rewrite it to read the `include` entries:
  - python is an int ≥ the measured worst case (51);
  - each other leg is exactly 45 (null control, pinned);
  - `timeout-minutes` is exactly `${{ matrix.timeout }}`.

  The check count stays the same. Its message cites section 1's figures. The brief's "do not edit tests/entities.py" binds that file's structure, while its "every check must still pass" forces this pin's edit; the fixer records both in the body.
- **Mutation proof** on the rewritten check:
  - python 75 → 50 fails;
  - actions 45 → 75 fails;
  - dropping the `include` timeout fails;
  - a comment-only edit passes.
- **Finder's harness at both ends:** section 1's enumerator, re-run at the merge base (re-derive; do not carry these figures).
- **At the head:** the PR's own `codeql / Analyze (python)` job, since the diff touches `codeql.yml`. Report its duration, its conclusion and its log's `features.py` extraction line against the base's, with `tests/closure.py`'s extraction as the runner-speed null control.
- No goldens and no claim files move. `tests/structure.py` budgets are untouched. No new file, so no `tests/closure.py` classification: both files are already measured, and `tests/closures.json` lists `tests/entities.py` and `tests/harness_headers.py` as readers of `codeql.yml`.

## 8. Hot files and serial position

- `.github/workflows/codeql.yml`: no other live group lists it.
- `tests/entities.py` is a hot file: R10-SUITE-HOST-DETERMINISM, R10-FLY-STAMP-FLUSH-COST and R10-I18N-DE list it. The edit is one check block (~15 lines), so no `after` edge; merge main before the handoff.
- Serial position: wave 1, CP lane, no predecessors. Ship it ahead of any group that lengthens `tests/features.py`, because every main push until then risks a cap.

## Notes for the fixer

- Dispatch `ci.yml` with inputs empty for any extra CodeQL figure; `pr=<N>` from your ref is refused by the prelude. Carry: R10-HOTFIX-CODEQL-HEADROOM (item 93aad749)
- The brief's dispatch inputs contradiction is resolved by the form above. Carry: R10-HOTFIX-CODEQL-HEADROOM (item e017bcd8)
- Leave `tests/features.py` and the wrapping alone: the per-statement wrap slowed extraction and evaluation (#3266 jobs 128428511054, 128440898484). Carry: R10-HOTFIX-CODEQL-HEADROOM (item 6e003ed3)
- Brief premise corrected by section 1: measurement 2's "no growth in the files" does not hold over 475 runs. Carry: dismissed: superseded by section one measurement (item recut-3838ebda)
