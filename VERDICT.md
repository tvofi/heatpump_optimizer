Fix review: blocked f2daca863fb67409458f788e61839d4460a17ccb body-stale: the body still describes round 6, says no carry file was written and the three jobs are not routed, and never names #2952 or carry-2952.json, which this head adds

bus-nonce: ca05621bdd40126db7813f0929c8a4f1

## Round

Review round 7 of #2925, dispatched past the three-round rule. Head measured: `f2daca863fb67409458f788e61839d4460a17ccb`. It merges code head `7af0ba5f9` and origin/main `ce5940c0d`. Still the head at verdict time (`git ls-remote`: refs/heads/fix/r10-rca-prepr-head-graders and refs/pull/2925/head both at f2daca863).

## Block

Round 6's block, `carry-missing`, is settled **in the tree**. Record section 7 now ends each of `briefs`, `pr-contract` and `budget-raise-gate` with `Carry: #2952`. #2952 is open (filed by tvofi at 2026-10-29T14:01:22Z). Its brief, `dev/programme/carries/carry-2952.json`, is new at this head and passes `brief_lint.mjs` with 0 errors. It is a valid destination: no live roster group names #2952, on origin/main or origin/handoff/audit-r10-roster. It states its control (the enumeration rule, plus the arm's self-test and `mutants.py` as the null). It states its precondition (budget-raise-gate reads live reviews, so its local run is partial and is never reported as a pass) and a re-measure instruction.

**The PR body was not updated for round 7, and it contradicts the head.** The brief asks for the body to match the head, and `fix-review.md` step 10 reads the carry from the body:
- `## Re-cut` still says: "They are not routed to a later stage from this body ... this seat filed no issue and wrote no roster or carry file", and "The diff against the previous head is `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md` alone". The r7 delta (`git diff 3efeea217...7af0ba5f9`) also adds `dev/programme/carries/carry-2952.json` and a `tests/closures.json` entry.
- `## Head` describes code head `d379cfa43` measured against `b87019b86`. It does not describe `7af0ba5f9` or its two commits (`c78ea804e`, `7af0ba5f9`).
- `## Mutation proof` says "This round adds no production line; its diff is the record alone". It is still true that no production line is added, but the second half is false.
- `## Forward-carry` routes only `R10-RECORD-API-O1`. `carry_audit.py pr 2925` reports 2 items: 1 routed, plus 1 bad destination (finding 3). No body item routes the three jobs to #2952. The only place they are routed is the record.
- `## Figures` and `## Red checks` cite CI at `2c62c682d`, two heads back.

The repair is a body rewrite and nothing else: describe `7af0ba5f9`; name #2952 and `carry-2952.json` under `## Forward-carry`, each with a `Carry: #2952` line; and re-take the figures at this head. No code change is owed.

## Findings

- The body is stale against the head, as set out under `## Block`. Carry: dismissed: settled by this PR's own body rewrite before merge, which is no later stage
- Record line 7 says "review round 7 filed #2952". #2952 was filed by tvofi (author_association OWNER) at 2026-10-29T14:01:22Z, after round 6's verdict (13:49Z) and before round 7. A review seat files nothing, and the issue body names #2925 as the writer of the carry. The sentence should credit the owner, or say "filed after review round 6". Carry: dismissed: a one-line correction to this PR's own record, owed in the same push as the body rewrite
- `carry_audit.py --roster-ref origin/handoff/audit-r10-roster pr 2925` prints `BAD-DEST #2925 review 6495961723 item a3103224: R10-RCA-PREPR-HEAD-GRADERS is not a group of the roster`. An earlier review on this PR carried to the RCA id, which is not a roster group, so the PR shows a bad destination even with a correct body. Carry: dismissed: that review's item is superseded by #2952 and carry-2952.json; the orchestrator's split should note it rather than re-carry it
- Record section 7's proposed policy line for `gate-scoping.md` ("prepr.sh is not CI" naming step 6d's graders arm) is "proposed and not made". The body does not surface it to the owner, and no destination holds it. Under CLAUDE.md, a policy change is surfaced in the pull request for the owner's approval. Carry: dismissed: the owner's decision, not a stage's; the body rewrite should list it under its own heading so the owner sees it
- `carry-2952.json`'s brief names pr-contract's checkers as `policy_lint.mjs`, `figure_lint.mjs`, `preflight.sh`, `prepr.sh` and `carry_audit.py`. pr-contract.yml's restore list at this head is pathspecs (`.claude/workflows/*.mjs`, `*.py`, `vendor`, `tools/audit/*.sh`, `tools/audit/record-predicate`, ...), and the job also runs `tools/ci/codescan_wait.py`. The named list is a snapshot. Its `remeasure` field already tells the stage to re-read the workflow and not the carry, so this does not mislead the stage. Carry: dismissed: the carry's own remeasure instruction covers it

