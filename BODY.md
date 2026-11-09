R10-HOTFIX-RECORD-ISSUE: #201, the programme's coordination and record issue, hit GitHub's 2,500-comment cap. Every comment on it is now refused with `HTTP 403: Commenting is disabled on issues with more than 2500 comments`, so `record_beat.py` printed OWED for #3350's record line and every later merge would do the same. Owner ruling (tvofi, 2026-11-09 ~22:35Z), answering whether to open a continuation issue and move the policy and tools to it: "Yes". The continuation is #3394, "Programme coordination and record (continuation of #201)". #201's body now starts with a line pointing to it. A body edit is not a comment, so it still lands.

The design is one definition. `tools/policy/budget_raise_gate.py`, which already owned the tracking-issue constant (`MANDATE_ISSUE`) that `gh_comment.py` and `merge_train.py` import, now holds `RECORD_ISSUES = (201, 3394)` and `RECORD_ISSUE = RECORD_ISSUES[-1]`, plus `on_record_issue(comment)`. Writers post to `RECORD_ISSUE`. Readers of the record (a mandate grant, its revocation) read every issue in `RECORD_ISSUES`. Mandate 6715477401 is on #201 and still resolves by id, since comment ids are global. A revocation the owner posts on #3394 still voids a #201 grant. Before this change, the kill switch could only be read on #201, which can no longer take a comment, so it would have been dead.

- Writers: `record_beat.py` (the merge line; the template now ends `Leaves #3394 open.`), `nightly.yml`'s record-autofix comment (it reads the constant through `python3 -I -c ... from budget_raise_gate import RECORD_ISSUE`, pinned by `tests/entities.py`), and `handover_prompt.py`'s coordination step.
- Readers: `budget_raise_gate._mandate`, `merge_train._mandate_read` and `orchestrator_tick._thread` read every record issue. `plan_page.py` and `carry_audit.py` leave both issues out of the open-issue and orphan counts, so #3394 does not show up as an unplanned orphan.
- Guards: `gh_comment.py`'s mandate guard covers a post or patch on any record issue, with the grants read from every record thread. A new `closed_record_guard` refuses a post to #201 and names #3394 instead of returning a bare 403. A patch to an old #201 comment still passes, because edits still land. The seat-gh shim's deny-by-default guard is now `trackers='201 3394'`. `gh_calls.py`'s self-test pins that line to `RECORD_ISSUES`, refuses a raw post and a `gh issue comment` on #3394, and runs a mutant that drops it.
- Policy: `CLAUDE.md` (index rows), `delivery-status-tracking.md` item 3, `writing-for-agents.md`, `orchestrator.md`, `nudge.md`, `HANDOVER.md`, instrument pages, `sweep_template.md` and the two web workflows now name #3394. `.claude/rules` and `.cursor/rules` were regenerated.
- Kept deliberately: `governance.yml`'s `delivery-status-publish` still splices the ledger region into #201's **body**. Body edits are unaffected by the cap, and `tests/delivery_status.py` and `tests/entities.py` pin that region where readers look for it. Historical citations of the form `#201 comment <id>` are reads of the record and stay as written. Decision records (0009, 0011-0016) record what was decided and are not rewritten.

Alternatives considered:
- A second constant per writer. Refused: it is the drift this replaces.
- A new `record_issue.py` leaf module. Refused: a new tracked file needs a measured closure re-derived off Linux, and `budget_raise_gate.py` was already the module the guard and the train import "for one definition of the revocation test, the grant reading and the tracking issue" (gh_comment.py `_gate`).
- Having the shim read the number at run time from `budget_raise_gate.py`. Refused: it costs a python spawn on every gh call, and an unreadable file would need a fail-open or fail-closed choice. The literal plus a self-test pin is the mechanism already in the tree.

After the merge (an action, not a carried finding):

