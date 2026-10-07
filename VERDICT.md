Fix review: merge 29d863f7b08f09f1003505bd21ef9ebebf3bb3d1
bus-nonce: 7ad6ce7b591862a655908b0787c95ced

Reviewer r9c-rev-2011, round 2. Measured head 29d863f7b08f09f1003505bd21ef9ebebf3bb3d1 = no-ff merge of fixer eda2317a into round-1 head e1531dbb; origin/main still be0cb821; `git merge-tree --write-tree origin/main <head>` rc=0. Judged the delta e1531dbb..29d863f7b08f09f1003505bd21ef9ebebf3bb3d1 (4 files); round-1 RESULTs on e1531dbb carry (workflow pin mutation 1/2191 FAIL, friction arm 100/1, both restored green).

RESULT round-1 seams: `.claude/workflows/web-stamp.js:153` now names dev/programme/plan-2026-09-open-issues.md, dev/programme/delivery/<N>.md, dev/programme/register/audit-2026-09.md -- all three exist at the head. `pr_contract_shapes.py:60` probes dev/programme/HANDOVER.md (exists; py_compile ok). `policy_budgets.json` record.opens re-pointed.
RESULT budgets: `node tools/policy/policy_lint.mjs --budgets` with the e1531dbb json vs the head json -> byte-identical output (diff rc 0); `role record ~7242 tokens, cap 6904 +band 500 = 7404`; no cap value changed in the diff. Not a raise. (ev2/budgets_oldjson.txt, ev2/budgets_head.txt)
RESULT policy_lint default run at head: rc=0, 0 FIXTURE VACUOUS.
RESULT plant M1 (DELIVERY_ROW old-only): rc=1, VACUOUS on 'a merged row deleted' and 'no existing list'.
RESULT plant M2 (DELIVERY_ROW new-only): rc=1, VACUOUS on 'a merged row deleted, old spelling'.
RESULT plant M3 (drop the dev/programme REPORTER_INPUTS line): rc=1, VACUOUS on 'the moved plan edited'. All restored; tree clean.
RESULT enumeration at head (body's rule, ev2/enum_head2.txt): 135 lines; vs round 1 exactly the three blocked files left the list. Every remaining hit outside the five #2012 files (merge_train.py, bus.sh, open_pr.sh, handoff_push.sh, handover_prompt.py) is in the body's dispositions: both-spellings readers, old-to-new maps, path-independent fixtures, rules paths: globs (carry-1922/R9-RO-9), and the new prose/fixture disposition line covering delivery_status.py, closure.py, roster_lib.py, merge_throughput.py, counts.mjs, gh_comment.py, codeql.yml, role files, D11.md, dev/archive. I opened each of those: comments or quoted examples, none read as a path by code. No live seam remains.
RESULT red checks (commit check-runs API, ev2/check_runs_head2.tsv, 34 runs at read): failure = budget-raise-gate, delivery-status, nightly-status -- all three named and answered in ## Red checks (budget-raise-gate: path-only edit, owner approval at head under mandate 5951564627, which is the orchestrator's to give). Previous head e1531dbb: only delivery-status/nightly-status failed (answered), budget-raise-gate cancelled; its full gate concluded without red. At this head Analyze (python), closures, coverage, fast (3.14) were still in_progress at read: not cited; the merge train's CI gate decides.
RESULT invariants: VERSION, manifest version, notes heading, claim files untouched.
Head in body: 29d863f7b08f09f1003505bd21ef9ebebf3bb3d1 present.

Not re-derived: entities `2191` at the new head -- I measured 2191/2191 at e1531dbb; the delta adds no entity check and I did not re-run the 8-minute script (CI's fast lane covers it).

Non-blocking observations (outside the body's grep class, for the orchestrator):
- record.opens still lists `.claude/workflows/wave-4-groups.json`, absent at the head (now dev/archive/rosters/wave-4-groups.json). Same dead-path shape; role cost is driven by rule globs, so no figure moves either way.
- No MAIN_STATE_REPORTERS case pins the `dev/programme/HANDOVER.md` REPORTER_INPUTS entry alone (M3 removed it together with the plan entry); dropping only that entry would survive.
- web-stamp.js is a Workflow body (top-level return); `node --check` rejects it at both heads, so syntax was not machine-checked -- the edit is inside one template string.

Forward-carry: none claimed; none needed.
