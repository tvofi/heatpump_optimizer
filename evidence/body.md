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

The only write path is `roster_edit.write_roster()`, push-race retry included. Without `--apply` the sync is a dry run.

Commit resolution (design 6.4, predicate 3) works like this:

- Every `resume.commit` must match the sha grammar, then is resolved by prefix with `git rev-parse --disambiguate`, filtered to commit objects by `git cat-file --batch-check`, and must name exactly one commit.
- A done group's commit must also be an ancestor of `origin/main`. An ancestry git cannot read (rc 128, for example a checkout with no `origin/main`) is invalid, never valid.
- Any other record is printed as `RECORD-INVALID <group> <why>`. This is a finding, not a refusal, because a non-zero sync makes the beat skip its record.
- The length test is gone.
- An open group's commit is only resolved, not checked against `origin/main`, because its handoff head is legitimately not on main yet. M16 pins it.

This round answers review #2 (probe/rev-2554-e07a772e, blocked at d82acd2e):

- **carry-missing (items b1ecb708, 4c5f0868).** The four texts are now on R10-ORCH-MACHINERY at `origin/handoff/audit-r10-roster` `743463c61f6a`, each citing #2554 (see `## Figures`). The body routes them there and quotes the landed entries; no request to the orchestrator is outstanding.
- **nightly-status destination (item 57bf9e90).** The body now reads `Carry: R10-REPLAY-LANE`, the in-progress group that holds the item at `743463c61f6a`, in place of the done R10-REPLAY-CAP.
- **Surviving plants RA, RB, RF (and RC).** Each now has a call-site fixture in `roster_sync.py`'s self-test and a plant in the driver (M17 to M20). The false `n/a` under `## Unpinned sites` is replaced by a disposition per site.

Review #1's items (closures 8fac8b5b, pr-contract c0223ec1, sibling topics bf644354, docstring 5ed82be8, unpinned arms d470e3e7, design trace b1ecb708) were settled at d82acd2e per review #2's Evidence; their figures are re-taken below at this head.

## Head

`d270da26b386414811e6fa12750ee10f5477c37d` merges the authored code head `97280902daf9194d30c3b90b9b95d25626e561ef` and then merges origin/main `46e368127` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`97280902daf9194d30c3b90b9b95d25626e561ef`. From the reviewed head `d82acd2eddf8` it carries, in order:

- a merge of `origin/main` `5a755f53efda` (`db85cd51e`, no conflict);
- `819eff3ea`, the RA/RB/RF/RC fixtures and plants M17 to M20;
- `673daec50`, the no-origin fixture built with `throwaway_git_init`, which prepr's throwaway-git check required;
- a merge of `origin/main` `214350c42f40` (`1ecddec16`), which conflicted, resolved as described below;
- a merge of `origin/main` `302f665711fb` (`8b8db81f0`, no conflict);
- `0111d36e0`, the `tests/closures.json` INERT READS entry `ci_predict.py --apply-inert` wrote for `tools/audit/seat/r10_roster_sync_mutants.py`. `ci_predict` predicted a red `closures` without it; it now prints `no closures or fast red predicted`.
- a merge of `origin/main` `46e3681276f9` (`97280902d`, no conflict; delivery rows only).

Every figure below was taken at this head's tree, measured from 2026-10-22T00:19Z (origin/main `46e3681276f9` at that time).

