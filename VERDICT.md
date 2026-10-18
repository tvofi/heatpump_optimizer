Fix review: merge 834990ca265eb7dbb24165d7148159cb09ce8728

bus-nonce: 6785c0fef2b1f486c31c0e2305e765d8

PR #2386 (R10-TOOLS-O1), review round 1. Measured at head 834990ca265eb7dbb24165d7148159cb09ce8728, from a detached worktree; merge base 234087a5105d, origin/main 64b1f82a3958. The contract was read from origin/main, and the roles diff from the merge base to main is empty.

RESULT mutation_m1_bare_backticks dq_rows=1 check=FAIL "no script in tools/pr/ runs a command inside a double-quoted label" (got 1, wanted 0); the row evaluates to "slot: command not found" + "ok   a  script is recorded here..."
RESULT mutation_m2_stray_zero label="ok   0" (wrong label, the 4th argument is dropped by st)
RESULT baseline_line_1738 "slot: command not found" + "ok   0" (both defects reproduce)
RESULT head_line_1774 "ok   a `slot` script is recorded here, inside the slot this run holds (#2267)"
RESULT restored dq_backticks tools/pr/*.sh rows=0 check=ok
RESULT reader_planted_sites 3/3 reported (app_push.sh:772, push.sh:294, preflight.sh:284 with \` un-escaped)
RESULT class_sweep tools/pr/*.sh rows=0; tools/audit/**/*.sh (21 files) rows=0; all 65 tracked *.sh rows=0; merge-base prepr.sh rows=1 (line 1738 = this diff's line)
RESULT class_open seams=0 (the body's dispositions match: one seam, closed here)
RESULT unquoted_heredoc_backticks tools/pr + tools/audit = 0 (reader blind spot, see note 2)
RESULT git_grep_d15_restart_gaps old_path_hits=0; hits = new path's own usage line, tests/closures.json inert_reads, delivery row
RESULT rename similarity: only the usage line changed
RESULT d15_restart_gaps plant 0/3600/5400/12054 -> restart_gaps 0/0/1/1 (matches the docstring; --plant 12054 reads restart_gaps=1)
RESULT inert_reads_earned line removed -> ci_predict "PREDICT closures INERT READS tests/harness_headers.py: dev/audit/harnesses/d15_restart_gaps.py" rc=1; present -> rc=0; CI closures success at head
RESULT release_files VERSION/manifest/RELEASE_NOTES.md untouched (three-dot diff empty)
RESULT merge_tree origin/main rc=0 (no conflict)
RESULT structure STRUCTURE RATCHET PASSED; tmp_paths 0 refused; gate MODE: SCOPED -- 1 script(s) run; bash -n prepr.sh ok
RESULT ci 45 check-runs, all completed, 0 failure (success or skipped); body "Red checks: none" is consistent
RESULT body_head 834990ca names this head (step 7)

Not re-derived: the body's "277 passed" self-test tally. CI instrument-self-tests is green, but its job log blob is blocked by this container's proxy, so I cite the conclusion only. The full prepr self-test was not re-run (heavy-scripts rule). The mutation proof above drives the exact function and row.

Local environment note: tests/entities.py at head fails 1 of 2346 here, the graders-head-copy delivery_status stub-step case (every case rc 0). The diff touches neither tests/entities.py nor .github/workflows/tests.yml, and CI fast and graders-head-copy are green at this head. The failure comes from this container, not the PR (evidence/entities-local-env.txt).

Non-blocking notes (none is a step-15 breach; carry into a later push to these files):
1. dq_backticks was inserted between closure_lane's 9-line doc comment ("Which scripts this machine may record...") and closure_lane(). There is no blank line between the two comments, so closure_lane's comment now reads as dq_backticks' and closure_lane() has none. Move dq_backticks above that comment block.
2. The reader's comment says "quoted heredocs are skipped", but the code skips every heredoc, including unquoted ones, where a backtick IS evaluated. Today there are zero such sites in tools/pr or tools/audit (measured). The fix is to skip only when the delimiter is quoted or escaped, and scan the body as double-quoted otherwise.
3. Owner question, not blocking: should dev/audit/harnesses/README.md be recreated (INSTRUMENTS.md and CODEOWNERS still name it)?

Evidence: evidence-2386/ (class-sweep.txt, mutation-proof.txt, harness-move.txt, inert-reads-earned.txt, cheap-checks.txt, check-runs-834990ca265eb7dbb24165d7148159cb09ce8728.json, entities-local-env.txt, unquoted-heredoc-sweep.txt, repo-wide-dq.txt)
