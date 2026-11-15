Fix review: merge d24189bd656ff982867bff3c7f55df985e573214

bus-nonce: b7a7b2e52445fb6979090f2cf86c13b5
pending-ci: governance / instrument-self-tests, governance / env-matrix, tests / browser (classify prints "WAIT d24189bd656ff982867bff3c7f55df985e573214 pending: gate red: none"; the aggregate `gate` run shows failure in the packet digest while those are in_progress, classify reports no red)

Round 2, delta review over 6dc42ccc267162b473d552d5f39f389d9c9a224e. The delta is tools/audit/seat/body_push.sh and its instrument note only: no production (custom_components/) code, so no widening.

## Evidence
- Previous finding (class-open: body_push.sh:175 refreshed with no --base) is resolved. The class rule `grep -n 'figure_block.py" refresh' tools/audit/seat/*.sh` returns three sites (ev/enumeration.txt): update_pr.sh:107 and open_pr.sh:122 (closed in round 1) and body_push.sh:213, which now passes `--base "$FB"`: the open PR's recorded base.sha via pr_recorded_base when origin holds fix/<topic> with an open PR, origin/main only where no PR exists yet, and a refusal (keep_refused, nothing pushed) when the PR list or the recorded base cannot be read. No call site is left open.
- `bash tools/audit/seat/body_push.sh --self-test` at head: 49 checks, 0 failed (ev/bp-selftest.log), including the precondition that OLDBASE differs from origin/main's tip, the equal-base null control, mut:bpbase killed, the unreadable-base refusal with nothing pushed, and the fix/t-without-open-PR arm.
- My own mutant: deleting `--base "$FB"` from the refresh line makes the self-test fail (rc 1, many FAIL lines, ev/mutant-nobase.log). Restored; tree clean.
- Merge with origin/main: git merge-tree --write-tree exits 0, clean (ev/merge-tree.txt).
- VERSION, manifest, notes heading, claim files, budgets and closures are untouched by the delta. carry_audit at head: 0 findings.
- shellcheck is not installed in this seat; not run.
- CI at head: classify rc 3 (WAIT) after about 12 minutes of polling, last line in ev/classify.txt. Not a red, not GREEN; the relay posts once green. review_packet's introduced-red refusal is the same unfinished instrument-self-tests job, not a finding.
- Reviewed head: ev/HEAD.txt.
