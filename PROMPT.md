CLOUD PROBE seat for tvofi/heatpump_optimizer, topic r10-cop-gate-vent-r2, at head 1afdef8872a5da2eedff32916c1095e114198fae. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: a read-only probe. Measure what the brief below asks against the tree at 1afdef8872a5da2eedff32916c1095e114198fae (`git fetch origin 1afdef8872a5da2eedff32916c1095e114198fae`); change no tracked file and send no code to any ref.
Output: write your result as a body file and run `bash tools/audit/seat/body_push.sh r10-cop-gate-vent-r2 <result.md>`, which pushes refs/heads/handoff-body/r10-cop-gate-vent-r2; that push is the return signal. A return push carries only your own result tokens.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
DESIGNER seat (round 2 of 3), group R10-COP-GATE, vent-freeze design (carry 8/9). Contract dev/governance/roles/designer.md at origin/main.
Your round-1 note: handoff-body/r10-cop-gate-vent at ce5ca88b394bd2013d58f0f3d740aecf673826fe. Design review: revise, at handoff-body/r10-cop-gate-vent-drev (git fetch origin handoff-body/r10-cop-gate-vent-drev && git show FETCH_HEAD:BODY.md). Read it in full.
Revise exactly the three points:
1. COP row (flow_meter.cop_evidence): split the COP decision on heat evidence. Lift the vent freeze only for measured-heat folds (counter span _async_learn_heat_span, or a measured flow heat). Keep the freeze on the inferred path, or prove with a harness arm and its null that a window does not move the inferred fold under COP_ASK_TOLERANCE and COP_TRACKING_ERROR_GATE.
2. draw-range power_frozen (room_air=False site): decide it together with point 1 and say why. It either stays frozen, or is lifted only where the draw is judged against measured heat.
3. Harness: for each lifted learner, add an arm that feeds a window-shaped interval through the production fold, with the latch clear and the window present, and reports how far the learned quantity moves against a no-window null. A learner whose output moves keeps the freeze.
Also settle the reviewer's carried notes in the note itself:
- the true site count is 13 call sites plus the DHW callable, and coordinator.py:9780 must be named;
- the buffer row must be settled by reading the topology;
- the counter-span refusal code changes because of the order of the freeze check, so the failing test must assert the code.
Re-measure every line number at origin/main. Keep everything the review accepted unchanged.
Return the revised note via body_push.sh r10-cop-gate-vent <note.md>, fast-forwarding the orphan ref. Never production code, and never open a PR. If a hook refuses you, stop and report.
