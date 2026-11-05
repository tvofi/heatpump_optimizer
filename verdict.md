Fix review: blocked 5ee2be2db0abefd7988a4465b4f431334925895e carry-missing: the gate-lease _free_slot is_file TOCTOU the body leaves open is in no roster carry, and three concluded reds are unnamed in Red checks

bus-nonce: b75283b556476b0f0589bcecef7b7c96

## Head

I measured 5ee2be2db0abefd7988a4465b4f431334925895e, the head the dispatch names and the head `## Head` names. `git ls-remote origin refs/pull/3170/head` re-read the same head at the end of the review.

- Merge base: 6777ec33337b256d29ea145d98da413dbf076a2a. origin/main was at dad3178d6 when I read it.
- This is round 4, the final round the owner's mandate allows. It is a delta review over the round-2 block at 0a459e60.
- Contract currency: `git diff <mb>...origin/main -- dev/governance/roles/` touches only proposal-triage.md, so fix-review.md is current.
- I judged the change only through the three-dot diff. Since 0a459e60, the PR's own patch changed in nightly.yml, host_zone_features.py, card.mjs, finite_boundary.py, golden.py, guard_pins.py and ha_contract.py. Its patch to coordinator.py, entities.py, features.py, gate_lock.py, coverage_tree.sh, closures.json and the delivery row is byte-identical to round 2's.

## Block

1. **carry-missing: the gate-lease `_free_slot` TOCTOU is not carried to any stage.**
   - The body's carries list says of Carry 2 (0-based 1): "The `_free_slot` is_file TOCTOU in `tests/gate_lock.py` is NOT built here and stays open in this carry (Forward-carry)". But `## Forward-carry` reads "none".
   - The roster carry it points to has no such text. That carry is origin/handoff/audit-r10-roster 56c3ebcd8, dev/programme/rosters/wave-r10-groups.json, R10-SUITE-HOST-DETERMINISM `carry`[1], line 14857. It says only "Make the check deterministic (wait on a condition, never a fixed window), then re-measure the pair of runs".
   - None of `_free_slot`, `TOCTOU` or `is_file` appears anywhere in dev/programme on that ref. On origin/main, `_free_slot` appears only in dev/audit/rca/R10-RCA-GATE-LEASE-FLAKE.md. That RCA is about the earlier torn-create seam, which fab4a07c1 fixed, not about this one.
   - The finding is live at this head. tests/gate_lock.py is untouched since round 1. With a delay-only plant (a 30 ms sleep after `_read_at` returns None for a slot path, and no logic changed), `one_winner` reads red **8 of 10** (ev/gl_head_toctou.txt). The PR's test-side condition wait makes the check see the overlap more reliably. It does not remove the production race behind the flake carry [1] exists for.
   - So once this merges, the cause and its control exist only in verdict refs and this PR's text. That is the case rule 10 blocks on.
   - To settle it, write the TOCTOU into the group's roster carry (or a named next part), with the delay-only plant (ev/gl_toctou.py) as its precondition control: the fix must turn it green. Then name that roster SHA in `## Forward-carry`. Alternatively, build the fix in `_free_slot`.
2. **root-cause-unanswered: three concluded reds at this head are unnamed in `## Red checks`.** `pr-contract` refuses on all three in every run since. The latest is 127129922291, which started after the last red concluded.
   - `governance / policy-docs` (127109349298): `machinery_ratchet: dev/governance/config/machinery_budgets.json is absent at 5ee2be2d...` (exit 2). The file is absent at the head and at the merge base 6777ec33, and present on origin/main. This looks inherited from main's newer machinery ratchet, red on any head whose base predates it. The body owes that answer, naming base 6777ec33 and the check.
   - `governance / delivery-status` (127109349630): `DELIVERY STATUS OVERDUE — 10 rowed, 10 pending, 10 overdue`. pr-contract says the diff touches what it reads (.github/workflows/nightly.yml), so the body must name it and answer it.
   - `tests / nightly-status` (127109349506): `NIGHTLY FAILED: slow failed last night`. The diff adds a step to that very `slow` job, so the body must answer whether the red is this PR's own.
   - `merge_train.py classify` printed `RED 5ee2be2d... pending: none red: gate` (rc=1). This is not APPROVAL-OWED. The body's `## Red checks` covers only 0a459e60's replay red, and says this head "has no CI yet".

   I cannot tell for each red whether a cheaper detector existed, because main moved after prepr.sh ran on 04dc6057. So the class is `unanswered`, not `detectable`.

The host-zone class itself is closed at this head (Evidence). If the orchestrator splits the group, the host-zone part is the mergeable one. The `_free_slot` race needs its own part, and the reds need a body answer.

## Findings

- Gate-lease `_free_slot` is_file TOCTOU (tests/gate_lock.py, unchanged by this PR) is still live at the head: delay-only plant 8 of 10 red. It is in no roster carry and no `## Forward-carry` (Block 1). Write it into R10-SUITE-HOST-DETERMINISM's carry with ev/gl_toctou.py as its precondition control, or build it. Carry: R10-SUITE-HOST-DETERMINISM
- Three concluded reds at the head are unnamed in `## Red checks`, and pr-contract refuses on them (Block 2). policy-docs (machinery_budgets.json absent at base 6777ec33, present on main) looks inherited. delivery-status and nightly-status each need an answer because the diff touches nightly.yml. Carry: R10-SUITE-HOST-DETERMINISM

## Evidence

