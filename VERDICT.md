Fix review: merge 93ba227138a2c024bf81e44e74f2b11cb572bd76

bus-nonce: 4dd5b1a4590a2321a847ad3fe72b5b1b

## Findings

- Residual: line 9 of the PR body is still stale at this head, as the previous verdict found. It cites `git diff --shortstat 0a8033305d...HEAD` as `39 files changed, 578 insertions, 761 deletions` and says `git diff --name-only 0a8033305d...HEAD -- custom_components` is empty. Re-run at this head, those commands print `2216 files changed, 138804 insertions(+), 9608 deletions(-)` and 52 paths, because 0a8033305d is far behind the merge base. Against the merge base 13cbe48de4, the PR's own figures are `40 files changed, 602 insertions(+), 755 deletions(-)` and 0 `custom_components/` paths (ev/body_line9.txt, ev/head_unchanged.txt). The sentence's claims still hold: the PR deletes more than it adds and writes no production code. Only the base and figures are stale. Carry: dismissed: body hygiene, no later stage reads the figure, and measured against the merge base the PR still deletes more than it adds and touches no custom_components path

## Evidence

- **Round.** This is a re-issue round at an unchanged head, after the previous verdict on probe/rev-3451-546905d0 (1e6e309a7473d637f353ddc1ce5f761a1412612d). That verdict was `blocked ci-red` only because the required job `governance / policy-docs` was cancelled at its timeout in run 43688486622. The packet's `## Review scope` reads `delta` over reviewed head 93ba2271, and its delta diff is empty. The original change was not re-reviewed, as the brief directs.
- **The head is unchanged.** `git ls-remote origin refs/pull/3451/head` prints 93ba227138a2c024bf81e44e74f2b11cb572bd76, and the GitHub PR API reports the same head. The previous probe's `ev/HEAD.txt` names this same SHA. Its tree is cd15f7d77bc50fb63d46491314068425bf1d8e66, and `git diff 93ba2271 93ba2271` is 0 bytes (ev/head_unchanged.txt). So the tree is the one the previous verdict measured.
- **CI is APPROVAL-OWED, the only state that now separates this PR from merge.** `merge_train.py classify 93ba2271 --pr 3451` exits 4 (ev/classify_last.txt). It prints: `APPROVAL-OWED 93ba227138a2c024bf81e44e74f2b11cb572bd76 2 budget raise(s), first .claude/workflows/policy_budgets.json: files.dev/governance/roles/proposal-triage.md: 36 -> 40 (a cap went up): a raise is the owner's (0013): tvofi's approval is on 939c91fc0e31, not this head 93ba227138a2: an approval covers only the commit it was given on`. I judged the head as GREEN, as the brief directs. The owner's approval follows this verdict.
- **The previous block is resolved.** The packet's live digest shows the re-run `governance / policy-docs` job, id 132743706674, at `success`. The cancelled job was 132734039270. `gate` (132745271028) and `budget-raise-gate` (132745294630) are red only on the owed approval, as the packet's `approval-owed` advisory confirms. Every other required context in `merge_train.py owed-reds` (ev/owed_reds.txt) is `success` in the digest (ev/review_packet.md).
- **Merge with main.** At origin/main b046b22d6ed8e0ebc5fead18b6f5cd9178b1b12d, `git merge-tree --write-tree origin/main 93ba2271` exits 0 with tree 4f7b2f60d8098df1f1097c9223b603bae8982367 (ev/merge_tree.txt). I committed that tree and ran `node tools/policy/policy_lint.mjs --budgets` on it, with rc 0 (ev/budgets_merged.txt). It prints:
  - `corpus: ~69077 tokens, cap 69333 +band 500 = 69833`
  - `always-loaded ~3604 / 3849`
  - `role fixer ~6279 / 6352`
  - `role record ~7236 / 7905`
  - `role policy ~10012 / 10458`
- **Previous findings re-measured at the head, not copied.**
  - `bash tools/audit/seat/bus.sh --self-test` prints `bus self-test: 239 checks, 0 failed`, rc 0, on Linux (ev/bus_selftest_head.txt). The tree is unchanged, so mutants A and B of the previous round still apply to the same lines. I did not re-run them.
  - `policy_lint.mjs --budgets` at the head prints `dev/governance/roles/proposal-triage.md 40 40 563 563`, rc 0 (ev/budgets_head.txt).
  - `grep -c proposal-triage dev/governance/config/policy_budgets.json` prints 2 at the head.
- **Versions.** Against the merge base, `git diff --name-only` over `VERSION`, the manifest, `RELEASE_NOTES.md` and both claim files prints nothing (ev/body_line9.txt).
- **Mutation.** The delta is empty and writes no production line, so no new targeted mutant is owed.
