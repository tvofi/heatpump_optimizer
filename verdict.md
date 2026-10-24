Fix review: merge b475cb1061a7bc3671b876daba665b3b95afff41

bus-nonce: 5a25570bb786266a4cfcdf9037773f30

## Scope

PR #2764 (round-10 roster batch, critical path), reviewed at head b475cb1061a7bc3671b876daba665b3b95afff41, the live head when the review began and again when this verdict was written. Review round: the first verdict by this seat on this PR; the earlier head 6fdf9bf5d is superseded per the body. Role file dev/governance/roles/fix-review.md read from origin/main; the merge-base...origin/main diff of dev/governance/roles/ is empty.

## Evidence

- Diff (three-dot, merge base 0810d5b8f): exactly two paths, dev/programme/rosters/wave-r10-groups.json (+283/-17) and dev/programme/delivery/2764.md (+1, the PR's own delivery row). VERSION, the manifest and RELEASE_NOTES.md are untouched. ev/git_checks.txt
- The roster at the head is byte-identical to origin/handoff/audit-r10-roster 1558cf55fb9073f3d3dbe72c536a186906657775. That branch is 35 commits past its base 50c690758, every one a `roster_edit <op> <group> (tools/audit/seat/roster_edit.py)` commit, and all 35 touch only the roster file. ev/git_checks.txt
- Null control: no main commit has touched the roster between 50c690758 and origin/main, so this overwrites nothing. My keyed comparison finds 0 groups removed, the original 181 groups in their original order as the head's prefix, and no top-level key changed. ev/figures.txt
- Every figure in the body re-derived independently, in Python keyed on `group` (my own comparison, not the body's jq): main 181, head 187, 6 new (the six the body names), 12 changed. resume.stage main→head: done 102→105, not-started 45→49, in-progress 21→21, queued 6→6, carries-open 6→5, absorbed 1→1. All match. The 12 changed groups and their changed fields are listed in ev/figures.txt; only after, carry and resume move.
- JSON valid. The file round-trips byte-exactly through `json.dumps(indent=1)`, roster_edit.py's canonical form, so there is no hand splice. ev/json.txt, ev/roundtrip.txt
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` at the head: `TOTAL: 0 error(s) across 1 file(s)`, matching the body. ev/brief_lint.txt
- Mutant on the instrument: planting a dangling `after` edge (R10-FLOW-AUTOTRAIN → R10-NOPE-MUTANT) makes brief_lint print 1 error; the file was restored afterwards. So a 0 here means something. ev/mutant_dangling_after.txt
- Carry reachability, with `carry_audit.py check` over the body's Forward-carry lines. With `--roster-ref` at this head: `1 routed, 0 unrouted, 0 bad destination(s)`. With `--roster-ref origin/main`: `BAD-DEST ... R10-RCA-CODESCAN-WAIT is not a group of the roster; R10-TRAIN-UPGRADE is not a group of the roster`. That second run is the refusal this PR exists to clear, so the both-ends check holds. ev/carry_audit_head.txt, ev/carry_audit_main.txt
- Carry content at the head, checked against the body:
  - R10-RCA-CODESCAN-WAIT has 1 carry entry, from R10-GATE-DEFER 5150d172. It names M1 (and M4's self-test case) as landing in R10-GATE-DEFER and M3 as still owed here.
  - R10-ORCH-LEDGER has 12 entries. The 12th is the R10-GATE-DEFER GATE_WAIT_MAX_S text.
  - R10-FLOW-AUTOTRAIN has 9 entries; the two new ones are the train-upgrade and re-scope text. Its `after` now includes R10-TRAIN-UPGRADE.
  - R10-TRAIN-UPGRADE's brief is the owner-ordered merge_train.py upgrade.
- `python3 tools/audit/seat/roster_sync.py --self-test` at the head: `roster_sync self-test: 55 checks, 0 failed`. `carries-open` is in PROTECTED_STAGES on main (05d056931). ev/roster_sync_selftest.txt
- Merge: `git merge-tree --write-tree origin/main b475cb10` exits 0 (tree 5ddbedf7a) with no conflicting path; origin/main is 0810d5b8f, the PR's base. ev/git_checks.txt
- CI on this head, from the check-runs API, every run completed: 35 success, 17 skipped, 1 neutral (CodeQL summary), 0 failure. This includes gate (both runs), pr-contract (both runs), governance / instrument-self-tests, tests / closures, tests / fast (3.14) and tests / briefs. ev/check_runs.txt
- No gate check is red on this head, so step 11 is owed no answer. The mutation lane drew no mutant (the diff holds no production line); the heavy runs are cited, not re-run.
- Step 6 (class rule) and step 14 (moved metrics) do not apply: the diff is roster state only and moves no budget, closure, golden or score.
- Step 7: the body names b475cb1061a7bc3671b876daba665b3b95afff41, the head reviewed.

## Findings

- The body's `## Red checks` paragraph is stale at this head. It says governance / instrument-self-tests stays red until a separate roster_sync.py fix lands, but that fix (05d056931) is already on main, and the check is green on this head. The paragraph answers a red the head does not have, and no rule needs it. Carry: dismissed: wording only, no red check exists at this head to answer
- The body's `## Head` first paragraph says b475cb10 "merges origin/main 0810d5b8f ... into this PR's previous head". The history has no merge: 94a1b7de3 is a single commit on 0810d5b8f and b475cb10 its child, which the second paragraph describes correctly. Carry: dismissed: inaccurate body template sentence, the head SHA and diff are correct
- The body says R10-RCA-CODESCAN-WAIT "carries its countermeasures M1 and M3". The carry itself records M1 (and M4's case) as landing in R10-GATE-DEFER and only M3 as still owed in R10-RCA-CODESCAN-WAIT. That group's brief still names R10-CI-LAYOUT-P2 as the countermeasure destination, which the carry entry corrects ("its former destination, is done"). The carry is the binding text, and it is correct. Carry: dismissed: the roster carry already states the correct split and supersedes both the body's summary and the brief's stale destination
