# Review packet #3419
head: cd13fd1f345086d79eefe4f968f646b55a00d84d
base: 30c785330fc727ae26d6a6d2d51b38f1856fe87c

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
arch-score / arch-score id=130310581609 queued
arm id=130307810163 skipped
budget-raise-gate / budget-raise-gate id=130310581429 queued
cancel-superseded id=130307835694 queued
codeql id=130310535322 skipped
codeql / Analyze (actions) id=130310581502 in_progress
codeql / Analyze (javascript-typescript) id=130310581568 queued
codeql / Analyze (python) id=130310581495 in_progress
governance id=130310535362 skipped
governance / delivery-status id=130310581800 queued
governance / delivery-status-publish id=130310582835 skipped
governance / env-matrix id=130310581507 queued
governance / instrument-self-tests id=130310581776 queued
governance / policy-docs id=130310581559 queued
governance / record id=130310583238 skipped
governance / wave-script id=130310581481 queued
hassfest id=130310535678 skipped
hassfest / hassfest id=130310581785 queued
kernel-points id=130310583115 skipped
prelude id=130307835441 success
refresh id=130307835678 in_progress
tests id=130310534669 skipped
tests / briefs id=130310581619 queued
tests / closure-scope id=130310581782 queued
tests / mutation id=130310581639 queued
tests / nightly-status id=130310581661 queued
validate id=130310534994 skipped
validate / validate-hacs id=130310581642 success

## Refusals
none

## Advisories
none

