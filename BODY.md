The roster's `resume.stage` is a claim a person writes, and until now nothing
compared it with the repository, so a group whose pull request had merged
stayed `in-progress`. `roster_sync.py` makes that comparison, and
`state_docs.py beat --apply` runs it on every pass. Part of #2496.

The sync derives only what a read can measure:

- A group whose pull request is MERGED becomes `done` at the merge commit.
- A group whose pull request is OPEN becomes `in-progress`, with the number in `resume.pr`.
- A branch with no pull request, or with only a closed-unmerged one, changes nothing. Absence is not evidence.
- A merged body's `Carry: <GROUP>` items are appended through `carry_audit.py`'s own parser. A destination that is done is refused.
- A human disposition is never overwritten. That covers `deferred`, `refused`, `refuted`, `absorbed`, `rca-done`, and any wording neither tuple classifies.

The only write path is `roster_edit.commit_roster()`. Without `--apply` the sync is a dry run.

This round answers review #1 (probe/rev-2554-2c937958), which listed five blocking items and one non-blocking item:

- **closures (item 8fac8b5b).** `roster_sync.py`, `roster_edit.py` and `carry_audit.py` now sit beside `ref_privacy.py` on `tests/closure.py`'s exception list, the precedent set by #2310. They are also added to `tests/entities.py`'s recorded closure, because `state_docs.py` imports `roster_sync`, which imports the other two.
- **pr-contract BAD-DEST (item c0223ec1).** Fixed by merging current `origin/main`. It is re-measured below with `--roster-ref origin/handoff/audit-r10-roster`.
- **Sibling topics (item bf644354).** When two groups' topics both match a head, only the longer topic gets it. A sibling's pull request can no longer decide the shorter group's stage or reopen it.
- **Unpinned arms (item d470e3e7).** New fixtures pin the `<topic>-` arm, carry dedupe, the issue-destination filter and the rc-path `_reset`. The reviewer's R9 (`-pr` not stripped) could not be pinned, because no input tells it apart: `<topic>-pr` already starts with `<topic>-`. The strip was dead code, so I deleted it instead of building a fixture for it.
- **Docstring (item 5ed82be8).** The withdrawn "2 of 48 / 47" count is removed. The design is now cited at `handoff/orch-machinery` 09174d94, `dev/audit/design/orch-machinery/DESIGN.md` section 6.4.
- **Design trace (item b1ecb708).** Of the four predicates, this diff builds commit resolution and dispositions the other three to a live group. See `## Forward-carry`. Every carry there is a precondition the orchestrator lands on the roster; this seat does not edit the roster.

Commit resolution (design 6.4, predicate 3) works like this:

- Every `resume.commit` is resolved by prefix with `git rev-parse --disambiguate` and must name exactly one commit.
- A done group's commit must also be an ancestor of `origin/main`.
- Any other record is printed as `RECORD-INVALID <group> <why>`. This is a finding, not a refusal, because a non-zero sync makes the beat skip its record.
- The length test is gone.
- An open group's commit is only resolved, not checked against `origin/main`. On the live roster, the first cut (ancestry checked for every stage) flagged R10-RCA-FRICTION's handoff head `d1611efe6`, which is legitimately not on main yet. Checking ancestry only for done groups removed that false positive, and M16 pins it.

## Head

`57bde327dc0e51df57edb6d393e48495b94ead0a`. It merges `origin/main` `1ebc737e7e18` (2026-10-21T20:56Z) into the round-1 head `b96aab8b8` with no conflict, then adds 7 commits. Every figure below was taken at this head, measured at 2026-10-21T21:07Z.

## Mutation proof

`python3 tools/audit/seat/r10_roster_sync_mutants.py` applies one one-occurrence plant to `roster_sync.py`, runs its self-test, and restores the file; it prints `restored`. Every plant goes red with a named `FAIL`, never with a crash alone. The self-test now prints each `FAIL` as it happens, so a later crash cannot swallow it.

