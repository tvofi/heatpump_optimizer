# Box D3-g27 null control: usable, red on artefact checks only

`fullgate.py null` (comment-only marker): gate_rc=1, wall 3862 s, load1 0.92 at the end (provisional).
Red scripts and failed-check counts (null.json fail_lines): closure.py selftest 2, entities.py 1, harness_headers.py 4.

- tests/closure.py selftest (2): "a refused merge surfaces merge()'s reason" / "a merge that succeeds carries no merge reason" -- status skip-not-under-scoped in this worktree; the same 2 as box D3-top6's null.
- tests/entities.py (1): "and is accepted when it does [the scoped path records only what the diff can reach]" -- a scoped-gate workflow check reading the worktree's git state, not production.
- tests/harness_headers.py (4): the depth-root/inlined-walk check names this seat's own untracked harnesses (fullgate.py, finalize.py, this box's probes); round4/D6/claims.py header drift (claims_true 122 vs 123, claims_false 1 vs 0) and the byte-identical output check it triggers -- the same artefacts box D3-top6's null shows.
- tests/stress.py passed (no budget red), so no machine-caused script; no card.mjs heap failure; not re-taken.

A key is KILLED only when a script fails more checks than these counts (fullgate.py's own comparison).
The probes under probes/ were written while this null ran (before harness_headers.py ran) and are present for every key gate,
so the harness_headers.py count is the same population for the null and the keys.