## carry_audit at the head
NOTE body item 0bbcfcc2: dismissed:R10-RCA-MAIN-SELFTESTS-RED is resume.stage done, and the countermeasure lands in this PR
NOTE body item 88ef2721: dismissed:a local timing failure under strace, not reproduced untraced or on the final replay, and the job's own traced run on main is its detector
CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
ok         python3 -I tools/ci/selftest_scope.py check --traces <dir>/selftest-trace
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py record --step beat-job-rows --step carry-check-and-the --step cloud-relay --step field-coverage --step handover-prompt --step hooks-setup --step open-pr --step plan-page --step post-merge-bookkeeping --step post-merge-record-line --step pr-args --step prepr --step roster-queue-runner --step self-tests-outside-seat --step selftest-scope --step selftest-scope-mutants --step selftest-wiring --step state-doc-writer --step update-pr --step verdict-bus
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py static
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 -I tools/ci/selftest_scope.py --self-test
             `tools/ci/selftest_scope.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"
             `tests/closure.py` is in the tree at this head

FIGURES: 6 resolved, 0 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/.github/workflows/governance.yml b/.github/workflows/governance.yml
index cb6507cad4..8a2461d898 100644
--- a/.github/workflows/governance.yml
+++ b/.github/workflows/governance.yml
@@ -332,10 +332,15 @@ jobs:
           done
           echo "selftests=${SELFTESTS:-all}: $(wc -l < "$RUNNER_TEMP/selftest-scope.txt") of $(wc -w <<< "$known") gated step(s) run"
 
+      # `settle` rewrites the index after the checkout's last second, so no
+      # traced step's first `git status` re-reads the files the checkout wrote
+      # last (R10-HOTFIX-PREPR-READSET: run 42780661829 put those reads in prepr).
       - name: Install strace for the read-set measurement
         id: strace
         if: env.SELFTEST_TRACE != ''
-        run: sudo apt-get update -q && sudo apt-get install -y -q strace
+        run: |
+          sudo apt-get update -q && sudo apt-get install -y -q strace
+          python3 -I tools/ci/selftest_scope.py settle
 
       # THE FIVE SLOWEST SELF-TESTS START HERE AND ARE READ AT THE END
       # (R10-HOTFIX-SELFTEST-TIMEOUT). Run in line they were most of this
diff --git a/dev/programme/delivery/3419.md b/dev/programme/delivery/3419.md
new file mode 100644
index 0000000000..a7cf41b0f9
--- /dev/null
+++ b/dev/programme/delivery/3419.md
@@ -0,0 +1 @@
+- [#3419](https://github.com/tvofi/heatpump_optimizer/pull/3419) — **open**, R10-HOTFIX-PREPR-READSET: settle the racily clean index before tracing the self-tests (R10-HOTFIX-PREPR-READSET)
diff --git a/tools/ci/selftest_closures.json b/tools/ci/selftest_closures.json
index cf873bcd70..5ab7906e14 100644
--- a/tools/ci/selftest_closures.json
+++ b/tools/ci/selftest_closures.json
@@ -176,6 +176,7 @@
    "files": [
     "tools/audit/seat/beat_jobs.py",
     "tools/audit/seat/beat_jobs_selftest.py",
+    "tools/audit/seat/beatd.jobs.json",
     "tools/audit/seat/fixtures/beat_jobs/**",
     "tools/audit/seat/ledger.py",
     "tools/audit/seat/orchestrator_tick.py",
@@ -192,9 +193,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "beatd": {
    "run_sha": "890c4cc0063250459d54f074ae06e1953ddfa0feb7148a64ef54276c2a968407",
@@ -327,17 +328,17 @@
     "tools",
     "tools/audit",
     "tools/policy",
-    "tools/policy/policy_lint.mjs",
     "tools/pr/app_approve.sh"
    ],
    "dirs": [
     "tests",
     "tools/audit",
-    "tools/audit/seat"
+    "tools/audit/seat",
+    "tools/policy"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "ci-predictor": {
    "run_sha": "e06a8fb9b8d49bc863a2e947c030db8b387e81a3f5d114bcb83c22f22534e174",
@@ -546,6 +547,8 @@
    "run_sha": "3b48ec7e71b49eae06fc284309966260011f2c4017ab49fd6a752c95b149868f",
    "files": [
     "dev/governance/roles/fix-review.md",
+    "tests/closures.json",
+    "tests/mutation_table.py",
     "tests/throwaway_git.sh",
     "tools/audit/carry_audit.py",
     "tools/audit/seat/**",
@@ -557,6 +560,7 @@
     "objects",
     "packed-refs",
     "refs",
+    "tests",
     "tools",
     "tools/audit",
     "tools/audit/seat",
@@ -564,6 +568,7 @@
     "tools/pr/app_comment.sh"
    ],
    "dirs": [
+    "tests",
     "tools/audit/seat",
     "tools/audit/seat/beatd_shims",
     "tools/audit/seat/fixtures",
@@ -573,9 +578,9 @@
     "tools/audit/seat/instruments",
     "tools/audit/seat/shims"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "cloud-setup-profile": {
    "run_sha": "0a2fb43948f79c43c90c697eeff8b63e4c98d7ab176a35b3e06398f29fcd69a8",
@@ -1616,6 +1621,7 @@
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
     "tools/audit/seat/state_docs.py",
+    "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
     "tools/audit/seat/sweep_driver_selftest.py",
     "tools/audit/seat/sweep_gantt.py",
@@ -1705,9 +1711,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "figure-census": {
    "run_sha": "740c9b07ed8530eb237326010160ac6b0a36a741f8dd09a41ce91c3a78aaacb7",
@@ -1994,26 +2000,32 @@
   "handover-prompt": {
    "run_sha": "978bb964bf6f2b3577322b27c19093a8d35e6e9ed1da21d05f37a4dd47b0644f",
    "files": [
+    "tests/layout.py",
     "tools/audit/seat/handover_prompt.py",
-    "tools/audit/seat/roster_lib.py"
+    "tools/audit/seat/roster_lib.py",
+    "tools/policy/budget_raise_gate.py"
    ],
    "probes": [
     ".",
     ".claude/rules",
     "dev/governance/roles",
     "dev/programme/delivery",
+    "tests",
     "tools",
     "tools/audit",
     "tools/audit/seat",
+    "tools/policy",
     "tools/pr/app_push.sh",
     "tools/release/stamp.py"
    ],
    "dirs": [
-    "tools/audit/seat"
+    "tests",
+    "tools/audit/seat",
+    "tools/policy"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "heartbeat-andon": {
    "run_sha": "c37a5295c81af9650f42bdf9a55da123d3989f942b8d748425ffabd644f2cf47",
@@ -2135,6 +2147,7 @@
     "tools/audit/seat/selftest_wiring.py",
     "tools/audit/seat/shims/**",
     "tools/audit/seat/state_docs.py",
+    "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
     "tools/audit/seat/sweep_driver_selftest.py",
     "tools/audit/seat/sweep_gantt.py",
@@ -2159,9 +2172,9 @@
     "tools/audit/seat/instruments",
     "tools/audit/seat/shims"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "lane-skip-decision": {
    "run_sha": "93637fa3725f392f833de33b8fae0b336cf07368c62ed558f20de81a51e82d82",
@@ -2619,6 +2632,7 @@
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
     "tools/audit/seat/state_docs.py",
+    "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
     "tools/audit/seat/sweep_driver_selftest.py",
     "tools/audit/seat/sweep_gantt.py",
@@ -2693,7 +2707,6 @@
    ],
    "probes": [
     "-",
-    "-c",
     ".",
     "config",
     "objects",
@@ -2727,9 +2740,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "orchestrator-tick": {
    "run_sha": "3d6d9b5492e86cf277695081249b8930a14cd223f8b17a1a2a162c5e2337c19f",
@@ -2873,6 +2886,7 @@
   "plan-page": {
    "run_sha": "87be7bdeb72cf26e61fa3d08fdbf093158083de1b44904cad7a2b2f150cf5736",
    "files": [
+    "tests/layout.py",
     "tests/throwaway_git.py",
     "tools/audit/merge_throughput.py",
     "tools/audit/seat/bottleneck_check.py",
@@ -2882,6 +2896,7 @@
     "tools/audit/seat/roster_lib.py",
     "tools/plan/durations.json",
     "tools/plan/replan.py",
+    "tools/policy/budget_raise_gate.py",
     "tools/release/stamp.py"
    ],
    "probes": [
@@ -2890,6 +2905,7 @@
     "tools",
     "tools/audit",
     "tools/plan",
+    "tools/policy",
     "tools/release"
    ],
    "dirs": [
@@ -2897,11 +2913,12 @@
     "tools/audit",
     "tools/audit/seat",
     "tools/plan",
+    "tools/policy",
     "tools/release"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "plan-public": {
    "run_sha": "abc70dfd4be9ad00009e8ed57e464993780ee62569627840b5783c3ad3b70b6f",
@@ -3639,41 +3656,53 @@
    "run_sha": "7f9730626bce97831ee61c879e8b929c037930447bf2bd8c202bbac5e13ade99",
    "files": [
     "dev/governance/roles/nudge.md",
+    "tests/layout.py",
     "tools/audit/seat/postmerge.py",
     "tools/audit/seat/record_beat.py",
-    "tools/audit/seat/roster_lib.py"
+    "tools/audit/seat/roster_lib.py",
+    "tools/policy/budget_raise_gate.py"
    ],
    "probes": [
     ".",
+    "tests",
     "tools",
     "tools/audit",
-    "tools/audit/seat"
+    "tools/audit/seat",
+    "tools/policy"
    ],
    "dirs": [
-    "tools/audit/seat"
+    "tests",
+    "tools/audit/seat",
+    "tools/policy"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "post-merge-record-line": {
    "run_sha": "f0f980b0b4885b93951ea498acfffac8c721e177169e6cef1a0cf54ac6ae6c3f",
    "files": [
+    "tests/layout.py",
     "tools/audit/seat/record_beat.py",
-    "tools/audit/seat/roster_lib.py"
+    "tools/audit/seat/roster_lib.py",
+    "tools/policy/budget_raise_gate.py"
    ],
    "probes": [
     ".",
+    "tests",
     "tools",
     "tools/audit",
-    "tools/audit/seat"
+    "tools/audit/seat",
+    "tools/policy"
    ],
    "dirs": [
-    "tools/audit/seat"
+    "tests",
+    "tools/audit/seat",
+    "tools/policy"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "pr-args": {
    "run_sha": "899b6b6134adb436b9d10b4079f0d6107dc774ba0b279abe835eef473262ec0f",
@@ -3788,6 +3817,7 @@
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
     "tools/audit/seat/state_docs.py",
+    "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
     "tools/audit/seat/sweep_driver_selftest.py",
     "tools/audit/seat/sweep_gantt.py",
@@ -3862,7 +3892,6 @@
    ],
    "probes": [
     "-",
-    "-c",
     ".",
     "config",
     "objects",
@@ -3896,9 +3925,9 @@
     "tools/site/.gitattributes"
    ],
    "dirs": [],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "pr-merger": {
    "run_sha": "49a4573210ed0ee90b52759978d16a2c1f80c901a1e4dca863184a8daaaa8890",
@@ -3939,7 +3968,6 @@
    "files": [
     ".claude/hooks/**",
     ".claude/settings.json",
-    ".gitattributes",
     ".github/workflows/**",
     ".gitignore",
     "CLAUDE.md",
@@ -3958,7 +3986,6 @@
     "tests/card_drift.mjs",
     "tests/closure.py",
     "tests/closures.json",
-    "tests/env_drift.py",
     "tests/gate_lock.py",
     "tests/harness_headers.py",
     "tests/layout.json",
@@ -3977,7 +4004,6 @@
     "tools/audit/seat/review_packet.py",
     "tools/audit/seat/roster_lib.py",
     "tools/audit/worktree_gc.sh",
-    "tools/merge/ledger_merge.py",
     "tools/policy/brief_lint.mjs",
     "tools/policy/budget_raise_gate.py",
     "tools/policy/counts.mjs",
@@ -4009,6 +4035,7 @@
     "tools/policy/fixtures/policy-rot/prepr/upstream/**",
     "tools/policy/fixtures/policy-rot/prepr/wrong-head.md",
     "tools/policy/fixtures/red-ancestry/**",
+    "tools/policy/fixtures/required-contexts.json",
     "tools/policy/policy_lint.mjs",
     "tools/policy/render_md.mjs",
     "tools/policy/role_pack.py",
@@ -4692,11 +4719,12 @@
     "tools/replay",
     "tools/site"
    ],
+   "index": true,
+   "objects": true,
    "git": [
     "?",
     "add",
     "archive",
-    "branch",
     "cat-file",
     "checkout",
     "clone",
@@ -4716,9 +4744,7 @@
     "rev-list",
     "show",
     "update-ref"
-   ],
-   "index": true,
-   "objects": true
+   ]
   },
   "probe-bridge": {
    "run_sha": "e800b265b68d9dcb6f4afbfbe05d49e2f3ebd3842b235ef2997e664d9434e7df",
@@ -5216,12 +5242,14 @@
   "roster-queue-runner": {
    "run_sha": "d5cd705b4d2a5ded00be29cdd0c36a43a31afc42011bdb9205b6cf665468041f",
    "files": [
+    "tests/layout.py",
     "tests/throwaway_git.py",
     "tools/audit/carry_audit.py",
     "tools/audit/seat/ref_privacy.py",
     "tools/audit/seat/roster_edit.py",
     "tools/audit/seat/roster_lib.py",
-    "tools/audit/seat/roster_queue.py"
+    "tools/audit/seat/roster_queue.py",
+    "tools/policy/budget_raise_gate.py"
    ],
    "probes": [
     ".",
@@ -5230,16 +5258,18 @@
     "refs",
     "tests",
     "tools",
-    "tools/audit"
+    "tools/audit",
+    "tools/policy"
    ],
    "dirs": [
     "tests",
     "tools/audit",
-    "tools/audit/seat"
+    "tools/audit/seat",
+    "tools/policy"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "roster-sync-reconciler": {
    "run_sha": "176c372108c490c2302baaa98ecc0a8a8317d1cd8e51f20abe4f257ad0ee74ea",
@@ -5485,10 +5515,13 @@
     "tools/audit/archscore/metrics",
     "tools/audit/seat",
     "tools/plan",
+    "tools/policy",
     "tools/policy/fixtures/policy-rot",
     "tools/policy/fixtures/policy-rot/prepr",
     "tools/release"
    ],
+   "index": true,
+   "objects": true,
    "git": [
     "?",
     "cat-file",
@@ -5498,9 +5531,7 @@
     "merge-base",
     "rev-list",
     "show"
-   ],
-   "index": true,
-   "objects": true
+   ]
   },
   "selftest-scope": {
    "run_sha": "f5ec792ec3efe1110346aa55286c78476472afa3a83a128272f5e87587085203",
@@ -5515,6 +5546,8 @@
    ],
    "probes": [
     ".",
+    ".github",
+    ".github/workflows",
     "tests",
     "tools",
     "tools/ci"
@@ -5522,9 +5555,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "selftest-scope-mutants": {
    "run_sha": "00b691b683d6ff8e9527d535aafec449ad59e72a20cd3c063182d4a30fb9af60",
@@ -5540,6 +5573,8 @@
    ],
    "probes": [
     ".",
+    ".github",
+    ".github/workflows",
     "strace",
     "tests",
     "tools",
@@ -5548,9 +5583,9 @@
    "dirs": [
     "tests"
    ],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "selftest-wiring": {
    "run_sha": "12270ecc61efdff0edc98cfa58e949ce640919b1af72f63631fb59c588cb8f86",
@@ -5670,6 +5705,7 @@
     "tools/audit/seat/selftest_wiring.py",
     "tools/audit/seat/shims/**",
     "tools/audit/seat/state_docs.py",
+    "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
     "tools/audit/seat/sweep_driver_selftest.py",
     "tools/audit/seat/sweep_gantt.py",
@@ -5802,9 +5838,9 @@
     "tools/replay",
     "tools/site"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "stamp-round-close-mutation": {
    "run_sha": "cbebd8930d74d0d4b42e51386b58cf9d8cef34662c52b45463b62d5588a7da88",
@@ -5827,6 +5863,7 @@
   "state-doc-writer": {
    "run_sha": "78e714c49c75381ec173e957096d960d7899d651c3167a99cbf70097d17ee208",
    "files": [
+    "tests/layout.py",
     "tests/throwaway_git.py",
     "tools/audit/carry_audit.py",
     "tools/audit/merge_throughput.py",
@@ -5845,6 +5882,7 @@
     "tools/audit/seat/topic_grammar.py",
     "tools/plan/durations.json",
     "tools/plan/replan.py",
+    "tools/policy/budget_raise_gate.py",
     "tools/release/stamp.py"
    ],
    "probes": [
@@ -5856,6 +5894,7 @@
     "tools",
     "tools/audit",
     "tools/plan",
+    "tools/policy",
     "tools/release"
    ],
    "dirs": [
@@ -5863,11 +5902,12 @@
     "tools/audit",
     "tools/audit/seat",
     "tools/plan",
+    "tools/policy",
     "tools/release"
    ],
-   "git": [],
    "index": false,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "superseded-run-canceller": {
    "run_sha": "9d9c67b9ee56ec126ff04839b0521157973902359bf2934fe831626812b75f5d",
@@ -6584,6 +6624,7 @@
     "tools/audit/seat/seat_venv.sh",
     "tools/audit/seat/selftest_wiring.py",
     "tools/audit/seat/state_docs.py",
+    "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/sweep_driver.py",
     "tools/audit/seat/sweep_driver_selftest.py",
     "tools/audit/seat/sweep_gantt.py",
@@ -6658,7 +6699,6 @@
    ],
    "probes": [
     "-",
-    "-c",
     ".",
     "config",
     "objects",
@@ -6692,9 +6732,9 @@
    "dirs": [
     "tools/audit/seat"
    ],
-   "git": [],
    "index": true,
-   "objects": false
+   "objects": false,
+   "git": []
   },
   "verdict-bus": {
    "run_sha": "a781e6b79a8ef1a37712210f6277a5db65f5e0347994818965eac6f5d54e737d",
@@ -6708,6 +6748,7 @@
     "tests/card_drift.mjs",
     "tests/closures.json",
     "tests/layout.json",
+    "tests/mutation_table.py",
     "tests/structure_budgets.json",
     "tests/throwaway_git.py",
     "tests/throwaway_git.sh",
@@ -6740,6 +6781,7 @@
     "tools/audit/seat/review_packet.py",
     "tools/audit/seat/roster_lib.py",
     "tools/audit/seat/seat_venv.sh",
+    "tools/audit/seat/survivor_list.py",
     "tools/audit/seat/tick_loop.sh",
     "tools/audit/seat/train.sh",
     "tools/audit/seat/update_pr.sh",
@@ -6782,13 +6824,13 @@
     "tests",
     "tools/audit/seat"
    ],
+   "index": true,
+   "objects": true,
    "git": [
     "ls-tree",
     "merge-base",
     "show"
-   ],
-   "index": true,
-   "objects": true
+   ]
   }
  }
 }
diff --git a/tools/ci/selftest_scope.py b/tools/ci/selftest_scope.py
index 99a69b914d..124ce4bbd2 100644
--- a/tools/ci/selftest_scope.py
+++ b/tools/ci/selftest_scope.py
@@ -6,7 +6,8 @@
     python3 -I tools/ci/selftest_scope.py ids
     python3 -I tools/ci/selftest_scope.py record [--step ID]... [--out PATH]
     python3 -I tools/ci/selftest_scope.py check --traces DIR [--write PATH]
-    python3 -I tools/ci/selftest_scope.py --self-test
+    python3 -I tools/ci/selftest_scope.py settle
+    python3 -I tools/ci/selftest_scope.py --self-test [--wrapper PATH] [--workflow PATH]
 
 WHY (R10-CI-SELFTEST-SCOPE, owner lever 3, #201 comment 6707834331).
 `tools/` is INERT in tests/closure.py, so no tool has a closure there and this
@@ -48,6 +49,10 @@ entry. Over-approximation (an entry naming a file no longer read) is safe
 and is reported, not refused. `--write` saves the run's own measurement,
 which main uploads as the `selftest-closures` artifact: commit that file, or
 re-record with `record` (Linux, strace).
+THE SETTLED INDEX, `settle`, runs untraced before any step is (CI's strace
+step; `record` itself): a fresh checkout leaves racily clean index entries,
+whose content the first index-refreshing git command re-reads, so without it
+those reads land in whichever traced step refreshes first.
 
 BLIND SPOTS, stated: a path a process named relative to a working directory
 the trace does not decorate (a non-*at syscall after a chdir) is resolved
@@ -196,6 +201,22 @@ def wiring_gaps(steps: list[Step]) -> list[str]:
     return gaps
 
 
+SETTLE_CALL = re.compile(r"^python3 -I tools/ci/selftest_scope\.py settle$", re.M)
+
+
+def settle_gaps(steps: list[Step]) -> list[str]:
+    """CI's half of the settled index (R10-HOTFIX-PREPR-READSET): an untraced
+    step ordered before the job's first traced one (a gated step, or `launch`,
+    which starts traced ones) runs `settle` as a line of its own, so a failure
+    fails the step. `record` settles itself; on a pull request the step never
+    runs, so this static read is the only pin on the line."""
+    first = next((i for i, s in enumerate(steps) if s.gated or s.id == "launch"), len(steps))
+    if any(s.id in UNGATED and SETTLE_CALL.search(s.run or "") for s in steps[:first]):
+        return []
+    return ["UNSETTLED job: no untraced step before its first traced one runs "
+            "`python3 -I tools/ci/selftest_scope.py settle` on a line of its own"]
+
+
 # ---------------------------------------------------------------------------
 # the table
 
@@ -621,10 +642,68 @@ def drift(table: dict | None, measured: dict[str, dict], steps: list[Step]) -> t
 # ---------------------------------------------------------------------------
 # recording: the job, replayed through the same wrapper CI uses
 
+def _index_path(root: Path, env: dict | None = None) -> Path:
+    out = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-path", "index"],
+                         cwd=root, env=env, capture_output=True, text=True).stdout.strip()
+    return Path(out) if out else root / ".git" / "index"
+
+
+def racy_entries(root: Path, env: dict | None = None) -> list[str]:
+    """Tracked files whose mtime second is not before the index's own: git
+    cannot vouch for them from stat data, so the next index-refreshing
+    command (`git status`, `git diff`) opens and hashes each one. The second
+    is the coarser of git's two racy tests (with and without USE_NSEC)."""
+    try:
+        stamp = int(_index_path(root, env).stat().st_mtime)
+    except OSError:
+        return []
+    listed = subprocess.run(["git", "ls-files", "-z"], cwd=root, env=env,
+                            capture_output=True, text=True).stdout.split("\0")
+    racy = []
+    for rel in filter(None, listed):
+        with contextlib.suppress(OSError):
+            if int((root / rel).lstat().st_mtime) >= stamp:
+                racy.append(rel)
+    return sorted(racy)
+
+
+def settle_index(root: Path, env: dict | None = None) -> int:
+    """Rewrite the index in a second later than every tracked file's mtime,
+    so no entry is racily clean when a traced step starts. Without it the
+    content reads of a fresh checkout's last-written files fall to whichever
+    traced process first refreshes the index -- a read set that moves with
+    scheduling, not with the tree (R10-HOTFIX-PREPR-READSET)."""
+    racy = racy_entries(root, env)
+    if not racy:
+        return 0
+    newest = max(int((root / r).lstat().st_mtime) for r in racy if (root / r).exists())
+    if newest > time.time() + 5:
+        print(f"selftest_scope: settle: {racy[0]} is stamped in the future, so no index can vouch for it",
+              file=sys.stderr)
+        return 1
+    # File and index stamps come from the kernel's coarse clock, which lags
+    # time.time() by up to a tick: a rewrite just past the second boundary
+    # can still be stamped in the old second, so wait past it and retry.
+    for _ in range(3):
+        while time.time() < newest + 1.1:
+            time.sleep(0.05)
+        subprocess.run(["git", "update-index", "-q", "--really-refresh", "--force-write-index"],
+                       cwd=root, env=env, capture_output=True)
+        left = racy_entries(root, env)
+        if not left:
+            return 0
+        newest = max(int((root / r).lstat().st_mtime) for r in left if (root / r).exists())
+    print(f"selftest_scope: settle left {len(left)} racily clean index entr(ies), e.g. {left[0]}",
+          file=sys.stderr)
+    return 1
+
+
 def record(root: Path, only: list[str] | None, out: Path) -> int:
     if shutil.which("strace") is None:
         print("selftest_scope: record needs strace (Linux)", file=sys.stderr)
         return 2
+    if settle_index(root):
+        return 1
     steps = workflow_steps(root)
     gaps = wiring_gaps(steps)
     if gaps:
@@ -726,7 +805,7 @@ def static_check(root: Path = ROOT) -> int:
     """The pull-request side: the job's gating is consistent and the table is
     not stale against it. No tracing; the drift check is main's."""
     steps = workflow_steps(root)
-    problems = wiring_gaps(steps)
+    problems = wiring_gaps(steps) + settle_gaps(steps)
     table = load_table(root / TABLE)
     if table is None:
         problems.append(f"UNREADABLE {TABLE}")
@@ -743,9 +822,10 @@ def static_check(root: Path = ROOT) -> int:
 
 # ---------------------------------------------------------------------------
 
-def self_test(wrapper: Path = ROOT / WRAPPER) -> int:
-    """The refusals, over fixtures; `wrapper` is the selftest_step.sh under
-    test (selftest_scope_mutants.sh hands it a mutant)."""
+def self_test(wrapper: Path = ROOT / WRAPPER, workflow: Path = ROOT / WORKFLOW) -> int:
+    """The refusals, over fixtures; `wrapper` is the selftest_step.sh and
+    `workflow` the live job's file under test (selftest_scope_mutants.sh hands
+    either a mutant)."""
     passed = failed = 0
 
     def ck(name: str, ok: bool) -> None:
@@ -1116,6 +1196,9 @@ def self_test(wrapper: Path = ROOT / WRAPPER) -> int:
         if shutil.which("strace") is None or _traced():
             print("  skip the recorder end to end: no strace here, or this run is itself traced")
         else:
+            ns = _index_path(root).stat().st_mtime_ns
+            os.utime(root / "tools/x/a.py", ns=(ns, ns))
+            racy_before = racy_entries(root)
             out = io.StringIO()
             scratch, tempfile.tempdir = tempfile.tempdir, str(root.parent / f"{root.name}-tmp")
             os.makedirs(tempfile.tempdir)
@@ -1136,6 +1219,8 @@ def self_test(wrapper: Path = ROOT / WRAPPER) -> int:
             ck("record: a detached self-test's reads are its waiter's",
                "tools/x/slow.sh" in slow_e.get("files", ()) and "tools/x/slow.sh" not in a_e.get("files", ()))
             ck("record: it leaves no trace directory behind", left == [])
+            ck("record: it settles a racy index before tracing (racy before, none after)",
+               "tools/x/a.py" in racy_before and racy_entries(root) == [])
             part = root / "part.json"
             part.write_text(json.dumps({"steps": {"slow": {"run_sha": "old", "files": [], "probes": [],
                                                            "dirs": [], "index": False, "objects": False}}}))
@@ -1252,13 +1337,22 @@ def self_test(wrapper: Path = ROOT / WRAPPER) -> int:
            rc_bad == 1 and "UNDER-SCOPED step slow: files misses ['docs/d.md']" in out.getvalue()
            and ", 1 refusal(s)" in out.getvalue())
         out = io.StringIO()
+        with contextlib.redirect_stdout(out):
+            rc_us = main(["static"], root)
+        ck("static: a job that never settles the index is refused (UNSETTLED)",
+           rc_us == 1 and "UNSETTLED job" in out.getvalue())
+        settled = e2e.replace("      - name: Launch\n", "      - name: Strace\n        id: strace\n"
+                              "        run: python3 -I tools/ci/selftest_scope.py settle\n"
+                              "      - name: Launch\n", 1)
+        (root / WORKFLOW).write_text(settled)
+        out = io.StringIO()
         with contextlib.redirect_stdout(out):
             rcs = [main(["static"], root), main(["ids"], root),
                    main(["select", "--change", "M:tools/x/a.py"], root)]
         ck("static, ids and select over a fresh table",
            rcs == [0, 0, 0] and "0 problem(s)" in out.getvalue() and "a slow\n" in out.getvalue()
            and "MODE: SCOPED -- 1 step(s) run\n  run a\n" in out.getvalue())
-        (root / WORKFLOW).write_text(e2e.replace("cat tools/x/a.py", "cat tools/x/a.py tools/x/a.py"))
+        (root / WORKFLOW).write_text(settled.replace("cat tools/x/a.py", "cat tools/x/a.py tools/x/a.py"))
         out = io.StringIO()
         with contextlib.redirect_stdout(out):
             rc_st = main(["static"], root)
@@ -1312,6 +1406,75 @@ def self_test(wrapper: Path = ROOT / WRAPPER) -> int:
         m = re.search(r'^UNTRACED="([^"]*)"$', wrapper.read_text(), re.M)
         ck("wrapper: its UNTRACED list is UNGATED", bool(m) and sorted(m.group(1).split()) == sorted(UNGATED))
 
+    # A racily clean index (R10-HOTFIX-PREPR-READSET): entries whose file
+    # mtime second is not before the index's, which a fresh checkout leaves
+    # for the files it wrote last. The first index-refreshing git command
+    # re-reads each one's content, so those reads land in whichever traced
+    # step runs it first (main run 42780661829: prepr's `git status`).
+    # `settle` clears them before any step is traced; a racy fixture is its
+    # control.
+    with tempfile.TemporaryDirectory() as td, throwaway_git_environ():
+        root = Path(os.path.realpath(td))
+        env = throwaway_git_init(root, "-q")
+        names = [f"docs/f{n}.md" for n in range(3)]
+        for rel in names:
+            (root / rel).parent.mkdir(parents=True, exist_ok=True)
+            (root / rel).write_text(f"{rel}\n")
+        subprocess.run(["git", "add", "-A"], cwd=root, env=env, check=True)
+
+        def make_racy() -> None:   # every file stamped with the index's own mtime
+            ns = _index_path(root, env).stat().st_mtime_ns
+            for rel in names:
+                os.utime(root / rel, ns=(ns, ns))
+        make_racy()
+        ck("racy_entries: files stamped in the index's own second are named (the control)",
+           racy_entries(root, env) == names)
+        traced_status = shutil.which("strace") is not None and not _traced()
+
+        def status_reads() -> set[str]:
+            log = root.parent / f"{root.name}-status.trace"
+            subprocess.run(["strace", "-f", "-q", "-y", "-e", "trace=%file", "-o", str(log),
+                            "git", "status", "--porcelain"], cwd=root, env=env, capture_output=True)
+            got = fold_trace(log.read_text().splitlines(), root, set(names), {"docs"}, *_git_dirs(root))
+            log.unlink()
+            return got["files"]
+        if traced_status:
+            make_racy()
+            ck("a git status over that racy index opens every racy file (the control)",
+               status_reads() == set(names))
+            make_racy()
+        rc = settle_index(root, env)
+        ck(f"settle: no index entry is left racily clean (rc={rc})", rc == 0 and racy_entries(root, env) == [])
+        if traced_status:
+            ck("and a git status after it opens no tracked file", status_reads() == set())
+        else:
+            print("  skip the traced git status over a racy index: no strace here, or this run is itself traced")
+        ck("settle over an index with no racy entry changes nothing (rc 0)", settle_index(root, env) == 0)
+        make_racy()
+        rc = main(["settle"], root)
+        ck(f"the `settle` command settles that racy index (rc={rc}; racy before it, none after)",
+           rc == 0 and racy_entries(root, env) == [])
+
+    # The settle call's place in a job (settle_gaps): an untraced step before
+    # the first traced one, on a line of its own; the null control first.
+    gate = "steps.scope.outputs.a == 'true'"
+    call = "python3 -I tools/ci/selftest_scope.py settle\n"
+
+    def job(strace_run: str, a_first: bool = False, after: str = "") -> list[Step]:
+        a = Step("A", "a", gate, "x\n" + (call if a_first else ""))
+        head = [Step("Choose", "scope", "", "echo\n"), Step("Strace", "strace", "", strace_run)]
+        return head + ([a] if a_first else []) + [Step("Launch", "launch", "", "x\n" + after)] + \
+            ([] if a_first else [a])
+    ck("settle_gaps: an untraced step before the first traced one settling passes (null control)",
+       settle_gaps(job("apt\n" + call)) == [])
+    ck("settle_gaps: no settle call is refused", settle_gaps(job("apt\n")) != [])
+    ck("settle_gaps: a settle whose failure is swallowed is refused",
+       settle_gaps(job("apt\n" + call.replace("\n", " || true\n"))) != [])
+    ck("settle_gaps: a settle only in a traced (gated) step is refused",
+       settle_gaps(job("apt\n", a_first=True)) != [])
+    ck("settle_gaps: a settle only in launch, which starts traced steps, is refused",
+       settle_gaps(job("apt\n", after=call)) != [])
+
     # The live table names no landed retired path (tests/layout.py's guard
     # refuses a new reference to one, and a diff re-adding one), and the
     # list it is checked against is not empty (the check's own precondition).
@@ -1326,23 +1489,27 @@ def self_test(wrapper: Path = ROOT / WRAPPER) -> int:
            bool(gone) and named == [] and retired_paths(Path(tempfile.gettempdir())) == [])
 
     # The live job: its gating is consistent (the seat's own null control).
-    live = workflow_steps(ROOT)
+    live = job_steps(workflow.read_text())
     ck(f"the live job parses ({len(live)} steps) and its gating is consistent",
        len(live) > 3 and wiring_gaps(live) == [])
+    ck("the live job settles the index in an untraced step before its first traced one",
+       settle_gaps(live) == [])
     print(f"selftest_scope self-test: {passed + failed} checks, {failed} failed")
     return 1 if failed else 0
 
 
 def main(argv: list[str], root: Path = ROOT) -> int:
-    if argv == ["--self-test"]:
-        return self_test()
-    if argv[:2] == ["--self-test", "--wrapper"] and len(argv) == 3:
-        return self_test(Path(argv[2]).resolve())
+    opts = dict(zip(argv[1::2], argv[2::2]))
+    if argv[:1] == ["--self-test"] and len(argv) % 2 == 1 and set(opts) <= {"--wrapper", "--workflow"}:
+        return self_test(Path(opts.get("--wrapper", ROOT / WRAPPER)).resolve(),
+                         Path(opts.get("--workflow", ROOT / WORKFLOW)).resolve())
     if argv == ["ids"]:
         print(" ".join(gated_ids(workflow_steps(root))))
         return 0
     if argv == ["static"]:
         return static_check(root)
+    if argv == ["settle"]:
+        return settle_index(root)
     if argv[:1] == ["select"] and ("--base" in argv or "--change" in argv):
         steps = workflow_steps(root)
         if "--change" in argv:          # a hypothetical diff: STATUS:PATH ...
diff --git a/tools/ci/selftest_scope_mutants.sh b/tools/ci/selftest_scope_mutants.sh
index 6fdc634ba6..7d2ff3123d 100644
--- a/tools/ci/selftest_scope_mutants.sh
+++ b/tools/ci/selftest_scope_mutants.sh
@@ -10,6 +10,7 @@
 set -u
 src=tools/ci/selftest_scope.py
 wrapper=tools/ci/selftest_step.sh
+workflow=.github/workflows/governance.yml
 tmp=$(mktemp -d)
 trap 'rm -rf "$tmp"' EXIT
 python3 -I "$src" --self-test > /dev/null || { echo "BASELINE RED: the unmutated self-test fails"; exit 1; }
@@ -33,12 +34,23 @@ wrapper_mutant() { # <label> <old> <new>
   out=$(python3 -I "$src" --self-test --wrapper "$tmp/step.sh" 2>&1); rc=$?
   report "$1" "$rc" "$out"
 }
+workflow_mutant() { # <label> <old> <new>
+  apply "$workflow" "$2" "$3" "$tmp/wf.yml" || { echo "MUTANT NOT APPLIED: $1"; exit 1; }
+  out=$(python3 -I "$src" --self-test --workflow "$tmp/wf.yml" 2>&1); rc=$?
+  report "$1" "$rc" "$out"
+}
 scope_mutant "a missing bg trace skipped" 'broken.append(f"MISSING trace' 'None and broken.append(f"MISSING trace'
 scope_mutant "an empty trace read whole" 'return "EMPTY"' 'return ""'
 scope_mutant "a partial trace read whole" 'return "" if seen["root"] in seen["ended"] else "PARTIAL"' 'return ""'
 scope_mutant "a signal death read as partial" '(?:exited with|killed by) ' '(?:exited with) '
 scope_mutant "check drops the trace refusals" 'refuse = broken + refuse' 'refuse = refuse'
 scope_mutant "record passes over a broken trace" 'return 1 if failed or broken else 0' 'return 1 if failed else 0'
+scope_mutant "settle never rewrites the index" '["git", "update-index", "-q", "--really-refresh", "--force-write-index"]' '["true"]'
+scope_mutant "the settle command a no-op" 'return settle_index(root)' 'return 0'
+scope_mutant "settle_gaps reads no job" 'if any(s.id in UNGATED and SETTLE_CALL.search' 'if True or any(s.id in UNGATED and SETTLE_CALL.search'
+scope_mutant "static skips the settle check" 'problems = wiring_gaps(steps) + settle_gaps(steps)' 'problems = wiring_gaps(steps)'
+workflow_mutant "CI never settles the index" 'python3 -I tools/ci/selftest_scope.py settle' 'true'
+workflow_mutant "CI swallows a failed settle" 'python3 -I tools/ci/selftest_scope.py settle' 'python3 -I tools/ci/selftest_scope.py settle || true'
 wrapper_mutant "only launch untraced (the incident's wrapper)" 'case "$UNTRACED" in *" ${GITHUB_ACTION:-} "*)' 'case " launch " in *" ${GITHUB_ACTION:-} "*)'
 wrapper_mutant "no strace exec'd anyway" 'if ! command -v strace > /dev/null 2>&1; then' 'if false; then'
 wrapper_mutant "exit lines suppressed (-qq)" 'exec strace -f -q -y' 'exec strace -f -qq -y'

## Before you return the verdict (P275)
Run `python3 -I tools/audit/carry_audit.py check --body <PR body file> --comments <file holding [{"id": 0, "body": <verdict.md text>}]>`. Give every reported item its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>`;
an evidence line flagged by its wording takes `Carry: dismissed: evidence, not a finding`. Return the verdict only at rc 0.
