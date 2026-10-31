# D10 verifier report, round 10 (single verifier: V1, V2 and V3)

Tree: detached worktree at handoff/audit-r10-register 9355f107d. load1=7.60, thread_factor=1.000. Counts only, so contention does not apply.

## D10-s1-51: apply_schedule returns success for a bogus entry_id
- V1: the finder's harness as its header says gave silent=1 (apply_schedule) and raised=7. With `--perturb` (the `_loaded_entries` call moved ahead of the early return) the count fell to silent=0. The number moved the stated way.
- V2: my own script, scratchpad v10.py, called the registered handler directly with no schema applied. It returns `{'updated': {}, 'reason': 'nothing to apply'}` for `{entry_id:'nope'}`, for `{}`, and for one key it does not recognise. Source: services.py:979-982 returns early before `_loaded_entries`.
- V3: reachable in real Home Assistant. services.yaml exposes the action, every field is Optional and the entry_id field is accepted. The early return does not depend on any stub. Consequence: nothing is written and the response wrongly reports success instead of an error. Severity is low. Class P2 is confirmed: the entry guard is present at the 7 sibling actions and missing here. The seam rule loops over every registered action, so it enumerates every seam.
- Vote: verify, severity low.
