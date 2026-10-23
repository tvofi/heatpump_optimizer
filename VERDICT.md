Fix review: merge ac6dc1328702d5a8be9caeba4098277acd1e6794
bus-nonce: cfe22928e2b3da566bb5aa8054d0b0bb

Round 2, group R10-CI-LAYOUT-P2, scoped to the resolution delta c40335889..ac6dc1328 over round 1's `Fix review: merge c40335889dd453c206c0d6a77b6301fe7dc1a8e1` (bus review/2673 97ef9d882). Measured from a detached worktree at ac6dc1328702d5a8be9caeba4098277acd1e6794; head re-read before posting, unchanged. Roles current (`git diff MB...origin/main -- dev/governance/roles/` empty).

## RESULT lines

- Delta: two commits. d2b3d797a = merge(c40335889, origin/main f8cc41ab0); ac6dc1328 = merge(c40335889, d2b3d797a), tree identical to d2b3d797a (9c88d5178). `git show --cc` empty on both: no hand resolution. No head-note or row commit besides.
- `git diff c40335889 ac6dc1328` is byte-identical to main's own `git diff 25816d5eb f8cc41ab0` over the same paths: 22 `dev/programme/delivery/*.md` rows (#2653, #2672, #2676 added; 19 modified) and `dev/programme/triage/s5-batch2.md` (#2672). None is a P2b file: `git diff c40335889 ac6dc1328` over P2b's 105 non-row paths is empty.
- Graders at the head: `ruleset_cutover.py --self-test` 94 checks, 0 failed; `ci_predict.py` no closures or fast red predicted against f8cc41ab0, rc 0; `policy_lint.mjs` TOTAL 0 errors across 50 files, PRE-CUT-OVER note, rc 0.
- `git merge-tree --write-tree origin/main ac6dc1328` (origin/main 6120fb513) rc 0; `tests/closures.json` resolved by the ledger driver (`LEDGER-MERGE: resolved`).
- VERSION, manifest version, notes heading, both claim files: untouched (three-dot).

## CI at the head, read from check-runs (evidence/check_runs.txt)

- Code run 40037871505 (suite 108526368634): every lane concluded; `governance / delivery-status` success (job 120701784313), so the body's delivery-status red is cleared, not merely answered. `gate` (job 120711168084) FAILs on exactly `governance / policy-docs`, `wave-script`, `env-matrix` (this run): the base-pinned trio, answered in `## Red checks` and verified in round 1. `pr-contract / pr-contract` (job 120710848199) success at 23:38:28Z, after every red in that suite concluded.
- Edit run 40037870394 (suite 108526365906, created 23:09Z by the body patch): `pr-contract` (job 120702174658) failure in `codescan_wait.py` (exit 1) while CodeQL Python was still running (concluded 23:37:19Z); its `gate` (job 120702332495) red by consequence. Fail-closed, the shape round 1's note 1 named; not a body defect.

## Cut-over preconditions, `--dry-run --window --head ac6dc1328 --pr 2673` (GET only)

`reds-at-head: FAIL -- reds besides the base-pinned: ['pr-contract / pr-contract']` (the edit run above; delivery-status no longer listed). `main-ratchet-green` PASS, `caller-is-owner` PASS; `main-push-idle` and `queue-drained` FAIL on live state (main Tests run in progress; open #2678, #2677, #2675), window-time conditions, not this diff's. WINDOW DRY-RUN REFUSED, nothing written.

## Non-blocking notes

1. **`reds-at-head` still refuses at this head**, now only on the edit run's fail-closed `pr-contract`. Before `--disable`: `gh run rerun 40037870394 --failed` (CodeQL has concluded, so its `codescan_wait` can pass), then re-run `--dry-run --window --head ac6dc1328…` and confirm `reds-at-head: PASS`. Same class as round 1's note 1, already carried; not re-carried. Carry: R10-CI-LAYOUT-P2
2. **Body `## Head` and `## Red checks` describe older heads.** `## Head` says ac6dc1328 "merges origin/main f8cc41ab0" and "any resolution inside the code head is described below", but the main merge is d2b3d797a and nothing below describes it (its `--cc` is empty, so there is nothing to describe); its second paragraph still reads "The PR head is the code head `ca1bc2b0e` plus this PR's row commit". `## Red checks` still calls `delivery-status` red (job 120645455492), but it is success at this head. The code run's `pr-contract` passes the body as written. Carry: R10-CI-LAYOUT-P2