| mutant | what it breaks | rc | fails | a failing check |
|---|---|---|---|---|
| M1_deferred_overwritten | protected stage | 1 | 2 | `a deferred stage is never overwritten` |
| M2_open_not_in_progress | open PR | 1 | 3 | `open PR: stage in-progress with its number` |
| M3_merged_without_commit | merge commit | 1 | 3 | `merged PR: stage done at its merge commit` |
| M4_carry_to_done_appended | done destination | 1 | 2 | `a Carry: to a done group is refused, not appended` |
| M5_second_parser | one parser | 1 | 2 | `carry_audit's parser is used: ...` |
| M6_dry_run_writes | `--apply` gate | 1 | 1 | `dry run creates no roster branch ...` |
| M7_exact_match_only (review R2) | `<topic>-` arm | 1 | 4 | `a head matching only through the <topic>- arm decides its group` |
| M8_sibling_decides | longest topic | 1 | 2 | `a sibling's open PR decides the sibling and never reopens the shorter topic's done group`, `a sibling's merge moves only the sibling to done` |
| M9_carry_dedupe_dropped (review R6) | held carry | 1 | 3 | `the dry run plans no append of an item the destination holds` |
| M10_issue_dest_appended (review R8) | issue destination | 1 | 1 | `an issue destination is neither appended nor refused ...` |
| M11_rc_path_no_reset | rc-path `_reset` | 1 | 1 | `and the refused pass leaves no local commit (the rc path's reset)` |
| M12_length_test | prefix resolution | 1 | 4 | `a unique 12-hex prefix on origin/main is valid (no length test)` |
| M13_off_main_accepted | done ancestry | 1 | 1 | `a done group's commit off origin/main is RECORD-INVALID` |
| M14_ambiguous_accepted | ambiguity | 1 | 1 | `an ambiguous prefix is RECORD-INVALID` |
| M15_record_invalid_silent | the printed finding | 1 | 1 | `a commit the checkout does not hold is RECORD-INVALID, printed and not a refusal` |
| M16_open_head_on_main | open handoff head | 1 | 1 | `an open group's handoff head off origin/main is valid` |

The reviewer's R9 anchor (`if name.endswith(PR_SUFFIX):`) is no longer in the file, because the strip it mutated is deleted (see the opening section). The reviewer called R5 (`closed_decides`) equivalent, and it stays equivalent: a closed PR has no merge commit, so it is skipped.

## Unpinned sites

`n/a: every added predicate in roster_sync.py has a plant above that turns it red. The ambiguous-prefix arm is pinned through commit_verdict, a pure function, because a fixture with two commits sharing a 7-hex prefix would need a brute-forced collision.`

## Null control

- `r10_roster_sync_mutants.py --null` prints `RESULT mutant=NULL_no_plant rc=0 fails=0`.
- Gate hole, using the reviewer's plant. One line appended to `roster_sync.py` in a detached worktree, then `python3 tests/closure.py select --diff HEAD`:
  - At the pre-fix merge `9df522f18540` it prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. The same is true for a plant in `roster_edit.py` and one in `carry_audit.py`.
  - At `243df21db1eb` (the closure commit) all three plants print `MODE: SCOPED -- 1 script(s) run, 32 scoped out` with `RUN tests/entities.py`.
- Sibling probe: the reviewer's `sibling_probe.py`, run unchanged over a detached worktree.
  - At `b96aab8b85f1`: `caseA_misattributed= 1`, `caseB_done_reopened= 1`.
  - At `c716e8e31b3c` (the matching fix): `caseA_misattributed= 0`, `caseB_done_reopened= 0`.
  - The probe's own null is `null_no_sibling_group_still_matches= 1` at both ends. A `-2` head still decides a group when no sibling group exists, so the fix narrows matching only where two topics compete.
- Commit resolution on the live roster (`origin/handoff/audit-r10-roster` `ae0f167c9`, through `roster_sync.invalid_commits('.', roster)` in this full clone):
  - `records=60 short=6 invalid=0`.
  - The design's length test applied to the same 60 records marks all 6 short ones invalid.
  - Before the done-only ancestry rule, the same call printed `invalid=1` (R10-RCA-FRICTION, an in-progress handoff head).
- The base harness `dev/audit/harnesses/r10_roster_sync_base.py` keeps its own control at both ends. See `## Figures`.

## Figures

