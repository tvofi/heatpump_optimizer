Fix review: merge 42bee4bde021e9934e85cba43a34be6c99c05f30

bus-nonce: 1679f4fb7879f2bfa3d757af90f28a88

Delta review (round 6) of R10-UPDATE-PR-LOCK after the recarry. Round 5 measured `67ee6adfd712786da12241bf59bb5b78030c2d80` and blocked it `ci-red` only: `pr-contract` failed on both of that head's runs because `carry_audit.py` read `R10-UPDATE-PR-SIGNALS` as a BAD-DEST, its roster not yet on main. The code itself verified clean there. This head is that same code plus a clean merge of origin/main, so the new surface is the resolution delta alone (`fix-review.md` step 12, #1667), and the delta is empty.

## The delta

- RESULT head parents: `42bee4bd` has `67ee6adf` and `d42eb15a`; `d42eb15a` merges origin/main `6f25795bc` into the code head `931e9a0f`. `67ee6adf` is an ancestor of the head, and merge-base(origin/main, head) is `6f25795bc`.
- RESULT three-dot delta: `git diff $(git merge-base origin/main 42bee4bd)...42bee4bd` = 5 files, 175 insertions, 9 deletions — the identical file list and counts as `git diff $(git merge-base origin/main 67ee6adf)...67ee6adf`.
- RESULT blob identity, every changed path: `git rev-parse <head>:<p>` equals `git rev-parse 67ee6adf:<p>` for all five — `dev/programme/delivery/2469.md` 663eb3b5, `tools/audit/seat/INSTRUMENTS.md` caa071d7, `tools/audit/seat/cloud_relay.sh` 21f2139e, `tools/audit/seat/pr_args.sh` ce84ab48, `tools/audit/seat/update_pr.sh` 8532317b. The reviewed code is the same bytes.
- RESULT patch identity: the two three-dot patches with `index` lines stripped, `diff` exits 0 — `ev/delta-42bee4bd.patch` against `ev/delta-67ee6adf.patch`.
- RESULT what the recarry added: `git diff --stat 67ee6adf 42bee4bd` = 6 files, all main's own (`dev/programme/delivery/{2464,2473,2474,2475,2476}.md` and `dev/programme/rosters/wave-r10-groups.json`). No production file, no test file, no gate file.
- RESULT contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- RESULT merge: `git merge-tree --write-tree origin/main 42bee4bd` exits 0 with tree `c025d0bd`; no claim-file conflict.

## CI at this head

`repos/tvofi/heatpump_optimizer/commits/42bee4bd.../check-runs` (the API, not `gh pr checks`): 49 runs, all completed — 33 success, 16 skipped, 0 failure, 0 cancelled. Every run carries `head_sha 42bee4bd`. Both `pr-contract` runs are success (118479548651 at 05:58:45Z, 118479695048 at 05:59:19Z); `mutation` 118479551653, `closures` 118479880252 and `Analyze (python)` 118479620760 (the last to conclude, 06:25:41Z) are success.

The `pr-contract` log prints `record red-history 24 commit(s) between origin/main and this head, every failure conclusion across them: none` (`failingCheckNames` excludes `pr-contract` from its own walk) and `CARRY-AUDIT: 3 finding item(s): 3 routed, 0 unrouted, 0 bad destination(s)` — the roster row merged as `1e30f876` resolves all three of the body's carries. The round-5 red is gone from the branch's history walk and green at this head.

## Carried and re-run verification

- RESULT `bash tools/audit/seat/pr_args.sh --self-test` at the head: `pr_args self-test: 56 checks, 0 failed`. Its own mutant arms report ok (`mut:lock`, `mut:unlock`, `mut:stop`, `mut:watch`) and so do the dead-run null control and the detached-child arm.
- RESULT `bash tools/audit/seat/cloud_relay.sh --self-test` at the head: `cloud_relay self-test: 74 checks, 0 failed`.
- Round 5's hand-built mutant table (nine rows), the base-tree control (`56 checks, 3 failed` with origin/main's `update_pr.sh`) and the base self-tests (46/0 and 69/0) measure the identical bytes proved in the delta above, so they carry rather than being re-built.
- RESULT `python3 -I tools/audit/carry_audit.py check --body <head body>` in the head tree: `3 routed, 0 unrouted, 0 bad destination(s)`, rc 0.
- VERSION, the manifest version and the RELEASE_NOTES heading are untouched (three-dot diff empty). No golden, claim, closure or budget file is in the diff.

## Instruments

The harness is the PR's own self-test arms, run unmodified from the head worktree. I built no mutant this round: the production bytes are identical to the round-5 tree where nine hand-built mutants were run, and I re-ran the harness's inline mutant arms above.

## Red checks

The branch's only red gate is `pr-contract` (round 0's `02369b10` and `d2d361a4`, then `67ee6adf`). The body names `pr-contract` and answers the trigger with the cheaper detector it uses, `python3 -I tools/audit/carry_audit.py check --body <body>` before the push at the cost of one python spawn; `red-history` finds no other failing check across the 24 branch commits. The body's `## Red checks` does not enumerate `67ee6adf`'s two run ids (118467040392, 118467201379); the check, cause and detector it states are the same ones. Carry: dismissed: the same check, cause and cheaper detector are already answered in the body, and a run-id enumeration constrains no later stage.

## Evidence

`~/hpo-seats/r10s3/rev-2469r6/ev` — `ci-summary.txt` and `check-runs-42bee4bd.json` (both name the head SHA), `delta-review.txt`, `delta-42bee4bd.patch`, `delta-67ee6adf.patch`, `pr_args-selftest.txt`, `cloud_relay-selftest.txt`, `pr-contract-run-39377731567.log`, `body.md`.
