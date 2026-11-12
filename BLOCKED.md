# BLOCKED: body_push.sh exit 4, REFUSED CARRY-LANDED

Topic r10-outside-contributor-cycle-p2. Code head `40abc1bd0a2cf1fd9524aa824713d6a0207a5d3d` is on `handoff/r10-outside-contributor-cycle-p2`; `tools/pr/prepr.sh` printed `PRE-PR: 40abc1bd0a2cf1fd9524aa824713d6a0207a5d3d 0000000000000000000000000000 rc=0` on it with this body. The refused body is kept by body_push.sh at `handoff-wip/r10-outside-contributor-cycle-p2-body` `56771374a7a1c2d7c0a64eed1439c4ad39cf22d9`. The seven carries name the round's roster, which this seat may not write: the relay folds them and re-runs `bash tools/audit/seat/body_push.sh r10-outside-contributor-cycle-p2 <body.md>`.

`body_push.sh`'s output, verbatim to its last line (lines naming a path on this host left out: 0):

```
fill-red: the diff adds no unpinned mutation site; nothing written
ref_privacy (body) ok: no host identity in the body
review-packet handoff: R10-OUTSIDE-CONTRIBUTOR-CYCLE at 40abc1bd0a2c, 0 live, 0 dispatched carries, 0 refused
CARRY-MISSING R10-OUTSIDE-CONTRIBUTOR-CYCLE body item d4703cd1: not in its brief or carries: "- **The interface to part 1's module.** The two calls above are this part's assumption; part 1 had p"
CARRY-MISSING R10-OUTSIDE-CONTRIBUTOR-CYCLE body item 8da136bb: not in its brief or carries: "- **`tools/ci/selftest_closures.json` re-record is owed, on top of part 1's entry, once part 1 is on"
CARRY-MISSING R10-OUTSIDE-CONTRIBUTOR-CYCLE body item 53108d53: not in its brief or carries: '- **The live checks the design owes are not run.** This seat has no `gh`, no App key and no fork pul'
CARRY-MISSING R10-OUTSIDE-CONTRIBUTOR-CYCLE body item aa80140a: not in its brief or carries: "- **The three instruments' guides and decision 0017 are part 1's files.** They owe: remerge_main.sh'"
CARRY-MISSING R10-OUTSIDE-CONTRIBUTOR-CYCLE body item f7754778: not in its brief or carries: '- **Carry 14, round 3:** `_post_agent_approval`\'s body under a bare `--mandate` id reads "under <id>'
CARRY-MISSING R10-OUTSIDE-CONTRIBUTOR-CYCLE body item cc5c19fe: not in its brief or carries: "- prepr-ci-predict: unenforced: `tools/pr/ci_predict.py` runs the base's `carry_audit.py` in a `--sh"
CARRY-MISSING R10-OUTSIDE-CONTRIBUTOR-CYCLE body item 3518898b: not in its brief or carries: "- brief: cost: the dispatch asks for code against the interface the design fixes for part 1's module"
CARRY-LANDED: 7 missing
body_push: a carry above is not in its group's brief or carries; land it on the round's roster branch (carry_audit.py land-ops), then push the body
body_push: REFUSED CARRY-LANDED
```
