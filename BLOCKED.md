# BLOCKED: r10-fly-stamp-flush-cost, repair round for #3296

The code is on refs/heads/handoff/r10-fly-stamp-flush-cost at b4446e5cb97958de79c1c9d38d25e7679624de68, a fast-forward from the PR head 01e9c612. tools/pr/prepr.sh with the body: rc=0. carry_audit check: 2 routed, 0 unrouted.

body_push.sh refuses the body with CARRY-LANDED: 2 missing. Both of its Carry: R10-FLY-STAMP-FLUSH-COST items (the brief-mandated post-merge beat-dispatch measurement, and one friction line) must first be appended to the group's carries on the round roster branch. This seat may not write that branch (brief: write only the return refs). The refused body is kept at refs/heads/handoff-wip/r10-fly-stamp-flush-cost-body, at da2447df3a5077007c2b606f366d87aafd1cb168.

Question: will the orchestrator or the standing-roster seat land these two roster_edit.py ops (output of carry_audit.py land-ops, verbatim below) and then re-run `bash tools/audit/seat/body_push.sh r10-fly-stamp-flush-cost <body>` from the kept body? Or should the friction item be dropped from the body?

```
append-carry R10-FLY-STAMP-FLUSH-COST 'From #3296 (r10-fly-stamp-flush-cost), body item 7ab754eb: Post-merge measurement owed at the first stamp after merge, for one beat-only dispatch: its jobs and runner-minutes by the runs jobs API (`python3 -I dev/audit/harnesses/r10_rca_flush_dispatch.py runs <id>`). The job list should show record-autofix alone running. The same measurement must also confirm nightly-status'\''s reading of that run: the run'\''s `display_title` is `Nightly record beat`, and the next PR'\''s `tests / nightly-status` grades the last schedule or lanes=all run, not the beat. This seat has no workflow-dispatch right. Carry: R10-FLY-STAMP-FLUSH-COST (items 7ab754eb)'
append-carry R10-FLY-STAMP-FLUSH-COST 'From #3296 (r10-fly-stamp-flush-cost), body item 37f02097: fixer-step-push: stale: refs/heads/handoff-wip/r10-fly-stamp-flush-cost held a previous seat'\''s BLOCKED commit (e4b03333) not on the PR head'\''s line, so a fast-forward step push was refused. I did not force it, and no step was pushed before the handoff. Carry: R10-FLY-STAMP-FLUSH-COST (items 37f02097)'
```
