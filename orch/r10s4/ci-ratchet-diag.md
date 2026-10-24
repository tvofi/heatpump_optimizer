# ci-ratchet diagnosis (run 39611184226, head 5d433771a)

Root cause: .github/workflows/tests.yml (ci-ratchet job, step "Gather ...", line ~2883-2920 at origin/main):
`gh api "repos/<repo>/actions/artifacts?per_page=100" --jq '...' > window.json || true`.
The UNFILTERED artifacts list (repo has ~18,183 artifacts, 182 pages) now returns HTTP 500 with Content-Length 0
for most calls (reproduced locally: 2 of 3 plain calls 500, 1 of 3 200; per_page=5 and name=ci-metrics-* filtered calls
return 200). gh prints "unexpected end of JSON input" (the empty body hits its --jq parse), exits 1, `|| true`
swallows it, window.json is empty, python json.load(open(window)) then raises JSONDecodeError (Expecting value, line 1 col 1).
So: server-side GitHub 500 on a huge unfiltered list, plus `|| true` hiding it. Not a token/permission/filter problem.

Started: ci-ratchet job last success = run 39585211229 (job started 11:27Z 2026-10-21, head 9e2f6ed9d); first failure
run 39585970262 (11:34Z); failed in every main push since (11 consecutive). The workflow/script were NOT changed
(last touch of tests.yml 2026-10-20, ddfbf8ac7 train hold; ci_ratchet.py older). The changed condition is the artifact
count growing (high push rate today) past what the unfiltered endpoint serves.

Blocks merges: NO. Required contexts in ruleset 23698884 (16 listed): fast (3.14), browser, briefs, closure-scope, closures,
typing, hassfest, validate-hacs, policy-docs, wave-script, pr-contract, env-matrix, Analyze x3, mutation, budget-raise-gate.
ci-ratchet absent; the workflow comment says "Not a required context". It does make main push runs red.

Smallest sound fix (not written): tests.yml, the window query. Query the three lanes by name
(`?name=ci-metrics-$lane&per_page=100`, which works, 72 KB each) in a loop and merge them, instead of the
unfiltered list; and drop `|| true` (or retry, then fail loudly with the HTTP status) so an empty window.json can no
longer reach python. Optionally guard python with a size check. Keep the null-safe .workflow_run.id // .run_id selection.
Worked check: `gh api ".../actions/artifacts?per_page=100&name=ci-metrics-fast"` returns 200 with workflow_run.id populated.
