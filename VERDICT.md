Fix review: merge aea79fa6b388ca546f69fdcac5ec0a006aac05dd

bus-nonce: 750a33ff5dcc1fc787832fb7a32d8be2

Round 1. The measured head is `aea79fa6b...`: `af03a14e` (the fix) plus the orchestrator's recarry of `origin/main` `e2a47458f` plus `record: the delivery row for #2514`, whose only content is `dev/programme/delivery/2514.md`. All figures below were taken at `f0b1844b`; the same `--series`, job-log and null-control runs stand, and the delta re-run at this head is stated where it applies.

## The block and its closure

Round 1 blocked `harness: class-open tests/replay.py:377`: the invariance claim the PR exists to correct survived unchanged 25 lines below the correction ("... invariant across runners"). `af03a14e` is comment-only and says "cancels MOST of the interpreter factor, not all of it: the ratio keeps a residual runner-class spread, so it is bounded, not invariant, across runners". No figure added. The enumeration `git grep -n "invariant across runners" -- tests dev/audit/harnesses docs dev/programme` returns nothing at this head. The body's `## Head` names the commit and records the closure. Closed.

## Verified

1. Series derivation, re-derived from live GitHub rows: `RESULT series_rows=22 api_failures=0 no_slow_lane=0 no_logs=0 off_main=58`, `RESULT era_rows pre=17 post=5`, `RESULT old_pre_spread=min0.2441_max0.4050_factor1.659`, `RESULT new_post_spread=min0.0868_max0.1114_factor1.283 median=0.0877`, `RESULT old_post_spread=min0.2599_max0.4190_factor1.612`, `RESULT corr_new_post_ref_ms=-0.616 n=5`. One row per era re-read from its own job log, and all five post rows: 2026-10-15 run 38699166296 (0.2452, ref_ms 54.81, no loop_ref_ms, pre era); 2026-10-17 run 39011974246 (0.0868 / 161.10 / 13.98 ms); 2026-10-18 run 39106988523 (0.0875 / 127.94 / 11.19); 2026-10-19 run 39218718759 (0.0877 / 161.39 / 14.15); 2026-10-19 dispatch 39256093598 (0.0982 / 157.17 / 15.43); 2026-10-20 run 39387919507 (0.1114 / 84.05 / 9.36). Re-record arithmetic re-done: sqrt(2) x 0.0877 = 0.124, sqrt(2) x 0.1114 = 0.1575, floors 0.062 and 0.0788, 0.32 % under 0.0618, 1.27 x 0.0701 = 0.089.
2. Mutation proof: `RESULT self_test checks=7 failed=0`; the body's mutation (`loop_cpu_ms / row["ref_ms"]` -> `loop_cpu_ms / row["loop_ref_ms"]`) gives `FAIL: post: the old figure is derived`, `RESULT self_test checks=7 failed=1`. The era key is sound: 9d20cc2d6 changed the denominator and added `loop_ref_ms` in one commit.
3. Null control, my own interleaved run (git archive exports of c35302773 and 0c298f6b5, six each): `RESULT arm=c3530277 n=6 min=0.0739 max=0.1046 median=0.0859 spread=1.415`, `RESULT arm=0c298f6b n=6 min=0.0717 max=0.1060 median=0.0838 spread=1.478`, `RESULT paired_median_ratio=0.9756`. The later head reads 2.4 % lower, not +27 %: flat.
4. Red-check claim: all 17 required contexts of ruleset 23698884 concluded green at this head. `nightly-status` is red, is not among them, and is main's own red (run 39387919507, `event=schedule`, `head_branch=main`, `head_sha=0c298f6b`), whose slow job ends `FAIL synthetic-dhw-only.json: cycle_cost [loop_cpu_ratio 0.1114 over its budget 0.111]` with the doubled arm at 0.2616 / injected_ratio 1.0001. The diff touches no `COST_BUDGETS` line (block byte-identical to 4e5801eb5) and no `.github/workflows/` file.
5. Owner boundary: the branch's own diff is `dev/audit/harnesses/r10_replay_loopnorm.py` and `tests/replay.py`; zero `.github/workflows/` paths; the cap re-record is unperformed. CODEOWNERS carries no `tests/replay.py` entry.
6. Carries, re-run at this head: `CARRY-AUDIT: 7 finding item(s): 7 routed, 0 unrouted, 0 bad destination(s)`; #2272 OPEN. Items are real: `tests/replay/` holds only `synthetic-dhw-only.json`; the fixture would owe the `tests/entities.py` and `tests/features.py` closure sets (both list it today) and a `COST_BUDGETS` row; #2271 is OPEN and `replay_doc.py:497-510` raises the named refusal; the D14-s3 re-run is in the roster carry.
7. Structure and gate, re-run at this head: `STRUCTURE RATCHET PASSED`, every metric equal to its budget; `MODE: SCOPED -- 3 script(s) run, 30 scoped out` (tests/debug_collect.py, tests/entities.py, tests/features.py) at merge-base `e2a47458f`; the delivery row is inert (`dev/programme/` is on `INERT`); `figure_lint --pr-body` `FIGURES: 10 resolved, 2 not verified, 0 refused`; `git merge-tree --write-tree origin/main aea79fa6` clean (exit 0).

## For the record

The push-time `prepr` skipped its closures step under `PREPR_SKIP_CLOSURES=1` (the owner's ruling, `gate-scoping.md`), so the re-recording is CI's: the `closures` context concluded `success` at this head and is the covering check. This diff adds no read.

## What I could not establish

- The body's local null-control figures (medians 0.0711/0.0701, maxima 0.081/0.0719) did not reproduce: this box ran at load1 51.3-202.3, not 15-29, and my medians were 0.0859/0.0838, maxima 0.1046/0.1060, per-run spread 1.41/1.48. The paired ratio 0.976 is the arm that carries the claim and it confirms it. Carry: dismissed: the pairing is the control and it holds; the absolute level is the box's.
- The twelve-run local figure 0.0618 the floor argument rests on is not recorded in the tree; the arithmetic is re-done, the runs are not re-derivable. Carry: #2272
- The owner's 2026-10-19 diagnostics reading (2 dropped credential values) is not reproducible from this box; the refusal mechanism is. Carry: #2272
- The self-test pins `figures()`, not `series_report`'s pre/post partition; the partition is exercised only by `--series`, reproduced exactly against six job logs. Carry: dismissed: empirical reproduction stands in for the pin; not a claim the body makes.
