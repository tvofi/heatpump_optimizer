Fix review: blocked 78509aca050bf6b53f055507232051741cab67c9 root-cause-unanswered: pr-contract went red at 79554e2f, the body states a false cause and gives neither a cheaper detector nor a finding that none exists
bus-nonce: 6eeae5bba46ee30345de8c2236e30978

Round 1. Seat r9c-rev-2015, from a detached worktree at 78509aca050bf6b53f055507232051741cab67c9 (merge base and origin/main 59b5ac6e). Heavy runs not repeated (host load 191 to 367); CI check-runs read through the API.

## The blocking item (fix-review.md step 11)

The pr-contract job at 79554e2f (job 112755516860, evidence/prcontract_79554e2f.log) failed with three `[pr-body]` errors: `## Red checks` did not name `CodeQL`, `delivery-status` or `nightly-status`. The body says instead that it failed because "the head before the delivery row and the since values existed". That is not what the log says. The body also does not give either of the two answers step 11 accepts (a cheaper detector with its standing cost, or a finding that none exists). One honest answer is available: those three reds appeared only after the push, so prepr could not have seen them. This is a body-only repair. No code change is needed.

## Verified
- RESULT layout_since_2015=17. The 17 entries are exactly the 17 retired entries whose old path left the tree or whose new path appeared in this diff (evidence/layout_since.txt). The diff adds no retired entry (158 at base, 158 at head). The 69 remaining null entries are untouched.
- RESULT delivery_row=present: dev/programme/delivery/2015.md, in the same shape as the 2008 and 2009 rows.
- RESULT codeql_rename_only=true: all three files are R100 renames. Alerts #25, #23 and #22 on the same rules were already dismissed at the old paths ("used in tests"), so the same dismissal applies at the new paths.
- RESULT carry_1922=present: the new entry in dev/programme/carries/carry-1922.json hands governance_cost.py and d11lib.py (and the INERT_EXCEPT, entities and closures.json follow-ups) to R9-RO-9, with a control. `tests/layout.py --report` names both as "reintroduces moved path ... since 2015" and exits 0 in REPORT mode until R9-RO-9 (evidence/layout_report.txt).
- RESULT mutation_header_corpus: `len(parts) == 6` changed to `5` makes `closure.py selftest` rc=1, including "the header corpus is the six-part path under dev/audit/rounds". Restored, the output is "ALL 33 closure shrink pins PASSED".
- RESULT null_control: at base `True False ['dev/audit/rounds/round3/D2/planted_live.py']`, at head `False True []`, which matches the body.
- RESULT oldpath_grep: the body's grep returns 6912 lines at base and 269 at head. The executable hits left over are dispositioned in the body. A grep for split forms found no undispositioned executable read (evidence/split_form_grep.txt).
- prepare_baseline --strip-self-test ok. tmp_paths self-test 42/0. codeowners_gap --check uncovered_files=0. stamp --self-test pass.
- CI's prepr self-test at the head (instrument-self-tests, job 112774138241) is 193 passed, 0 failed. The local 186/7 and the in-prepr 183/10 are therefore environmental. The cause of the 3-check difference between the two local runs was not established.
- `merge-tree --write-tree origin/main HEAD` rc=0. VERSION, the manifest, RELEASE_NOTES, the claim files and `*budgets.json` are untouched.
- delivery-status (UNCHECKED: merge-collection skip over main's window) and nightly-status (main's scheduled run 37595831734) are red on #2011, #2013 and #2014 as well. They come from main, not from this pull request.

## Body corrections owed with the fix
- "The 69 other landed-but-null since entries" (and "the 69 landed entries" under Forward-carry): 69 entries are null, but only 68 have landed. .claude/workflows/carry-1921.json has not moved yet.
- Optional: name the three prior dismissals (#22, #23, #25) under CodeQL so the orchestrator can mirror them.

## Not re-derived
- The D6 register regeneration (claims.py needs the HA venv, which this Mac lacks). Rely on CI's fast and closures lanes, which were still in progress at review.
- budget-raise-gate has one cancelled run and one successful twin at the head. The orchestrator should rerun the cancelled run before merging.

Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2015/evidence
