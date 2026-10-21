R10-PLAN-ARTIFACT: the round's plan page is built only by tracked instruments. `tools/audit/seat/plan_page.py --plan plan.json --html out.html` draws what the out-of-tree `gen.py` + `tpl.html` drew (reference `7bc61133` on `probe/plan-port-src`, read, not merged), from `tools/plan/replan.py`'s plan.json and the roster through `roster_lib`. It refuses (exit 1, nothing written) a plan whose roster blob is not the roster's blob at its ref now. `replan.py --check` applies the same rule, `replan.stale_reason`; until now it printed PLAN OK on a stale plan.

Design (fixer.md step 17):
- **The owner of the page is a new module beside `plan_table.py`, not an `--html` flag on it.** `plan_table.py` is in `tests/entities.py`'s recorded closure (`state_docs.py` spawns it), and its model is dependency depth over the roster. The page's model is replan's schedule. Folding the page into `plan_table.py` would put two models in one file and widen a recorded closure. `plan_page.py` sits under the INERT `tools/audit/` prefix, the same as every seat instrument.
- **The freshness rule has one owner, `replan.py`, because replan.py writes plan.json.** The page imports it, so `--check` and the page cannot disagree about which plans are current. `load_roster` now takes its blob from `replan.roster_blob`, so the blob is derived in one place.
- **plan.json now records the duration model it was computed with** (`generated.model`: sizes, live fraction, the sizes provenance). The ETA text states the plan's figures, not those of whatever `durations.json` holds at render time. A plan without that record is refused with a replan instruction.
- **What changed from `gen.py`:**
  - Dropped: the dependency-depth table, and "ready · depth N".
  - Every literal count is now filled from plan.json. Examples: the 5-group stamp cadence comes from `caps.stamp_every`, the 0-minute window from `caps.batch_window_minutes`, and the "S above M" sentence from `sizes_provenance`.
  - The axis runs to the last planned stamp. The minor stamp lands `closure_lead_minutes` after closure, so it was never drawn before.
  - The link caption printed the *skipped* count as the drawn count. It now prints the drawn count.
  - The tooltip is built with `textContent`, not `innerHTML`.
  - The round number and the `R<N>-` prefix come from the roster path, not a hard-coded `R10-`.
- **A third PR lookup was added, beyond the brief: the one roster group id a PR title names.** It is the last fallback, after `roster_lib.group_for_branch` and then gen.py's tail match. The live check below shows #2524 and #2528 named by neither branch rule. A title naming two groups maps to neither.

## Head

`43b1307e5db4f6959e2705fff38afea38a137f75` is the head this body leaves, unchanged by this re-take (no code pushed). It is `closures-autofix`'s commit `ci: re-record closures` on top of `2b1ba538fa8a780d4a0b1d43b721daa3274df6f0`, and touches `tests/closures.json` alone: it adds `dev/audit/harnesses/r10_mermaid_gantt_title.mjs` to `inert_reads["tests/harness_headers.py"]` and re-times `tests/boost_drift_replay.py` (`seconds` 303.9 -> 752.2). `git show --stat 43b1307e5db4f6959e2705fff38afea38a137f75` names that one file.

`2b1ba538fa8a780d4a0b1d43b721daa3274df6f0` merges origin/main `03b49e152` into the authored code head `e8810a6e7dd0c42bae53a7af801c4dd98854adce` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`e8810a6e7dd0c42bae53a7af801c4dd98854adce`. Merge base and `origin/main` tip at measurement: `6961f06637964001a2ed544e495ea0312eeefa37`, at 2026-10-21T10:45Z. Roster ref `origin/handoff/audit-r10-roster` at `05b3bd68f0f5`, roster blob `8974a63d916c`.

## Mutation proof