- `python3 tools/audit/seat/roster_sync.py --self-test` -> `roster_sync self-test: 51 checks, 0 failed`.
- `python3 tools/audit/seat/r10_roster_sync_mutants.py` -> the table above, rc 0, `restored`.
- `python3 tools/audit/seat/roster_edit.py --self-test` -> `roster_edit self-test: 94 checks, 0 failed`. `python3 tools/audit/seat/state_docs.py --self-test` -> `state_docs self-test: all checks passed`.
- `python3 dev/audit/harnesses/r10_roster_sync_base.py` -> `RESULT base_apply_rc=2 head_apply_rc=0`, `base_stage=in-progress head_stage=done`, `head_noapply_stage=in-progress`, `base_deferred=deferred head_deferred=deferred`, `control=PASS`.
- Gate scope: `python3 tests/closure.py select --diff 1ebc737e7e18` -> `MODE: FULL`. `tests/closure.py` is a gate file, and the gate cannot scope a diff that touches one. I ran the scripts the diff reaches and left the full run to CI:
  - `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` (3.13 venv from `tests/requirements-ci.txt`) -> `ALL 2382 ENTITY CHECKS PASSED`, rc 0, 427 s wall.
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` (same venv) -> `ALL 109 HARNESS HEADER CHECKS PASSED`, rc 0, 165 s wall.
- `run_always` lines:
  - `tests/env_drift.py --claims-only origin/main` -> `claims hygiene: origin/main ok`.
  - `tests/closure.py selftest` -> `ALL 124 closure shrink pins PASSED`.
  - `tests/layout.py` -> `layout self-test: ok`.
- `python3 -I tests/layout.py --guard --base 1ebc737e7e18` -> `layout: GUARD: 0 refusal(s)`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `39 self-testing, 39 wired, 0 unwired`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` -> `0 refused`.
- `python3 -I tools/policy/agreement_py.py --out ag.json && node tools/policy/agreement.mjs --py-json ag.json` -> `unregistered=0`, `AGREEMENT ok`.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` -> `PRE-PR: 57bde327dc0e...`, rc 0. Its step 6d prints `the diff adds no unpinned mutation site`.
- `python3 tools/audit/archscore/score.py --diff 1ebc737e7e18` -> `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` -> `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`. With `--roster-ref HEAD`, the head's tree roster, the result is the same. The null control is `--roster-ref b96aab8b85f1`, the round-1 head's tree: `1 routed, 0 unrouted, 5 bad destination(s)`, every one `R10-ORCH-MACHINERY is not a group of the roster`, which is the refusal pr-contract printed.
- The roster carries this body depends on, read at `origin/handoff/audit-r10-roster` `3a5e096f8` (re-fetched just before this push):
  - The `ci_predict.py` carry is present on R10-ORCH-MACHINERY as `From #2554 (item 4ddebe42): ci_predict.py does not run the layout guard`. It landed at `b6e8c76eb`.
  - The `ref_privacy` carry is present on R10-POLICY-GATE-SCOPING as `From #2554 (item 4ddebe42): ref_privacy --check ignores \b on a macOS seat (BSD grep)` (`jq` over its `carry` for `ref_privacy`: 1 entry).
  - None of the three `b1ecb708` dispositions below is on R10-ORCH-MACHINERY yet (`jq` over its `carry` for `b1ecb708`: 0 entries). Each one is a request for the orchestrator to land.

## Red checks

- `closures` (run 119202770035) and `closures-autofix` (119216792955, `skip-merge-failed`). Cause: this diff gave `state_docs.py`, which `entities.py` loads, an import of `roster_sync` (and through it `roster_edit` and `carry_audit`), but left all three under the INERT `tools/audit/` prefix. Answered: the three now sit on `tests/closure.py`'s exception list and in `entities.py`'s recorded closure, and the plants in `## Null control` show the gate now selects `entities.py`. The cheaper detector is `tests/closure.py select --diff HEAD` with a one-line plant in each newly imported file, which takes about a second per file. No pre-handoff step runs it. Closure-file edits are measured by CI, so this push carries `PREPR_SKIP_CLOSURES=1`. Carry: dismissed: answered in this diff (item 8fac8b5b)
- `pr-contract` (119217234807): `BAD-DEST` on b79e7e68 and 00bf85b5, because R10-ORCH-MACHINERY was not a group of the head's tree roster. Answered: merging `origin/main` brings the group into the tree, and the carry audit above reads 0 bad destinations. The cheaper detector is that same `carry_audit.py check --body` run before `body_push.sh`, under a second. Carry: dismissed: answered by the merge (item c0223ec1)
- `nightly-status` grades `main` (the replay `loop_cpu_ratio` budget), not this branch. Carry: R10-REPLAY-CAP (item 57bf9e90)

## Forward-carry

