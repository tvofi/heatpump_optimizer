Owner ruling (tvofi, 2026-11-01): a review-strength guardrail trip dispatches the planted-defect audit it names, and P0 = 0.28, ALPHA = 0.05 is adopted; the guardrail still sets no exit code and blocks nothing. Built as the beat job row `audit-dispatch` in `tools/audit/seat/beat_jobs.py` (job table `beatd.jobs.json`, interval 1800 s): it runs `review_strength.py --fetch --guardrail` and writes one `DISPATCH: planted-defect-audit arm=<arm> cut=<span>` line per sustained trip of an arm. Round 2 repairs the round-1 block: (1) the memory is keyed on the arm and the trip, not on the sliding cut, so a still-tripped arm dispatches once, and again only after it has read `ok` or `insufficient`; (2) a readable run rewrites the job file, so a failed run's `audit-dispatch: UNREADABLE` clears on the next good run, DISPATCH lines kept; plus the case for output whose only GUARDRAIL line is the unclassified one. `carry-201.json` records the ruling. Carries 13 (DISPATCH-REG), 48 and 50 (BEATD) are answered together by this one row. Alternative not taken: a standalone script; the row reuses the digest, fold and memory the other rows share.

## Head

71eca59832171f8940547f304a59289cd8f18404 (origin/main dc0a170b is an ancestor of this head, merged; prepr.sh run at this head, no second run owed).

## Mutation proof

Re-taken from scratch at this head: `python3 -I tools/audit/seat/beat_jobs.py --self-test` plants each `MUTANTS` entry in a temp copy of `beat_jobs.py` and requires its named case to turn red; it prints `beat_jobs self-test: 124 checks, 0 failed`, i.e. every row below red at the mutant and the same case green on the unmutated null control.

| mutant | change | case red at the mutant |
|---|---|---|
| audit_trip_any_arm | the trip regex also matches `ok` | a would-trip arm gives one DISPATCH line; ok and insufficient give none |
| audit_no_memory | drop the `arm not in tripped` test | null: a repeat of the same arm line dispatches nothing and writes no byte |
| audit_key_by_span | re-key memory by the sliding span | a second arm dispatches; the still-tripped arm at a slid cut gives none |
| audit_trip_never_clears | an arm reading ok never leaves memory | null: a trip that clears and trips again dispatches again |
| audit_no_clearing_write | write the job only when `new` | a good run after a failed one clears UNREADABLE |
| audit_unclassified_kept | drop the `" unclassified "` filter | output whose only GUARDRAIL line is the unclassified one is UNREADABLE |
| audit_rc_ignored | `rc != 0` not read | a failed run is UNREADABLE, never a dispatch |

Unpinned sites: the new code is in `tools/`, which `mutation-autofix` does not mutate; the in-tree `MUTANTS` harness above is its pin.

## Null control

Cases `audit-dispatch null: a trip that clears and trips again dispatches again`, `...: a still-failing run stays UNREADABLE`, `...: a repeat of the same arm line dispatches nothing and writes no byte` and `...: only ok and insufficient arm lines write no job, no digest, no memory`. Finder's harness at both ends (the reviewer's hourly sweep of the real `audit_dispatch`, 2026-11-01T00:00Z to 2026-11-06T09:00Z, 60-day window, local bus, no `--fetch`, 130 cuts): at the baseline `f6a299d3` it emits 38 distinct DISPATCH lines; at this head 3, which are three distinct trip episodes (model:sonnet read `ok` at the 2026-11-01T04:00Z to 08:00Z cuts, so its second dispatch follows a clear, and `all` tripped once). Perturbation: that clear-and-retrip is the null control of the keying, not a slide. `stale_probe.py` (trip, fail, recover-same-cut, recover-ok, ok-again): at the baseline the digest reads `audit-dispatch: UNREADABLE review_strength boom` after all of the last three; at this head the UNREADABLE line is gone after recover-same-cut and the DISPATCH line is kept.

## Figures

- `python3 -I tools/audit/seat/beat_jobs.py --self-test`: 124 checks, 0 failed (107 at the merge base).
- `python3 -I tools/audit/seat/review_strength.py --self-test`: 116 checks, 0 failed.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2632 ENTITY CHECKS PASSED.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: `MODE: SCOPED -- 1 script(s) run`, `tests/entities.py`.
- The sweep counts above: `python3 -I $EXPORT/sweep_row.py <seat dir> <repo> <cache dir>` (sha1 56bc3f1f688a; drives the row's real `audit_dispatch` once per hourly cut over cached `review_strength.py --guardrail` outputs, the reviewer's sweep adapted to count the row's DISPATCH lines), run with the `beat_jobs.py` of `f6a299d3` and of this head; the reviewer's own count was 37 keys over its cuts, mine is 38 lines over mine because my local bus snapshot differs.

## Red checks

none

## Forward-carry

none

## Friction

none