Driver: `python3 dev/audit/harnesses/r10_plan_page_mutants.py`. It applies one exact one-occurrence replacement, runs `plan_page.py --self-test`, restores the file byte for byte, and refuses a file with uncommitted edits. Every row printed `verdict=killed`. Each row below gives the mutant, then the red checks:
- `live` (LIVE_STAGES branch → `False`): `live`, `rows carry the live class`, `the summary strip counts live`, `... ready`.
- `blocked` (`elif blk and not part:` → `False`): `blocked: an after target not done`, `rows carry the blocked class`, `the summary strip counts blocked`.
- `partial` (the `R<N>-X:` title match → `False`): `partial: a merged R9-PART: title on an open group`, `rows carry the partial class`.
- `blocked-by-less-done` (done targets kept in `blk`): `blocked-by is the roster's after less the done groups`, `ready: its only after target is done`.
- `pr-by-merge-commit`: `done: the PR is found by merge commit`.
- `pr-by-branch`: `done: the PR is found by branch when no merge commit matches`.
- `pr-sha8-fallback`: `done: no PR found falls back to the commit's sha8`.
- `branch-tail-fallback`: `the open PR maps by the branch-tail fallback`.
- `title-fallback`: `an open PR whose branch names no group maps by its title`.
- `closed-strike`: `a closed issue's chip is struck`.
- `tracking-excluded`: `the open-issue count leaves out the tracking issue`.
- `page-refuses-stale` (`if stale:` → `False` in `main`): `a stale plan is refused, nothing written`.
- `freshness-rule` (`if have != want:` → `False` in `replan.stale_reason`): `a stale plan is refused, nothing written`, `and replan --check refuses the same plan`.
- `stamp-on-axis`: `a planned stamp is drawn`.

`replan.py --self-test`'s own mutation harness has a new `freshness` row with the same deletion. It printed `mutation freshness: 'if have != want:' -> rc=1` and `ok self-test fails when freshness is deleted`.

One survivor in the first pass, disclosed: `pr-by-merge-commit` survived because fixture PR #21 also carried `R9-DONE-SHA:` in its title, so the title fallback answered for it. The fixture now names its group by merge commit alone, and the re-run kills it.

## Null control

- M0, nothing replaced: `RESULT mutant=M0 rc=0 fails=0 verdict=null`.
- **Freshness at the merge base: PLAN OK on a stale plan.** The plan was built at `--roster-ref b5ec0c98` (the roster one commit back, blob `eaf4288a90d0`) and relabelled to the live ref. The base's `replan.py --check` printed `PLAN OK` with rc 0. The head refused it, rc 1: `freshness: plan.json is stale: built from roster blob eaf4288a90d0, but origin/handoff/audit-r10-roster:... is now 8974a63d916c`. The head passes a plan built at the live blob (`PLAN OK`, rc 0). On the stale plan, the page printed `refused, nothing written`, rc 1, and the output file did not exist afterwards.
- **The refusal fired for real once during this work.** A plan built before a fetch moved the roster ref (blob `d5b1fbee4f8d` → `8974a63d916c`) was refused by the page's own fetch-then-check.
- `selftest_wiring.py --check` with `governance.yml` reverted to the base printed `UNWIRED tools/audit/seat/plan_page.py` (`37 wired, 1 unwired`). At the head it printed `38 wired, 0 unwired`.
- **The mermaid `;` needs no fix.** Harness: `node dev/audit/harnesses/r10_mermaid_gantt_title.mjs <dir>` over mermaid 11.4.1 and jsdom 24.1.3 from npm. On `plan_table.gantt()` of its own fixture it printed `RESULT arm=tree parsed=true title="Fix waves; crit = the critical path"`. The 11.4.1 lexer rule is `title\s[^\n]+`, so a title runs to the line's end. The null arm, `; x` appended to the `dateFormat` line (rule `[^#\n;]+`), printed `parsed=false`. So the parser can refuse a `;`; it does not refuse one in the title. `plan_table.py` is unchanged.

## Figures

