Fix review: blocked 8527dbc2146afdc6ddc0d801518f6cf70094fd13 root-cause-unanswered: fast (3.14) went red, unanswered (entities.py's deployment-shape lane, #1218: tests/arch_score_head.py's closure is a second full-coverage closure; the PR's own red, at e5301f5e and again at this head)

bus-nonce: 880f4b3b1d176048c6706e898ec69708

Round 3. PR #1851 (R9-EG-A1), head 8527dbc2146afdc6ddc0d801518f6cf70094fd13 (live head re-read 2026-10-02T17:45:07Z, unchanged). Evidence: evidence/ (HEAD.txt names the head). Reviewed from a detached worktree at the head. The C3 class question is closed by tvofi's ruling (option B) and not re-litigated here. From the next round the fixer owes a re-cut body (fixer.md).

## The round-3 delta (cb1d68eb6): it does what the ruling asked

1. ABOUT.md "Known limit: interleaved effect-free statements" is present. It says that C3 enumerates spellings and that the class is open. It names rt_04h/i/j as KNOWN-OPEN, tells a reviewer to read a duplication-driven IMPROVES against the diff, and owes the class fix to R9-EG-A2. That is accurate, with one exception: "the same delta-S as `id(N)` gave" is not re-derived. The three spellings read +14.1502, which is the uncharged `pass` figure. The body's own table gives `id(N)` (rt_04) +32.01. My C3-ablated re-run of rt_04 was stopped at its time limit, so the phrase is UNVERIFIED and contradicts the body's figure.
2. RESULT rt_04h_dup_assert_uncharged KNOWN-OPEN IMPROVES admissible +14.1502; rt_04i_dup_assign_uncharged likewise; rt_04j_dup_walrus_uncharged likewise. Each is pinned in expected.json at IMPROVES/KNOWN-OPEN.   (calib-summary.txt)
3. tests/arch_score.py: `games` is filtered to label == "GAME", and a new check pins `len(known) == 3` and all IMPROVES. Mutants, replayed against the same recorded collection (cached_run.py is my driver, not the fixer's). The control M0 is the unmodified copy: ALL 139 PASSED.
   - RESULT M1 games filter widened to GAME+KNOWN-OPEN: KILLED, "no red-team attempt reads IMPROVES" FAIL [rt_04h, rt_04i, rt_04j]
   - RESULT M2 known check expects != IMPROVES: KILLED
   - RESULT M3 known check expects 4: KILLED
   - RESULT M4 rt_04h relabelled GAME (a KNOWN_OPEN entry dropped): KILLED, 3 FAIL (row pin, no-IMPROVES, known count)
   - The known check partly duplicates the per-row "classifies as recorded" pins. What it adds alone is the count, which M3 shows is live.
4. RESULT CALIBRATION 77/103 labelled cases classify as their label says. RESULT GAME 23: NULL admissible 12 and WORSENS inadmissible 11, none IMPROVES. RESULT expected.json vs e5301f5e: the only diff is the three added KNOWN-OPEN rows, and _sensitivity is unchanged. No other verdict moved.
5. RESULT full `tests/arch_score.py` at this head, run locally after the main merge: ALL 139 ARCHITECTURE SCORE CHECKS PASSED, rc=0, real 355.6s (arch_score_full.txt). CI agrees: fast (3.14) job 110933687925 prints "ALL 139 ARCHITECTURE SCORE CHECKS PASSED" and "ALL 4 ARCHITECTURE SCORE HEAD CHECKS PASSED", and arch_score.py takes 580s there.
- Forward-carry: present in R9-EG-A2's brief on handoff/audit-r9-fixplan (0ae4eb67d). It names the three spellings and states the fix, the flip to NULL/inadmissible and the re-calibration as owed.
- VERSION, the manifest and RELEASE_NOTES.md are untouched (three-dot diff). `git merge-tree --write-tree origin/main HEAD` exits 0.

## Blocking: fast (3.14) is red, and the red is this PR's

RESULT check-runs at 8527dbc2: every check is success, skipped or neutral except fast (3.14), which is a failure (job 110933687925, MODE: FULL). "1 TEST SCRIPT(S) FAILED" = tests/entities.py, "2 of 2062 ENTITY CHECKS FAILED":
- `the deployment-shape lane's closure is the whole tracked package, so any production diff selects it (#1218)`. It asserts `_D308_FULLCOV == [tests/deployment_shape.py]`, and the result is full-coverage closures=['tests/arch_score_head.py', 'tests/deployment_shape.py'].
- `and the lane's docstring records those measured numbers as the selection-cost note (#1218)`, with missing markers ['90 of the 435', '325 pairs'].

Attribution:
- The same two checks fail at the previous head e5301f5e (job 110916401839).
- The merged base 5f87e25a is green on fast (3.14) (job 110927136599).
- Current main 8fa06663 is red on a different check: `no job-level if leads with always()` (job 110936760309). That red is main's, not this PR's.

The cause is in this diff: `tests/arch_score_head.py` reads the whole package, so it is a second full-coverage closure, and the #1218 note's derived numbers no longer match. The body has no Root cause section, and its only mention is "tests/entities.py ... the gate is CI's". The check also has to go green, not only be answered. Either amend the #1218 lane to admit arch_score_head.py with a re-derived note, or narrow arch_score_head.py's closure.

## Owed in the same push (would not block alone; listed so round 4 is the last)

- ABOUT.md, in the calibration section: "All 17 red-team attempts read NULL or inadmissible." This is false at this head. There are 23 GAME attempts, and 3 more red-team attempts read IMPROVES admissible. The sentence contradicts the new Known-limit section in the same file.
- calibrate.py's report prints "RED TEAM 23/23 attempts read NULL or inadmissible; IMPROVES: none" and says nothing about KNOWN-OPEN. A reader of the instrument's own report does not see the documented limit. Add a KNOWN-OPEN line.
- Body: "passes at this head, 135 checks" should be 139. "23 of 23 red-team attempts read NULL or inadmissible; none reads IMPROVES" needs the scope "attempts labelled GAME", as the Round-3 paragraph already says.
- ABOUT.md "the same delta-S as id(N) gave": see item 1.