- `tools/pr/ci_predict.py`, the predictor behind `body_push.sh`, does not run the layout guard (`grep -c 'layout.py\|--guard' tools/pr/ci_predict.py` -> `0`). Its control: a layout-violating fixture must make `ci_predict` predict red. Present at `b6e8c76eb`. Carry: R10-ORCH-MACHINERY (item 4ddebe42)
- `ref_privacy.py --check` enforces nothing on a macOS seat, because its site scan keys on `\b` through the host's `git grep -E`, which does not honour it. Its control: on a host whose `git grep -E` ignores `\b`, a planted host name must still be refused. Present at `3a5e096f8`. Carry: R10-POLICY-GATE-SCOPING (item 4ddebe42)
- Design 6.4 predicate 1, **gate coverage**, dispositioned and not built. Carry text for R10-ORCH-MACHINERY: "From #2554 (item b1ecb708): design 6.4 predicate 1, gate coverage, was assigned to R10-ROSTER-OPS (done at 929275e8) and not built there. owner_gate becomes structured {class, mandate, paths}, and readiness is class x in-force mandate scope, read from tools/policy/budget_raise_gate.py's own constants: code-owned <- code-owned|all, budget <- budget-raise|all, policy <- all only. It prints GATE-READY or GATE-OWNER <class>. Control: the run that prints the live roster's gate set at the mandate's scope returns every covered group ready and none blocked on the owner." It is not built in `roster_sync.py` for two reasons. It changes the roster's `owner_gate` schema, and its consumer is the tick's owner-gated count, which is R10-ROSTER-OPS's carry[0] and the design's PLAN section. Neither reads a pull request. Carry: R10-ORCH-MACHINERY (item b1ecb708)
- Design 6.4 predicate 2, **absorbed-edge closure**, dispositioned and not built. Carry text for R10-ORCH-MACHINERY: "From #2554 (item b1ecb708): design 6.4 predicate 2. resume.stage absorbed with absorbed_into <group> joins roster_lib.DONE_STAGES only when every after edge of the absorbed group is on the absorbing group or its transitive closure; otherwise ABSORB-EDGE-MISSING and the stage stays open. Control: a deliberately absorbed group missing one edge is refused." It is not built here for two reasons:
  - The fail-safe half already holds. `absorbed` is outside `DONE_STAGES` (`roster_lib.py`), so an absorbed group stays open today, and `roster_sync` protects the stage.
  - The rest would change `DONE_STAGES`, which `pr_cap.py`, `prune_refs.py`, `handover_prompt.py` and the tick all read. `jq '[.groups[]|select(.resume.stage=="absorbed" or .resume.absorbed_into!=null)]|length'` over the live roster -> `0`.

  Carry: R10-ORCH-MACHINERY (item b1ecb708)
- R10-ROSTER-OPS carry[4] (from #2545), the **brief pinned at handoff**, dispositioned and not built. Carry text for R10-ORCH-MACHINERY: "From #2554 (item b1ecb708): pin a group's brief at handoff (its hash beside resume) and compare it on each later pass, printing a brief that moved after its handoff (design section 3(d), carried from #2545). Control: a brief edited after its pin is reported on the next pass, and an unedited one is not." The handoff is the dispatcher's event, and no pull-request read observes it, so the pin belongs where the handoff is written. Carry: R10-ORCH-MACHINERY (item b1ecb708)

## Friction

- cloud_dispatch: stale: the payload says "the toolchain (venv python, node, gh) is on PATH". In this seat `python3` was the system 3.11 without `voluptuous`, and `gh auth status` printed `Failed to log in to github.com using token (GH_TOKEN)`. I built a 3.13 venv from `tests/requirements-ci.txt` for the gate runs. Carry: R10-ORCH-MACHINERY (item 4c5f0868)

## Approval

Behaviour change: `state_docs.py beat` gains `--apply`. On each pass it runs `roster_sync.py`, which writes `resume.stage`, `resume.commit`, `resume.pr` and a destination group's `carry` through `roster_edit.py`'s lint gate, on measured evidence only. It also prints `RECORD-INVALID` lines, which write nothing. Without `--apply` the beat behaves as before, and the one-shot form is a dry run unless `--apply` is given. Rollback: revert this merge. Nothing reads `resume.pr`, and no other behaviour changed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01MWa7pKJZABy1JvGSSV8qAY
