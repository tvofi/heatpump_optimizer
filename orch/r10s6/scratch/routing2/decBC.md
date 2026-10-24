
## B. The 32 live groups with no issue

Search: the open-issue list cached once by audit 1 (`gh issue list --state open --limit 500 --json number,title,labels`, /private/tmp/claude-501/s/issues.json, 53 issues), matched against each group's brief. A match is wired only where the issue names the group's own defect class or ask.

| group | stage | verdict | issue / body file | evidence |
|---|---|---|---|---|
| R10-FLOW-JIDOKA | in-progress | WIRE #2428 | carry-missing friction | brief: "Of 133 blocked fix reviews in round 10, 25 were carry-missing"; #2428 is `[policy] recurring friction: carry-missing` |
| R10-FLY-CARRY-DISPOSITION | not-started | WIRE #2428 | carry-missing friction | brief: lets the orchestrator add the `Carry:` marker a carry-missing block asks for |
| R10-FLOW-ROSTER-FREEZE | not-started | WIRE #2389 | head-moved rework | brief: the roster PR's review "comes back head-moved or body-stale: #2559 lost five reviewer rounds" |
| R10-FLOW-BODY-ONLY | not-started | WIRE #2389 | head-moved rework | brief: "every body fix moves a clean head" (#2513, #2544, #2548, #2529, #2549) |
| R10-FLY-ROW-HEAD-CARRY | not-started | WIRE #2389 | head-moved rework | brief: carry CI results across a head move that changes only the delivery row |
| R10-FLY-CARRY-DOC-CONTEXT | not-started | WIRE #2389 | head-moved rework | brief: app_approve.sh carries a verdict across a main merge that moves only md context lines |
| R10-STRUCTURE-ALIAS | in-progress | WIRE #2235 | N-structure-blind | brief: seam_cut_total counts occurrences, so a local alias pays; #2235's mechanism is "measures a name or regex proxy instead of the property it gates" |
| R10-DIAG-REDACT | not-started | WIRE #2271 | DIAG-REPLAY sanitise half | #2271 title: "fill the bundle's replay half through the export's allowlist and sanit[ise]"; brief: "R10-DIAG-REPLAY, the group that held it, is done" |
| R10-FLY-CAP-LINE | not-started | ABSORB into R10-FLOW-WIP, set done | - | same seam: orchestrator_tick.py:607-611 is the WIP line FLOW-WIP owns (pr_cap.py, orchestrator_tick.py in its files); the line still names no exception |
| R10-FLOW-BOARD | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Flow board (Lean study K1)"; no open issue tracks the Lean study |
| R10-FLOW-MQ-PROBE | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean study K9" |
| R10-FLOW-POSTMERGE | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean flow study, mechanisation" |
| R10-FLOW-RECORD-PITCH | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean study K6" |
| R10-FLOW-WIP | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean study K4" |
| R10-FLOW-AUTOTRAIN | in-progress | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "Lean flow study, mechanisation" |
| R10-FLOW-TOOLKIT-MODEL | not-started | NEED-ISSUE (umbrella) | lean-flow-study.md | brief: "the Lean flow study's projection model" |
| R10-FLOW-AUDIT-PLAN | not-started | NEED-ISSUE (umbrella) | round11-readiness.md | brief: "Mechanise P3 for round 11" |
| R10-ROUND-PLAYBOOK | not-started | NEED-ISSUE (umbrella) | round11-readiness.md | brief: "run round 11 onwards from the tree alone"; #2395 is ARCH-DOCS's docs scope, not dev/audit/README.md |
| R10-ORCH-REVIEW-PACKET | not-started | NEED-ISSUE (umbrella) | seat-context-cost.md | brief: owner ruling 2026-10-24, card 8; #2505 is the machinery design, not this |
| R10-POLICY-ROLE-PACK | not-started | NEED-ISSUE (umbrella) | seat-context-cost.md | brief: owner ruling 2026-10-24, token pre-study (b) |
| R10-FLOW-DESIGN-STAGES | not-started | NEED-ISSUE | design-stages.md | no open issue names design stages |
| R10-FLY-OPENPR-ATOMIC | not-started | NEED-ISSUE | openpr-atomic.md | not done: `git grep -iE 'pr close' origin/main -- tools/audit/seat/open_pr.sh` is empty |
| R10-FLY-RELAY-REVIEW-FF | carries-open | NEED-ISSUE | relay-review-ff.md | #2664 merged 811cd01; 9 carries still open; no issue |
| R10-FLY-ORPHANS-REWRITTEN | not-started | NEED-ISSUE | orphans-rewritten.md | no open issue |
| R10-FLY-DEPGRAPH-STALE | in-progress | NEED-ISSUE | depgraph-stale.md | pins patched (tests/requirements-ci.txt:30 aiohttp 3.14.5) but the cause (graph not updating) is the owed work |
| R10-FLY-STAMP-CHECK-NOTES | not-started | NEED-ISSUE | stamp-check-notes.md | not done: `git grep -- --check-notes origin/main -- tools/release/stamp.py` is empty |
| R10-FLY-MANDATE-REVOKE-GUARD | not-started | NEED-ISSUE | mandate-revoke-guard.md | not done: `git grep -iE 'revok|withdraw-mandate' origin/main -- tools/pr/gh_comment.py` is empty |
| R10-TRAIN-OVERLAP-GRADE | queued | NEED-ISSUE | train-overlap-grade.md | a third-instance barrier; no open issue |
| R10-NIGHTLY-HB-RESPAWN | queued | NEED-ISSUE | nightly-hb-respawn.md | residual of #2605; no open issue |
| R10-FLY-PRUNE-REFS | not-started | NEED-ISSUE | prune-refs.md | not done: prune_refs.py last changed 730ac0c14 (a prune family), neither defect |
| R10-CLOSEOUT-CLEANUP | not-started | NEED-ISSUE | closeout-cleanup.md | runs last; no open issue |
| R10-IMMERSION-LATCH | queued | NEED-ISSUE | immersion-latch.md | D15 finding; no open issue |

