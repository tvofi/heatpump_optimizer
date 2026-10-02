Fix review: merge 96caaf6c8477b3fd962cd3de37613e0974ae410d

PR #1820, R9-PROC-3, round 3. This round judges only the merge delta. 96caaf6c merges main 411368b6 into eff1a2a3. The combined diff (`git diff-tree -c`) names only `tools/audit/briefs/fixer.md`, so every other file merged cleanly. Judged: `git diff 411368b6 96caaf6c -- tools/audit/briefs/fixer.md` (`fixer_vs_main.diff`), against main's own change since 90335cbd (`fixer_main_side.diff`).

## Is any rule lost from either side?

**PROC-1 (main) keeps everything.** The result against main removes no PROC-1 text:
- the roster `jq` and background-job lines;
- the line saying pinning is `mutation-autofix`'s and that local `--pin-killed` is not used;
- "steps 2–8 re-executed (past the handoff, where its delta reaches)";
- the "merge, never a re-cut" paragraph;
- the landing paragraph;
- the trimmed ratchet text.

**PROC-3 (this PR) keeps everything.** Its three changes to fixer.md land:
- "Seats are LOCAL-ONLY … hand off locally" is dropped, and the orchestrator opens the PR as `hpo-author`;
- the body rides `handoff-body/<topic>` through `body_push.sh`, off the code head, and `prepr.sh` step 1a enforces that;
- the orchestrator writes the delivery row.
PROC-3's own landing clause ("the only merge that ever was") gives way to PROC-1's merge-not-recut paragraph. That paragraph is the newer rule from tvofi and it supersedes the clause, so nothing that still binds is lost.

**What was dropped in the compression is reasons and pointers, not rules:**
- the reason clause "the worktree `app_push.sh` refuses when dirty";
- the wording "fast-forward" and the root paths after "step 1a";
- the path citation `docs/decisions/0011-app-authored-identity.md`, now just "(decision 0011)".

## Checks at 96caaf6c (`checks_96caaf6c.txt`)

- `policy_lint.mjs`: TOTAL 0 errors across 40 policy files.
- `--budgets`: fixer.md is at 278/280 lines and 4585/4585 tokens, within the cap and not raised.
- `rules_sync --check`: ok.
- The fixer's self-test (146/0), structure, entities, brief_lint and prepr-with-body figures are cited, not re-run.

## Non-blocking, routed to PROC-1 with orchestrator.md

- **Last path citation of decision 0011 removed.** This merge removes the only remaining citation of `docs/decisions/0011-app-authored-identity.md` from a brief: at 411368b6 fixer.md was the one hit, and at 96caaf6c no brief cites it. `policy_lint.mjs:548-552` still says "fixer.md and fix-review.md cite it and are capped", which is now stale. No check refuses this, because 0011 is not in `EXCLUDED_BECAUSE_CITED`. Either restore the path once the cap allows, or correct that comment.
- **`orchestrator.md` still says "LOCAL-ONLY"** (seats LOCAL-ONLY). This is outside this delta.

CI was not re-run, per the review rules. The merge still owes green CI at the PR head and tvofi's code-owner approval.