- After this merges, the orchestrator re-runs `tools/audit/seat/seat_venv.sh --install-shims <bin dir>` on each host. Installed shim copies keep the old `tracker=201` until then, so #3394 is unguarded on that host. The install is a host action, not a tree change.
- `budget-raise-gate` runs the gate from the base commit, so a mandate or revocation on #3394 is read by that gate only from the first base that carries this merge. Until then, every grant in force (6715477401) is on #201, which the old gate reads.

## Head

`6604ac0856acbbb54f66e4de4343e4c44a4afada`, measured on merge base `b8f67a7751` (origin/main at handoff; `git merge-tree --write-tree origin/main HEAD` reports no conflict).

## Mutation proof

Each mutant edits `tools/policy/budget_raise_gate.py`, the one definition. The four self-tests listed below run against it, and the file is restored with `git checkout` after each mutant:
- **M1**, writers back to #201 (`RECORD_ISSUE = RECORD_ISSUES[0]`): killed. `record_beat` fails `the comment goes to the record issue, never #201 (closed to comments at its cap)`. `gh_comment` fails `arm6_a_grant_on_the_continuation_issue_is_guarded`, `arm6_record_issues_are_201_then_its_continuation` and `arm7_a_post_to_201_is_refused_naming_the_record_issue`. `budget_raise_gate` fails `mandate: the record issue is the last of RECORD_ISSUES, and #201 one of them`.
- **M2**, #201 no longer read as a record issue (`on_record_issue` over `RECORD_ISSUES[-1:]`): killed. `budget_raise_gate` has 9 failures, among them `mandate: a mandate on #201, the record before the comment cap, still passes` and the e2e `a raise approved at the head under a mandate in force exits 0`. `gh_comment` has 6, among them `arm6_brief_row_refused_on_post`. `orchestrator_tick` has 5, among them `record issues: null control: the same #201 grant with no revocation is in force` and `MAIN mandate: mandate in force`.
- **M3**, the gate's revocation thread reads #201 only (`for n in RECORD_ISSUES[:1]` in `_mandate`): killed by `budget_raise_gate` e2e `... after reading the comment, every record issue since it was written, then the body`.
- **Shim**: `gh_calls.py --self-test` carries its own mutant, `mutant: the continuation dropped from the trackers lets its planted post through`, which is killed. That self-test also pins `trackers=` to `RECORD_ISSUES`.

Script that ran M1 to M3 and the null, with the four self-tests named in the null below: a bash loop of `sed -i` on the line, then `timeout 600 python3 <tool> <self-test flag>`, then `git checkout -q -- tools/policy/budget_raise_gate.py`. `git status --short | wc -l` printed `0` after it.

## Null control

