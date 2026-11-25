Design review: revise fe76bbf2a68fea88d0acded237187feee2bd399e architecture-unsound

Base read: 91f6e91bea926777d03fc23de1c21e5247abf290 (an ancestor of origin/main). No open design/* ref overlaps these hot files; design/R11-CI-CASE-SELECT touches neither ci.yml's concurrency nor sweep.py.

Revise points:
1. architecture-unsound: design.md §3 "L6. Gate sweep" (a). The note says "the sweep acts only on a run whose own gate is green". The tree says otherwise. tools/ci/sweep.py:16-19 and `settle` (sweep.py:384-419) act on a completed V whose gate is not green, V's own gate included, and the docstring names "a decider that ended red or cancelled -- would stay red". Adding `workflow_run.conclusion != 'cancelled'` to gate-sweep.yml:27 drops that settle for any decider cancelled at the LIVE head. Two examples are a cancel by hand, and a priority-held run that cancel_superseded.py:289-290 drops unrun after HELD_MAX_AGE_S. The gates that deferred to that decider then stay red until a new event. No finding names this behaviour change. Fix wanted, either one: (a) drop L6a; or (b) skip only a cancelled V whose head_sha is no longer the PR's head, and give sweep_selftest.py a null row. In that null row a decider is cancelled at the live head and settle still re-runs the gate that deferred to it. With either fix, state how §4 W1's "on a decider's completion" re-run survives the skip.
2. architecture-unsound: design.md §4 W1, "replacement holding no runner". The new sweep arm POSTs `rerun-failed-jobs` on deferred runs and never names `stale_pin`. sweep.py:43-50 never re-runs a stale pin: a re-run replays the event's base.sha programs (#3261: a pre-#3246 busy() ran ten times). In that case the sweep dispatches one fresh run instead. Fix wanted: route the W1 arm through the same stale-pin rule (STALE-PIN dispatch, not re-run). Add a sweep_selftest.py row: a deferred run whose base pin predates a tools/ci change gets a dispatch and no re-run. Its null row is the same run at a current pin, which gets re-run.

Decisions routed:
- decision: owner. The "Ruling needed" section, on CI-5's `CI-main` serialization (ci.yml:69-76). No lever in this note changes it, and it blocks no lever.

Notes for the fixer (carried, not revise points):
- L1 must rewrite the ci.yml:66-68 comment, "Supersession is cancel-superseded's alone", and its tests/entities.py pin in the same PR. Otherwise the comment contradicts the new `CI-pr-<number>` group. Carry: R11-CI-3885-QUEUE (item l1-comment)
- L7's sibling sweep is complete at base. The only whole-run POST .../rerun calls in production are merge_train.py:4572 and cancel_superseded.py:316. codeql-triage-poll.sh:16 already passes `--failed`. merge_pr.sh:192/316 and gh_read.py:795 are self-test fakes. Carry: dismissed: sibling sweep complete (item l7-sites)
- L1's bot exemption matches cancel_superseded.py:104 `BOT = "github-actions[bot]"`. Carry: dismissed: verified consistent (item l1-bot)

Checked and sound: the owning seam (§2) against the tree; L2's harness is the finder's, ci3885_light.py, as carry-3885.json carry 1 names it; the null controls (11-24) are set for each lever; cost is split into separate small PRs.
Token count: not reported by this harness.