- `plan_page self-test: 36 checks, 0 failed`: `python3 -I tools/audit/seat/plan_page.py --self-test`. GitHub is never reached: `main` runs with a fetch that fails the test if called.
- `self-test: 0 failed`, including 6 new freshness arms and the `freshness` mutant: `python3 tools/plan/replan.py --self-test`.
- `RESULT survived=0`: `python3 dev/audit/harnesses/r10_plan_page_mutants.py`.
- Live page against the roster at blob `8974a63d916c`: `python3 tools/plan/replan.py --out plan.json` then `python3 tools/audit/seat/plan_page.py --plan plan.json --html round-10-plan.html --github-snapshot snap.json`. This container's `gh` token is refused (`gh auth status`: "The token in GH_TOKEN is invalid"), so the snapshot was assembled as follows:
  - Open PRs and open issues from the GitHub MCP tools (`list_pull_requests state=open`, `list_issues state=OPEN`).
  - Roster issues not open marked CLOSED.
  - Merged PRs from `git log origin/main --first-parent --merges` "Merge pull request #N from <owner>/<branch>" subjects, with merge sha and title. This misses a squash-merged PR. The 2026-10-10 onward non-merge first-parent commits are stamps, nightly-kill records and three `record:` rows, none of them a group's PR.
- What the sanity checks measured on that page, out-of-tree style, each by regex over the written HTML:
  - Group rows: 108, and the roster has 108 groups.
  - Name set equal to the roster's, with the `R10-` prefix stripped.
  - Stages: 50 done rows against 50 roster `done`. 21 live rows against 21 `in-progress`. 14 ready + 23 blocked = 37, against 34 `not-started` + 3 `queued`.
  - Open PRs shown on open rows: 11 of 14 (#2513 #2521 #2524 #2527 #2528 #2529 #2531 #2545 #2547 #2548 #2549). #2529 maps by the tail fallback (`fix/r10-ci-layout-g` → R10-CI-LAYOUT). #2524 and #2528 map by title.
  - The three not shown, each dispositioned: #2550 is a `record:` row, owned by no group. #2544, the dependency bump, names no group by branch or title; R10-DEPENDABOT-AIOHTTP's `resume.branch` is `fix/r10-dependabot-aiohttp`. #2525 maps by title to R10-OPENPR-SILENT, a done group, whose row shows its merged PR #2422 by design.
  - Merged PRs shown on an open row: 0.
  - Done rows whose PR cell is a number: 50 of 50.
  - Machine paths (`/home/`, `/Users/`, `/tmp/`) in the page: 0, by `grep -c`.
- `selftest_wiring: 38 self-testing, 38 wired, 0 unwired`: `python3 -I tools/audit/seat/selftest_wiring.py --check`.
- `tmp_paths: 0 refused`: `python3 -I tools/audit/seat/tmp_paths.py --check`.
- `ref_privacy --check ... 0 refused`: `python3 -I tools/audit/seat/ref_privacy.py --check`.
- Scope: `python3 tests/closure.py select --diff 6961f0663796 --workdir "$D"` printed `MODE: FULL`, reason `tests/closure.py changes the gate itself`. The change there is the INERT comment for `tools/plan/`, which named the out-of-tree renderer. The following were run locally with `PYTHONPATH=tests/hastub` and the seat venv; the rest is CI's:
  - `ALL 2375 ENTITY CHECKS PASSED`: `python3 tests/entities.py`.
  - `ALL 109 HARNESS HEADER CHECKS PASSED`: `python3 tests/harness_headers.py`.
  - `STRUCTURE RATCHET PASSED`: `python3 tests/structure.py`.
  - `ALL 124 closure shrink pins PASSED`: `python3 tests/closure.py selftest`.
  - `claims hygiene: origin/main ok`: `python3 tests/env_drift.py --claims-only origin/main`.
  - `layout self-test: ok`: `python3 tests/layout.py`.
- `tests/closures.json` gains one `inert_reads` entry, `tests/harness_headers.py` -> `dev/audit/harnesses/r10_plan_page_mutants.py`. That script discovers harness files by their RESULT headers, and prepr's closure predictor refused the head without the entry (`CI PREDICT: 1 predicted red(s) on closures`). It was written by `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --apply-inert`, which then printed `CI PREDICT: no closures or fast red predicted`. The code is byte-identical to the head the figures above were first taken at (`0a0d5d06`). The three self-test and mutant figures were re-taken at this head.
- That `CI PREDICT: no closures or fast red predicted` was a false negative, and the closures red it missed is answered under `## Red checks`. At `e8810a6e7dd0c42bae53a7af801c4dd98854adce`, `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base 6961f06637964001a2ed544e495ea0312eeefa37` printed `CI PREDICT: no closures or fast red predicted against 6961f0663796`. Null control, same tree and command, with one extra `.mjs` path appended to `inert_reads["tests/harness_headers.py"]` in the worktree (then `git checkout -- tests/closures.json`): `PREDICT closures INERT READS tests/harness_headers.py: dev/audit/harnesses/r10_mermaid_gantt_title.mjs (a new file beside 3 it lists)`. The rule: `inert_siblings` predicts only when that list already names at least 3 files with the new file's directory and suffix. At `6961f066`, `e8810a6e` and `03b49e152` the list names 2 `dev/audit/harnesses/*.mjs` (`r10_stats_window.mjs`, `r9_fr3_family_consumer.mjs`), read with `git show <ref>:tests/closures.json` and a filter on that prefix and suffix.
- `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`, rc 0: `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>`. Roster ref at `23ef06dc6cc7` on 2026-10-21. Null control: the same check without `--roster-ref`, in a checkout of `43b1307`, printed `2 bad destination(s)` (rc 1). That is the in-tree read `pr-contract` makes, and its output is quoted under `## Red checks`.
- `Architecture score: dS +0.0000 NULL`: `python3 tools/audit/archscore/score.py --diff origin/main`. No file under `custom_components/` changed.

## Red checks

The reds on this branch's pushed commits, from the check-runs at each commit between the merge base and the head (`pull_request_read get_check_runs` at the head, `actions_list list_workflow_jobs` for run 39592967889 at `2b1ba538`): `closures` at `2b1ba538`, `nightly-status` at `2b1ba538` and at `43b1307`, and `pr-contract` at `43b1307`. At `43b1307` the latest `closures` runs are green (jobs 119239132126 and 119231851596), as are the rest. The other jobs are skipped or green.

- **`closures` (job 119212886451, run 39592967889, at `2b1ba538`): this PR's own red, already repaired by the bot.** The failing step is `Fail if tests/closures.json under-approximates`. The cause is that `tests/harness_headers.py` reads every file under `dev/audit/harnesses/`, and this diff adds `r10_mermaid_gantt_title.mjs` there without an `inert_reads` entry. `closures-autofix` (job 119219923777, `Merge UNDER-SCOPED recordings` then `Push the merged closures`) pushed `43b1307` with that entry. `closures` is green at `43b1307`. By `ci-autofix.md`, the bot's repair is the fix and is not repeated here, so no code moved in this re-take.
  The cheaper detector exists and ran: `tools/pr/ci_predict.py`, which `body_push.sh` and `prepr.sh` run. Its standing cost is seconds, and it runs no test. It missed this one. Its `inert_siblings` arm only predicts a new file beside at least 3 listed files of the same directory and suffix, and `tests/harness_headers.py`'s list held 2 `.mjs` harnesses. The figure and its null control are under `## Figures`. Process state (c): the predictor was followed and did not produce the intended result for a suffix with fewer than 3 listed siblings. The threshold is deliberate: the docstring says it stops `tools/audit/seat/`'s two individually named files reading as a glob. So the countermeasure belongs in the predictor and in a root-cause seat beside this fix, not inside it (`defect-root-cause.md`). Cost of this occurrence: one red `closures` run of about 15 minutes (12:09:54 to 12:25:15Z, `Re-record the closures`) and one bot commit on the reviewed head.
- **`nightly-status` (job 119220466241 at `43b1307`, job 119198245423 at `2b1ba538`): main's red, not this diff's.** The failing line is `NIGHTLY FAILED: mutation-nightly, slow failed last night.`, `scheduled run 39563978649, 2026-10-21T07:43:20+00:00, head c77f89d`. `c77f89dc619c` (`Merge pull request #2540 from tvofi/record/autofix`) is on `origin/main` and an ancestor of this PR's base `03b49e152` (`git merge-base --is-ancestor c77f89d 03b49e152` exits 0). No commit of this branch was in that run. This diff does touch one reporter input, `.github/workflows/governance.yml`. That touch is the one added step `Show the plan page refusing its own fixtures` in its self-test job. `tests/nightly_status.py` reads the scheduled runs of `tests.yml` (`DEFAULT_WORKFLOW = "tests.yml"`), and this diff does not change `tests.yml` or `nightly_status.py`. So the step cannot move what it grades. Answer: the red is owned on `main` by the orchestrator, per `defect-root-cause.md`, through the `mutation-nightly` and `slow` lanes of run 39563978649. It is not this PR's to fix. No cheaper detector is owed by this diff, because the cheapest detector of a nightly lane's failure is that lane.
- **`pr-contract` (job 119220476142 at `43b1307`): the body's carry destination against the head's tree roster.** The failing lines are `BAD-DEST body item 3bed3711: R10-ORCH-MACHINERY: R10-ORCH-MACHINERY is not a group of the roster` and its twin `2aaba703`, then `CARRY-AUDIT: 2 finding item(s): 0 routed, 0 unrouted, 2 bad destination(s)`. The step reads `dev/programme/rosters/wave-r10-groups.json` from the PR's checkout. At `43b1307` that file names `R10-ORCH-MACHINERY` 0 times, and at `origin/main` 1 time (`git show <ref>:dev/programme/rosters/wave-r10-groups.json | grep -c R10-ORCH-MACHINERY`). The group was appended on the roster ref on 2026-10-20 (`2f36fd104 roster_edit append-group R10-ORCH-MACHINERY`). It reached `main`'s tree with `5226fd2d1` (`Merge pull request #2559 from tvofi/fix/audit-r10-roster`, 2026-10-21T17:36+02:00), after this branch's last main merge `2b1ba538` (13:14+02:00). The first-parent log of `origin/main` with `-S R10-ORCH-MACHINERY` on that file shows it. The destination is live on the roster ref (`resume.stage` `not-started`), and `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check` passes this body (under `## Figures`). The step goes green on the orchestrator's next `origin/main` merge into this head. This seat does not move the frozen head (`fixer.md` step 6). Cheaper detector: `prepr.sh`'s carry arm, run with the roster ref; the in-tree read cannot see a group that reaches `main` after the merge base.
- Earlier local red, answered before: `tests/harness_headers.py` refused the first copy of `r10_plan_page_mutants.py` (`depth seams: ... parents[3]`). It now uses the canonical `repo_root` walk. The cheaper detector is that script itself, run locally before the push, so nothing further is owed.

## Unpinned sites

n/a: no production module under `custom_components/` changed. The predicates `plan_page.py` adds are each pinned by a self-test arm, shown killed under `## Mutation proof`.

## Forward-carry

- R10-ORCH-MACHINERY's item (3), "the plan page as a tree instrument sharing one model builder with `plan_table.py`, driven by `state_docs.py` ... failing to an explicit UNAVAILABLE page", is partly landed here, and its premise changed:
  - The page exists as `tools/audit/seat/plan_page.py`.
  - Its model is the schedule replan.py writes, not `plan_table.py`'s dependency-depth waves. The two cannot share one builder without one of them computing a schedule the other does not hold.
  - It refuses a stale or violating plan with exit 1 and writes nothing, rather than writing a page of zeros.
  - What remains for that stage: driving it from `state_docs.py`; an UNAVAILABLE page in place of no page, if the design still wants one; and the five generator-defect fixtures. Before building on this, re-measure with `python3 -I tools/audit/seat/plan_page.py --self-test` at that stage's merge base.

  Carry: R10-ORCH-MACHINERY
- The orchestrator's out-of-tree `gen.py` / `tpl.html` should be retired once this merges, since the page they drew is now this instrument's output. The re-measure is the live sanity run under `## Figures`. Carry: R10-ORCH-MACHINERY

## Friction

`none`

## Attribution

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01C68C1zSdZZ7gKc15C8NY6e
https://claude.ai/code/session_01S25pjzsWGC2U7zMp9yJg5U
