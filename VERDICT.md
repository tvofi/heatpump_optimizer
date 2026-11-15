Fix review: blocked 6dc42ccc267162b473d552d5f39f389d9c9a224e class-open: tools/audit/seat/body_push.sh:175

bus-nonce: 1ba2f55ff2cd00bf075a06e2e2106054

## Block
The body's class rule (`grep -n "figure_block.py\" refresh" tools/audit/seat/*.sh`) returns three call sites at this head (ev/enumeration.txt): update_pr.sh:107 and open_pr.sh:122, both closed here, and `tools/audit/seat/body_push.sh:175`, which runs `figure_block.py refresh "$ABS"` with no `--base`, so it renders against figure_block.py's default `origin/main` (tools/pr/figure_block.py:280). It is neither in the diff nor dispositioned in the body's "Class seams" line, which lists two sites. body_push.sh is the handoff body push; the body must either close it (take the recorded base where a PR exists) or state why `origin/main` is correct there, as it does for op_figures p1.

## Evidence
- Head measured: 6dc42ccc267162b473d552d5f39f389d9c9a224e (ev/HEAD.txt). Round 1.
- classify at head: GREEN (ev/classify.txt). merge-tree against origin/main: clean (ev/merge-tree.txt).
- `pr_args.sh --self-test` at head: 269 checks, 0 failed (ev/pr_args-selftest.log), including mut:opbase and mut:updbase killed, the equal-base null control and the unreadable-base refusal. The two closed sites are sound.
- VERSION, manifest, notes, claim files, budgets and closures untouched.
- carry_audit: 0 findings.
