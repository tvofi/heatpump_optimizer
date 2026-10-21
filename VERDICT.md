Fix review: blocked 085a4cafa84022120460fd23701a21883321536f harness: class-open tools/audit/seat/ci_predict_replay.sh:47

Round 2. Group: none (no entry for r10-openpr-row-push in origin/handoff/audit-r10-roster's dev/programme/rosters/wave-r10-groups.json at 31e162fd3, searched with jq). Reviewed against the PR body.
Measured at head 085a4cafa84022120460fd23701a21883321536f (ev/HEAD.txt). Before writing, refs/pull/2560/head and fix/r10-openpr-row-push-pr were still 085a4cafa84022120460fd23701a21883321536f. Merge base 289426c1f. dev/governance/roles/ is the same at the merge base and at origin/main 3688cf259.

## Blocking

1. **class-open** (step 6). The body's enumeration rule (`grep -nE "checkout -q --detach|reset -q --hard|worktree add -q -B|worktree remove --force|branch -D" tools/audit/seat/*.sh tools/audit/seat/*.py tools/pr/*.sh`) returns 43 lines at this head (ev/class-search.txt). `tools/audit/seat/ci_predict_replay.sh:47` (`git -C "$here" worktree remove --force "$wt"`) is not a self-test or app_approve fixture, it is not in the diff, and the body does not disposition it (`grep -c ci_predict_replay` on the body = 0, ev/body.md). Round 1's verdict listed it and said "The re-pushed body should name it". My reading is that it is outside the class: it force-removes only `$scratch/wt-$sha`, a detached worktree it adds itself under a caller-given scratch directory, and it holds no branch. So the fix is one disposition line in the body and no code. That disposition is mine and not the body's, and the contract does not let a reviewer supply it.

## Non-blocking (fix in the same body edit)

- The figures line quotes `ref_privacy --check`: "111 line(s) added since 289426c1fdde judged". At this head and at the code head 88a352d3b it prints **113** (ev/ref-privacy-head.txt, ev/ref-privacy-codehead.txt). 111 looks carried over from round 1's base 03b49e152. Not verified as quoted.

## Round-1 blocking items: resolved at this head

RESULT r1-item1 instrument-self-tests: `python3 -I tools/audit/seat/ref_privacy.py --check` prints `19 file(s) with a push site, 9 guarded, 113 line(s) added since 289426c1fdde judged, 0 refused`, rc 0 (ev/ref-privacy-head.txt). CI's instrument-self-tests check-run 119221975434 succeeded on this head. `--self-test` prints `66 checks, 0 failed` (ev/ref-privacy-selftest.txt).
RESULT r1-item1 mutant: deleting the new PUSHERS entry for pr_args.sh makes `--check` print `REFUSE tools/audit/seat/pr_args.sh:353 ... 1 refused`, rc 1 (ev/mutant-pushers.txt). The entry carries the fix. Step 14: the diff names one file with a reason and changes no rule, scope or pattern, so ref_privacy is not gamed. The stub at pr_args.sh:353 pushes only to the self-test's scratch origin, which matches the "fixture" reason.
RESULT r1-item2 pr-contract: `carry_audit.py check --body` on the current body prints `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (ev/carry-audit.txt). Both pr-contract runs on this head succeeded (119221974401, 119223585472). The rows follow-up for #2547/#2548/#2549 moved into the Summary as the orchestrator's follow-up. Forward-carry is none, and nothing in the diff changes how a later stage works, so step 10 has nothing to carry.
RESULT r1-item3 red checks: the body's `## Red checks` names instrument-self-tests and pr-contract with a cheaper detector and a standing cost each, and calls nightly-status main's. At this head the only red is nightly-status (119221976298), which grades main, and this diff does not reach what it reads. Not all of the head's runs had concluded when I checked (Analyze (python) and browser in progress; coverage, fast (3.14) and typing queued; ev/check-runs.tsv). No root-cause-unanswered applies.

## What holds (carries forward)

RESULT delta: the authored diff at this head equals round 1's (03b49e152...f8694ba2d) plus exactly the two PUSHERS lines (ev/delta-r1-r2.diff). So round 1's mutants A-E on production lines (oplock, unpushed, both, a differently named lock, an inverted ancestry check), all killed, and its null control (62 checks, 4 failed at 43f79c08b with the head's pr_args.sh) carry unchanged.
RESULT selftest-head: `pr_args self-test: 62 checks, 0 failed`, `delivery_row self-test: 5 checks, 0 failed`, rc 0 (ev/selftest-head.txt). This matches the body.
RESULT merge: `git merge-tree --write-tree origin/main 085a4cafa84022120460fd23701a21883321536f` (origin/main 3688cf259) exits 0 with tree 2e21422a7 and no conflict (ev/merge-tree.txt).
RESULT structure: `STRUCTURE RATCHET PASSED` (ev/structure.txt).
RESULT untouched: VERSION, the manifest, RELEASE_NOTES, the claim files, *_budgets.json and closures.json are not in the three-dot diff (ev/untouched.txt).
RESULT head-in-body: the body names 085a4cafa84022120460fd23701a21883321536f as the head, with code head 88a352d3b. Both confirmed.
Harness: there is no committed finder harness. The finding's evidence is the reflogs and lock files in the body. The race arm is the fixer's own instrument, disclosed as such. I measured with it, with round 1's mutants, and with my PUSHERS mutant.
Not re-run: archscore (the round-2 delta is a registry dict entry) and entities.py (closure-scope is green on this head, 119221976399).

bus-nonce: fa6eb2e975611e9aca353f4d9f00ea4d
