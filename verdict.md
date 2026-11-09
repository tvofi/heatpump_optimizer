Fix review: merge 43136fbca4b5ba2a6f7f137f60cf67951a305c94

bus-nonce: bfca54d4d3ed57448fe954adfedaeb59

## Scope

This is round 3, a delta review. I reviewed head 43136fbca4b5ba2a6f7f137f60cf67951a305c94 against merge base daf8b349fd30cc60786eeca333a426b693aa4c5f and judged only the points of the round-2 verdict (verdict/3304 7d34055f3, blocked 2bf0e026, class-open). The repair is commit 2135d8b92. Every other commit in 2bf0e026..head is a main merge. Each of those has an empty `git show --remerge-diff`, so there is no resolution delta.

## Round-2 items at this head

- Block (replan `dispatch_tier` keeps the production-only hotfix arm): closed. The arm is now `roster_lib.is_hotfix(group)` (tools/plan/replan.py:432). The finder's fixture flips at the head: R10-HOTFIX-X (instrument) gets tier 2 and holds the real slot at t0, ahead of R10-OUT at tier 3. At 2bf0e026 it got tier 6 and OUT held the slot. On the live roster at 00885c69, the open is_hotfix groups not at TIER_HOTFIX go from 7 at 2bf0e026 to 0 at the head, the same seven groups round 2 named.
- Finding 2 (open_driver counts a hotfix by name only, not by kind `bug`): closed. `default_class` takes the roster's `is_hotfix` set, and `run_pass` builds that set and passes it through `order`. A kind-bug group with no HOTFIX name now opens ahead of an outside group (`['r10-bugfix', 'r10-out']`). At 2bf0e026 the order was reversed.
- Finding 3 (merge_train.py.md leaves out the outside term): closed. The doc now states the drain order (`--priority`, roster hotfix or `--front`; then outside; then critical path; then arrival) and the branch-then-`group_for_pr` mapping.
- Finding 4 (fork-head fallback in the tick and in gate_priority): closed for the tick. `owed_levels` now falls back to `rl.group_for_pr(roster, n)`. For gate_priority, the body records the disposition that `derived_priority` runs before a pull request exists (prepr step 1b0) and receives only a branch. The function signature confirms it: `derived_priority(branch, *, repo, ref, fetch)` takes no pull-request number. I accept that disposition.
- Repair beyond the verdict: merge_train `drain_order` now puts a roster hotfix that was spooled without `--priority` into the priority tier (`Train._hotfix` through `_roster_is`). The fixture drains `[8, 31, 7]` at the head and `[31, 7, 8]` at 2bf0e026.

## Evidence

- Head: `git ls-remote` shows fix/r10-outside-first at 43136fbca4b5ba2a6f7f137f60cf67951a305c94 at the start, after CI, and before this write (`ev/final-refs.txt`, `ev/HEAD.txt`). The body's `## Head` names it.
- Role file: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current. I read it through role_pack.py.
- Merge: `git merge-tree --write-tree origin/main <head>` gives rc 0 and tree d3402b92 at origin/main 425b8584 (`ev/merge-tree.txt`). Earlier, at origin/main daf8b349, it gave rc 0 and tree 2c821351.
- Class search: I ran the body's hotfix-predicate rule widened to `HOTFIX|hotfix|kind "bug"|== "bug"` over tools/ (*.py, *.sh, *.mjs), with selftests and comment lines dropped (`ev/class-search-head.txt`, 97 lines). The sites that decide an order are replan `dispatch_tier`, open_driver `default_class` and `run_pass`, merge_train `drain_order` and `_hotfix`, roster_lib `is_hotfix` and `dispatch_rank`, and gate_priority and orchestrator_tick, which reach the predicate through `dispatch_rank`. All of them now read `roster_lib.is_hotfix`. open_driver also keeps its old `r10-hotfix-`/`R10-HOTFIX-` name test as an extra arm. The remaining hits are docstrings, help text, fixtures, provenance names (merge_throughput, probe_bridge, record_row, agreement.mjs, field_coverage.mjs, cancel_superseded, gh_comment, stamp) or plan_page's tier label. None of them orders work. The search finds no open site.
- Harness: the finder named no harness. I rebuilt the round-2 finder's blocking fixture (`ev/hotfix-predicate.txt` on verdict/3304) as my own reviewer harness, `ev/hotfix_harness.py.txt`. It puts one instrument-class R10-HOTFIX group and one outside group through replan, dispatch_rank, open_driver and drain_order, and adds a kind-bug arm. I ran it at 2bf0e026, at the merge base and at the head (`ev/harness.txt`).
  - At the merge base, replan gives both groups tier 4 and roster_lib has no `dispatch_rank`. The outside ordering is this PR's feature, so the base is flat by design.
  - At the head: replan tiers 2 and 3, hotfix first on the real slot; dispatch_rank `[0, 1]`; open_driver `['r10-hotfix-x', 'r10-out']`; kind-bug order `['r10-bugfix', 'r10-out']`; drain `[8, 31, 7]`.
