Fix review: blocked 3fd85299d9c2314a3316c1956a97d37a9d95de77 mutation-survivor: theil-sen-ordered-pairs, round_slope's pair rule k2 != k1 is unpinned and moves the published round cost 4.63 to 3.58 h

bus-nonce: 8659d78b3923e1471fef0e8507091644

## Block

Round 1. The brief requires a kill for reviewer-planted mutants on the model, the Theil-Sen slope named. One survives:
`tools/plan/size_durations.py` `round_slope`, `for k2, h2 in pts[i + 1:] if k2 != k1]` replaced by `... if k2 > k1]`
(keep only pairs whose later row has the larger x). `size_durations.py --self-test` stays `0 failed` (rc=0), because every
Theil-Sen fixture in the self-test (`rs` with rounds 1,1,1,3,3; the `round_slope` fixture with rounds 1..4; carries 1..5)
lists its rows in ascending x, so a filter that drops descending pairs drops nothing there. On real data rows are in roster
order, and the mutant moves the published model: with the cache I rebuilt over REST (PRs merged by `sizes_measured_at`
2026-11-01T07:38:26Z, roster at 534e120c8), `round_hours` 4.63 -> 3.58, `carry_hours` 0.33 -> 0.03, `first_round_hours` M
14.9 -> 18.3, `sizes_hours` M 22.3 -> 24.0, XL 31.1 -> 32.5. The repair is a self-test arm whose rows are not sorted by x
(for example the existing 5.5 h fixture listed in reverse) plus the mutant in `r10_plan_durations_mutants.py`; then steps 2-8
of `fixer.md` re-run.

## Findings

- Surviving mutant `theil-sen-ordered-pairs` on `round_slope` (above): the pair-orientation rule of the Theil-Sen slope, used for both `round_hours` and `carry_hours`, is pinned by no check; the fixer adds an unsorted-x arm and the mutant to the harness. Carry: R10-PLAN-REAL-DURATIONS
- The body's `## Red checks` reasons from the wrong branch: it says no workflow run exists for `handoff/r10-plan-real-durations`, but the PR head branch is `fix/r10-plan-real-durations-pr` and 55 check runs exist at this head (ev/checkruns.txt). None concluded red, so the conclusion `none` holds at this head, but the stated reason must be re-taken from this head's own check runs. Carry: R10-PLAN-REAL-DURATIONS
- The body's `## Mutation proof` says "twenty one-occurrence replacements"; the harness holds nineteen replacements plus the M0 null (20 entries), so the stated figure is wrong by one and must read nineteen. Carry: R10-PLAN-REAL-DURATIONS
- The body's ownership paragraph says no roster group exists ("Proposal, nothing written to the roster"); at origin/handoff/audit-r10-roster 7a426457a the group `R10-PLAN-REAL-DURATIONS` now exists with the proposed size, models, after-list and files, so the body must name it as the owning group at that roster SHA. Carry: R10-PLAN-REAL-DURATIONS

## Evidence

- Head reviewed: 3fd85299d9c2314a3316c1956a97d37a9d95de77, from a detached worktree at that SHA (ev/HEAD.txt). Base and merge base e4c9e2016a455d787d3a7604ef88c803c3ba5c70 = origin/main at review time; `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty, so the contract is current.
- Merge: `git merge-tree --write-tree origin/main 3fd85299d` exits 0 (tree e9a45cab8), no conflict, no claim-file driver invoked.
- Fixer's harness, re-run as evidence: `r10_plan_durations_mutants.py` prints `RESULT mutant=M0 rc=0 fails=0 verdict=null`, all 19 named mutants `verdict=killed` rc=1, `RESULT survived=0` (ev/mutants.txt). The brief's "twenty mutants" is 19 plus the null.
- Reviewer's own harness (mine, not the finder's; ev/reviewer_mutants.txt, script at mine/rev_mutants.py in the review directory, not landed): null rc=0; killed: pctl-scale (p/100 -> p/101, 10 FAIL), theil-sen-p75 (median -> p75 of slopes, 5 FAIL), rounds-not-added-back, carry-baseline-p75, per-carry-unadjusted, active-gap-merged, min-cell-6; SURVIVED: theil-sen-ordered-pairs. `RESULT reviewer-survived=1`.
- Real-data effect of the survivor: ev/ordered_pairs_effect.txt, ev/rederive_mutant_ordered_pairs.json.
- Self-tests at the head: `size_durations self-test: 0 failed`, `replan.py self-test: 0 failed`, `plan_page self-test: 66 checks, 0 failed`, each rc=0 (ev/selftest_*.txt).
- Model figures re-derived: GraphQL is refused in this seat, so I rebuilt the PR cache over REST (my own fetcher: 800 closed, 766 merged since 2026-10-10; 758 merged by 07:38:26Z) and ran `size_durations.py --roster-ref 534e120c8` (roster tip at the measurement instant). Exact match with durations.json: `first_round_hours` {S 12.1, M 14.9, L 16.4, XL 22.6}, every `first_round_by_class_hours` cell (S instrument 11.7, S production 16.1, M instrument 13.6, M production 17.2, L production 16.0), `carry_baseline`, `carry_hours` 0.33, `carries_per_part` 11.0, n=189 (S 123, M 49, L 11, XL 6). Small differences I attribute to my REST rebuild (comments read now, not at 07:38Z), not verified either way: `round_hours` 4.63 vs 4.62, S `review_rounds` 2.31 vs 2.33, M `sizes_hours` 22.3 vs 22.2, `carry_part_hours` 19.9 vs 19.8 (ev/rederive_0738.json).
- Independent recomputation outside the tool from the rows: S/instrument p75 of round-adjusted hours = 11.7 (n=83) and M/production = 17.2 (n=31) at slope 4.62 and 4.63 both. Hand check from PR timestamps: R10-TARIFF #2282 first commit 13:23:50Z to merge 01:31:46Z = 12.13 h, R10-GATE-YIELD #2275 = 6.76 h, both equal to the tool's row hours (ev/spot_rows.txt).
- Roster: `carry_audit.py --roster-ref origin/handoff/audit-r10-roster pr 3097` prints `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` rc=0; the body carries nothing, so no destination needed resolving (ev/carry_audit_pr.txt).
- Privacy: no added line and nothing in durations.json matches a home path, an email address or a Home Assistant entity id (ev/privacy.txt, empty).
- Gate: delivery row dev/programme/delivery/3097.md in the three-dot diff; claim files, VERSION, manifest, RELEASE_NOTES.md untouched (grep count 0, ev/files.txt); `tests/structure.py` prints `STRUCTURE RATCHET PASSED`, no budget file in the diff; `closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`; the new harness is added to tests/closures.json's list beside its siblings. `tests/entities.py` and `tests/harness_headers.py` could not run in this container (missing homeassistant/paho modules in both venvs; failures unrelated to this diff), so I cite CI's `tests / closures` for them.
- CI at this head: `merge_train.py classify 3fd85299d...` exited 0 at 15:42:46Z, `GREEN ... pending: none red: none`; 55 check runs at the head, none concluded red (ev/checkruns.txt, ev/classify.txt). Head re-read before posting: still 3fd85299d9c2314a3316c1956a97d37a9d95de77.
