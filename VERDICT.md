Fix review: merge 2e3a13f00ce601de2880f395487893f9a892c427

bus-nonce: cdfe061791b40b6d92a39a2232b11d45
pending-ci: gate

## Review

- Round: second round over #3905 (first was blocked at 7f4028cb65 on a merge conflict). The packet's scope line reads `full`, because the dispatch passed the head as `--reviewed-head`. The previous verdict judged nothing but the conflict, so I reviewed the whole three-dot diff against 70f410e996, with the 7f4028cb..head resolution as its centre.
- Merge with main: `git merge-tree --write-tree origin/main 2e3a13f00ce601de2880f395487893f9a892c427` exits 0, and origin/main is 70f410e996, the PR's base (ev/merge-tree.txt).
- The ci.yml resolution is a union. `group:` is the PR's `CI-pr-<number>` arm with its `|| format('CI-{0}', github.run_id)` fallback, and #3904's `github.event_name == 'push' ... 'CI-main'` arm is gone. `cancel-in-progress:` is the PR's expression, and every push event reads false. The comment keeps #3904's text, from "A push to main's run is no exception" through "concluded verdict", after the L1 text. So main's behaviour is preserved: every push run gets a run-id group (`CI-99` in the model) and never cancels anything in progress.
- The tests/entities.py resolution is a union. `_CI_PLANTS` names at the head = origin/main's names + the PR's six L1 plants (`the PR group on every pull_request action`, `the PR group's cancel on every pull_request action`, `PR re-runs in the PR group`, `bot-sent pushes in the PR group`, `the PR group cancelling nothing`, `no PR group`). The only names missing are the three CI-main plants #3904 removed (`push re-runs in the main group`, `every push in its own group`, `the main group cancelling in progress`). #3904's two plants are rewritten to target the new expression and are still caught (`_CI_PLANT_MISSED == []`). In the per-sender loop, `want` is `CI-pr-7` only for a non-bot synchronize's first attempt and `CI-99` everywhere else, including push: #3904's `want` with the PR's arm added. #3904's `_CC_COALESCED = set()`, `_CC_TWIN_ROUTE` and main-cancel.yml pins (entities.py around line 33084) are untouched by the PR, and they pass at the head.

## Notes

- Note: stale-body: the body still describes the pre-merge state. It says "Push runs keep their groups byte-identical. The `CI-main` arm of the `group:` expression is unchanged", that the pin "wants `CI-main` for a push's first attempt", that "push attempt 1 still renders `CI-main`", and that "`the main group cancelling in progress` is re-cut". At this head, `CI-main` is gone (#3904), push renders `CI-99` with no cancel, and that plant is main's `a run-id group cancelling in progress`, rewritten as a `re.sub` over the `cancel-in-progress:` line. The code is right; only the body is stale.

## Evidence

- RESULT: mutation proof at the head, under my harness `ev/umbrella.py`. It is the seat's own instrument, not the finder's. It executes tests/entities.py's top-level statements one at a time and skips any that raise, up to the umbrella check. Each of four ci.yml mutants turns `the CI umbrella` to FAIL (ev/mutant-m1..m4.txt):
  - m1 restores main's run-id group and `cancel-in-progress: false`;
  - m2 re-adds #3904's removed `CI-main` push arm, which pins main's behaviour;
  - m3 drops the sender clause from `cancel-in-progress` only;
  - m4 drops `run_attempt == '1'` from `cancel-in-progress` only.
  At the unmutated head the check reads `ok` and `_CI_PLANT_MISSED == []` (ev/head-umbrella-twin.txt).
- RESULT: full `PYTHONPATH=tests/hastub python3 tests/entities.py` at the head, with HPO_CI_METRICS unset, prints `ALL 2779 ENTITY CHECKS PASSED`, rc=0. The 54 indented FAIL lines are planted-mutant self-test output. `a measured script's late-writing descendant is waited for, not recorded as nodata` reads `ok` here, which agrees with the body: its local red came from an inherited HPO_CI_METRICS (ev/entities-full-head.txt).
- The twin-route and main-cancel checks around entities.py:33084 pass at the head (ev/head-umbrella-twin.txt). These are `a superseded long-job pull-request run is cancelled; pr-contract same-SHA twins are not`, `#3885: main-cancel.yml cancels superseded main runs on a push to main only ...` and their null controls. The `_cc_pr_event` model sets no `github.event.action`, so that check renders every pull_request pair into the run-id group. The synchronize arm is pinned by the umbrella's per-event × attempt × sender loop instead.
- Merge: `git merge-tree --write-tree origin/main <head>` exits 0 at origin/main 70f410e996 (ev/merge-tree.txt).
- Claims, versions: the three-dot diff touches 5 files (ci.yml, harness ci3885_queue.py, delivery/3905.md, closures.json, entities.py). No claim file, VERSION, manifest or RELEASE_NOTES change. No `custom_components/` line changes, so nothing widens and no production mutant is drawn.
- Not re-derived: the figures (66 runs / 664 runner-min / 124 jobs on 2026-11-25, and 1 / 1 / 0 on 2026-11-24) and the null arm `supersede_null_same_head_code` need `ci3885_queue.py fetch` over the Actions API, which this seat cannot reach. figure_lint resolves both commands in the tree (ev/review-packet.md). The body's "failing first" run against the old ci.yml is covered in substance by mutant m1.
- CI: `merge_train.py classify 2e3a13f00ce601de2880f395487893f9a892c427 --pr 3905` printed `WAIT 2e3a13f00ce601de2880f395487893f9a892c427 pending: gate red: none` (exit 3) throughout ~30 min of polling, 05:20 to 05:50 UTC (ev/classify.txt), hence `pending-ci: gate`. review_packet refused `introduced-red: unreadable` because instrument-self-tests was in progress at render, and classify decides.
- Environment: venv-ha lacked paho and scipy, which I installed to a side directory for the harness runs only. The comms heartbeat was restarted once after its background limit.
- Self-audit: `carry_audit.py check` over this verdict exits 0 (0 finding items). The PR body's own carry_audit at the head reads 0 items (ev/review-packet.md).
