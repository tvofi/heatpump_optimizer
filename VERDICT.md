Fix review: merge 7fb8680c857220f629c328b842f152d2c236542a

bus-nonce: 978ea4fe6265e95d2999bb974bad455d

## Evidence

Round: first review (no prior reviewed head). Measured from a detached worktree at 7fb8680c857220f629c328b842f152d2c236542a, three-dot against merge base a7628041dc02e298c5399003d4c0576391dd5c4e; `refs/pull/3445/head` still reads that sha at verdict time (ev/HEAD.txt).

- RESULT self-test: `review_packet self-test: 108 checks, 0 failed`; `body_patch self-test: 109 checks, 0 failed` (ev/review_packet-selftest.txt, ev/body_patch-selftest.txt). Both body figures re-derived.
- RESULT mutants (my own driver, ev/mutants.txt; each applied to the head file, self-test run, file restored): M1 range back to 1-based KILLED (5); M2 live-roster count KILLED (1); M3 round-topic scope dropped KILLED (1); M4 snapshot-ancestor-of-tip dropped KILLED (2); M5 snapshot-in-head dropped KILLED (1); M6 WAIT/GREEN condition dropped KILLED (2); M7 REQUIRED scope dropped KILLED (1); M8 GREEN dropped from the deferral KILLED (1); M9 `^Carry N:` anchor dropped KILLED (2); M13 `continue` turned into return KILLED (1); NULL docstring edit SURVIVED. The body's named mutants per carry agree with mine in kind and counts.
- RESULT wiring mutants not pinned by the self-test: M10 `dispatch_prompt` returns None, M11 `gather` passes round_topic None, M12 `gather` drops the snapshot advisory: each SURVIVED the self-test. M10 and M11 were measured live instead (next two lines), so the fix's production path is shown working; see Findings.
- RESULT finder's harness, carry 15 (live `handoff` on this PR's own topic and body, ev/handoff-live.txt): at the base file `25 carries, 20 refused` (refuses carry 23..25 etc., the moving-target defect); at the head `25 live, 5 dispatched carries, 0 refused`; at the head with M10 applied the refusals return. The dispatch PROMPT holds exactly Carry 4, 15, 16, 18, 19 (ev/dispatch-carries.txt).
- RESULT finder's harness, carry 16 (live, PR #3377 at head 3bdc73b336, the real `round_ref`, `origin_handoff_tip`, `is_ancestor`; ev/carry16-live-3377.txt): accepted with `roster snapshot 7696a3ba07..., 154 commits behind handoff/audit-r10-roster; a later landing takes the rest`; null with round_topic None refuses `handoff/audit-r10-roster 31dc837478 is not an ancestor of 3bdc73b336`, as before.
- Carry 4: d0f91346bd is an ancestor of the merge base; `body_patch.sh` self-test holds the Dependabot `--commits-file` arm, its non-Dependabot null and two mutants (ev/carry4-bodypatch.txt); the carry's second control (a Dependabot PR with a human commit still refuses) is policy_lint.mjs's `'human commit'` self-test case at line 4026. Disposition "already built at the base" verified.
- Carry accounting against the dispatch brief: 4 built at base, 15/16/19 built here, 18 dismissed as superseded by 19 (the brief's own text for carry 18 carries that dismissal). Every dispatched carry is named in the body.
- Merge with main: `git merge-tree --write-tree origin/main <head>` rc=0, no conflict (ev/merge-tree.txt).
- VERSION, manifest, RELEASE_NOTES and tests/golden untouched three-dot; `env_drift.py --all`: NO UNCLAIMED DRIFT (56), NO STALE FIXTURE (56) (ev/env_drift.txt).
- CI: `merge_train.py classify 7fb8680c857220f629c328b842f152d2c236542a --pr 3445` exit 0: `GREEN 7fb8680c857220f629c328b842f152d2c236542a pending: none red: none` (ev/classify.txt). The one red check-run, `tests / nightly-status`, is outside `merge_train.py owed-reds` (ev/owed-reds.txt), so no `## Red checks` answer is owed.
- Body head: `## Head` names 7fb8680c85 (the reviewed head) and the code head 95ad6344e2, whose diff to the head is the one delivery-row file.
- Figure not re-derived: `tools/pr/prepr.sh` EXIT 0 at 95ad6344e2 was not re-run (heavy gate; cited CI `gate` success instead).
- Commit messages a7628041dc..HEAD read in full: no Claude, Co-Authored-By or session text.
- Architecture: added lines keep the existing pure-function/self-test seam shape; `import roster_lib` inside `gather` follows `handoff`'s existing local import. No breach found.

## Findings

- The self-test pins the pure helpers but not their wiring in `gather`/`handoff`: `dispatch_prompt` returning None, `gather` passing no round topic, and `gather` dropping the snapshot advisory each survive `--self-test` (M10-M12), so a later refactor could silently disable carries 15 and 16 in production while the self-test stays green. This review killed M10 and M11 by live runs (ev/handoff-live.txt, ev/carry16-live-3377.txt). Carry: dismissed: gather/handoff I/O wiring had no self-test seam at the base either and the live harness runs here show the path working; not a regression this PR introduces.