- Null control: the same harness with the HOTFIX name dropped (R10-FIX-X) and kind `bug` removed. At the head it gives replan tier 6, OUT first, dispatch_rank `[3, 1]`, `['r10-out', 'r10-fix-x']`, `['r10-out', 'r10-bugfix']` and drain `[31, 7, 8]`. These match the 2bf0e026 null results exactly, so the head's change comes from the predicate and from nothing else.
- Live roster: `ev/live_tiers.py.txt` applies the body's stated rule at roster 00885c6998b7 (`ev/live-tiers.txt`). It gives `9; 7` at 2bf0e026 and `9; 0` at the head, matching the body's figure taken at roster 93fd3041. Whatever script the body's `tiers.py` was, I re-derived the figure with my own.
- Mutation proof: I wrote 11 mutants on every production line 2135d8b92 changes, each applied to a git-archive copy of the head and run against the owner file's own self-test (`ev/mutants.txt`, script `ev/reviewer_mutants.py.txt`). All 11 were KILLED and none survived:
  - replan: replan-base-arm (the base predicate restored) and replan-arm-off;
  - open_driver: od-hotfix-set-off, od-order-drop, od-runpass-empty and od-runpass-drop;
  - orchestrator_tick: ot-fork-fallback;
  - merge_train: mt-drain-hotfix, mt-hotfix-default, mt-hotfix-pred and mt-roster-is-const.
  These cover the body's six named mutants and five more.
- Self-tests, all rc 0 with 0 failed (`ev/selftests.txt`):
  - head: replan 0 failed, open_driver 86, orchestrator_tick 286, merge_train 574, roster_lib 71, gate_priority 15. These match every count in the body's Figures.
  - 2bf0e026: 84, 285, 514, 71, 15.
  - merge base: 76, 283, 564, 67, 12.
- Three-dot diff: 12 files (`ev/three-dot-stat.txt`), the PR's own. The repair touches only its 6 files. No change to `VERSION`, the manifest, `RELEASE_NOTES.md`, any `*_budgets.json`, any claim file or `tests/closures.json`. The delivery row `dev/programme/delivery/3304.md` reads `**open**`, which is current. `tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0.
- `tests/entities.py`, run plainly with BASH_ENV absent: it did not run clean. It stops at import with `ModuleNotFoundError: No module named 'homeassistant'` from tests/harness.py:25 (`ev/head-entities.txt`), as in round 2. CI's `tests / closures` and `tests / fast (3.14)` concluded success at this head.
- CI at this head (`ev/checks.txt`, 68 check runs read paginated; `ev/runs.txt`):
  - The code run 42526232964 was cancelled at 21:57Z by something outside the workflow; cancel-superseded printed `0 superseded run(s)`. It was re-run as attempt 2 and concluded success at 23:27:49Z: `gate` 128897977586 success and `pr-contract / pr-contract` 128897797737 success. Every check started after 22:58Z is success or skipped.
  - The only reds are two `gate` runs of the edit runs 42526233329 and 42526489839, at 21:50Z and 21:54Z. Each logs `FAIL run(s) [42526232964...] at this head are still being judged; their gate decides` (`ev/deferral-gates.txt`), which is gate.py's deferral. merge_train calls this "A DEFERRED GATE IS NOT A VERDICT". The run they defer to has since concluded green.
  - `merge_train.py classify 43136fbc… --pr 3304` reads `RED … pending: none red: gate` (rc 1, last at 2026-11-09T00:12:39Z, `ev/classify.txt`). The cause is that `latest_runs` keeps the worst of each suite's latest `gate`, and gate-sweep.yml, which re-runs deferred gates when a CI run completes, has not run since 2026-11-08T12:22Z (`ev/gate-sweep-runs.txt` is empty after 23:00Z; its last five runs are at 12:20–12:22Z).
  - I judge the head GREEN on the deciding gate and say so here. The train's own classify will hold the head until those two deferral gates are re-run, so this verdict bypasses no CI check.
- Red checks: the body's `## Red checks` names and answers the three reds of earlier heads. The two deferral reds above are a sweep gap, not this diff's failure. The pr-contract run at 23:26Z, which started after the last red concluded, is green.
- Forward-carry: the body's one carry and two Friction items are dismissed with reasons, and the packet's carry_audit routed all three. The round-2 Findings all carried to R10-OUTSIDE-FIRST and are closed above.

## Findings

- Non-blocking: the two deferral `gate` runs at this head (128873108045 and 128874191966, edit runs 42526233329 and 42526489839) still read red after the code run they defer to concluded green. gate-sweep.yml has not fired since 2026-11-08T12:22Z, so `merge_train classify` reads this head RED until someone re-runs those two gate jobs. The PR's code is not the cause, and a sweep that never fires leaves every PR with an edit run in the same state. Carry: dismissed: an orchestrator re-run of the two gate jobs clears it for this PR, and the train's classify refuses the head until then, so nothing merges on the stale red; the sweep outage is main's to diagnose, not this PR's
