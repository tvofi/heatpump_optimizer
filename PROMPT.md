CLOUD DESIGNER seat for tvofi/heatpump_optimizer, topic r10-audit-coverage, at head 437f1ba9b521199b360d84effe6a621573d34663. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/designer.md from main, and follow it exactly. The base is 437f1ba9b521199b360d84effe6a621573d34663 (`git fetch origin 437f1ba9b521199b360d84effe6a621573d34663`); name it in the note. Write no production code.
Output: write the note as design.md in a directory of your own and run `bash tools/audit/seat/bus.sh push-design r10-audit-coverage <design.md>`, which pushes refs/heads/design/r10-audit-coverage; that push is the return signal, and the design/r10-audit-coverage tip is the SHA you hand off. You may push only to that ref. Open no pull request, push no handoff ref and write no delivery row.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
PRE-STUDY seat (designer, read-only), topic r10-audit-coverage. Requested by tvofi on 2026-10-30: "a pre-study on whether the audit dimensions and harnesses cover the production code and instruments and repo machinery as it looks like in v10.0.0, and fold any gap fixes in as an endgame group". Contract: dev/governance/roles/designer.md at origin/main, which says what a design note is. You write no production code and open no PR.

What v10.0.0 means: origin/main plus every round-10 roster group not yet done. The roster is dev/programme/rosters/wave-r10-groups.json on origin/handoff/audit-r10-roster. Read each open group's brief and files, so you know which modules, instruments and machinery will exist at closeout: new services, blueprints, buttons, instruments, workflows and harnesses that are still in flight.

The coverage surfaces to measure:
1. Audit dimensions. dev/governance/dimensions/D0.md to D15.md, plus the finder contract dev/governance/roles/COMMON.md.
2. Finder scopes. dev/audit/config/scopes.json and rotation.json. Run tools/audit/check_scopes.py: disjoint and complete within each dimension. Measure completeness against the tree, not against the scopes file's own list.
3. Bug classes. dev/audit/config/bugclasses.json: classes, barriers and RCA links. Find any class with no barrier and no RCA (fold_ledger.py check).
4. Harnesses. dev/audit/harnesses/ and dev/audit/rounds/round9/: which re-run green at main, which are stale (moved paths, dead imports), and which production seams have none.
5. The three bodies of code:
 (a) production, custom_components/heatpump_optimizer/** including blueprints, services, the card and translations;
 (b) instruments, tools/**, especially tools/audit/seat/, tools/pr/, tools/policy/ and tools/plan/;
 (c) repo machinery, .github/workflows/**, the hooks, CODEOWNERS and the rulesets, the policy linters (brief_lint, policy_lint, agreement), the closure and gate machinery in tests/, the merge train and stamp.

For each body, build a matrix of path or module against dimension, finder scope and harness, and mark each cell covered, partial or uncovered. Coverage means a dimension brief and a finder scope that would actually read that path or seam, not just a glob that happens to match. Test that claim by sampling. Count with an enumerator, a command that prints the number, never a carried figure.

Deliverable: a design note (BODY.md) pushed with tools/audit/seat/body_push.sh r10-audit-coverage <file>. It contains:
- the coverage matrix in summary, with the full table as an appendix or an ev/ file;
- every gap, with its evidence and the command that shows it, plus a null control showing the measure flags a known-covered path as covered;
- the fix for each gap: a scope edit, a dimension-brief edit, a new or repaired harness, a bugclass barrier, or an instrument check. Mark each fix as tree work (scopes.json, harnesses, tools) or as a policy edit (dimension briefs and role contracts are policy; the orchestrator approves them under its mandate);
- a proposed endgame group under "## Roster entry", in roster JSON: group R10-AUDIT-COVERAGE-ENDGAME, with its size, brief, files, hot_files, fixes and after-edges. It must run after every group that adds code, so it measures the final v10.0.0 tree, and before R10-CATALOG-PR and the closeout stamp. Its brief must re-measure every gap at its own merge base, because groups landing after this pre-study change the tree. Show that brief_lint passes the entry: run node tools/policy/brief_lint.mjs on a scratch copy of the roster with the entry appended, at origin/main. Never backtick a symbol that does not exist yet, and never cite a path that does not exist yet (brief-citations.md);
- the gaps that are too large for one group, split out with a recommendation.
Work from a detached worktree at the head this payload names. Run anything over 60 s in the background with a log. No host paths in the note. If a hook refuses you, stop and report.
