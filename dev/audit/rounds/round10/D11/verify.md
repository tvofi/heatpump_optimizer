# D11 round 10 -- verifier report (single verifier, V1+V2+V3)

Checkout: detached worktree of handoff/audit-r10-register at 9355f107d, on a scratch branch `verify-d11-tmp` (non-main, as the hook needs). load1 8.5-9.3 during runs, thread_factor 1.000-1.001; all metrics are counts, contention-immune.

## D11-s1-01 / D11-s3-01 (same defect, two finders) -- verify, low
- V1: s1 harness escaped_heading_writes=1, control_refused=1; --perturb escaped=0. s3 harness refused_heading_payloads=2, multiedit_refused=0, null_refused=0; --perturb 3/1/0. Both move as stated.
- V2 (own harness: raw JSON piped to the unmodified `.claude/hooks/pre-edit.sh`, exit status): Edit `## v1.2.3` -> 2, Write -> 2, MultiEdit with the heading in edits[1] -> 0, MultiEdit body-line null -> 0. Escaped heading payloads = 1 of 3 tool shapes.
- V3: matcher `Edit|Write|MultiEdit|NotebookEdit` (.claude/settings.json:15) routes MultiEdit to the hook, so any harness offering MultiEdit reaches it; not a hastub path. Consequence bounded: stamp.py refuses at release time, so this is a lost early refusal (defense in depth), severity low. Seam rule (`grep 'k in ("new_string"'`) finds only the demonstrated join; it does not enumerate other payload-reading checks (the VERSION/manifest and .cursor checks are path-keyed and were confirmed to cover MultiEdit: VERSION via MultiEdit -> exit 2). Class: `new` -> correct to I3 (bypassable boundary of a governance check); P2 also fits. Duplicate: s3-01 should merge into s1-01.

## D11-s1-51 -- verify, low
- V1: lint_missed_stale_counts=1, retired_key_claims=3; --perturb -> 0 / 3, as stated.
- V2: tests/structure_budgets.json has 17 keys, 16 less `recorded_at`; no `cut_*` or `cross_seam_edges` key, only `seam_cut_total`. D7.md:13 says "all 24". Stale statements: 1 count + 3 retired-key mentions (D7.md:17, :18, structure.py:369).
- V3: docs only, not runtime; misleads a D7 finder seat. Seam rule grep also hits tests/structure.py:228 (a historical reference to cross_seam_edges, arguably fine), which the finder table omits -- the rule enumerates, the table classifies a subset. Class I5 confirmed (the lint gap side is I3/I4-adjacent).
