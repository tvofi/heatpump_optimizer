# R10 survey, 2026-10-21 ~08:00Z (read-only; origin/main df6ca4bc)

Raw evidence in this directory: roster.json (handoff/audit-r10-roster at survey start), roster-e5284a76.json (tip after the orchestrator's 09:58+02 union merge, see B), a-raw.txt, a-verdicts.txt, a-redanswers.txt, failure_logs.out, logs/<pr>/, orphans.out, b-raw.txt, mt-<pr>.txt, mtb-<topic>.txt, c-groups.txt, d-runs.txt.
Method: `gh pr view`, `gh api repos/tvofi/heatpump_optimizer/commits/<head>/check-runs --paginate` (newest started_at per name, not success/skipped), `bash tools/audit/seat/failure_logs.sh <pr> <dir>`, `git ls-remote --heads origin`, `git merge-tree --write-tree origin/main <head>`, `bash tools/audit/seat/bus.sh orphans --min-age-h 0`.
Required contexts (ruleset 23698884, `gh api .../rulesets/23698884`): fast (3.14), browser, briefs, closure-scope, closures, typing, hassfest, validate-hacs, policy-docs, wave-script, pr-contract, env-matrix, Analyze x3, mutation, budget-raise-gate. `nightly-status` and `instrument-self-tests` are NOT in that list.
`nightly-status` is red at every head (Section D); it is listed per PR below but is not what blocks any of them.

## Section A. Open PRs

Behind = `git rev-list --count <head>..origin/main`. merge-tree rc was 0 (clean) for all 12 (`git merge-tree --write-tree origin/main <head>`; mt-<pr>.txt).

| PR | branch | head | draft | roster group (from PR title) | behind | non-green latest check-runs at head |
|---|---|---|---|---|---|---|
| 2513 | fix/r10-roster-ops | 716a34f2 | yes | R10-ROSTER-OPS (in-progress) | 75 | instrument-self-tests (failure), nightly-status |
| 2519 | fix/r10-train-hold | dfba5276 | no | R10-TRAIN-HOLD (in-progress) | 0 | nightly-status; coverage, fast (3.14), Analyze (python) still running |
| 2521 | fix/r10-i5-docs | 35ae9dae | yes | R10-I5-DOCS (in-progress) | 75 | pr-contract, nightly-status |
| 2524 | fix/r10-pusher-reap | 50571afa | yes | R10-UPDATE-PR-SIGNALS (in-progress, roster resume.branch None) | 69 | pr-contract, nightly-status |
| 2525 | fix/r10-wip-cap | 00118887 | yes | R10-OPENPR-SILENT per title (roster: done, "delivered by PR #2422") | 69 | env-matrix, policy-docs, pr-contract, nightly-status |
| 2526 | fix/r10-gate-priority | baa75f58 | no | R10-PREPR-CAP (in-progress) | 69 | nightly-status only |
| 2527 | fix/r10-freq-defrost | 3ce0b78f | yes | R10-FREQ-DEFROST (in-progress) | 6 | fast (3.14) failure; mutation still running (since 07:08Z); nightly-status |
| 2528 | fix/r10-prepr-closures | a4f01a42 | yes | R10-PREPR-CAP | 69 | pr-contract, nightly-status |
| 2529 | fix/r10-ci-layout-g | e9d54acd | yes | R10-CI-LAYOUT (in-progress) | 69 | instrument-self-tests, policy-docs, pr-contract, nightly-status |
| 2531 | fix/r10-ci-ratchet-red | fddca812 | yes | R10-CI-RATCHET-RED (in-progress) | 66 | pr-contract, nightly-status |
| 2534 | dependabot/pip/tests/pip-ac46af0822 | b01e7004 | no | none (see note) | 49 | typing, pr-contract, nightly-status |
| 2542 | record/autofix | c2bbc473 | no | n/a (record beat, hpo-author) | 0 | pr-contract (in_progress at survey), nightly-status |

Note 2519 head moved during the survey: fb6d355b to dfba5276 (a main merge by tvofi, 09:51+02). Head list at 07:46Z in the brief was fb6d355b.

### Per-PR detail

**#2513** handoff/r10-roster-ops 4e2223a5 exists; NOT an ancestor of head. Head-only: 14 commits (main merges, record rows, row commit 716a34f2). Handoff-only: 3 (`4e2223a57 fix(roster): drop-carry keeps the emptied carry key`, `cf90776b5 ci: wire the roster-ops mutation harness's self-test`, `514ea584b record: the delivery row for #2513`). Merge-base c89cdf73. `git merge-tree origin/fix/r10-roster-ops origin/handoff/r10-roster-ops` rc=1 (conflict), bus.sh says repair=review. First error (instrument-self-tests, logs/2513): `UNWIRED tools/audit/seat/r10_roster_ops_mutants.py: no workflow run line names its self-test` / `selftest_wiring: 38 self-testing, 37 wired, 1 unwired`; the handoff's cf90776b is the wiring fix. Body `## Red checks` names instrument-self-tests (answered), does not name nightly-status. Fix-review comments: none.
**#2519** handoff/r10-train-hold a8c8287f is an ancestor of head. Newest `Fix review:` comment 6305871760 (hpo-approver, 01:38Z) "Fix review: merge 6efcb1ac090e19522c95701db295908fb52990ab" - does NOT name the current head dfba5276, but 6efcb1ac is an ancestor and `git diff f639f3b0d 6efcb1ac | git patch-id` = `git diff origin/main...head | git patch-id` = 9cadcb908209 (branch diff byte-identical; head moved only by two main merges fb6d355b, dfba5276). verdict/2519 tip 390a95d5. Body `## Red checks` names nightly-status and answers closures/closures-autofix/pr-contract of an earlier head. No red required check at dfba5276; 3 required still running.
**#2521** handoff/r10-i5-docs 7a7102eb ancestor of head. pr-contract first error (logs/2521): `UNROUTED body item edad96f3 (## Forward-carry) [section]: "The D7.md and D9.md lines of #2222 are already in R10-BRIEFS-FOLD's brief, the money_currency comment in R10..."` then `CARRY-AUDIT: 1 finding item(s): 0 routed, 1 unrouted`. Body updated 22:55Z, red run 00:13Z, so the body is what failed. Red section answers a local entities.py failure only; nightly-status and pr-contract not named. No verdict.
**#2524** handoff/r10-pusher-reap 9719443b ancestor of head. pr-contract: `UNROUTED body item 7ccf959f (## Forward-carry): 'none -- no finding here changes how a later stage must work.'`, 2 UNROUTED `## Friction` items (daemonize-instrument, entity-classification), `CARRY-AUDIT: 3 finding item(s): 0 routed, 3 unrouted`. Body Red checks = "none"; names neither red. No verdict. Roster group has no branch recorded.
**#2525** handoff/r10-wip-cap 80fe9ac0 ancestor of head. env-matrix: `6 declared outcome(s) held, 10 did not, across 6 environment shape(s)` (e.g. `FAIL shallow / policy_lint rc=0 -- rc=1 FIXTURE VACUOUS: checkCitationPresence reported 1 of 2 earned exclusions...`). policy-docs: `FIXTURE VACUOUS: checkCitationPresence reported 1 of 2 earned exclusions with every citation of them elided from the corpus` (TOTAL 0 error(s) across 41 policy file(s) before it). pr-contract: `check env-matrix is red and ## Red checks does not name it` (also nightly-status, policy-docs). Body Red section names harness_headers / entities heartbeat reds of an older head, not these. #2542 (main + 2 commits) has policy-docs and env-matrix green, so main does not carry this red. Title says R10-OPENPR-SILENT, a group the roster marks done by #2422. No verdict.
**#2526** handoff/r10-gate-priority 31529479 ancestor of head. Comment 6308994719 (05:43Z) "Fix review: merge baa75f58ae7f9c00334d92da24d3285e1b047277" = current head. verdict/2526 tip a8421d7c. Only nightly-status red (unrequired); body Red checks does not name it, pr-contract is green.
**#2527** handoff/r10-freq-defrost fe9038fb ancestor of head. Comment 6304555973 (00:01Z) "Fix review: blocked de28f656... root-cause-unanswered: mutation went red, unanswered" - names an old head (code head 4f2ac0ca, final de28f656); the fixer has since pushed fe9038fb "kill the two watchdog bound mutants, record the pin" and two main merges. Body `## Red checks` now names `mutation` (answered) but not fast / closures / nightly-status. Red at head: `fast (3.14)` (logs/2527/fast--3.14--119088663302.log:11725) `>>> FAILED: python3 tests/structure.py` = `3 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED` (class_excess_loc 18299->18297, max_class_loc 8541->8539, seam_cut_total 718->717; recorded_at 4e5801eb5064); the log tells the fixer to run `python3 tests/structure.py --record` and say the rows in the commit message. Null control: `python3 tests/structure.py` on origin/main prints no gain lines, so the gains are this branch's. `git diff origin/main...head -- tests/structure_budgets.json` is empty. closures at head: success; pr-contract success; mutation: in_progress since 07:08Z.
**#2528** handoff/r10-prepr-closures e3251349 ancestor of head. pr-contract: `UNROUTED body item 6f639041 (## Forward-carry) [section]: '- A later seat reading how a handoff runs the gate needs the new default without opening prepr.sh...'` `CARRY-AUDIT: 1 finding item(s): 0 routed, 1 unrouted`. Body Red checks: `none`. No verdict.
**#2529** handoff/r10-ci-layout-g 2fd3fd45 ancestor of head. Three distinct reds, all at the live head: (1) instrument-self-tests: `tools/audit/seat/handoff_push.sh: line 55: i: unbound variable` (the branch edits handoff_push.sh, +97 lines; the log shows no ref_privacy REFUSE line, so the body's answer about 16 ref_privacy refusals does not describe this failure); (2) policy-docs: `REFUSED registry: pinned tools/policy/agreement_restore.py is unregistered: DECLARED names neither an arm for its input nor none` / `FIELD COVERAGE REFUSED` (the branch adds agreement_restore.py, +296); (3) pr-contract: `check nightly-status is red and ## Red checks does not name it` (diff touches .github/workflows/governance.yml) and policy-docs not named. Body names instrument-self-tests only. No verdict.
**#2531** handoff/r10-ci-ratchet-red 8457652c ancestor of head. pr-contract: `check nightly-status is red and ## Red checks does not name it. It grades main, but this diff touches what it reads (.github/workflows/tests.yml)`. That is the only pr-contract error (1 error). Body Red checks answers ci-ratchet-on-main only. No verdict. See D: main's current ci-ratchet red reads `GREW critical_path_minutes: 56.5 (budget 54.825)`, which is not the window-fetch-empty defect this PR title names.
**#2534** dependabot[bot] PR, no handoff ref. Diff (`gh pr diff 2534`): requirements-ci.txt + requirements-typing.txt aiohttp 3.14.4 -> 3.14.5; requirements-typing.txt certifi 2026.7.22 -> 2026.10.19, pillow 12.3.0 -> 13.0.0 (major), uv 0.12.5 -> 0.13.4. typing first error: `ERROR: THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE` (logs/2534/typing-118981576305.log:164). pr-contract: 9 errors, first `the pull request author is dependabot[bot]; a pull request is authored by the hpo-author App (decision 0011) - re-open it via tools/audit/app_push.sh, never push.sh`; also all 7 body headings absent. Roster group R10-DEPENDABOT-AIOHTTP (issue 2504) is NOT this PR: its work is merged as #2487 (`deps: aiohttp 3.14.4 in both locks`, MERGED; main pins aiohttp==3.14.4 in both files, `git show origin/main:tests/requirements-*.txt`) though the roster still shows in-progress at 1a9b9096. #2534 is a new bump (3.14.5).
**#2542** record/autofix, hpo-author, 2 commits over main df6ca4bc. Body answers record / nightly-status / delivery-status; pr-contract running at survey. No handoff, no verdict (record PR).

### Recommended next action, Section A

- #2513 update_pr - handoff 4e2223a5 holds the instrument-self-tests fix (cf90776b) and drop-carry fix the head lacks; the two sides conflict (merge-tree rc=1, delivery/2513.md duplicated), so route through the fixer to reconcile (bus.sh says repair=review), then update_pr, then recarry.
- #2519 merge-ready - verdict `merge` at 6efcb1ac covers identical branch diff (patch-id 9cadcb908209 both); wait for coverage / fast (3.14) / Analyze (python) at dfba5276, then merge_train.
- #2521 return-to-fixer - red required pr-contract: `UNROUTED body item edad96f3 (## Forward-carry)`; route the carry into the destination group (R10-BRIEFS-FOLD) / roster, name nightly-status in Red checks.
- #2524 return-to-fixer - red required pr-contract: `UNROUTED body item 7ccf959f / 2fae73cd / 979aedf2 (Forward-carry 'none', two Friction items)`; body Red checks "none" is stale.
- #2525 return-to-fixer - red required env-matrix, policy-docs, pr-contract; first error `FIXTURE VACUOUS: checkCitationPresence reported 1 of 2 earned exclusions...`; body answers other reds. Main does not carry it (#2542 green on both).
- #2526 merge-ready - verdict merge at the live head baa75f58; only unrequired nightly-status red; recarry by train (behind 69, merge-tree clean).
- #2527 return-to-fixer - red required `fast (3.14)`: `3 STRUCTURE BUDGET(S) IMPROVED AND NOT YET RECORDED` from tests/structure.py (run `python3 tests/structure.py --record`, rows in the commit message); the prior blocked verdict (root-cause-unanswered, mutation) was answered in the body and at 4f2ac0ca..fe9038fb; mutation still running, so re-review after fast and mutation are green.
- #2528 return-to-fixer - red required pr-contract: `UNROUTED body item 6f639041 (## Forward-carry)`; name nightly-status.
- #2529 return-to-fixer - red required policy-docs (`pinned tools/policy/agreement_restore.py is unregistered`), instrument-self-tests (`handoff_push.sh: line 55: i: unbound variable`), pr-contract (nightly-status/policy-docs unnamed).
- #2531 return-to-fixer - red required pr-contract only: name `nightly-status` in `## Red checks` (body edit; code needs no change per the pr-contract text). Also confirm the PR addresses main's current ci-ratchet reason (D).
- #2534 return-to-fixer - cannot merge as is (typing lock hashes broken; author dependabot[bot] is refused by pr-contract). Needs a re-lock re-opened through app_push.sh by a new fixer item (pillow 13 is a major); it is not R10-DEPENDABOT-AIOHTTP (that is #2487, merged) - close #2534 once the re-opened PR exists.
- #2542 record-automerge - clean, behind 0, only pr-contract in flight and unrequired nightly-status red.

## Section B. Orphan handoffs

`bash tools/audit/seat/bus.sh orphans --min-age-h 0` (rc 1): 9 stranded, 1 superseded; `skipped no-body=26 named=10 ancestor=91 young=0`. Ages are bus.sh's.

| topic | tip | age | body ref | BODY.md first line | roster group / stage | in main? | open or merged PR | action |
|---|---|---|---|---|---|---|---|---|
| audit-r10-roster | 9c02a6ac at survey start; now e5284a76 | 5.2h | yes c025e447 | "Roster for round 10, fourth landing..." (stale: names code head 7e8e5e5a, groups 90 to 91) | none (it is the roster) | no, 118 ahead / 0 behind (tip is a union merge of main) | 8 earlier landings MERGED (#2475 #2471 #2467 #2417 #2384 #2380 #2377 #2356); none open | open |
| r10-earlycutoff-coverage | ecaf178c | 110.3h | yes d7830d26 | "Why this change, and what it measures." | R10-REGISTRY-LEAK done; roster note: "Carry discharged 2026-10-20: ... landed on main via #2397" | not an ancestor, but all 51 added non-blank lines are present verbatim in origin/main tests/features.py; `git cherry` shows it as unapplied commit | #2397 MERGED 2026-10-18 | dispose |
| r10-merge-pr-mandate | 6219325c | 62.6h | yes ef8aaecc | "Group R10-MERGE-PR-MANDATE. No issue is filed..." | R10-MERGE-PR-MANDATE in-progress, 6219325c | no; 1038 behind, 3 ahead, 5 files +171/-13; merge-tree rc=1 (INSTRUMENTS.md, merge_pr.sh, proof_watch.py) | none | needs-fixer |
| r10-night-folds | b4d0dd97 | 16.3h | yes 9634d69c | "The heat-loss learners absorb solar-aperture error..." (Closes #2223) | R10-NIGHT-FOLDS in-progress (no commit recorded) | no; 106 behind, 8 ahead, 12 files +644/-46; merge-tree clean | none | open |
| r10-pre-edit-hook | 6d0df376 | 123.2h | yes 753b8d70 | "The pre-edit hook decided its RELEASE_NOTES heading rule..." (Closes #2220) | R10-PRE-EDIT-HOOK done 0570b86e | no; bus.sh SUPERSEDED | #2323 MERGED (head 8fef39fc) | dispose |
| r10-rca-handoff-slip | 5c500b79 | 13.4h | yes 90df761f | "record: RCA for the orphaned-handoff class (N-orphaned-handoff)" | none (0 roster mentions) | no; 84 behind, 1 ahead, 1 file +257 (dev/audit/rca/N-orphaned-handoff.md; main lacks it); clean | none | open |
| r10-rca-harness-friction | d1611efe | 55.6h | yes a32fbfd1 | "R10-RCA-HARNESS-FRICTION: the root-cause analysis for four friction issues..." | R10-RCA-FRICTION in-progress, d1611efe | no; 905 behind, 9 ahead, 10 files +763/-6; merge-tree rc=1 (dev/audit/config/bugclasses.json, dev/governance/roles/orchestrator.md) | none | needs-fixer |
| r10-replay-cap | 38aec7bf | 11.8h | yes 9f6cec59 | "# Summary - The nightly slow lane's replay check went red on 2026-10-20" (Part of #2272) | none | no; 78 behind, 1 ahead, tests/replay.py +11/-7; merge-tree rc=1 (tests/replay.py) | none | needs-fixer |
| r10-roster-ops | 4e2223a5 | 12.1h | yes 474c298b | "R10-ROSTER-OPS. roster_edit.py gains set-after and drop-carry..." | R10-ROSTER-OPS in-progress, 9969e3ca | no; 87 behind, 5 ahead | #2513 OPEN, head 716a34f2 behind the handoff | update (via fixer; bus.sh repair=review, merge-tree head+handoff rc=1) |
| r10-roster-sync | a6d8a78e | 11.6h | yes 89aac9b9 | "The roster's resume.stage is a human claim and nothing compared it with the repository..." | none by name (appears in R10-ROSTER-OPS and R10-ORCH-MACHINERY text) | no; 87 behind, 7 ahead, 7 files +1250/-24 (roster_sync.py absent on main); merge-tree clean | none | open |

### audit-r10-roster (requested commands)
- `git diff --stat origin/main...origin/handoff/audit-r10-roster -- dev/programme/`: carries/carry-201.json 9 lines; rosters/critical-path.json +17; rosters/wave-r10-groups.json 379 lines; 3 files, 337 insertions, 68 deletions. Roster 98 groups on the branch (91 on main at the time of the first count).
- `git diff --stat origin/handoff/audit-r10-roster...origin/main -- dev/programme/rosters/`: empty (re-run at tip e5284a76; 0 commits behind main). Main carries no roster change the branch lacks.
- Tip moved during the survey: bus.sh printed 9c02a6ac (uncovered=117), `git ls-remote` now e5284a76 (118 ahead). Commit `e5284a76e tvofi 10-21 09:58 Merge origin/main into handoff/audit-r10-roster (union)`.
- BODY.md at handoff-body/audit-r10-roster c025e447 is the fourth landing's body (merged); a new landing needs a re-taken body before open_pr.sh.

### Recommended actions, Section B

- audit-r10-roster: open (open_pr.sh) a fifth roster landing, after re-taking the body; the 4th-landing BODY.md is stale.
- r10-earlycutoff-coverage: dispose - content landed as #2397 (MERGED 2026-10-18; 51 of 51 added lines present in main's tests/features.py; the roster note on R10-REGISTRY-LEAK says so); prune the handoff and body refs.
- r10-merge-pr-mandate: needs-fixer - conflicts in 3 files (merge-tree rc=1) and main already carries tvofi's 0ed4aceb2 "fix(merge_pr): owner mode takes the mandate id and reads it live; a draft refuses unless --ready" (2026-10-18; main's merge_pr.sh has `MANDATE REQUIRED` and `mandate_in_force`, proof_watch.py has `--mandate`); the handoff's residual is MANDATE_COVERS_CODE_OWNED in budget_raise_gate.py (0 on main) and the governance.yml self-test wiring; a fixer must rebase and cut it to the residual, or the group is closed as superseded.
- r10-night-folds: open (open_pr.sh) - clean merge-tree, group in-progress, 106 behind (recarry at open).
- r10-pre-edit-hook: dispose - #2323 MERGED, roster done 0570b86e, bus.sh SUPERSEDED.
- r10-rca-handoff-slip: open (open_pr.sh) - doc-only, clean; no roster group exists for it, so the opener needs a disposition row (R10-RCA group or a new one).
- r10-rca-harness-friction: needs-fixer - 905 commits behind, conflicts in bugclasses.json and orchestrator.md (the diff also touches dev/governance/roles/fix-review.md, orchestrator.md: policy files).
- r10-replay-cap: needs-fixer - this is the fix for the nightly `slow` red (Section D: `loop_cpu_ratio 0.1114 over its budget 0.111`; main still has 0.111, handoff raises to 0.124); conflicts only in the comment block above COST_BUDGETS (main's #2514 edited those comments). Rebase, then open; the cap is in tests/replay.py's own table, not a *_budgets.json.
- r10-roster-ops: update - see #2513.
- r10-roster-sync: open (open_pr.sh) - clean, 7 commits, new tools/audit/seat/roster_sync.py; no PR; group attribution to settle (the body's carries point at R10-POLICY-GATE-SCOPING).

## Section C. Groups "blocked on owner disposition"

Computation (`tools/audit/seat/orchestrator_tick.py:1651-1661`, phrase at 1659): `gated = [g for gid,g in groups.items() if gid in open_g and g.get("owner_gate")]` and the line `N group(s) blocked on owner disposition; oldest issue #<first gated issue> is Nd old -- surface them to the owner`. `open_g = roster_lib.open_groups(roster)` = stage not in DONE_STAGES. So it counts a free-text `owner_gate` field on any open group; it asks no question. Run against roster-e5284a76.json with roster_lib: 52 open of 98, 14 gated (matches the 14).

None of the 14 carries a question with options or a "recommended" marker. Every `owner_gate` is an approval note on the eventual merge (code-owned path or policy file), and 9 say "mandated approval under 6175172275" (mandate scope all, to 2026-10-28 per R10-CI-LAYOUT's gate text). Searching their briefs and gate text for recommend/option/decision found only: R10-BRIEFS-FOLD "Countermeasure M4 is adopted under mandate 6175172275 (the recommended option)"; R10-CI-LAYOUT "R-10 option B: pr-contract lists open code-scanning alerts ..." (chosen; "the pr-contract change is policy and needs the owner's approval"); R10-REPLAY-SCOPED "A blanket per-PR lane is refused permanently; do not offer it as an option."

| group | stage | issues | disposition text (owner_gate) | options / recommended |
|---|---|---|---|---|
| R10-I5-DOCS | in-progress (PR #2521 open) | 2222, 2298 | "code-owned: tests/stress.py (comment only)" | none |
| R10-BRIEFS-FOLD | not-started | 2222, 2269 | "policy: dimension briefs"; brief: "Policy: tvofi approves before merging" | none; M4 noted as the recommended option, adopted |
| R10-REPLAY-LANE | in-progress (roster); PR #2514 MERGED | 2271, 2272 | "code-owned: .github/workflows/" | none |
| R10-REPLAY-SCOPED | not-started | 2273 | "code-owned: .github/workflows/" | none; per-PR blanket lane refused |
| R10-TRAIN-HOLD | in-progress (PR #2519 open) | 2302 | "code-owned: .github/workflows/ (workflow change, approved under mandate 6175172275)" | none |
| R10-POLICY-LINT-FAMILY | not-started | 2410 | "policy: tools/policy/ is in POLICY_GLOBS; tvofi approves under the mandate" | none |
| R10-MERGE-SUBJECT-HARDEN | not-started | 2494 | "policy: tools/policy/agreement.mjs is in POLICY_GLOBS; tvofi approves under the mandate" | none |
| R10-CI-LAYOUT | in-progress (PRs #2529, plus later PRs) | 2495 | code-owned + policy; each PR approved at merged head by CODEOWNER session under mandate 6175172275; "tvofi's own step: the ruleset 23698884 required_status_checks PUT at PR 2's merge" | R-10 option B chosen; one real owner action: the ruleset PUT |
| R10-CEILING-PROBE | not-started | 2498 | "mandated approval under 6175172275" | none |
| R10-DEMAND-OVERBOOK | queued | 2499 | same | none |
| R10-BUFFER-STORE | queued | 2500 | same | none |
| R10-COP-PARTLOAD | queued | 2501 | same | none |
| R10-UPDATE-PR-SIGNALS | in-progress (PR #2524 open) | 2502 | same | none |
| R10-ORCH-MACHINERY | not-started | 2505 | "Mandated approval ... for the orchestrator-owned instruments; any change to a policy file ... is tvofi's and is approved before merging, per CLAUDE.md" | none |

Oldest gated issue per the tick is the first of the sorted issue list (#2222).

### In-progress / queued groups with no branch or PR (roster-e5284a76.json)
- R10-DEMAND-OVERBOOK, R10-BUFFER-STORE, R10-COP-PARTLOAD: stage `queued`, resume.branch None, no `after` open, no PR, no handoff ref (`gh pr list --state all --head fix/<t>`; `git ls-remote`). They are ready (after: R10-SETPOINT-BOOST done).
- R10-UPDATE-PR-SIGNALS: in-progress, resume.branch None, but PR #2524 (fix/r10-pusher-reap) is open and handoff/r10-pusher-reap exists; the roster has no branch for it.
- Roster stage stale (in-progress but PR MERGED): R10-SAV-REASONS (#2511), R10-REPLAY-LANE (#2514), R10-DEEPLINK-HANDLERS (#2452), R10-HANDOFF-ARCHIVE (#2488), R10-DEPENDABOT-AIOHTTP (#2487), R10-PREPR-CAP (#2341 merged; reopened, #2526/#2528 open).
- In-progress with a handoff but no PR: R10-NIGHT-FOLDS (handoff/r10-night-folds), R10-RCA-FRICTION (handoff/r10-rca-harness-friction), R10-MERGE-PR-MANDATE (handoff/r10-merge-pr-mandate) - see B.
- Open stage counts: not-started 33, in-progress 16 (as 18 rows listed incl. queued), queued 3.

### Ready-next, not started (not-started/queued, no open `after`)
R10-BRIEFS-FOLD (gated, wave 4), R10-POLICY-GATE-SCOPING, R10-SAV-COMFORT, R10-MUTATION-ANCHOR, R10-POLICY-LINT-FAMILY (gated), R10-MERGE-SUBJECT-HARDEN (gated), R10-DEMAND-OVERBOOK / R10-BUFFER-STORE / R10-COP-PARTLOAD (queued, gated), R10-THERMAL-POWER-OPTION, R10-LEARNER-DEFAULT, R10-MUTANT-SKIP. All other not-started groups are blocked by an open `after` (c-groups.txt, last block).

## Section D. nightly-status and main

- Feeder: `tests/nightly_status.py` (job `nightly-status` in .github/workflows/tests.yml) reports the newest concluded `schedule`-triggered run of the Tests workflow (`tests.yml`) on main; it is not a required context.
- Newest concluded schedule run: 39387919507, 2026-10-20T07:39:11Z, head 0c298f6b, conclusion failure (`gh api repos/tvofi/heatpump_optimizer/actions/runs/39387919507`). Failing job: `slow` (job 118512165515). First error: `FAIL synthetic-dhw-only.json: cycle_cost  [1 offender(s): loop_cpu_ratio 0.1114 over its budget 0.111]` then `1 of 93 replay checks FAILED` and `##[error]Process completed with exit code 1`.
- The prior night, 39218718759 (2026-10-19, head c3530277), also failed; 2026-10-18 succeeded. A new schedule run 39563978649 (2026-10-21T07:43:20Z, head c77f89dc) is in progress; `workflow_dispatch` runs on main: none in the last 3 are on main (they are on fix/r10-freq-defrost and handoff/r10-sav-reasons branches).
- The fix exists unopened: handoff/r10-replay-cap (0.111 to 0.124, see B) - needs a rebase (conflict in the comment block).
- Newest concluded push-triggered Tests on main: 39548715713, 2026-10-21T05:17:30Z, head 739c8369, failure; failing job `ci-ratchet` only (119065361551); error line: `GREW  critical_path_minutes: 56.5 (budget 54.825)` then `##[error]Process completed with exit code 1`. Previous pushes 39548631112 (8cf0b74c), 39544843463 (958cc1b7) fail on `ci-ratchet` too. Last 25 main push runs: 15 failure, 8 success, 2 in progress. Two push runs in progress now (39561825114 c77f89dc, 39564080883 df6ca4bc).
- Caveat: PR #2531 (R10-CI-RATCHET-RED) is titled for "the window fetch refuses rather than reading empty"; the current ci-ratchet reason in the newest log is a real metric growth (critical_path_minutes 56.5 over 54.825), not an empty window. Whether 14 earlier failures share this reason was not read.

RESULT: survey complete; no write performed outside this directory and the worktree.
CHECKS-RUN: gh pr view x12; check-runs API at 12 heads (+2519 re-run); failure_logs.sh x12; merge-tree x12 and x8 handoffs; bus.sh orphans; roster_lib open_groups; ls-remote handoff/review/verdict refs; tests/structure.py on origin/main (null control for 2527).
UNCERTAINTIES: heads/tips moved during the survey (2519, audit-r10-roster) so figures are as of ~08:00Z; failing-step identification for #2529 and #2527 is from interleaved logs; "behind" counts are against df6ca4bc; roster group for #2525 inferred from its title; nightly-status red is main's and not evaluated per PR.
ESCALATE: R10-CI-LAYOUT's owner-only ruleset PUT (23698884) at PR 2's merge; policy-file merges (R10-BRIEFS-FOLD, R10-RCA-FRICTION touching orchestrator.md/fix-review.md) under mandate 6175172275; the #2534 dependabot disposition.