The same four self-tests on the unmutated head: `record_beat self-test: 17 checks, 0 failed`; `gh_comment.py self-test`: `TOTAL: 0 failed`, `SELF-TEST PASSED`; `budget_raise_gate self-test: 277 checks, 0 failed`; `orchestrator_tick self-test: 304 checks, 0 failed`. A post or a `gh issue comment` on the issue after the continuation (#3395) still reaches the real gh (`gh_calls.py` `null control: a gh issue comment on the issue after it reaches the real gh`), and a #201 post to another repository is not refused (`arm7_a_post_to_201_of_another_repository_passes (null control)`). A #201 grant with no revocation is in force (`record issues: null control` in the tick).

## Figures

- `python3 tools/policy/budget_raise_gate.py --self-test`: `277 checks, 0 failed`.
- `python3 tools/pr/gh_comment.py self-test`: `TOTAL: 0 failed`.
- `python3 tools/audit/seat/record_beat.py --self-test`: `17 checks, 0 failed`. `python3 tools/audit/seat/postmerge.py --self-test`: `19 checks, 0 failed`.
- `python3 tools/audit/seat/record_beat.py --dry-run 3350` prints `Merged #3350 b8f67a775137a8032d5c71b34ea64165c1d4613a (R10-OUTSIDE-INTAKE). Closed issues: none. Leaves #3394 open.` and posts with `--issue 3394`. That is the line owed for #3350.
- `python3 tools/audit/seat/merge_train.py --self-test`: `608 checks, 0 failed`. `python3 tools/audit/seat/orchestrator_tick.py --self-test`: `304 checks, 0 failed`. `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `45 checks, 0 failed`. `bash tools/audit/seat/merge_pr.sh --self-test`: `22 checks, 0 failed`.
- `python3 tools/audit/seat/gh_calls.py --self-test`: `200 checks, 1 failed`. The failure is `gh api dot segments resolving to #201 is refused`, and it is local to macOS `/bin/bash` 3.2. At `origin/main` (`git archive` of tools/ into scratch) the same failure appears: `196 checks, 1 failed`. CI runs Linux bash.
- `python3 tools/audit/seat/plan_page.py --self-test`: `76 checks, 0 failed`. `python3 tools/audit/carry_audit.py --self-test`: `402 checks, 0 failed`. `python3 tools/audit/seat/handover_prompt.py --self-test`: `20 checks, 0 failed`. `python3 tools/audit/seat/record_row.py --self-test`: `all checks passed`. `python3 tools/audit/seat/proof_watch.py --self-test`: `47 checks, 0 failed`. `python3 tools/audit/seat/pulse.py --self-test`: `58 checks, 0 failed`.
- Moved mutant anchors: `python3 tools/audit/seat/r10_mandate_guard_mutants.py --self-test`: `8 checks, 0 failed`. `python3 tools/audit/seat/r10_roster_ops_mutants.py --self-test`: `343 checks, 0 failed`. `python3 dev/audit/harnesses/r10_plan_issues_chart_mutants.py M0 orphans-dropped tracking-orphan` and `python3 dev/audit/harnesses/r10_plan_page_mutants.py tracking-excluded`: `RESULT survived=0` for each.
- `node tools/policy/policy_lint.mjs --budgets` exits 0. Rows: `CLAUDE.md` 3605 tokens against its cap of 3605. `.claude/rules/delivery-status-tracking.md` 765 against 766, paid by `GitHub issue` becoming `Issue`. `.claude/rules/writing-for-agents.md` 834 against 836.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 tools/audit/seat/selftest_wiring.py --check`: `127 self-testing, 127 wired, 0 unwired`, `0 index gap(s)`.
- `node tools/policy/brief_lint.mjs` exits 0.
- `python3 tools/audit/archscore/score.py --diff b8f67a7751 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select`: `MODE: FULL`, reason `.github/workflows/nightly.yml changes the gate itself`, so CI runs the full suite. Locally, `PYTHONPATH=tests/hastub python3 tests/entities.py` hit its 1500 s timeout (rc 124) while ci-ratchet's artifact fetch was getting `HTTP 502` from GitHub, so it gives no local verdict. Its edited pins were checked directly on `nightly.yml`'s non-comment job lines: `from budget_raise_gate import RECORD_ISSUE`, `issues/$RECORD_ISSUE/comments` present, and `issues/201/comments` absent. All three printed `True`. `ok   exactly one handover, with no date in its name` printed before the timeout.
- Seam census: `git grep -n -E '#?\b201\b' -- tools dev/governance .claude tests CLAUDE.md AGENTS.md .github`. Every write or coordination site it returns is either rewired above or is one of these:
  - `governance.yml` `delivery-status-publish` edits #201's body. Kept, because a body edit is unaffected by the cap.
  - `#201 comment <id>` citations. Reads, which stay valid.
  - The decision records 0007-0016. They record what was decided and are not rewritten.
  - Test fixtures that use 201 as a historical number: `gh_calls.py`'s spelling table (201 is still a tracker), `friction_issues.mjs`, `cloud_relay.sh`, and `gh_comment.py`'s privacy negatives.
  - HTTP status 201, in `gate.py`, `sweep_selftest.py` and `app_push.sh`.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

This policy change carries out the owner's ruling (tvofi, 2026-11-09 ~22:35Z), "Yes", to open a continuation issue and move the policy and tools to it. The orchestrator approves it under mandate 6715477401, scope all.