The `214350c42f40` merge conflicted in `tools/audit/seat/roster_edit.py`, semantically. Main's #2569 (R10-ROSTER-PUSH-RACE) rewrote `main()`'s write path: a detached worktree, a push by the commit's sha, and a re-fetch plus re-apply of the op when a rival moved the branch, at most `PUSH_ATTEMPTS` times. This branch had lifted the old path into `commit_roster()` so `roster_sync.py` shares it. Taking either side would have lost behaviour: main's side drops the shared path, and this branch's side drops the race fix. The old `commit_roster()` also pushed by branch name, which the detached worktree no longer has. The resolution takes main's loop unchanged into one function, `roster_edit.write_roster(checkout, ref, branch, worktree, roster_path, msg, push, lint_cwd, label, edit)`. `main()` passes an `edit` that runs `apply_op`. `roster_sync.sync` passes one that re-derives the plan from the bytes loaded at that attempt's base, so a retried sync is computed on the rival's tip. Two of `roster_sync`'s self-test checks read `refs/heads/<branch>` in the checkout, and the detached path makes no such branch. They now run the pass in a persistent `--worktree` and check that worktree's HEAD is back at base. That is the state `prepare_worktree`'s unpushed-edit guard reads, and M11 still turns it red. One check was a duplicate of `and the branch did not land` and was dropped; `the retry lands once the refusal is cleared` still covers the next pass not being refused. That is why the self-test went from 54 checks to 53. Main's own race instruments, at the head named in `## Head`: `roster_edit.py --self-test` -> `roster_edit self-test: 106 checks, 0 failed`; `bash dev/audit/harnesses/r10_roster_push_race.sh . <mode>` -> `mode=shared silent_losses=0 false_reports=0 refused_edits=0 pushes=2`, `mode=separate silent_losses=0 false_reports=0 refused_edits=0 pushes=2`, and the null `mode=solo ... pushes=1`; `python3 tools/audit/seat/r10_roster_ops_mutants.py` -> every plant listed (A1 to A7, C1 to C8, P1 to P3, D1) `rc=1` with `fails>=1`. No race fixture drives `roster_sync` itself: the retry is `write_roster`'s, and `roster_edit`'s self-test pins it through `main()`. The sync's part is the `edit` callback, which the race re-runs and which is the same derive the dry-run fixtures pin.

## Mutation proof

`python3 tools/audit/seat/r10_roster_sync_mutants.py` applies one one-occurrence plant to `roster_sync.py`, runs its self-test, and restores the file; it prints `restored`. Every plant goes red with a named `FAIL`, never with a crash alone.

| mutant | what it breaks | rc | fails | a failing check |
|---|---|---|---|---|
| M1_deferred_overwritten | protected stage | 1 | 2 | `a deferred stage is never overwritten` |
| M2_open_not_in_progress | open PR | 1 | 3 | `open PR: stage in-progress with its number` |
| M3_merged_without_commit | merge commit | 1 | 3 | `merged PR: stage done at its merge commit` |
| M4_carry_to_done_appended | done destination | 1 | 2 | `a Carry: to a done group is refused, not appended` |
| M5_second_parser | one parser | 1 | 2 | `carry_audit's parser is used: ...` |
| M6_dry_run_writes | `--apply` gate | 1 | 1 | `dry run creates no roster branch ...` |
| M7_exact_match_only | `<topic>-` arm | 1 | 4 | `a head matching only through the <topic>- arm decides its group` |
| M8_sibling_decides | longest topic | 1 | 2 | `a sibling's merge moves only the sibling to done` |
| M9_carry_dedupe_dropped | held carry | 1 | 3 | `the dry run plans no append of an item the destination holds` |
| M10_issue_dest_appended | issue destination | 1 | 1 | `an issue destination is neither appended nor refused ...` |
| M11_rc_path_no_reset | rc-path `_reset` | 1 | 1 | `and the refused pass leaves no local commit (the rc path's reset)` |
| M12_length_test | prefix resolution | 1 | 5 | `a unique 12-hex prefix on origin/main is valid (no length test)` |
| M13_off_main_accepted | done ancestry | 1 | 1 | `a done group's commit off origin/main is RECORD-INVALID` |
| M14_ambiguous_accepted | ambiguity | 1 | 1 | `an ambiguous prefix is RECORD-INVALID` |
| M15_record_invalid_silent | the printed finding | 1 | 1 | `a commit the checkout does not hold is RECORD-INVALID, printed and not a refusal` |
| M16_open_head_on_main | open handoff head | 1 | 1 | `an open group's handoff head off origin/main is valid` |
| M17_unreadable_ancestry_ok (review RA) | rc 128 mapping | 1 | 1 | `a checkout with no origin/main reads the ancestry as unreadable` |
| M18_non_commit_counted (review RB) | commit-type filter | 1 | 1 | `a prefix resolving only to a blob does not resolve to a commit` |
| M19_sha_grammar_dropped (review RC) | sha grammar | 1 | 1 | `a value outside the sha grammar is RECORD-INVALID, by the grammar` |
| M20_shared_topic_first_only (review RF) | shared topic | 1 | 1 | `groups sharing one topic share its pull requests` |

