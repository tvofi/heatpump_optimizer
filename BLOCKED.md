# BLOCKED: r10-gate-busy-defer-3, body_push refused on unlanded carries

The code is at `handoff/r10-gate-busy-defer-3` = 88e1140b7764571118943c5e92ef64bb21a054f0, and it is clean.
`tools/pr/prepr.sh <body>` returns rc=0 at that head, and origin/main 28d46c49 was unmoved at the push.
The body is kept by `body_push.sh` at `handoff-wip/r10-gate-busy-defer-3-body`.

`bash tools/audit/seat/body_push.sh r10-gate-busy-defer-3 <body.md>` refused with `CARRY-LANDED: 3 missing`.
Each body carry has to be in its roster group's brief or carries on `handoff/audit-r10-roster` before the
body is pushed. This seat may write no branch but its return refs, and roster edits are the
standing-roster seat's (`roster_edit.py`, behind its lint gate), so it did not land them. It did not
dismiss them to get past the refusal either.

## The question

Will the orchestrator (or the standing-roster seat) apply these three ops to `handoff/audit-r10-roster`?
They are `carry_audit.py --roster-ref origin/handoff/audit-r10-roster land-ops --body <body> --topic
r10-gate-busy-defer-3`, verbatim:

```
append-carry R10-RCA-GATE-BUSY-DEFER-2 'From r10-gate-busy-defer-3, body item 39f0a86e: **#3278'\''s RCA document, on branch `fix/r10-rca-gate-busy-defer-2`, not edited here.** Its §1 sentence "In #3261, the higher gate waits one poll, then passes" becomes untrue at this head. That gate now publishes the deferral at once, and `settle` re-runs it (race harness `pair`: gate-wait 0 s, RESIDUAL-RED 0). Its §5.2 countermeasure, a fresh dispatch where a re-run would replay a stale pinned program, stays needed: `settle` re-runs through the same job-rerun API, so a re-run of a run created before this merges executes the old waiting program. Re-measure with that document'\''s own `census` arm after this merges (a group of `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`; the orchestrator appends it with `tools/audit/seat/roster_edit.py append-carry`, this seat writes no roster). Carry: R10-RCA-GATE-BUSY-DEFER-2 (items 39f0a86e)'
append-carry R10-HOTFIX-GATE-BUSY-DEFER 'From r10-gate-busy-defer-3, body item f0580525: **A prelude holds a runner while it waits on another run** (`prelude.wait_sources`, up to `WAIT_MAX_S` = 8700 s). This is the same runner-queue cost this PR removes from the gate; #3282'\''s review run'\''s prelude held one 11:16:40–11:48:01Z (its `prelude` job'\''s started and completed stamps). It is legitimate only while the queue it lengthens is measured. Re-measure from the jobs API at your own merge base (a group of `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster`; the orchestrator appends it with `tools/audit/seat/roster_edit.py append-carry`, this seat writes no roster). Carry: R10-HOTFIX-GATE-BUSY-DEFER (items f0580525)'
append-carry R10-HOTFIX-GATE-BUSY-DEFER 'From r10-gate-busy-defer-3, body item 39b1bb0a: brief-cause: contradiction: the brief'\''s "nothing re-judges it" against #3282'\''s own runs, where tvofi re-ran the gate 4 s after the code run concluded and 8 s before the sweep'\''s read, which is why the sweep'\''s log reads reruns=0. Carry: R10-HOTFIX-GATE-BUSY-DEFER (items 39b1bb0a)'
```

Once they land, re-run `body_push.sh r10-gate-busy-defer-3` on the body kept at the `-body` ref
(`git show origin/handoff-wip/r10-gate-busy-defer-3-body:<its file>`). That is the return signal, and it
opens the PR. Then `git push origin :refs/heads/handoff-wip/r10-gate-busy-defer-3`.