- RESULT host-zone class at the head. My own runner is ev/runz.sh, which sets `HASTUB_TZ` and `TZ` to the zone with `PYTHONPATH=tests/hastub`. It is the reviewer's, not the fixer's harness.

  | zone | tests/features.py | tests/finite_boundary.py |
  |---|---|---|
  | UTC | ALL 4800 passed (rc 0) | ALL 108 passed (rc 0) |
  | Europe/Stockholm | ALL 4800 passed | ALL 108 passed |
  | America/New_York | ALL 4800 passed | ALL 108 passed |
  | Asia/Tokyo | ALL 4800 passed | ALL 108 passed |
  | Asia/Kolkata | ALL 4800 passed | ALL 108 passed |

  The rows are in ev/head_*.summary.txt. Round 2's block (finite_boundary New_York 1 of 108 and Kolkata 2 of 108) is settled. The body's 4800 per zone re-derives exactly.
- RESULT null controls, one planted host-zone dependence per script, each run under the same five zones (ev/mutant_*.diff, ev/mut_*.summary.txt):
  - `fb_leaf` (the harness's finite_boundary_leaf_zone: naive leaves read as UTC): New_York 2 of 108, Tokyo 1, Stockholm 1, Kolkata 1, UTC ALL 108. **KILLED.** This matches the body's figures.
  - My own writer-side plant (ev/mutant_fb_naive_t0.diff; the name is historical): `_with_instants` writes naive leaves as UTC wall time. New_York 2 of 108, and Stockholm, Tokyo, Kolkata and UTC ALL 108. **KILLED**, though only by New_York. The arm detects this plant where the zone's offset pushes an instant past a lead, and nowhere else. I note this; it does not block.
  - `feat_humidity` (the harness's humidity_now): New_York, Tokyo and Kolkata 1 of 4800, Stockholm and UTC ALL 4800. **KILLED.** This matches the body.
- RESULT gate-lease (carry [1]):
  - The planted torn-create control still reads red at the head: 3 of 20 (ev/gl.py, ev/gl_head_planted.txt).
  - The production TOCTOU is still live (Block 1).
- RESULT coverage descendants (carry [2]), using ev/crv.py (round 1's reviewer harness), which runs the head's `_coverage_revalidation` against a tree's coverage_tree.sh:
  - At the head, a late writer is waited for: `entities` is not `nodata`. Bound 0 refuses, naming the script (ev/crv_head.txt).
  - Mutant with the `wait_descendants "$s" || return 1` line deleted (ev/mutant_cov.diff): late reads `entities.nodata`, and bound 0 does not refuse (ev/crv_mutant_nowait.txt). So the entities check reads red. **KILLED.**
- The entities HEAD-vs-worktree row (carry [5]) and the base-red entities checks (carry [4]) are NEXT PART in the body and stay in the roster's carry list. Nothing in this diff builds them, so there is no control to run.
- RESULT diff read (round-4 changes):
  - finite_boundary's arm reads a naive leaf in the store's own `_naive_zone`, and in UTC when that is None. This matches store.py:163 (`naive_zone or bound.tzinfo`, where bound is `as_utc(now()) + lead`).
  - ha_contract constructs the unconfigured zone from a fresh copy of the provider's own util/dt module. It no longer asserts `HASTUB_TZ` unset.
  - golden pins `DEFAULT_TIME_ZONE = SCENARIO_ZONE (UTC)` only inside `capture_coordinator`, and restores it in `finally`.
  - guard_pins freezes an aware clock.
  - card.mjs's seam check runs on its own UTC-grid clock and restores `ctx.Date` in `finally`.
  - The diff adds no suite-wide TZ pin. The nightly step sets Kolkata on purpose.
- RESULT standing checks (ev/standing.txt):
  - Both claim files, VERSION, manifest.json and RELEASE_NOTES.md are unchanged in the three-dot diff, and the diff holds no `*_budgets.json`.
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (ev/structure_head.txt).
  - `GOLDEN_MODE=drift python3 tests/env_drift.py --all 6777ec33` in the gate environment: `NO UNCLAIMED DRIFT: 56`, `NO STALE FIXTURE: 56`, rc=0 (ev/env_drift_all_mb.txt).
- RESULT merge: `git merge-tree --write-tree origin/main 5ee2be2d` exits 0. Its only note is `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree.txt).
- RESULT CI: I read all 69 check runs at the head across both pages (ev/check_runs.tsv). The non-green runs are gate ×3, pr-contract ×3, delivery-status, nightly-status and policy-docs. The job logs are ev/job_*.log.gz.
- Figures I did not re-derive:
  - the `--suite` sweep's 38-command per-zone table (before at 1a148834, after at e581b01c);
  - the scratch-baseline env_drift runs under four zones;
  - the `--golden-zones` counts;
  - the six-zone mutant table beyond the three mutants above;
  - the Europe/London row.

  I did not run the 38-command sweep. The brief scoped the measurement to the host-time scripts, and the block does not turn on the sweep.
- Review packet: `review_packet.py render` returned `UNAVAILABLE: ... HTTP 503` twice. The PR body and checks were read live instead (MCP pull_request_read and the check-runs API).

## Friction

- The brief asks for handoff-wip pushes at milestones, but the payload says to push nothing except the probe ref. I followed the payload and pushed only probe/rev-3170-b75283b5. Carry: dismissed: a brief-wording conflict, resolved by the payload's own rule; no defect in the PR
- A frugal-routing hook refused routine status polls as "inline search" more than once. Waiting moved to background tasks; no check was skipped. Carry: dismissed: seat tooling friction, no defect in the PR
