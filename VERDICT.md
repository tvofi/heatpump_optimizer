Fix review: merge a0c4431df91e75b3c7ed4976586c0da86e292214

bus-nonce: d452d47f143d63d5746d0454cb2e5fa0
head-measured: a0c4431df91e75b3c7ed4976586c0da86e292214 (re-read at post time: `refs/pull/2336/head` and `refs/heads/fix/r10-feeds` both still this sha; the body edit moved no commit)
round: 2 (the first round returned `blocked ... harness:`; this verdict replaces it)
previous verdict: `review/2336` 819504e2b51437160b1536a7e5f151ee4c8a2f46 -- `blocked a0c4431df harness` on the enumerator's dead perturb arm

## The block is cleared

The block was: `dev/audit/rounds/round10/D14/sweep_n_no_expiry.py --perturb` no longer runs at this head because this diff removed its anchor line, and the body did not say so (`fix-review.md` step 2 / `fixer.md` step 3's "say so"). The new body (`handoff-body/r10-feeds` `c35ffce9ac118e86bb848d6a691761c1c131852a`, re-posted to the live PR, identical to it bar a trailing newline) discloses it. I re-derived every figure of the disclosure rather than taking it:

    anchor `grep -n "step_start >= end" custom_components/heatpump_optimizer/coordinator.py`
      8f174c4ce  :6726            if step_start >= end:
      e8718ec3b  :6726            if step_start >= end:
      a0c4431df  ABSENT

    arm at the base (git archive of 8f174c4ce), --perturb
      SEAM coordinator.py:_known_prices_for(perturbed):22 _known_prices_for UNBOUNDED
      RESULT seams=1 / RESULT unbounded=1        <- the 0 -> 1 perturbation the arm exists to show
    arm at the head, --null (its sibling, still applies)
      RESULT seams=1 / RESULT unbounded=0
    arm at the head, --perturb                  AssertionError: perturbation anchor missing

The class rule the disclosure names, run by this seat over the head and the merge base (`git show`, no worktree), reproduces its count and its membership exactly:

    RESULT multi-line-literal anchors handed to replace/find/index/split = 22 count
    RESULT alive in the head package       = 19 count
    RESULT dead at head, dead at base too  = 2 count
    RESULT dead at head, ALIVE at base     = 1 count
      KILLED BY THIS DIFF: dev/audit/rounds/round10/D14/sweep_n_no_expiry.py:69 .replace() '            if step_start >= end:\n                break\n'
      dead at both ends:   dev/audit/rounds/round10/D14/sweep-I1/enumerate_i1.py:108 .replace() '    if xs:\n'
      dead at both ends:   dev/audit/rounds/round10/intake/intake.py:398 .find() '\n## '

So the class the arm belongs to has one member, it is this one, the two other dead literals are dead at the base as well (not this diff's) and neither is production text. The disclosure states the arm is deliberately **not** re-anchored because `dev/audit/rounds/round10/D14/` is outside this group's architect note, and names the claim it carried as still pinned by `tests/entities.py`'s N-no-expiry arm at an exact count with its own planted-lookup perturbation — which the first round verified discriminating. That is `fixer.md` step 3's obligation discharged: the arm that cannot run is named, measured at both ends, and its replacement named. The file-scope decision the disclosure defers is the orchestrator's, and this verdict does not require it.

## Nothing else moved

The change is body-only: the code head is the same sha, so the tree is identical and every measurement of round 1 stands unchanged. A line-for-line diff of the body I reviewed against the live one is the two disclosure paragraphs and blank lines, nothing else — no figure, heading or claim altered. Re-checked at the head: `## Head` still names `a0c4431df`. A new `pr-contract` run started `18:33:48Z`, eight seconds after the body edit `18:33:40Z`, and concluded **success** at `18:34:12Z`, so step 11's gate is satisfied for the body as it now stands; the last check to conclude red on this head is still the `pr-contract` of `17:17:33Z`, eleven minutes before it.

## Carried forward from round 1 (all re-stated here; the evidence is under `evidence/`)

    finder harnesses, byte-identical at base, head and d23205d13, run at each end
      stale_price        uncovered_current_price_published 4 -> 0, uncovered_price_booked 4 -> 0, control_covered_published 2 -> 2
      tibber_ingress     empty_ok_wipes 1 -> 0, startless_rows 96 -> 0, misplaced_steps 95 -> 0
      weather_warn       no_entity 4 -> 1, empty_forecast 4 -> 1, control_48_rows 0 -> 0
      probe_n_no_expiry  probe_failures 2 -> 0, CONTROL covered forecast=-2.0 plan=49.5 at both ends
      weather_probe      empty_ok_wipes 1 -> 0
      probe_spot_head    spot_wrong 1 -> 0
      log_flood/probe    all 7 arms 1,1,1,2,2,1,1 -> 0, control.floods 0 -> 0
    mutation proof, all 12 named mutants killed by the checks the body names (M7/M8/M9 die as TypeErrors)
      M1 _covering_index end bound -> `return i` also drives the finder's harnesses: stale_price 0 -> 4 published, probe_n_no_expiry 0 -> 2
    class enumerators, at both ends
      sweep_n_no_expiry seams 9 -> 6, unbounded 6 -> 4 | sweep-N-silent-zero unguarded 2 -> 1
      p1_ts_seams seams_flagged 6 -> 3 | log_flood sites=85 latched=6 seams=79 -> sites=80 latched=6 seams=74
    barriers: allow-lists are the enumerators' own output (6 keys/6 sites and 63 keys/74 sites, zero set and count difference
      either way); red on the base package and green at the head; planted controls discriminate; ALL 2331 ENTITY CHECKS PASSED
    figures re-derived: 6133 candidate sites, 4368 unpinned, ledger completeness 7 -> 0, 39 loggers, 85/80 warn-error
      sites, searchsorted 2, bisect_left 0; STRUCTURE RATCHET PASSED with max_class_loc 8688 -> 8635 (down, re-recorded);
      archscore dS +0.0158 IMPROVES, coord_footprint 2575 -> 2547
    gate: ALL 4151 FEATURE CHECKS PASSED at the head, 632 s; claims hygiene ok; env_drift --all -> NO UNCLAIMED DRIFT: 56,
      NO STALE FIXTURE: 56, rc 0; VERSION 7.0.0, manifest and notes heading untouched; merge-tree rc 0, no conflicts
    red checks answered: mutation and pr-contract, both named in the body; the head's green mutation is not vacuous
      (7 mutants over 4 files, baselines rc=0, NULL_COMMENT survived, PIN RE-VERIFICATION 7 reproduced, MUTATION TABLE PASSED)
    forward-carry: the D1 step-3 edit is in R10-BRIEFS-FOLD's brief in dev/programme/rosters/wave-r10-groups.json, pending
      as the group's brief expects; both RCAs' countermeasures are built here
    head unchanged: refs/pull/2336/head and refs/heads/fix/r10-feeds both a0c4431df at post time

One figure disagrees with a second source and it is not the body's: the head's mutation-lane artifact prints `6134 candidate sites` where `inventory()` in this tree and the body both give 6133. Out of this PR's diff.
