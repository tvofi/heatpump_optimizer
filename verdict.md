Design review: approve 9edf64948f7522213ca07a313f5121fe4c20a72a

Round 4, the re-cut after the third revise. Reviewed from a detached worktree at 9edf64948f (one file, design.md), judged against base 030a4d377f, the base the note names. Change since round 3: `git diff 9cebbb202d..9edf64948f`, design.md only. Parts A, B and C are byte-identical to 9cebbb202d except the new carries.

## Round-3 point

- P1 (architecture-unsound, D's second run fetcher): answered as the fix wanted it. D adds no file. The reader is `round_metrics.py produce`'s directory, and `fetch_runs` (`tools/audit/seat/round_metrics.py:391`, at 030a4d377f) keeps four more fields read with `.get`. The existing keys stay `id, t, c, attempt` (:395), so `gate_conclusions` (:151) and `runner_line` (:216, the attempt rule :227) read as before.
  - The fake paginator at `round_metrics_selftest.py:203` already carries `event` and `head_branch` and lacks `head_sha` and `pull_requests`, so the `.get` reading leaves the existing producer arms valid. The new producer arm, and a mutant on the `pr` extraction, are in the evidence row.
  - `/attempts/<n>` is dropped: `fetch_runs` lists jobs with `filter=all` and keeps `run_attempt` (:400-404).
  - `tools/policy/field_coverage.mjs` names no `round_metrics` file at the base (grep prints nothing), so no registration is owed.
- Hot files (step 5): `handoff/r11-pre-round-metrics-p3` at fae479abae contains the base. Its diff to `round_metrics.py` touches no `fetch_runs`, `ci_runs` or `run_attempt` line (`git diff 030a4d377f fae479abae -- tools/audit/seat/round_metrics.py | grep -E '^[-+].*(fetch_runs|ci_runs|run_attempt)'` prints nothing). Among the open `design/*` refs, only this note's design.md names `round_metrics`, `fetch_runs` or `ci_runs`. The serial order "part 3 first, then D" stands.
- The notes from round 3 are now carries in the note's own "Notes for the fixer": [c-deferred], [d-p2-head-text], and [name-collision] (dismissed with a reason). That is what the re-cut owed (design-review.md, "Three notes at most").

## Routed

- decision: orchestrator. D's `after` edges are R11-PRE-ROUND-METRICS parts 2 and 3 merged. C's is R11-PRE-TOKEN-LEDGER. The note gives these at design.md:15 and :19, together with the option to dispatch C and D as separate parts.

## Notes for the fixer

- design.md:50 says `runs.json` is unchanged as "the same dicts, filtered". But `main` at `round_metrics.py:396` filters the same dict objects, so each `runs.json` row would also gain the four fields. That breaks nothing: `scorecard.py`'s consumers (:114-177) index only `id, t, c`. Its docstring at `tools/audit/seat/scorecard.py:14` still states `[{id, t, c, attempt}]`. Build `runs.json` from the narrow keys, or update that docstring and `instruments/scorecard.py.md:35` in the same diff. Carry: R11-PRE-NO-READ-BUILDERS (item runs-json-width)
- design.md:69 ([d-hotfile]) gives the enumerator `git diff --name-only $(git merge-base origin/main <ref>) <ref>`. Every `design/*` ref is a root commit holding only design.md, so `git merge-base` prints nothing for those refs. The diff then lists every tracked file, including `round_metrics.py`, for all 15 design refs. For `design/*`, read `git show <ref>:design.md | grep -E 'round_metrics|fetch_runs|ci_runs'` instead. Keep the merge-base form for `handoff/*` refs only. Re-run the enumerator at D's merge base. Carry: R11-PRE-NO-READ-BUILDERS (item d-hotfile-enumerator)
- `pull_requests[]` is empty on a run from a fork or from a head that no longer matches. The `head_branch` fallback at design.md:52 covers this, but an internal branch name can be reused across PRs. Add one fixture where two `pull_request` runs share a `head_branch`, have a null `pr` and belong to different PRs. Pin that the earlier red does not read the later PR's commit as `#<pr>`, or name the limit in the body. Carry: R11-PRE-NO-READ-BUILDERS (item branch-reuse)

Seat token count: not reported by this harness.