Also needing an issue: the three reopened groups (suite-env-flakes.md, gh-read-residue.md, no-footers-strict.md) and R10-ROUTING-INVARIANTS (routing-invariants.md). None of the 32 is already done or absorbed apart from R10-FLY-CAP-LINE; R10-FLY-RELAY-REVIEW-FF's PR merged but its carries are the open work.

## C. The 14 open issues listed only by done groups

| issue | verdict | PR / commit | residual and destination |
|---|---|---|---|
| #2235 | NOT DELIVERED (findings delivered) | #2340 8186403 (`Closes #2235`), #2401 07a0940, RCA #2415 f0a4aca | the class is live in R10-STRUCTURE-ALIAS (seam_cut_total counts occurrences); wire #2235 there |
| #2248 | NOT DELIVERED | #2675 94bec97 (`Part of #2248`) | seven unprobed writers filed as #2674; new R10-RESTORE-RACE-PROBE (issues 2248, 2674) |
| #2250 | DELIVERED | #2612 008ad15 | its one finding D9-s1-01 (fused objective, #2612 body section 1); close |
| #2252 | DELIVERED | #2435 05c39d3 | the relative trust region is the issue's whole ask (#2435 body "What changed"); accuracy.py's refit clip was out of scope by the body's own statement; close |
| #2257 | NOT DELIVERED | #2572 f24895c (`Part of #2257`) | seams (a)-(c), MX4, per-degree copy, mixing; new R10-ADVISOR-RESIDUE (fixes 2257) |
| #2258 | DELIVERED | #2647 14405df | owner items 1-3 answered (#2647 body); the body leaves verification to the orchestrator after merge; close |
| #2259 | NOT DELIVERED | #2401 07a0940 (`Part of #2259`) | #2401's table: item 2's "duplicated spellings of a one-statement rule" not delivered; new R10-ARCHSCORE-SPELLINGS (fixes 2259) |
| #2265 | DELIVERED | #2390 a96f4be | findings e, g, h, i landed with the two countermeasures (#2390 body line 3); close |
| #2269 | NOT DELIVERED | #2631 b24cfe5 (`Part of #2269`) | the two D0 carries from #2612; new R10-BRIEFS-FOLD-D0 (fixes 2269) |
| #2271 | NOT DELIVERED | #2399 0dac0bf (`Part of #2271`) | the sanitise half is R10-DIAG-REDACT's scope; wire #2271 there |
| #2272 | NOT DELIVERED | #2514 0280e6e, #2548 290712e (`Part of #2272`) | no real recorded day: tests/replay/ holds only synthetic-dhw-only.json; new R10-REPLAY-REAL-DAY (fixes 2272, after REPLAY-SCOPED and DIAG-REDACT) |
| #2298 | DELIVERED | #2521 92b5bf4 | docs/index.html declares 792 for the 1056x792 PNG, plus a check over every sized `<img>` (#2521 body line 9); close |
| #2410 | DELIVERED | #2669 5c9828f, 75bd9e6b1 | the family arm no longer re-files a member's occasions and its members list is complete (policy_lint.mjs:2799); policy_lint's stats run re-files in place if the live window is still over threshold; close |
| #2496 | DELIVERED | #2513 929275e | roster_edit.py has `set-after` and `drop-carry` (roster_edit.py header); residuals 3b97e1aa and 7f85b089 go to R10-ORCH-ROSTER-SCHEMA; close |

## D. The permanent check: R10-ROUTING-INVARIANTS

Group JSON: /Users/timmalmstrom/hpo-orch/r10s6/groups/R10-ROUTING-INVARIANTS.json (size M, after none, owner_gate "mandated approval under 6329234399", issue to be created from routing-issues-1/routing-invariants.md).

- Invariant 1 in carry_audit.py, with the consumed-versus-pending mark: every group `carry` entry is pending until it ends in `[implemented: <sha>]` (ancestor of origin/main), `[moved: <GROUP>]` or `[dismissed: <reason>]`. roster_edit.py gains `mark-carry`, and `set-stage` to a done stage refuses while a carry is pending, so a group cannot finish holding unimplemented work. `Dests.check` accepts a done group only for an item that group marked implemented or moved, and prints STRANDED otherwise. A new offline `carry_audit.py roster` subcommand checks every group with git alone.
- Invariant 2 in brief_lint.mjs's roster-shape block (the roster linter): a live group with empty `issues` and `fixes` is an error.
- Invariant 3 stays in `carry_audit.py sweep --issues`, except that a carry file no longer counts as an owner. #201 and the Tracking label are exempt.
- One live predicate: `absorbed` is not in roster_lib.DONE_STAGES (roster_lib.py:33). The group settles that in roster_lib.
- Wiring: governance.yml runs the offline check on every pull request and push, and the issue check on push to main. orchestrator_tick.py's default pass runs the offline check every tick and the issue check at most hourly from a cached list. The CARRY section is opt-in today (orchestrator_tick.py:2061).
- Migration: at merge the orchestrator marks the done groups' existing carries `[implemented: <resume.commit>]` with mark-carry, except the ones this file moved. This file's IMPLEMENTED and NO-OBLIGATION rows are the null control.
