# Round-2 evidence -- resolution delta -- PR #2129, head c565a0d5595b98eb862b1e43d1c930439f9d1fe1
Reviewer worktree at the head: /Users/timmalmstrom/hpo-seats/r9rev-2129/wt
Delta judged: 156fe40a1 (the throwaway_git repair) + merges with main tip a74520020 (#2121 content) + delivery row/merge commits.

## The repair commit 156fe40a1 (round-1 block, resolved)
tools/audit/seat/a1_dispatch_arms.sh only (+29/-15): the fixture repo now builds
through tests/throwaway_git.sh (throwaway_git_init / throwaway_git_clone, fixture
git calls under throwaway_git_env). Measured at effd8a95f (all six gate files
byte-identical between effd8a95f and c565a0d55: closure.py, derive_closures.sh,
a1_dispatch_arms.sh, entities.py, prepr.sh, tests.yml):
  python3 -I tests/throwaway_git.py --self-test -> 44 checks, 0 failed
  python3 -I tests/throwaway_git.py --check   -> 0 raw git init or clone site(s) refused, exit 0
  a1 arms re-run -> output byte-identical to the round-1 run (a1_arms_effd8a95.out vs a1_arms_head.out: diff empty; skip/scoped/full).

## Round-1 measurements that stand at this head
- closures/inert_reads tables byte-identical to round-1 head; the only tests/closures.json
  change in the delta is two recorded seconds refreshes from main's own re-record
  (features.py 730.5->288.5, config_flow_steps.py 38.0->15.2).
- All nine (a2) boundary probes re-run at the new head: unchanged
  (#2109 shape SCOPED, LICENSE SCOPED, docs/** SCOPED doc_claims, dev/governance
  + handoff/ + SECURITY.md + NOTICE SKIP, round20 SCOPED, custom_components 30-closure SCOPED).
- entities.py at the head: ALL 2260 PASSED (seat venv).
- (e) recording set (34 rec targets) and lane layout untouched by the delta.

## CI at the head (check-runs API, c565a0d5595b98eb862b1e43d1c930439f9d1fe1)
  instrument-self-tests  completed success  (round-1's block, green)
  pr-contract            completed success  (body names the reds)
  mutation, typing, briefs, policy-docs, delivery-status, nightly-status,
  budget-raise-gate, env-matrix, wave-script, closure-scope: success
  closures / coverage / fast (3.14) / browser: in progress at review time --
  the branch's own gate, merge_train waits on them; the closures full arm is
  itself the (e) acceptance instrument.
