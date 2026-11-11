Plan-page group r10-plan-page-residue, repair round 2: the hotfix mark is pinned where it is drawn, the REST read that fed `tools/plan/durations.json` lands as tracked code and the file is re-measured through it, and every survivor of `mutant_run.py --diff` is killed or answered below. Closes no issue.

## Head

329479fbd12c795669d19c2a54c287767e2344ba

## Mutation proof

- The round-2 verdict's four survivors are named mutants in `dev/audit/harnesses/r10_plan_page_mutants.py`, plus `hot-crit` (the critical-path restriction of `gating_crit`). Command: `python3 dev/audit/harnesses/r10_plan_page_mutants.py M0 hot-render hot-gates hot-notdone hot-crit`. Result: `M0 rc=0 fails=0 verdict=null`; `hot-render`, `hot-gates`, `hot-notdone` and `hot-crit` each `rc=1 fails=1 verdict=killed`; `survived=0`.
- The pins: one check reads the rendered page. It requires the `class="cp hotcp"` mark on exactly one name cell, R9-PART's (`marked()` in `plan_page.py --self-test`). A second check requires no marked row in five null fixtures: a non-hotfix on the edge, a hotfix that only an off-path group waits on, a released (`refuted`) predecessor, a closed (`deferred`) predecessor and a discharged predecessor. `hot-gates` dies on the `refuted` arm, because `refuted` is open but releasing. `hot-notdone` is not equivalent: it dies on the `deferred` arm, because `deferred` is closed but still gating (`roster_lib.CLOSED_STAGES` against `RELEASING_STAGES`).
- `hot-discharged` is answered by deletion. A discharged group is in `done` (`done = {...} | discharged` in `build_rows`), and the row's `hot` already excludes `done`. So `a not in discharged` in `gating_crit` could not change any output, and it is gone. The discharged null arm still pins the exclusion through `done`.
- Diff-mode driver, all three files at this head: `python3 tools/audit/seat/mutant_run.py --diff 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444...HEAD --path <file> --cmd 'python3 <file> --self-test' --report-only`. It ran once with `plan_page.py` (and `roster_lib.py`), once with `size_durations.py` and once with `replan.py`. Every survivor is in `## Unpinned sites`.
- Production survivors from the first diff run at 9774026d05, now answered:
  - `_plain_key`'s scalar branch: deleted. `replan` writes `sort_key` as a list (`plain(priority(n))`), and the caller reads `[0]` of it.
  - `_other_issues_sentence`'s zero branch: pinned (`== "no other open issue is on no open group."`). This corrects round 1's equivalence claim for `zero-other`. The general path renders "0 other open issues are …", a different sentence; no arm had read it.
  - `n_sched`: pinned. The lede must name the open, unscheduled count, and the fixture has at least one such group.
  - The in-review cap's `live_remaining_fraction` default: pinned (`live stage (cap)`).
  - The disjunctive tail of the part-merged null control: deleted. That `or` branch was never evaluated.

## Null control

- Hotfix mark: the five null fixtures above render no mark. The off-path arm asserts its own preconditions (R9-PART is a hotfix, and the off-path group's `after` names it). If either were lost, the arm reports "fixture lost its edge" instead of passing.
- REST read: `flatten(rest_node(...))` of a REST pull, its commits and its comments equals `flatten()` of the GraphQL node with the same data. With no commit read, both fall back to the creation time. `fetch_rest` is driven by an injected `get`. It returns the merged PRs only, across a full page. It stops at the first PR created before `since`, reads a PR created at the cut-off instant, stops on a short page without reading page 3, and never reads the page-3 sentinel. `_gh` returns stdout, and raises on a non-zero exit (`_gh (null)`). `read_prs`: a fresh read writes the cache, and a second call replays it without a read (one recorded read).
- `input_note` names `size_durations.fetch_rest (--via rest)` or `size_durations.fetch (--via graphql)`, and adds ", replayed from a --prs-cache file." only when the cache was read.

## Figures

- `python3 tools/plan/replan.py --self-test`: `model self-test: 0 failed`, `self-test: 0 failed`. `python3 tools/audit/seat/plan_page.py --self-test`: `93 checks, 0 failed`. `python3 tools/plan/size_durations.py --self-test`: `size_durations self-test: 0 failed`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Scope (`tests/closure.py select --diff 63bcdcaad8`): `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `scope.run` names `tests/entities.py`, and `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2707 ENTITY CHECKS PASSED`.
- Durations (Carry 0 item 3), reproducible from the tree:
  - Command: `python3 tools/plan/replan.py --measure-sizes --sizes-via rest --roster-ref origin/handoff/audit-r10-roster --out-durations tools/plan/durations.json`, with roster ref 943eb224e89b404300cc3d26cda14bcd5c42e9b3, merge base 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444 and `sizes_measured_at` 2026-11-11T04:56:48Z.
  - Result: `sizes_hours` S 21.6, M 32.4, L 35.6, XL 35.6; `round_hours` 5.65.
  - `sizes_provenance` now ends: "Input: 1021 merged PRs created since 2026-10-12, read by size_durations.fetch_rest (--via rest)."
  - The round-1 scratch cache (1044 PRs) is replaced. This read is the tracked `fetch_rest`, and its drop of PRs created before `since` is stated in its docstring.
  - Not verified: whether the GraphQL read gives the same PR set. No seat here can run both reads.
- Main tip at this measurement: origin/main dbd1ab5b0712ebc51e29ef8c001a2c0ef68af3cd, `date -u` 2026-11-11T06:05:35Z. `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict).
- Class enumeration (step 8): no issue is closed, and this is an instrument group. The class is "a drawn element with no reader". Its enumeration rule is the diff-mode driver above over every added line, and its survivors are dispositioned below.

