Fix review: blocked 9774026d059395474cd3a8fb115320c6a7dd3248 mutation-vacuous: hot-render hot-gates hot-discharged hot-notdone, and the durations input driver is not landed (fixer.md 18)

bus-nonce: 874a9352450cf4d9810664f7dbb5465d

Round 2 (delta re-review of 3bfdec2a09..9774026d05). The measured head is 9774026d059395474cd3a8fb115320c6a7dd3248. It was still the branch tip when this verdict was written (ev/head-at-verdict.txt).

## Block

The delta answers all three items the round-1 block named, and both of its findings. Two defects remain in what the delta adds.

- **The hotfix mark (Carry 5 item 3) is not pinned where it is drawn.** The self-test checks the `hot` flag on the rows from `build_rows`. Its `hot_page` is built from those rows, not from the rendered HTML. No check reads `hotcp`, `▲` or the title "hotfix blocking a critical-path group" in the page. My driver (ev/my-mutants.txt, ev/my-mutants-driver.py) found four survivors at this head. Each had `plan_page.py --self-test` rc=0 with no FAIL line:
  - `hot-render`: the `▲` span's `if r["hot"]` changed to `if False`. The carry's deliverable disappears from the page and nothing fails.
  - `hot-gates`: `roster_lib.gates(G[a])` dropped from `gating_crit`. A predecessor in a releasing stage would be marked. The body says the mark uses "the same gating edges as `Blocked by`", but nothing pins that.
  - `hot-discharged`: `a not in discharged` dropped from `gating_crit`.
  - `hot-notdone`: `g not in done` dropped from `hot`. This may be equivalent if every closed stage is a releasing stage. I did not establish that.

  Fix: add a page-level check that the `hotcp` mark appears exactly on the hot rows, and none on the cold fixture. Add fixture arms for a discharged predecessor and for a releasing-stage predecessor. For `hot-notdone`, either add an arm or record it as equivalent with the reason.
- **The re-measured `tools/plan/durations.json` cannot be reproduced from the tree.** The body says `size_durations.fetch` could not run (GraphQL 403). Its `--prs-cache` input was instead built over REST by a "scratch driver, sha1 8bba87c7...", and that driver is not in the diff. `fixer.md` step 18 says that a driver a body figure needs to be reproduced lands in the same pull request. `sizes_hours` (S 21.4, M 32.4, L 35.6, XL 35.6), `round_hours` 5.69 and `review_rounds` all depend on that input (ev/durations-diff.txt). The committed `sizes_provenance` also says "Measured by tools/plan/size_durations.py; re-derive, never edit", with no mention that the input was a REST-built cache. A reader re-deriving through the GraphQL path cannot tell whether a mismatch is drift or a different input. Fix: either (a) land the REST cache builder under `tools/audit/seat/` or `tools/plan/` and classify it, and state the REST input in `sizes_provenance`, or (b) have a seat with GraphQL re-run `replan.py --measure-sizes --out-durations` at the merge base without `--prs-cache` and commit that output, which the body already offers.

## Findings

- Follow-up: `size_durations.fetch` has only a GraphQL path. Here it turned a carry's one-command step into an unlanded scratch driver. The body's Friction dismisses this because "the relay has GraphQL". That dismissal holds only if remedy (b) above is taken. Under remedy (a) the REST path becomes tooling this PR lands. Carry: dismissed: settled by whichever remedy the block's second item takes in this PR

## Evidence

- Items the round-1 verdict blocked on, now answered:
  - Carry 0 item (1), closure conditions: `replan.CLOSURE_CONDITIONS` is in `summary.closure_conditions`. `check_plan` refuses a plan without it, and the page lede states it. The in-tree mutant `closure-conditions`, harness mutant `closure-conditions-text` and my `check-cc` (`check_plan` guard deleted) are all killed by a named FAIL.
  - Carry 0 item (3), durations: the file was re-measured in this PR (`sizes_measured_at` 2026-11-11T02:57:51Z, previously 2026-11-01T07:38:26Z). Its input is the defect in the Block's second item. I could not re-derive the figures: the cache and its driver are not in the tree, and this seat has no GraphQL. Carry: dismissed: evidence, not a finding
  - Carry 5 item (3), hotfix mark: built. Its row flag is pinned (harness mutants `hotfix-mark` and `hotfix-gates-crit` killed); its rendering is not, as the Block's first item says.
- Round-1 findings, now answered:
  - The `TypeError` arm now passes `str([...])`.
  - `review-min` and `wall-hours` are in-tree mutants, both "self-test fails when ... is deleted" ok (ev/selftest-replan.txt).
  - `eta-dash` and `zero-other` are recorded as equivalent. I re-ran `zero-other`: it exits rc=0 with no FAIL. That fits the body's equivalence claim, because the general path renders the same zero sentence. I accept it. Carry: dismissed: evidence, not a finding
- Removed mutant `stamp-on-axis`: `closure_at = max(stamps[-1].at, post_end)`, and the post-closure arm pins `pc["stamps"] == p0["stamps"]`, so no stamp lies past closure. Deleting the stamp term is a sound simplification, not a lost pin.
- Roster carries: the body names Carry 0 to Carry 5 individually (Carry 5 is also read as Carry 6). It does not send any item to a next part, and claims no part-2 item: Carry 5 item 3 is part 1 under round 1's reading. Carry 1 item 1 is still dispositioned "not reproduced". I did not re-derive the roster `source` figure. Carry: dismissed: evidence, not a finding
- RESULT self-tests at head: `replan.py --self-test` rc=0 "self-test: 0 failed"; `plan_page.py --self-test` rc=0 "91 checks, 0 failed". Both match the body's Figures.
- RESULT harness `r10_plan_page_mutants.py M0 hotfix-mark hotfix-gates-crit closure-conditions-text`: M0 null, three killed, `survived=0` (ev/harness-new-mutants.txt).
- Step 5: `VERSION`, the manifest and the notes heading are untouched. No claim or golden file is touched.
- Step 13: `git merge-tree --write-tree origin/main 9774026d05` rc=0, no conflict, against origin/main dbd1ab5b07 (ev/merge-tree.txt).
- Step 14: no budget, closures.json, INERT or golden file moves.
- CI: `merge_train.py classify` printed `WAIT ... pending: gate red: none` from 04:16Z on (ev/classify-poll.txt). This verdict's block does not depend on CI.
- Finder's harness: none. This is an instrument group fed by roster carries and closes no issue. Carry: dismissed: evidence, not a finding
