Fix review: merge 102620a3e4590a34461f3d0d154c925fd3da86a0

bus-nonce: 089afa6f3c5e5532f6f06286688d64d7
pending-ci: gate

## Evidence

Round 1, full review of PR #3892 (roster landing of carry-3881 for #3879), head 102620a3e4590a34461f3d0d154c925fd3da86a0, merge base 6a58ba5cb30bf231dd7c6f60c42dc0d7583cb699. Role contract current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.

- RESULT diff scope: 4 files, records only (`carry-3881.json` new, `delivery/3892.md` new, `wave-r11-groups.json`, one line of `tests/closures.json`); `VERSION`, `RELEASE_NOTES.md` and `custom_components/` untouched (ev/version-untouched.txt).
- RESULT carry file: `dev/programme/carries/carry-3881.json` at the head is byte-identical to the copy at 34cefdc5 (`cmp`).
- RESULT roster: `git diff f520ce0365 <head> -- dev/programme/` differs only in `delivery/3888.md` (main's) and `delivery/3892.md` (this PR's row); the roster and carries equal the roster branch tip, which is still `handoff/audit-r11-roster` = f520ce0365.
- RESULT stage edits: the four `resume.commit` values the roster sets (dc2b2bab31 #3875, f52e700df1 #3738, 34c7a3f610 #3871, dc5face1f6 #3877) are each merges on origin/main (ev/stage-commits.txt).
- RESULT null control, reproduced with my own probe body (one finding routed `Carry: #3881`), not #3879's live body, which now routes its carries to #3713: `carry_audit.py check` at b4a8bbd567 and at current origin/main bb6377b4da prints `BAD-DEST ... #3881 has no owner`, rc 1; at the head `1 routed, 0 bad destination(s)`, rc 0 (ev/carry-null-control.txt).
- RESULT mutation of the closures line: with `"dev/programme/carries/carry-3881.json"` deleted from `tests/closures.json` at the head, `tests/entities.py` fails `every tracked file is either measured or deliberately classified [these force the FULL suite when touched: dev/programme/carries/carry-3881.json]`, rc 1; restored, rc 0 (ev/mutant-closures-line-entities.txt, ev/entities-head.txt). The line is earned.
- RESULT `node tools/policy/brief_lint.mjs` at the head: rc 0, 0 errors (ev/brief-lint-head-full.txt).
- RESULT merge: `git merge-tree --write-tree origin/main <head>` against origin/main bb6377b4da exits 0 (ev/merge-tree.txt).
- RESULT figures: the body quotes none; figure_lint 0/0/0. Mutation proof n/a: no production, test or instrument line changes, and no finder's harness applies to a records landing.
- RESULT carry_audit on the PR body (packet): 1 item, routed (dismissed to P-R11-CARRY-LINE-OWN-FILE).
- RESULT CI: `merge_train.py classify 102620a3e4590a34461f3d0d154c925fd3da86a0 --pr 3892` polled 10:46 to 11:18 UTC, every run `WAIT 102620a3e4590a34461f3d0d154c925fd3da86a0 pending: gate red: none` (ev/classify-log.txt); no red at this head. Returned with `pending-ci: gate` per the brief: the relay posts only once green at this head.

## Notes

- Note: roster-duplicate: the roster this PR lands (commit 079ac8dd90, from the roster branch) holds the R11-OUTSIDE-HONEST-DHW-RUNS carry from #3877 twice, once with its `From r11-outside-3849, body item dca85603:` prefix and once without it and without the item tag; same instruction and control, brief_lint clean. Carry: dismissed: the destination seat reads one instruction twice; the cause of the copy is not measured, so it is not carried (finding-propagation.md)