## Unpinned sites

Every survivor of the three diff-mode runs at this head is listed here. Each one is a self-test line or the unreachable default named last.
- `plan_page.py`, 3 survivors, all equivalent:
  - The `[:3]` slice in two failure-detail arguments. The detail prints only on failure.
  - The `"f" * 40` length of a fixture merge SHA. It matches no roster commit at either length.
- `size_durations.py`, 6 survivors, all equivalent:
  - The fixture comment indices `(1, 2)`. Both sides of the comparison are built from the same nodes.
  - The `pages[3]` sentinel key. The page is read only under a production mutant, which the short-page arm kills.
  - Three single-line `check(...)` calls deleted. A deleted test arm cannot fail.
  - `gh_raised = False` flipped. That line is unreachable while `_gh` raises.
- `replan.py`, 10 survivors:
  - 9 are test-side equivalents. Six loosen a strict self-test bound (`<`/`>` to `<=`/`>=`), and correct code satisfies the strict bound. Two change a failure-detail argument. One (`rv("in-review", 99.0, unset) == ... < 98.0` to `<=`) loosens a bound the same way.
  - 1 is in production: `check_plan`'s `default=0` in the closure fallback. It is equivalent. The fallback runs only for a plan without a round-close stamp, and `check_plan` already refuses such a plan ("round close: 0 round-close stamps"). I measured this with an arm that removed the stamp and was refused there, then removed the arm.
- The mutation lane mutates `custom_components/` only, and this diff touches no file there. The pins above are in-tree self-tests and the tracked harness.

## Red checks

none owed.

## Roster carries (the group's six, origin/handoff/audit-r10-roster, field `carry`)

Carry 0 (closure rule, 20 slots, durations): all three items built here. (1) `summary.closure_conditions` carries the six conditions, `check_plan` refuses a plan without them, and the page states them in the lede. (2) 20 slots, provenance comment 6707334933, was built earlier in this PR. (3) Durations re-measured through the tracked REST read, above.
Carry 1 (outside priority, live stage, counts, None, headings): item 2 (live stage) built, its cap default now pinned. Items 3, 4 and 5 were built earlier. Item 1 (outside tiering): `dispatch_tier` reads `roster_lib.is_outside` and critical-path membership, and existing arms pin it. I could not re-derive whether COMBI-TANK and OUTSIDE-INTAKE have `source` unset, so there is no code change. Carry: dismissed: not reproduced at this head, the code reads the flag.
Carry 2 (count sentence): built. The singular, zero and plural shapes are pinned; the zero sentence is now pinned too.
Carry 3 (wave and sort-key None): built, with a wave-3 group as null control. `_plain_key` now takes the list `sort_key` only.
Carry 4 (part-merged strip, heading markers): built, with one predicate for the strip and the row.
Carry 5 (also read 1-based as Carry 6; items 1 to 5): item 1 (filter), item 2 (shares the count sentence with Carry 1 item 3), item 4 (done-row blockers) and item 5 (no html or body tag in the page template, so nothing to close) are as before. Item 3: a hotfix blocking a critical-path group gets a `▲` mark. Its title is "hotfix blocking a critical-path group", and it uses the gating edges of `Blocked by`. It is now pinned on the rendered page, with the five null arms above.
No carry is sent to a next part.

## Forward-carry

none

## Friction

size_durations.fetch: unenforced: it had only a GraphQL path, so a seat with REST only could not re-measure. Carry: dismissed: built in this PR as `size_durations.fetch_rest` (`--via rest`, `replan.py --sizes-via rest`), remedy (a) of the round-2 verdict.
handoff-wip step push: cost: refs/heads/handoff-wip/r10-plan-page-residue holds e1a7081119, a commit outside this head's ancestry whose tree equals 9774026d05's, so no fast-forward step push was possible and none was forced. Carry: dismissed: the code went straight to the handoff ref.
