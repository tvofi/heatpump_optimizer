Fix review: blocked e8c3fe927bb9a1d070f458d6aed9173d8a8bb192 stale-base: P401's defect is already fixed in this PR's own merge base, so the ACCEPT would re-dispatch landed work

bus-nonce: 424b69ed9765a5003896acbb9a62f600

Round: 1. Head measured: e8c3fe927bb9a1d070f458d6aed9173d8a8bb192 (still the head at posting).

## Block
- The ruling measures at origin/main 294a880da (2026-11-07 04:11). The PR's merge base d9af08062a (2026-11-09) contains 1e994e484 (2026-11-07 14:12, "pr_args.sh fixes its directory at source time", carries 7 and 16). At that commit pr_args.sh has `PR_ARGS_DIR=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)` at source time (line 181, mut:argsdir) and pr_tools_fresh reads it (line 183). The existing self-test at line 644 is the relative-source-then-cd arm that the ruling's Binding asks for.
- 294a880da has 0 occurrences of PR_ARGS_DIR; the head has several (ev/base294-count.txt, ev/head-count.txt).
- dev/programme/triage/s6-batch105.md (P362) already rules the same defect ("pr_tools_fresh resolves its directory after update_pr.sh has changed directory") and carried it to R10-OPENER-REUSE.
- The ruling's carry text asks R10-HANDOFF-PATH for "Resolve the directory once at source time (an absolute PR_ARGS_DIR beside PR_FRESH_PATHS)", which is already in the tree. Merged as written, a fixer would be dispatched to redo it.
- What would clear it: re-measure at the current main. If the defect no longer reproduces, rule P401 as a duplicate of P362 (a REJECT or a close naming 1e994e484). The part that may still stand is the operational one: the dispatch seat's scripts still export HPO_ALLOW_STALE_TOOLS=1 and can drop it. That is not a repo change.

## Findings
- Residual: the 77 STALE-CHECKOUT-notice count and the 175-commit lag were taken before 1e994e484 and cannot describe the current tree; I did not re-derive them. Carry: dismissed: moot if the PR is re-ruled; the fixer re-measures per its Binding.

## Evidence
- classify: GREEN e8c3fe927bb9a1d070f458d6aed9173d8a8bb192 pending: none red: none.
- merge-tree origin/main e8c3fe927bb9a1d070f458d6aed9173d8a8bb192: clean, rc 0. Diff vs d9af08062a is delivery/3383.md and triage/s6-batch130.md only; VERSION, notes and goldens untouched.
- Mutation proof: roster_edit.ruling_verdict on the file reads P401 ACCEPT, P402 None; flipping the verdict line gives REJECT. Reproduced.
- Citations at 294a880da: update_pr.sh cd "$M" line 53, pr_tools_fresh line 62; open_pr.sh cd "$M" line 42, pr_tools_fresh line 95; pr_tools_fresh at 168-179. Match the file.
- Destination R10-HANDOFF-PATH exists on handoff/audit-r10-roster d7d5ba411.
- The host-local log counts and the repro worktree were not re-derivable here.
- carry_audit on the packet: 0 finding items before this verdict.
