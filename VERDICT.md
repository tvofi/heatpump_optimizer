Fix review: merge fdc625099581f2f29f88caf2cc1dfddc94190645

bus-nonce: 11e9125b70fe47838695bd9ec76e4149

Round 1. Head measured: fdc625099581f2f29f88caf2cc1dfddc94190645 (re-read before posting; PR head is unchanged). Authored code head per body: bd13371c8; the extra commit adds only dev/programme/delivery/2983.md.

## Findings

None. The diff is two markdown files (the triage batch and its delivery row); no production code, budget, closure, claim, VERSION or notes line moves.

## Evidence

- RESULT already_held rule: at 882da1e01 (a commit, subject "Merge remote-tracking branch 'origin/main' into fix/r10-train-overlap-grade") tools/audit/seat/merge_train.py has `def already_held` at line 885 and `READMIT_SAME_VERDICT = (HOLDER, BRANCH_POLICY)` at line 685, as the body and triage say. Its docstring and the train_add (952, 970) and Train.queue_take (2767, 2780) callers match the triage's description of one shared predicate (ev/rule-lines.txt).
- RESULT #2978: head 882da1e01b3d, APPROVED by tvofi at that commit (review 5709680248), mergeable_state clean. It is still a draft PR per the API (draft: true). The merge verdict ref is origin/verdict/2978 (the packet's figure_lint also resolves 'gh pr view 2978'). #2982's verdict ref reads "Fix review: merge 8fd2d73a28f4032d593de1f5bc32f198062317f3", matching the triage's "8fd2d73a".
- RESULT mutation proof (ev/mutation-proof.txt, run in a detached worktree at the head): ruling_verdict reads P298 as ACCEPT and triage_refusal returns None for the citation; with Verdict: ACCEPT changed to REJECT it is refused ("is not an ACCEPT ruling (REJECT)"); with the file absent it is refused as not on the roster branch or origin/main. Matches the body.
- Train-log line numbers (#2976 2922/2956, #2980 2873/2903/2957, #2917 2542/2644, 2339-2341): not re-derivable here. merge_train/train.log is on the orchestrator's machine and this cloud checkout has none (packet figure_lint: 1 resolved, 1 not verified). Not verified by me; they are quoted as read from the live log, and nothing in the repo depends on them (the only consumer of the file is roster_edit's ruling gate).
- RESULT Carry destinations: carry_audit at the head: 0 finding items, 0 unrouted, 0 bad destinations. The body has no findings, no forward-carry (none) and no Carry lines; the triage adds no group or carry, and names R10-TRAIN-OVERLAP-GRADE, which #2978 carries.
- RESULT body vs head: the body's "## Head" names fdc62509 as the PR head and bd13371c8 as the authored code head, and the diff (2 files, 63 additions) matches. Name s6-batch67.md follows the existing s6-batch<N> file series.
- RESULT merge: git merge-tree --write-tree origin/main fdc625099581f2f29f88caf2cc1dfddc94190645 exits 0 (origin/main aced25893 equals the PR base; ev/merge-tree.txt).
- RESULT VERSION/manifest/RELEASE_NOTES untouched (three-dot diff lists only the two files). No Claude footer, Co-Authored-By or session link in the commits (git log --format=%B).
- CI at this head (check-runs API, read after about 5 minutes): no red check. Success: CodeQL x4, arch-score, budget-raise-gate, delivery-status, mutation, nightly-status, policy-docs, wave-script, hassfest, validate-hacs, briefs, closure-scope, arch-instrument, typing, fast (3.14), browser. Skipped: record, kernel-points, replay and the autofix lanes. Still running at read time: closures, coverage, env-matrix, instrument-self-tests. Those four are not required to be re-run by me; none can be moved by a markdown-only diff in a way I can see, and I did not wait for them. Sections 'Red checks: none' is therefore consistent so far.
- Not run: the claim drift, structure and card checks (the diff touches no fixture, budget or card); the finder's-harness measurement (none named; the diff is a ruling document).
