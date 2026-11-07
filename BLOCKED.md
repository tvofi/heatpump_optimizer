# BLOCKED: r10-gate-busy-defer-2, body push refused on two unlanded carries

The code is handed off: `handoff/r10-gate-busy-defer-2` at cc100c27555e6936dd179293cd8897dae0a3b9ae
(origin/main 294a880dae60 unmoved; `tools/pr/prepr.sh` rc=0; `--body-check` clean: CARRY-AUDIT 2 routed, 0 unrouted).

`tools/audit/seat/body_push.sh r10-gate-busy-defer-2 <body>` refuses:

    CARRY-MISSING R10-HOTFIX-GATE-BUSY-DEFER body item e57337c9: not in its brief or carries
    CARRY-MISSING R10-HOTFIX-GATE-BUSY-DEFER body item a5837b0c: not in its brief or carries
    body_push: ... land it on the round's roster branch (carry_audit.py land-ops), then push the body

The fixer brief forbids writing any branch but its return refs, so this seat cannot land them.
The refused body is kept at `handoff-wip/r10-gate-busy-defer-2-body` (body_push's own push).

**Question:** will the roster seat land the two ops below (from
`python3 tools/audit/carry_audit.py land-ops --body <body> --topic r10-gate-busy-defer-2`), after which
`body_push.sh` is re-run with the kept body? Or is either item to be dismissed instead
(`Carry: dismissed: <reason>`)? This seat judges that the second, re-runs executing the event base's
programs, is a real finding and must not be dismissed.

```
append-carry R10-HOTFIX-GATE-BUSY-DEFER 'From r10-gate-busy-defer-2, body item e57337c9: **Residual, stated plainly.** A code run longer than the bound still ends in the documented past-bound deferral red. #3263'\''s code run was still in progress 20 min in, so the replay at this head waits 720 s and then publishes that red. gate-sweep.yml re-judges it once the code run'\''s gate is green. The at-once red is gone for every sibling that finishes inside the bound. Whether to lengthen the bound (`ci.yml`'\''s gate `timeout-minutes`) is the orchestrator'\''s call. Carry: R10-HOTFIX-GATE-BUSY-DEFER (items e57337c9)'
append-carry R10-HOTFIX-GATE-BUSY-DEFER 'From r10-gate-busy-defer-2, body item a5837b0c: **A gate re-run executes the programs of its event'\''s original base, not of main.** `ci.yml`'\''s gate step restores `tools/ci/*.py` from `github.event.pull_request.base.sha`, and a re-run (gate-sweep.yml'\''s included) replays that event. So a PR whose last event predates a gate fix keeps running the old gate on every sweep re-run. #3261'\''s pair at attempt 10 ran 28482ece, before #3246. That changes how the orchestrator reads a red re-run gate after a gate fix merges: re-judge such a PR only after a fresh event (a push, an edit, a review), or read the `programs restored from` line first. `.github/workflows/ci.yml` is outside this group. This fixer writes no roster or brief, so it routes the finding to this group for the orchestrator to place (its gate-fix merge step in `dev/governance/roles/orchestrator.md` is the proposed home). Carry: R10-HOTFIX-GATE-BUSY-DEFER (items a5837b0c)'

```
