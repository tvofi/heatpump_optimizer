Fix review: merge 291c40e4e1d1a4e3931ab8fd7d8f7096cb1a1ee1

bus-nonce: 8b847983e879daec745aabe011ff1f4e

Round 1, record PR (no production code). Measured head 291c40e4e1d1a4e3931ab8fd7d8f7096cb1a1ee1.

## Findings

none

## Evidence

- Three-dot diff names exactly two files: dev/programme/delivery/3144.md and dev/programme/triage/s6-batch105.md. No claim file, VERSION, manifest, RELEASE_NOTES or golden change; no host path in added lines (ev/diff-files.txt).
- PR body: ## Head names the head and its authored code head; ## Red checks says none. Whole check-run set at the head (packet digest, all pages, plus merge_train classify): GREEN, pending none, red none (exit 0).
- merge-tree with origin/main (56630e7e6): exit 0, clean.
- P362 facts re-derived at origin/main: update_pr.sh line 23 sources pr_args.sh via dirname $0, line 32 sets M from --git-common-dir, line 42 is cd "$M", line 51 calls pr_tools_fresh; pr_args.sh line 171 resolves d from BASH_SOURCE[0] at call time, line 371 (pr_pushers default root) does the same; open_pr.sh calls pr_tools_fresh at line 93, before its only cd $WT at line 99. The only other BASH_SOURCE reader (line 420) is inside the self-test, not a production function. PR_FRESH_PATHS is at line 168. Ruling is consistent with the code.
- Roster (handoff/audit-r10-roster tip 6b279e3b5; the cited 9c1bb4673 is its ancestor): R10-OPENER-REUSE exists, stage not-started, after = [], owns update_pr.sh and open_pr.sh; R10-FLY-RELAY-REVIEW-FF is carries-open, so R10-RELAY-HANDOFF-ARM (after it) cannot be dispatched yet. The stated reason for choosing OPENER-REUSE holds. The group's files list does not name pr_args.sh; the carry text names it, so the fixer's scope is stated there.
- Open PRs: #3055 touches pr_args.sh; #3089 touches pr_args.sh, update_pr.sh and its instrument page. The "land after or rebase over" instruction matches.
- Carry text matches the ACCEPT ruling (fix in pr_args.sh, source-time variable beside PR_FRESH_PATHS, used by pr_tools_fresh and pr_pushers, controls in the fresh() arms, null, one mutant). The ruling states its one measured instance and its null control.
- "grep -n pr_args tests/*_budgets.json prints nothing" and HOT_FILES membership of both scripts re-derived (HOT_FILES in review_packet.py).
- Naming nit: the title and body say "s9 batch 105" while the file says session s10; the file's own attribution is internally consistent and no ruling depends on it.
- Not re-run: the body's roster_edit mutation proof and brief_lint figure (packet figure_lint resolved 2, not verified 0). Cheap-detector only; not a code change.
- carry_audit at head: 0 finding items.
