Fix review: merge 1281f5c1396c7bab49a9400def0425712cb44ab4

bus-nonce: 3138ea7e3b997f8a55f10c1a972257bd

Round: delta re-review of the repair after the blocked verdict at e8c3fe927bb9a1d070f458d6aed9173d8a8bb192 (stale-base). Head measured: 1281f5c1396c7bab49a9400def0425712cb44ab4.

## Evidence
- RESULT prior finding resolved: P401 is now ruled REJECT, a duplicate of P362, naming 1e994e484; `git merge-base --is-ancestor 1e994e484 1281f5c1396c7bab49a9400def0425712cb44ab4` succeeds; `PR_ARGS_DIR` with its `# mut:argsdir` line is at tools/audit/seat/pr_args.sh:181 at the head.
- RESULT HPO_ALLOW_STALE_TOOLS: not turned into a repo change; the ruling dismisses it as host-local seat script state.
- RESULT PR's own diff (three-dot, origin/main...head): 2 files, dev/programme/delivery/3383.md and dev/programme/triage/s6-batch130.md, 23 insertions. The delta since e8c3fe92 beyond these is merges of main only (including custom_components/ code from #3299); that code is main's own, reviewed there, and not this PR's change, so no wider review.
- RESULT mutation proof re-run (ev/triage_refusal.txt): ruling_verdict(P401)=REJECT and triage_refusal on a carry citing s6-batch130.md#P401 refuses "not an ACCEPT ruling (REJECT)"; with the verdict flipped to ACCEPT it returns None; P402 null control returns None.
- RESULT P362 carry exists: s6-batch105.md has ACCEPT carried to R10-OPENER-REUSE.
- Not re-run by me: the reproduction of the stale-sibling probe and the pr_args.sh self-test (my self-test invocation did not exercise it); I read the `fresh` block references and the code at pr_args.sh:181-190, which fix the directory at source time; CI's instrument-self-tests concluded green at this head.
- RESULT CI: merge_train.py classify exit 0, "GREEN 1281f5c1396c7bab49a9400def0425712cb44ab4 pending: none red: none". The packet's earlier `gate` failure was a render-time snapshot from a superseded run and is not red at settle. owed-reds lists the required set (ev/owed-reds.txt); none red.
- RESULT merge: `git merge-tree --write-tree origin/main 1281f5c1396c7bab49a9400def0425712cb44ab4` rc 0, clean.
- Body: head SHA in the body is the head measured; Red checks `none` is correct (no required red at settle); VERSION, manifest and notes untouched; no budget, golden or claim file in the PR's own diff.
- carry_audit at the head: 0 findings, 0 unrouted.

## Findings
- Residual: the packet's figure_lint reports the body's `git diff --stat origin/main...9fe80a40` figure as unverified (its flags are not checked); I re-derived it by hand (2 files, 23 insertions) and it matches. Carry: dismissed: re-derived by hand, matches the body
