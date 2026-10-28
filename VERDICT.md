Fix review: blocked df1ee7b4326fc721546c332d6587be28733f2ceb mutation-vacuous: diagnostics._over_age's implausible exception (`problem.get("problem") != "implausible"` -> `True`) survives tests/debug_collect.py (ALL 153 PASSED); an implausible input re-based past its limit is then relabelled stale
bus-nonce: f0dc42b4ceb786c5a38248197b5d0fe8

# Fix review -- PR #2873, R10-DIAG-AGES, round 3

Reviewed head: `df1ee7b4326fc721546c332d6587be28733f2ceb` (GitHub's `headRefOid`
at the start and again before publishing): the authored code head `796146175`
plus merges of main. Merge base: `e8cb7e683`. Worktree: detached at the head
under `~/hpo-seats/r10s6/rev-prod-s8/2873/`. This is the third round, so it is a
repair rather than a re-cut (`fix-review.md`, last line).

## Harness (both ends)

#2814 has no committed harness. The one that found round 1's block is the
round-1 reviewer's own `harness.py`, carried in `review/2873` (`c8ad00e23`,
`evidence/harness.py`) and nowhere in the tree. I ran it unmodified (copy in
`ev/round1-reviewer-harness.py`) at the merge base and at the head:

- RESULT base: a payload exported 14 min late reads `input_ages_minutes
  {'indoor': 2.0, 'outdoor': 5.0}` and problem age 2.0. R8b (exported 40 min
  late) reads `input_health "ok"`, `stale_inputs []` beside a "20 min"
  message. `self_tests_at` is absent. `_plan_is_stale` raises TypeError on a
  `'15'` interval.
- RESULT head: 16.0/19.0 and 16.0. R8b reads `"1 stale"`, `["indoor"]`,
  "last report 60 min", `{"indoor": 60.0}`: one age, one verdict.
  `self_tests_at` is stated, `plan_stale` is re-judged True at 96 min, and the
  bool and str intervals read False. `checks: 27` at both ends. R2's
  publish-instant null is unchanged between base and head.
- The download's other age leaves were checked for the class:
  `weather_stale_hours` is computed live from the coordinator at export
  (`diagnostics.py:371`), so it is not a publish-time residue.
  `early_cutoff.*_minutes` is configuration. Within #2814's scope I find no
  further open seam.

## Mutation proof (reviewer's mutants, `ev/mutants/mutants.py`, driver tests/debug_collect.py)

- RESULT NULL (copy of the head): `ALL 153 DEBUG COLLECT CHECKS PASSED`. The
  seven `FAIL a16:*` lines printed are the suite's own planted-defect
  controls, present in every run.
- RESULT N2 (`_aged_problem` never promotes to stale): `1 of 153` FAILED,
  killed.
- RESULT N3 (`_aged_problem` does not re-base the age): `3 of 153` FAILED,
  killed.
- RESULT **N1** (`_over_age`'s `problem.get("problem") != "implausible"`
  replaced by `True`): **ALL 153 PASSED, survived.** The body names this arm:
  "promotes a class to `stale` ... unless the class is `implausible`, which the
  reader sets after the age gate". It is reachable: `InputReader.read` runs
  `_age_gate` before setting `implausible` (`inputs.py:961-966`), so an
  implausible entry carries both `age_minutes` and `max_age_minutes`.
  `ev/mutants/n1_demo.txt`: the problem `{'problem': 'implausible',
  'age_minutes': 10, 'max_age_minutes': 30}` exported 40 min late stays
  `implausible` at the head and becomes `stale` under N1. No check pins it.
  The mutation table cannot see this arm (dropping an `and` operand is no
  operator it draws), so a green `tests / mutation` is not evidence for it.
- The eight `killed_by` rows the body lists are CI's to judge, and `tests /
  mutation` is success at this head (job 122597667664).

## Other checks

- RESULT `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are
  untouched by the three-dot diff.
- RESULT live checks at this head (`ev/checks-at-df1ee7b4....txt`): `tests /
  fast (3.14)`, `tests / closures`, `tests / mutation` and `pr-contract` are
  success, everything else success or skipped. The body's `## Red checks`
  answers the earlier reds; the dispatch notes pr-contract's earlier red was
  staleness.
- The body's local gate figures (`MODE: SCOPED -- 27 script(s) run`, 5857 s,
  the four host reds) were measured at `796146175` on another seat. I did not
  re-run the gate (CI's heavy runs are cited instead).

## Findings

- mutation-vacuous, blocking: `diagnostics._over_age`'s implausible exception
  is a stated, reachable behaviour with no check. Add a failing-first check in
  `tests/debug_collect.py`: an implausible entry re-based past its own
  `max_age_minutes` stays `implausible`, stays out of `stale_inputs`, and
  `input_health` / `problem_messages` render it as implausible. Its null is the
  same entry inside its limit. Show N1 red. Carry: R10-DIAG-AGES
- harness not landed: the harness that measured this finding at both ends,
  and found round 1's class-open, lives only in `review/2873`'s evidence.
  `fixer.md` step 18 lands a rebuilt harness under `dev/audit/harnesses/`
  so the next seat can re-run it; name it there as the round-1 reviewer's.
  Carry: R10-DIAG-AGES

Evidence: `ev/` (files name the head `df1ee7b4326fc721546c332d6587be28733f2ceb`
or the base). The mutants and the N1 demonstration are the reviewer's own
instruments.
