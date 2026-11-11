Fix review: merge 0cd785173433173b4f6e9d16a1b161bef464c516

bus-nonce: 5c96eff27e6a8d6b7aa37b48ab891aa1
pending-ci: gate (classify printed WAIT, pending, gate red: none, on every poll from 20:49 to 21:14 UTC)

Carry-only delta review: the merge of origin/main keeps the branch's own diff identical in every added and removed line; only context and hunk offsets moved.

## Evidence

- Scope: carry-only delta dee7a1fa45bb..0cd785173433 is a merge of origin/main (61afd4f2db10, parent 2) into the branch; no fixer commit (ev/HEAD.txt, `git cat-file -p` shows the two parents).
- Branch's own diff, old (merge-base cd36e79737..dee7a1fa45bb) against new (merge-base 61afd4f2db10..0cd785173433): the same 16 files, the same 489 insertions and 7 deletions (ev/branch-diff-old.diff, ev/branch-diff-new.diff).
- With the `index` and hunk-header lines removed the two diffs differ in exactly one place (ev/branch-diff-content-delta.txt): the two context lines of the hunk in tools/ci/selftest_closures.json that precedes the added `figure-block` entry. The old context read `"index": true, "objects": false`; the new one reads `"objects": false, "git": []`. Every added and removed line is byte-identical. The remaining differences are hunk-header line offsets in .github/workflows/governance.yml, tests/closures.json, tools/audit/seat/INSTRUMENTS.md, tools/policy/policy_lint.mjs and tools/pr/prepr.sh, shifted by main's own insertions above them.
- Why: main touched six of the branch's files (ev/overlap-files.txt). The five above only moved the branch's hunks. The sixth, tools/ci/selftest_closures.json, had its neighbouring entry rewritten by main (#3474/#3453 side: `"index": true` dropped, a `"git": []` key added), which is what the carry check saw as a changed diff.
- Both sides kept: the head's selftest_closures.json holds main's rewritten neighbour entry and the branch's `figure-block` entry unchanged (run_sha 7295269b8e4e..., files tests/throwaway_git.py and tools/pr/figure_block.py, `"index": false, "objects": false, "git": []`), and it carries main's `git` key on it. The `"index"` key count is 112 against main's 111 and the `"git"` count is 112 against 111, i.e. exactly the branch's one added entry; the file parses as JSON. The added `tests/closures.json` lines (main's remerge_main_selftest.py and harness entries) remain main's and the branch's entries are untouched.
- `git merge-tree --write-tree origin/main 0cd785173433` is clean (ev/merge-tree.txt); origin/main is 61afd4f2db10, the head's second parent, so the head is not behind main.
- Previous verdict findings: none to resolve (its `## Findings` was `none`).
- No production (custom_components/) file is in the delta, so nothing widens the review (fix-review.md step 12).
- CI: classify at this head printed `WAIT ... pending: gate red: none` on every poll made (no red at any poll).

## Findings

none
