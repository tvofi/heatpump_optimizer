Plan-page group r10-plan-page-residue, repair round: the three own-group items the review blocked on, the two follow-up findings, and every roster carry answered. Closes no issue.

## Head

1be2e399191dc8613371955ec5e8e2f0b5812ab9

## Mutation proof

Each predicate was mutated in place; the named check fails and the unmutated copy passes.
- `replan.py --self-test` in-tree mutants (rc=1, named FAIL): `review-min` (`max(rounds - 1, 1.0)` -> `rounds`), `wall-hours` (`closure_at` -> `closure`), `closure-conditions` (the statement emptied), plus the earlier `live-review-stage`, `closure-later-of`, `closure-check-later-of`.
- `dev/audit/harnesses/r10_plan_page_mutants.py` (full run, one line per mutant): `hotfix-mark`, `hotfix-gates-crit` and `closure-conditions-text` are each `verdict=killed`; the run ends `survived=1` on `stamp-on-axis`, which is not killable now. Closure is the later of the round-close stamp and the catalog step, so no stamp lies past it; the redundant stamp term was deleted from `swimlanes` and the mutant removed with it (the mutant survived the previous head too, at 3bfdec2a09).
- Why `review-min` survived the previous round: the fixture prices a round at 0 h (`round_hours=0.0`, one round), so every review price was 0 and no mutant of the formula could move it. The arms now build a 1 h round and S at 3.0 and at 1.4 expected rounds, where the floor and the fraction cap separate (1.0 against 1.4).
- `eta-dash` and `zero-other` (review residuals) are not killable here: an ETA is drawn only for a scheduled group, and `_other_issues_sentence` with no other issues is the zero clause already pinned by the singular/zero arm. Recorded as equivalent, no arm added.

## Null control

- The self-test arm that failed with a `TypeError` now passes `str([...])`; the detail is a string on failure.
- No post-stamp group: closure equals the stamp's `at` (arm unchanged). A plan whose `closure_conditions` is emptied is refused by `--check`.
- `wall_hours` with a post-stamp group runs to `summary.closure` and exceeds the no-catalog plan's; with none it equals the stamp.
- Review price: S at 1.4 rounds prices one round (1.0 h), not 1.4 h; in progress is not priced as in review.
- Hotfix mark: the same edge from a non-hotfix marks nothing; a hotfix no critical-path group waits on marks nothing (`rows` of the unchanged fixture, zero marked).

## Figures

- `python3 tools/plan/replan.py --self-test`: `self-test: 0 failed`. `python3 tools/audit/seat/plan_page.py --self-test`: `91 checks, 0 failed`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `bash tools/pr/prepr.sh`: rc=0 at the head above.
- Durations (carry 0 item 3): `tools/plan/durations.json` re-measured with `replan.py --measure-sizes --out-durations tools/plan/durations.json` at merge base 63bcdcaad827ad3d98f914bc2e5b6110f9bb9444, roster ref `origin/handoff/audit-r10-roster` at add34472b2, `sizes_measured_at` 2026-11-11T02:57:51Z. `gh api graphql` returns HTTP 403 here ("GitHub GraphQL is not available from Claude Code sessions"), so `size_durations.fetch` cannot run. I wrote its `--prs-cache` input over REST (1044 merged PRs created since 2026-10-12, fields as `flatten` builds them: first commit authored date, issue comments, merge commit) with a scratch driver, sha1 8bba87c74b87ca1d0878fbd381d8839079e45a7e; the measurement code is unmodified. Not verified: the REST cache equals the GraphQL one for the same PRs (no seat here can run both); a seat with GraphQL can re-run the same command without `--prs-cache` and replace the file. Result: S 21.4, M 32.4, L 35.6, XL 35.6 h.
- Date of the main tip these figures were taken against: origin/main 444cf62fab, 2026-11-11T03:44Z; `git merge-tree --write-tree origin/main HEAD` is checked below.
- Class enumeration (step 8): no issue is closed and this group is an instrument group; the self-tests and the mutant harness above are the evidence.
- Unpinned sites (6d): the diff changes no file the mutation lane reads (`prepr.sh` mutants step: skip); the in-tree mutants above are the pin.

## Red checks

none owed (`gate` at 3bfdec2a09 was the interim deferral the owner's 2026-11-09 ruling excludes).

## Roster carries (the group's six, origin/handoff/audit-r10-roster, field `carry`)

Carry 0 (closure rule, 20 slots, durations): all three items built here. (1) `summary.closure_conditions` carries the six conditions; `check_plan` refuses a plan without them; the page states them in the lede. (2) 20 slots, provenance comment 6707334933, was built earlier in this PR. (3) durations re-measured, above.
Carry 1 (outside priority, live stage, counts, None, headings): item 2 (live stage) built, now with arms that can fail; items 3, 4 and 5 built earlier; item 1 (outside tiering): `dispatch_tier` reads `roster_lib.is_outside` and critical-path membership and existing arms pin it; I could not re-derive whether COMBI-TANK and OUTSIDE-INTAKE have `source` unset, so no code change; the render being roster data is not verified. Carry: dismissed: not reproduced at this head, the code reads the flag.
Carry 2 (count sentence): built, singular and zero shapes pinned with mutants.
Carry 3 (wave and sort-key None): built, null control a wave-3 group.
Carry 4 (part-merged strip, heading markers): built, one predicate for strip and row.
Carry 5 (also read 1-based as Carry 6; items 1 to 5): item 1 filter, item 2 (shares the count sentence with Carry 1 item 3), item 4 done-row blockers and item 5 (no html or body tag in the page template, so nothing to close) as before; item 3 (a hotfix blocking a critical-path group is marked) is built here: `hot` on the row, a `▲` mark with the title "hotfix blocking a critical-path group", from the same gating edges as `Blocked by`.
Carry 0 item 3 and Carry 5 item 3 are no longer sent to a next part.

## Forward-carry

none

## Friction

size_durations.fetch: unenforced: it has only a GraphQL path, so a seat with REST only cannot re-measure. Carry: dismissed: a REST fallback is new tooling beyond this group's carries and the relay has GraphQL.
