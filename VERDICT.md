Fix review: merge b2de1d2fda8645b62f5665505f2e57c86d205a5a

bus-nonce: d36408bfe58001f3f637b1a76f5f3e4f

Round 1 of review for #2763. I measured head b2de1d2fda8645b62f5665505f2e57c86d205a5a, which was still the live head of `triage/s6-batch18` when this verdict was written (ev/scope_merge_commits.txt). origin/main and the merge base are both 0810d5b8f. The role contract is current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.

## Findings

- In the ruling, the #2758 instance says "pr-contract was red with \"`## Head` does not name 7f91e68\"". The verdict on #2758 (comment 6388869259) gets that message from the reviewer's local `policy_lint.mjs --pr-body` run, and says "No `pr-contract` run was listed among the head's 32 check runs". From this seat I could not read the check runs at 7f91e684, so I could not confirm that a pr-contract run went red there. The instance itself is real either way: the Head was stale after row commit 7f91e684, the review was blocked `body-head-stale`, and the body was re-taken. The count of 3 and the Binding do not change. Carry: dismissed: the wording of one instance's symptom does not change the ruling, its count or its destination.
- The body's `## Head` note says b2de1d2 "merges origin/main `0810d5b8f` ... into this PR's previous head". In fact b2de1d2 has one parent, 69efb1cb, which already sits on 0810d5b8f, so no merge commit exists. `tools/audit/seat/update_pr.sh` line 70 writes the "merges origin/main" clause whether or not `git merge origin/main` did anything. The SHAs in the note are correct, and pr-contract's body check accepts it (ev/pr_body_lint.txt). Carry: dismissed: the clause is wording only; every SHA in the note is correct and the body contract keys on the head SHA, so there is nothing for a later stage to fix.

## Evidence

- Scope: the three-dot diff from 0810d5b8f is exactly `dev/programme/triage/s6-batch18.md` (+24) and `dev/programme/delivery/2763.md` (+1). VERSION, the manifest and RELEASE_NOTES.md are untouched. Both files are under `dev/programme/`, which is INERT in `tests/closure.py` (line 273) (ev/scope_merge_commits.txt).
- Delivery row: `dev/programme/delivery/2763.md` is in the three-dot diff. It is one line naming #2763 as open with the PR's title, in the merged rows' shape, and it is the PR's own row.
- Body Head: it names b2de1d2fda8645b62f5665505f2e57c86d205a5a, the live head, and gives the code head as 69efb1cbb on merge base 0810d5b8f. That matches `git log`. This note is the one `update_pr.sh` writes, so this PR's own row went through the path the ruling prescribes.
- RESULT policy_lint: `policy_lint.mjs --pr-body` on the live body at --head b2de1d2 gives `PR-BODY: 0 error(s)`, red-history `record`, 2 commits, no failure conclusion (ev/pr_body_lint.txt). The perturbation, which points the Head note at 69efb1cb, gives 1 error, "`## Head` does not name b2de1d2" (ev/pr_body_lint_mutant.txt). So the check bites, and this is the instance class the ruling addresses.
- RESULT ruling_verdict: P87 = ACCEPT, and P99 = None (the null control, re-run) (ev/ruling_verdict.txt).
- RESULT figures: the body's `rg ... | uniq -c` gives `1 ACCEPT`, which matches (ev/figures.txt). Numbering: s6-batch17.md (P86) is on origin/triage/s6-batch17 and not at base, as the ruling says. Batch 16's file is not at base either. P87 does not appear in any other triage file.
- The ruling matches its finding. Each tree claim was read at the head:
  - `update_pr.sh` with code sha `-` calls `ensure_row` (line 63), prefixes `## Head` through `head_note.prefix` (lines 68-70), and pushes with `--row-only` (line 74).
  - `delivery_row.sh` defines `write_row`, `row_line`, `commit_row` and `ensure_row`, and `row_line` keys on the PR number. That supports rejecting candidate (b).
  - `open_pr.sh` calls `commit_row` and `head_note.prefix` (lines 50-65).
  - `app_push.sh` has the `--row-only` verdict (lines 107, 198-237).
  - `bus.sh dispatch` refuses a head without its row (line 378, self-test lines 733-738).
  - So ACCEPT (no code), with the barrier in the two seat briefs, follows from the cause the ruling states.
- Instances:
  - #2755: row commit 06cb984b exists ("record: the delivery row for #2755"). Verdict comment 6388572020 is "blocked ... body-head-stale", and it was later merged after a body re-take.
  - #2758: row commit 7f91e684 exists. Verdict 6388869259 is body-head-stale.
  - #2759: row commit 5c824098 is followed by an amendment, dcec0b01, which masked it, as the ruling states.
  - The source, s6 `proposals.md` `## V22`, is out of tree. It is named as such and I did not re-derive from it. "GitHub calls: 0" is the seat's own figure and cannot be re-derived.
- Mutation proof: n/a. The diff writes no production line, so `mutation` (green) drew no mutant. The `ruling_verdict` consumer check stands in.
- Forward-carry: the destination is the orchestrator's out-of-tree triage-seat and dispatch-seat prompts, with no roster group. That matches `## Forward-carry: n/a` and leaves nothing to open in a roster.
- Merge: `git merge-tree --write-tree origin/main b2de1d2` exits 0, tree 31f2fa9ef539. There is no conflict and no claim-file driver call.
- CI at b2de1d2 (ev/check_runs_summary.txt): 34 check runs, none concluded failure. Several were still queued or in progress when I read them (coverage, closures, typing, fast, browser, env-matrix, instrument-self-tests, codeql, arch-instrument). pr-contract and gate were not yet listed. The body's `## Red checks: none` holds so far, and the local body check above is the one pr-contract runs.
- Commits carry no Co-Authored-By or session trailer, and neither added file has a host or home path.
