Fix review: merge 46b9b4fd17f6b19d0fc4dedf066113516f3c639d
bus-nonce: 141604ec49c74f573c33067684327a30

Round 2, seat r9c-rev-2015. It supersedes the round-1 blocked verdict on 78509aca (review/2015 a58522a0). I reviewed the head's resolution delta and body. The round-1 measurements carry over because the code is unchanged.

- RESULT code_delta=auto-main-merge-only. 46b9b4fd has parents 78509aca and f060cb4c (origin/main, #2011). `git merge-tree --write-tree f060cb4c 78509aca` gives 8dd708b6, which equals 46b9b4fd^{tree}, so the merge has no resolution. range-diff shows the authored commits unchanged. Comparing the three-dot branch diffs (59b5ac6e...78509aca against f060cb4c...46b9b4fd), only tests/entities.py differs, and only in hunk offsets and context; the +/- lines are identical. Main's one edit to a moved file (tools/audit/ci-version-edit/pr_contract_shapes.py) followed the rename into dev/audit/harnesses/ci-version-edit/. At the head, nothing remains under the old tools/audit/round* or ci-version-edit paths except the two files carried on purpose (round4/D11 governance_cost.py and d11lib.py). #2011 added no new old-path reference.
- RESULT pr_contract_answer=present. Red checks now gives the true cause from job 112755516860: three `[pr-body]` errors, for CodeQL, delivery-status and nightly-status left unnamed. It also gives the step-11 answer: no cheaper detector, because the reds appeared after the push. This matches the job log (evidence/prcontract_79554e2f.log).
- RESULT count_fixed=true. The body now says "68 other landed-but-null ... (69 are null; carry-1921.json has not moved)", and Forward-carry says "68 landed entries". Both match evidence/layout_since.txt.
- RESULT codeql_dismissed=3/3. Alerts 31, 32 and 33 are dismissed ("used in tests") at the three new paths.
- The body's Head section names 46b9b4fd17f6b19d0fc4dedf066113516f3c639d, and it is the live head at posting time. The claim that 78509aca has the same tree as code head 9f3e62d8 holds: both are ddeba2fa.
- Carried from round 1: the mutation proof, the null control, layout since=2015 on exactly the 17 moved units, delivery row 2015.md, carry-1922 to R9-RO-9, R100 renames, CI's prepr self-test at 193/0, and VERSION, manifest, notes, claims and budgets untouched.

Orchestrator notes. Neither note is this PR's defect.
- At this head, fast (3.14), closures, coverage and Analyze (python) were still in progress when I posted. This verdict does not certify them; the merge train's CI gate does. budget-raise-gate has one cancelled run beside a successful one, so rerun the cancelled one.
- delivery-status is now OVERDUE on #2001's record row (main's backlog; this PR adds only 2015.md). nightly-status is main's scheduled run 37595831734. The body's delivery-status paragraph still describes the earlier UNCHECKED state. The trigger is answered, but the stated cause is out of date.

Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2015/evidence2 (round 2) and /Users/timmalmstrom/hpo-seats/r9c-rev-2015/evidence (round 1)
