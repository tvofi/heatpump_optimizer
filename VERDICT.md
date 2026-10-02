Fix review: blocked d5830a13cf705aa466e33169ade6d2136e4078f9 root-cause-unanswered: nightly-status went red, unanswered (the diff touches docs/plan-2026-09-open-issues.md, so the exemption is void, and pr-contract, a required check, refuses on it)

bus-nonce: 3c16b415d8befb93a65a5f14e48ec194

Round 4. PR #1851 (R9-EG-A1), head d5830a13cf705aa466e33169ade6d2136e4078f9 (live head re-read 2026-10-02T19:44:29Z, unchanged). Evidence: evidence/ (HEAD.txt names the head). The round-3 owed list is closed in full. Only a body answer is missing, and it does not move the code head.

## Round-3 owed list: all closed

- #1218 lane (tests/entities.py): `_D308_FULLCOV == _D308_ADMITTED`, where ADMITTED = [deployment_shape.py, arch_score_head.py] by name. The probe (d308_probe.py is my instrument; it execs the block from `_D308_DS =` up to the synthetic-predicate comment):
  - RESULT head: both #1218 checks ok.
  - RESULT third full-coverage closure injected (tests/zz_third_fullcov.py): FAIL, full-coverage closures=[arch_score_head, deployment_shape, zz_third_fullcov]. A third closure is still refused.
  - RESULT round-3 predicate (`== [_D308_DS]`) at head: FAIL. This is the control: the red was real and the admission is what clears it.
- RESULT the full `tests/entities.py` at head under the seat venv: ALL 2071 ENTITY CHECKS PASSED, rc=0 (entities-head.txt). CI agrees: fast (3.14) is a success (job 110981771738).
- The note in deployment_shape.py is re-derived: "90 of the 435", "325 pairs", and arch_score.py is in the no-production-closure list. The docstring check passes.
- Root cause for fast (3.14) at e5301f5e/8527dbc2: answered under `## Red checks`. It gives the cause, the process state (runnable here, not run), the cheaper detector (entities.py under the seat venv, about 3 min) and its standing cost.
- ABOUT.md, corrected in two places:
  - "All 17 red-team attempts..." now reads "Every red-team attempt labelled GAME reads NULL or inadmissible; the three labelled KNOWN-OPEN read IMPROVES".
  - The id(N) phrase now reads "+14.15 ..., the figure an uncharged `pass` gave". Both are true per my round-3 measurement (rt_04h/i/j +14.1502).
- calibrate.py's report adds a KNOWN-OPEN line. RESULT (the new summary() over my round-3 collection): "KNOWN-OPEN 3 attempts the counters do not close (ABOUT.md, Known limit); IMPROVES: rt_04h_dup_assert_uncharged, rt_04i_dup_assign_uncharged, rt_04j_dup_walrus_uncharged".
- The re-cut body says 139 checks and scopes the claim: "every red-team attempt labelled GAME ... (23 of 23, none IMPROVES); the three labelled KNOWN-OPEN read IMPROVES". The head named in `## Head` is d5830a13.
- The main merge has no hand resolution: `git merge-tree --write-tree 1c43a6c9d aa7a81192` gives cffd5e4d, which equals HEAD^{tree}. merge-tree against origin/main exits 0. VERSION, the manifest and the notes are untouched.
- arch_score.py is not re-run locally at this head. Its inputs since 8527dbc2 changed only in calibrate.py's summary() and the main merge. CI's fast (3.14) at this head is a success, and it runs the FULL suite, including arch_score.py. That run is cited, not re-taken.

## Blocking: nightly-status is red, and the body does not name it

RESULT check-runs at d5830a13: everything is success, skipped or neutral except:
- nightly-status: failure (job 110981771563). "NIGHTLY ABSENT: nothing failed, but mutation-ledger, mutation-ledger-push did not run in that scheduled run" (scheduled run 36984959667, head 492d840). That is main's `always()` defect, which hotfix #1859 addresses. The cause is not this PR's code.
- pr-contract: failure (job 111000342081, 19:42Z). "ERROR [pr-body] check `nightly-status` is red and `## Red checks` does not name it. It grades `main`, but this diff touches what it reads (docs/plan-2026-09-open-issues.md)". The earlier pr-contract and budget-raise-gate runs were cancelled and superseded.

fix-review step 11: the diff reaches the reporter's input (the plan), so the exemption is void, and the body must name the red and answer it. The answer can be the external cause and its owner (main's mutation-ledger jobs skipped in the 02T08:36Z nightly, fixed by #1859), with a `gh workflow run tests.yml --ref main` dispatch run id once it concludes, as the reporter's own text asks. This is a body edit only. If the code head stays d5830a13, every measurement above carries.
