Fix review: blocked 7cef1c324366950fa8e65976b40a040c3ca24a81 harness: the carries' remeasure command `moved_paths.py tools/audit/seat/*` crashes on the tracked directory tools/audit/seat/shims/

Round 2. Seat r9c-rev-2012, fresh detached worktree at 7cef1c324366950fa8e65976b40a040c3ca24a81 (contains origin/main be0cb821; merge-tree vs origin/main exit 0). Live head at posting: 7cef1c324366950fa8e65976b40a040c3ca24a81. Delta judged: 6f3609a4..7cef1c324366950fa8e65976b40a040c3ca24a81.

## The block

carry-1921.json and carry-1922.json now tell R9-RO-8 and R9-RO-9 to run `python3 tools/audit/seat/moved_paths.py tools/audit/seat/*`. Run as written at this head it exits 1 with `IsADirectoryError: [Errno 21] Is a directory: 'tools/audit/seat/shims'` (tracked: shims/seat-python, shims/seat-python3) before printing a single hit (evidence2/carry_cmd_new.txt). The body's own figure ran the five files by name, so it never hit this. The forward-carry's control as written cannot run. Fix (any one): make scan() skip non-files (or recurse), or change the carry command to `git ls-files tools/audit/seat | xargs python3 tools/audit/seat/moved_paths.py`; re-run it and put that figure in the body.

## RESULT lines (everything else checks out)

RESULT self-tests at head: merge_train 49/0 failed, handover_prompt 13/0, moved_paths 6/0, bus 45/0 (selftests.txt)
RESULT plant old line 78 (`tools/audit/briefs/`): handover_prompt 13 checks, 1 failed -- "every repository path the prompt names exists (missing: tools/audit/briefs/)" (plant78.txt)
RESULT plant `docs/delivery/<N>.md` in done criteria: 2 failed, the new arm names it by its directory (plantRow.txt)
RESULT moved_paths over the five files: 6f3609a4 = 20 hits (incl. handover_prompt.py:78 tools/audit/briefs/ and merge_train fixture lines 336/393/394/397); 7cef1c324366950fa8e65976b40a040c3ca24a81 = 12 hits, 9 FALLBACK + 3 STALE? (merge_train.py:160 split fallback to tools/policy/policy_lint.mjs at :161-162; handover_prompt.py:14,:76 .claude/rules/ = lifted prefix whose generated copy exists) -- matches the body's 20/12 and its dispositions (moved5_old.txt, moved5_new.txt)
RESULT classification: closure.is_inert('tools/audit/seat/moved_paths.py') = True (tools/audit/ prefix, not in INERT_EXCEPT, not header corpus). tests/entities.py could not run locally (no homeassistant module); CI's fast lane was in_progress at posting -- not verified by me.
RESULT tmp_paths --check: 0 refused, 0 stale allow entries at HEAD (tmp_paths.txt)
RESULT brief_lint carry-1921.json + carry-1922.json: 0 error(s) (brief_lint.txt)
RESULT check-runs at head: 18 success, 11 skipped, 1 neutral, 4 in_progress (CodeQL, browser, env-matrix, fast 3.14), budget-raise-gate cancelled; red delivery-status and nightly-status are main's and answered in the body's ## Red checks.
RESULT round-1 seam closed: handover_prompt.py:78 -> dev/governance/roles/ (exists); handoff_push.sh:4,:7 re-pointed; the retired tools/audit/handoff/ filter alternative removed.

bus-nonce: 07a42a823c5083624718b766c26ec08d