M12 moved from 4 fails to 5 because the new blob fixture uses a 12-hex prefix, which the length test refuses for the wrong reason.

The reviewer's own driver (`ev/tools/rev_mutants.py` on probe/rev-2554-e07a772e, sha1 `a70fb36a5e49`), run unchanged over this worktree: `NULL rc=0 fails=0`; `RA rc=1 fails=1`; `RB rc=1 fails=1`; `RC rc=1 fails=1`; `RD rc=1 fails=3`; `RE rc=1 fails=3`; `RG rc=1 fails=8`; `RF rc=0 fails=0`; `restored`. RF stays green because that plant is equivalent: its added condition `gid not in [groups already holding pr]` is true for every group on its own first visit, so it never restricts. With that plant applied, `matches()` over two groups sharing topic `r9-twin` and one PR gives `T-ONE=1 T-TWO=1`, the unplanted result. M20 is the restricting plant (a `break` after the first append), and it goes red.

## Unpinned sites

- RA, `invalid_commits`'s rc mapping `{0: True, 1: False}.get(rc)`: pinned by M17 through a call-site fixture, a fresh repository with no `origin/main` (rc 128).
- RB, the `cat-file --batch-check` commit-type filter: pinned by M18 through a call-site fixture, a blob written with `git hash-object -w` and recorded by its 12-hex prefix.
- RC, the `SHA_RE` grammar test: pinned by M19. The existing check now asserts the grammar's own reason, not only that the record is flagged.
- RF, the shared-topic rule in `matches()`: pinned by M20 through a direct `matches()` fixture. The live roster has no shared topic today (review #2's ev/shared-topics.txt), so the pin guards the docstring's claim, not a live case.
- The ambiguity arm: pinned by M14 through `commit_verdict`, a pure function. A call-site fixture would need two objects sharing a prefix, which needs a brute-forced collision. The call site's input to that arm is the filtered commit list, which M18 now pins.

## Null control

- `r10_roster_sync_mutants.py --null` prints `RESULT mutant=NULL_no_plant rc=0 fails=0`.
- Gate hole. A one-line plant appended to each of `tools/audit/seat/roster_sync.py`, `tools/audit/seat/roster_edit.py` and `tools/audit/carry_audit.py` in turn, then `python3 tests/closure.py select --diff HEAD`: each prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` with `tests/entities.py` in `scope.run`. Review #1 measured `0 script(s) run` for the same plants before the closure commit.
- Sibling probe: review #1's `sibling_probe.py` (taken from probe/rev-2554-e07a772e `ev/tools/sibling_probe.py`, sha1 `481665aee54f`), run unchanged over this worktree: `caseA_misattributed= 0`, `caseB_done_reopened= 0`, and its null `null_no_sibling_group_still_matches= 1`.
- Commit resolution on the live roster (`origin/handoff/audit-r10-roster` `743463c61f6a`, `roster_sync.invalid_commits('.', roster)` in this full clone; a record is a group with a non-empty `resume.commit`, short is under 40 characters): `records= 64 short= 6 invalid= 0`. Null: the same roster with one planted done group at `0000000deadbeef` reads `invalid= 1`.
- The base harness `dev/audit/harnesses/r10_roster_sync_base.py` keeps its own control at both ends. See `## Figures`.

## Figures

Python is a 3.13 venv built from `tests/requirements-ci.txt` (see `## Friction`).

- `python3 tools/audit/seat/roster_sync.py --self-test` -> `roster_sync self-test: 53 checks, 0 failed`.
- `python3 tools/audit/seat/r10_roster_sync_mutants.py` -> the table above, `restored`.
- `python3 tools/audit/seat/roster_edit.py --self-test` -> `roster_edit self-test: 106 checks, 0 failed`. `python3 tools/audit/seat/state_docs.py --self-test` -> `state_docs self-test: all checks passed`.
- `python3 dev/audit/harnesses/r10_roster_sync_base.py` -> `RESULT base_apply_rc=2 head_apply_rc=0`, `base_stage=in-progress head_stage=done`, `head_noapply_stage=in-progress`, `base_deferred=deferred head_deferred=deferred`, `control=PASS`.
- Gate scope: `python3 tests/closure.py select --diff 46e3681276f9` -> `MODE: FULL` (reason: `tests/closure.py changes the gate itself`). I ran the scripts the diff reaches and left the full run to CI:
  - `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` -> `ALL 2382 ENTITY CHECKS PASSED`, rc 0, 459 s wall.
  - `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` -> `ALL 109 HARNESS HEADER CHECKS PASSED`, rc 0, 197 s wall.
- `run_always` lines:
  - `tests/env_drift.py --claims-only origin/main` -> `claims hygiene: origin/main ok`.
  - `tests/closure.py selftest` -> `ALL 124 closure shrink pins PASSED`.
  - `tests/layout.py` -> `layout self-test: ok`.
- `python3 -I tests/layout.py --guard --base 46e3681276f9` -> `layout: GUARD: 0 refusal(s) against 46e3681276f9`.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> `selftest_wiring: 73 self-testing, 73 wired, 0 unwired`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` -> `tmp_paths: 0 refused`.
- `python3 -I tests/throwaway_git.py --check` -> `throwaway_git: 0 raw git init or clone site(s) refused`.
- `python3 -I tools/policy/agreement_py.py --out ag.json && node tools/policy/agreement.mjs --py-json ag.json` -> `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` -> `CI PREDICT: no closures or fast red predicted against 46e3681276f9`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` -> `PRE-PR: 97280902daf9194d30c3b90b9b95d25626e561ef 000000000000000000000000000`, rc 0; its step 6d prints `the diff adds no unpinned mutation site`.
- `python3 tools/audit/archscore/score.py --diff 46e3681276f9` -> `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` -> `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`, rc 0. Null control, `--roster-ref b96aab8b85f1` (the round-1 head's tree, which has no R10-ORCH-MACHINERY): `CARRY-AUDIT: 6 finding item(s): 1 routed, 0 unrouted, 5 bad destination(s)`, every one `R10-ORCH-MACHINERY is not a group of the roster`.
- The roster carries this body routes, read at `origin/handoff/audit-r10-roster` `743463c61f6a` with `jq` over each group's `carry` for the entries containing `2554` (R10-ORCH-MACHINERY `not-started`, R10-REPLAY-LANE `in-progress`):
  - R10-ORCH-MACHINERY holds 5: item 4ddebe42 (`ci_predict.py does not run the layout guard`), three for item b1ecb708 (`design 6.4 predicate 1, gate coverage`, `design 6.4 predicate 2, absorbed-edge closure`, `R10-ROSTER-OPS carry[4] (from #2545), the brief pinned at handoff`) and one for item 4c5f0868 (`Friction: cloud_dispatch: stale`).
  - R10-REPLAY-LANE holds 1: item 57bf9e90 (`nightly-status` grades `main`).
  - R10-POLICY-GATE-SCOPING holds the `ref_privacy` entry for item 4ddebe42.
  - Null: R10-REPLAY-CAP, the destination this body used to name, holds 0 entries containing `2554`.

## Red checks

- At d82acd2e the only red check-run was `nightly-status`. It grades `main` (the replay `loop_cpu_ratio` budget), not this branch. Carry: R10-REPLAY-LANE (item 57bf9e90)
- Earlier rounds' reds, answered in this diff and not recurring at d82acd2e:
  - `closures` and `closures-autofix`: this diff gave `state_docs.py` (loaded by `entities.py`) an import of `roster_sync`, `roster_edit` and `carry_audit` while all three sat under the INERT `tools/audit/` prefix. They now sit on `tests/closure.py`'s exception list and in `entities.py`'s recorded closure; the gate-hole plants in `## Null control` show the gate selects `entities.py`. The cheaper detector is `tests/closure.py select --diff HEAD` with a one-line plant in each newly imported file, about a second per file; no pre-handoff step runs it. Carry: dismissed: answered in this diff (item 8fac8b5b)
  - `pr-contract` `BAD-DEST`: R10-ORCH-MACHINERY was not a group of the head's tree roster. Answered by merging `origin/main`. The cheaper detector is `carry_audit.py check --body` before `body_push.sh`, under a second. Carry: dismissed: answered by the merge (item c0223ec1)
- `main`'s `ci-ratchet` red is runner-speed variance owned by R10-CI-LAYOUT, per this round's dispatch brief; I did not re-measure it, and this diff touches no ratchet file.

## Forward-carry

- `tools/pr/ci_predict.py`, the predictor behind `body_push.sh`, does not run the layout guard. Its control: a layout-violating fixture must make `ci_predict` predict red. Carry: R10-ORCH-MACHINERY (item 4ddebe42)
- `ref_privacy.py --check` enforces nothing on a macOS seat, because its site scan keys on `\b` through the host's `git grep -E`, which does not honour it. Its control: on a host whose `git grep -E` ignores `\b`, a planted host name must still be refused. Carry: R10-POLICY-GATE-SCOPING (item 4ddebe42)
- Design 6.4 predicate 1, **gate coverage** (`GATE-READY` / `GATE-OWNER <class>`), dispositioned and not built here: it changes the roster's `owner_gate` schema, and its consumer is the tick's owner-gated count; neither reads a pull request. Carry: R10-ORCH-MACHINERY (item b1ecb708)
- Design 6.4 predicate 2, **absorbed-edge closure** (`ABSORB-EDGE-MISSING`), dispositioned and not built here. The fail-safe half already holds: `absorbed` is outside `roster_lib.DONE_STAGES`, so an absorbed group stays open and `roster_sync` protects the stage. The rest changes `DONE_STAGES`, which `pr_cap.py`, `prune_refs.py`, `handover_prompt.py` and the tick all read. Carry: R10-ORCH-MACHINERY (item b1ecb708)
- R10-ROSTER-OPS carry[4] (from #2545), the **brief pinned at handoff**, dispositioned and not built here: the handoff is the dispatcher's event, and no pull-request read observes it. Carry: R10-ORCH-MACHINERY (item b1ecb708)

## Friction

- cloud_dispatch: stale: the payload says "the toolchain (venv python, node, gh) is on PATH". In this seat `python3` was the system 3.11 without `voluptuous`, and `gh auth status` printed `Failed to log in to github.com using token (GH_TOKEN)`. I built a 3.13 venv from `tests/requirements-ci.txt` and read the PR through the GitHub connector. Carry: R10-ORCH-MACHINERY (item 4c5f0868)

## Approval

Behaviour change: `state_docs.py beat` gains `--apply`. On each pass it runs `roster_sync.py`, which writes `resume.stage`, `resume.commit`, `resume.pr` and a destination group's `carry` through `roster_edit.py`'s lint gate, on measured evidence only. It also prints `RECORD-INVALID` lines, which write nothing. Without `--apply` the beat behaves as before, and the one-shot form is a dry run unless `--apply` is given. Rollback: revert this merge. Nothing reads `resume.pr`, and no other behaviour changed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01CSjA4w95bonGtnonS2kAC1
