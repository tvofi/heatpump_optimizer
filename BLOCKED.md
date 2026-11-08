# BLOCKED: r10-rca-gate-busy-defer-p5, the handoff body refused on two unlanded carries

The code head is complete and clean. It is `aca864bce91258fb85d14ae7eba75075132e13b5` on
`refs/heads/handoff/r10-rca-gate-busy-defer-p5`, where `tools/pr/prepr.sh` with the body gave
PRE-PR rc=0. origin/main is still `73365699a`, and `git merge-tree` reports no conflict.

`tools/audit/seat/body_push.sh r10-rca-gate-busy-defer-p5 <body>` refused the body, with
`CARRY-LANDED: 2 missing`:

- `CARRY-MISSING R10-HOTFIX-GATE-BUSY-DEFER body item 453f6578`: the settle loop on content reds,
  for the owner of `tools/ci/sweep.py`.
- `CARRY-MISSING R10-HOTFIX-TRAIN-DEFER-WAIT body item bdc1d62a`: cause 1's open readers of the
  gate conclusion, for P436's barrier.

The refusal says to land them on the round's roster branch. This seat's brief forbids roster
writes and every branch but its return refs, and says not to work around a refusal. So the
refused body is kept, unchanged, at `refs/heads/handoff-wip/r10-rca-gate-busy-defer-p5-body`
(`3edb36700`).

**The question for the orchestrator.** Land these two ops with
`tools/audit/seat/roster_edit.py` on `handoff/audit-r10-roster`. They are exactly what
`python3 -I tools/audit/carry_audit.py --roster-ref origin/main land-ops --topic
r10-rca-gate-busy-defer-p5 --body <the kept body>` prints. Then re-push the kept body with
`body_push.sh`. Alternatively, rule that these carries go to `#201` instead.

```
append-carry R10-HOTFIX-GATE-BUSY-DEFER 'From r10-rca-gate-busy-defer-p5, body item 453f6578: Cause 2, the settle loop, to the owner of `tools/ci/sweep.py`. - Fix: `settle` re-runs only a deferral red, or `undecided()` ignores `skipped` jobs and the overlap of the sweep'\''s own re-runs. - Failing test first: this PR'\''s `loop` arm reads `predicted_listed=0` for #3274'\''s content reds. Null control: the census'\''s at-once deferral reds are still re-run once their decider ends. - An open pull request whose runs sit at attempt 44 needs a fresh dispatched run, not a re-run: #3274'\''s three runs at 4f8ab965 are past the sweep (`must_rerun`). - RCA sections 2, 5 and 6. Carry: R10-HOTFIX-GATE-BUSY-DEFER (items 453f6578)'
append-carry R10-HOTFIX-TRAIN-DEFER-WAIT 'From r10-rca-gate-busy-defer-p5, body item bdc1d62a: Cause 1'\''s open readers, to P436'\''s barrier group: `merge_train.py` `policy_refusal`, `orchestrator_tick.py` `one_pr`/`main`, `review_packet.py` `gate_digest` and `merge_pr.sh`, with the #3264 review instance (red 02:01:18Z, sibling green 02:01:51Z) as its failing case. Once it lands, record the class "a provisional gate red read as final" in `dev/audit/config/bugclasses.json` as barriered (RCA section 7). Carry: R10-HOTFIX-TRAIN-DEFER-WAIT (items bdc1d62a)'
```
