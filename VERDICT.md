Fix review: merge 97839ed60f8b59cd59adc99d106b4e94ac4dccab

bus-nonce: 72b6ef1bf2d112a15eb226632d0456dd

Round: first review of this head.

## Evidence
- RESULT head measured: 97839ed60f8b59cd59adc99d106b4e94ac4dccab (ev/HEAD.txt); the PR body's `## Head` names the same head.
- RESULT CI: `merge_train.py classify 97839ed6... --pr 3366` exit 0, `GREEN ... pending: none red: none`. The `gate` red in the render-time packet was still in progress and has since concluded green. Body's `## Red checks: none` stands.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` exit 0 (tree 70a8d057), no conflict.
- RESULT mutation proof (body's two mutants, re-run): unmutated `cloud_dispatch.py --self-test` 147 checks, 0 failed (ev/null-control.txt). `ref_key ... if False else` gives 1 failed, "a reviewer at the handoff returns on probe/revt-..." (ev/mut1.txt). Main-side text mutant (line 266) gives 1 failed, "the reviewer blocks on main only for a merge-tree conflict" (ev/mut2.txt). Files restored.
- RESULT new mutants this PR adds to dev/audit/harnesses/r10_seat_selftests_mutants.py (cloud_dispatch-21..23, bus-16..19, cloud_relay-50..54, body_patch-2): `RESULT survivors=0`, all KILLED (ev/mutants.txt; the harness was started twice by mistake, so the file holds duplicate lines for some ids).
- Figure not re-derivable as quoted: the body says `--self-test` prints "146 checks"; at this head it prints 147 checks, 0 failed (main's merges added one).
- body_patch-2 is killed by the self-test message "mutant cmta changed nothing" (the self-test's own mutant finds its target line already replaced), not by a behavioural assertion on the commits-file argument. It counts as KILLED under the harness's rule; I built no stronger probe.
- Claim files, goldens, structure/policy budgets, closures.json, VERSION, manifest and RELEASE_NOTES are untouched by the three-dot diff.
- Policy approval: the diff changes dev/governance/roles/fix-review.md and standing-dispatch.md. The body says approval is pending; the owner's approving review is required before merge and is not mine to give.
- Forward-carry: body states a repair merge with carries unchanged from the earlier body; no new forward-carry owed.

## Findings
- Residual: the body's quoted self-test count (146) is one below the head's 147; informational only. Carry: dismissed: stale by one after main's merges, no effect on the claim.