## Evidence

- RESULT merge: `git merge-tree --write-tree origin/main f2daca863` exits 0, tree `b3fe967d3`. stderr prints `LEDGER-MERGE: resolved tests/closures.json`; no claim-file conflict. origin/main is at `e5ddba1fa`, 6 commits past the merge base `ce5940c0d`. (ev/merge-tree.txt)
- RESULT roles: `git diff ce5940c0d...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
- RESULT enumeration: the rule returns the same six jobs at HEAD, 3efeea217 and origin/main: budget-raise-gate.yml:66, governance.yml:124/1043/1144, pr-contract.yml:93, tests.yml:603. This re-derives carry-2952's "six jobs" figure. (ev/enum.txt)
- RESULT mutation proof (the arm's, re-run at this head): `python3 -I dev/audit/rca/prepr-head-graders/mutants.py .` gives M1 bad 5, M2 bad 1, M3 bad 1, M4 bad 1, M5 bad 3, the same as the body's figures. Null: `python3 -I tools/pr/ci_predict.py --self-test` prints `ci_predict self-test: 0 failed`, rc 0, 102 s wall. (ev/mutants.txt, ev/self-test.txt)
- RESULT r7 mutant (mine): deleting `control` from carry-2952.json's carry makes `brief_lint.mjs` print `carry 0: control is missing or is not a non-empty string`, rc 1. Unmutated: 0 errors, rc 0. The r7 carry is linted, not vacuous. (ev/mutant-carry-control.txt, ev/brief_lint.txt)
- RESULT scope: `tests/closure.py select --diff ce5940c0d` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`. `tests/structure.py` prints `STRUCTURE RATCHET PASSED`. VERSION, the manifest, RELEASE_NOTES.md and both claim files have an empty three-dot diff. (ev/closure-select.txt, ev/structure.txt, ev/untouched.txt)
- The r7 delta writes no production code line, so it draws no mutant. The `tests/closures.json` line adds carry-2952.json to `tests/entities.py`'s closure, which is the classification CLAUDE.md requires for a new tracked file. I did not re-run entities.py; CI `tests / closures` was still in progress.
- CI on f2daca863, read from the check-runs API at verdict time:
  - success: policy-docs, env-matrix, wave-script, briefs, budget-raise-gate, mutation, closure-scope, typing, browser, arch-score, delivery-status, hassfest, validate-hacs and two CodeQL analyses.
  - still in progress: fast (3.14), closures, coverage, instrument-self-tests, `codeql / Analyze (python)`, and the second run's prelude.
  - No pr-contract run on this head appears in the listing.
  - `tests / nightly-status` failure: its log names main's scheduled Nightly lane `slow` (run 40835853528) and says the check is not a required context. The diff touches none of what it reads (its scripts, ci.yml, tests.yml, nightly.yml, governance.yml, the plan, HANDOVER.md). It is the orchestrator's on main and owes this PR no answer.
- carry_audit: on the record as a body, `0 finding item(s)`, so the record's `Carry: #2952` lines are not counted as body items. On the PR, `2 finding item(s): 1 routed, 0 unrouted, 1 bad destination(s)`. (ev/carry_audit_record.txt, ev/carry_audit_pr.txt)
- Not re-derived: the record's section 4 census (history), the section 5 costs (keycount 584/69/71, jobtime 215.5 s / 477 s, 57 s weighted) and the section 6 plant timings. The r7 delta changes no code they measure, and the body says it did not re-take them.
- A frugal-routing hook (guard_inline.py) refused one inline Bash call as over its inline-search budget. I sent that one command, the carry mutant, to a worker exactly as written and did not override the hook.
