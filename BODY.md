R10-ORCH-ROSTER-SCHEMA, the #2733 remainder alone, as carry 31 (triage `dev/programme/triage/s6-batch71.md#P305`) asks: "Dispatch the remainder alone, ahead of this group's other carries." Part of #2733 and #2505; it closes neither, because the tick's default-pass issue line (carry 10 (c)) and this group's other carries are not built here (`## Forward-carry`).

**One predicate, three readers.** `roster_lib.pending_carries(group, legacy)` says which carries a group still owes: a carry is discharged by a mark at its end — `[implemented: <sha>]`, `[moved: <GROUP>]` or `[dismissed: <reason>]` (`roster_lib.carry_mark`) — or is legacy, meaning a closed group held it at the cut-over. `closing_stage(group, stage, legacy)` turns `done` over a pending carry into `carries-open`; `stranded(roster, legacy)` lists every pending carry on a group in `CARRY_CLOSED` (`DONE_STAGES` plus `absorbed`). The readers:

- **`roster_edit.py set-stage <G> done`** (and `set-resume --field stage done`) writes `carries-open` and prints `set-stage <G>: done -> carries-open (<n> pending carries); wires #a #b`, rc 0. Carry 31 rules out a refusal and a `--force-done` flag, so neither is added. The printed line names the issues the group wires, which stay wired. It does not say whether they are open: the writer makes no `gh` call (carry 17's rule).
- **`roster_sync.py`'s merge transition** applies the same `closing_stage`. The pass still reads the body's `Carry:` items, because the transition is a merge either way. A sync over the live roster changes nothing at the cut-over, since every carry a done group holds there is legacy.
- **`carry_audit.py roster [--open-issues FILE]`**, offline, prints `STRANDED <group> (<stage> | absorbed into <G>) carry[i]: ...`. With an issue list it also prints `ISSUE-STRANDED #n listed only by closed group(s): ...` and `ISSUE-UNLISTED #n`, and it never reports #201. Without a list the issue arm says nothing (`issues not measured`): an issue that was not read is not reported as routed. Summary line: `CARRY-ROSTER:`.

**`mark-carry <group> <index | --match TEXT> implemented <sha> | moved <GROUP> | dismissed <reason>`** selects the carry the way `drop-carry` does, through `_carry_index`, which both ops now share. It refuses a carry that is already marked, an unknown mark, `implemented` with no sha, `moved` to a group that does not exist, to the group itself or to a closed group, `dismissed` with no reason, and a value that contains `]`. `implemented` records that the sha is on main; it does not verify it (carry 10 (a)).

**The cut-over is a constant, not a migration.** `roster_lib.CARRY_CUTOVER` maps `dev/programme/rosters/wave-r10-groups.json` to roster commit `a4c9fa3d629017fb1a0e5394bbae79cdbdfa4f9b`, the roster branch tip when this branch was cut. A roster with no entry has no legacy carries, and a cut-over the clone cannot read is refused rather than read as "no legacy". Alternatives considered: (a) a `carry_cutover` field in the roster. That puts a code fact in data this seat may not write, and readers would need the field before the orchestrator sets it. (b) A tracked digest snapshot of the 498 legacy texts: a second copy of the roster's history, plus a new file to classify. (c) Marking every existing carry. That is the blanket migration carry 10 rules out. The constant needs one object every roster reader already fetches, and changing it is a one-line diff.

**brief_lint warns on an issueless live group** (invariant 2, carry 10 (c)): `a live group lists no issue in `issues` or `fixes` (#2733 invariant 2)`. It is a warning, so neither the `--push` lint gate nor a fly-in registration is blocked. It applies only to a group of the orchestrator's schema (one carrying `issues` or `fixes`), and "live" is the linter's existing rule (stage other than `done`), so no second stage list lives in JavaScript. `assertIssuelessWarning` drives the warning both ways in memory.

**Carry 24 / 27 are void at this roster, by their own re-measure clause.** #2855 is not in the open-issue list (closed), and #2429, #2436 and #2437 are also listed by `R10-FRICTION-REGRESSION` (carries-open), #2438 by `R10-FLOW-TOOLKIT-MODEL` (not-started). Carry 26's #2875 is now listed by `R10-FRICTION-REGRESSION`. The mechanism these carries ask for is still built (ISSUE-STRANDED/UNLISTED), and its controls run on fixtures.

## Head

`6aea809f6592` (6aea809f659243ced76f343d37bd152cf7cce12e). The commits: `ac09e1479`, the red tests; `173595a01`, the code; `2ea6ca6d9`, the plants plus set-resume's row; `8f16eed55`, the `C8` re-plant; `5fe2e7fdf`, the sync harness's M3 re-anchor; `6aea809f6`, L6 read from roster_lib's own line (the agreement lane refused a second spelling of the mark grammar; `python3 -I tools/audit/seat/r10_roster_ops_mutants.py L6` still prints `rc=1 fails=1`). Merge base `7539d1675d7f` = `origin/main` at 2026-10-31T16:20Z, unmoved since the cut, so no merge and no second prepr run were needed.

## Approval

The roster's `owner_gate` for this group reads "Policy: tvofi approves at merge (design section 8 rows vii and viii, DONE_STAGES and the roster schema); mandate 6329234399 applies." This diff does not change `DONE_STAGES`. It adds `CARRY_CLOSED` beside it and a carry-mark grammar to the roster schema, and it edits no file `CLAUDE.md` names as policy. Whether the mark grammar is covered by row viii is the orchestrator's call under the mandate; it is raised here and not decided here.

## Mutation proof

`python3 -I tools/audit/seat/r10_roster_ops_mutants.py`. Each plant is one exact single-occurrence replacement. The driver runs the planted file's own `--self-test` and restores it byte for byte, and it refuses to start on a dirty target. It now takes a plant's target file (`parts()`), so one driver covers all four Python files.

- **New plants (21), each `rc=1` with a named FAIL:** K1 2, K2 2, K3 6, K4 5, K5 4, K6 2, K7 2 (set-stage bypasses the shared predicate, which is carry 31's mutant), K8 2 (cut-over not read), K9 1 (set-resume bypass), L1 5, L2 4, L3 1, L4 1, L5 1, L6 1 (roster_lib), Y1 1 (roster_sync's merge bypass), R1 1, R2 1, R3 1, R4 1, R5 1 (carry_audit's roster arm).
- **Existing plants, after the re-anchor.** C1 and C4–C8 and P2 are re-anchored on the shared `_carry_index`. All are killed by a named FAIL except `C6`, which is killed by a crash (`KeyError: 'carry'`), as #2880's body already disclosed for it. `C8` crashed at first because the shared selector reads `g["carry"]` on its detached dict. It is re-planted to detach without crashing and now fails by name (`python3 -I tools/audit/seat/r10_roster_ops_mutants.py C8 C6`: `without a FAIL line: ['C6']`). Full sweep: `plants: 52`, all `rc=1`.
- **`r10_roster_sync_mutants.py`**: `M3` is re-anchored on `Change(gid, closed, ...)`, the one anchor this diff moved (every other anchor occurs once, measured by loading its `PLANTS` and counting each anchor in `roster_sync.py`). `python3 -I tools/audit/seat/r10_roster_sync_mutants.py`: 23 of 24 plants rc=1 with named FAILs and `restored`; `--null` prints `NULL_no_plant rc=0 fails=0`. `M9_carry_dedupe_dropped` survives (rc=0 fails=0), and it survives identically at `origin/main` `7539d1675` (the same command run there), because `already_carried` refuses the duplicate the dropped exact test used to catch. That predates this diff; it is in `## Forward-carry`.
- **brief_lint**, by hand, because no in-tree driver mutates the `.mjs` and the arm is in-memory: the warning's condition replaced by `false` prints `ISSUELESS VACUOUS: warned [] errors 0` with rc 1; the stage test dropped prints `warned [bare,closed]`. Both restored with `git checkout`.

## Null control

- **Each refusal and each downgrade has its null in the same run:** an open group's carry is not stranded; a group whose carries are all marked, or legacy, is written `done` by both set-stage and the merge; set-stage of a stage other than `done` is unchanged; a `moved` mark onto an open group lands; an issue a live group lists (in `issues` or in `fixes`) and #201 are not reported; a group of another schema and a group with an issue get no warning.
- **The cut-over is the live null.** `carry_audit.py --roster-ref origin/handoff/audit-r10-roster roster` reads `cut-over a4c9fa3d6290 (498 legacy carries); 0 stranded`. 498 is also the number of carries the 206 done groups hold at that roster (a `python3 -c` over the roster summing `len(carry)` per `resume.stage`). Had the legacy set been read wrong, the same run would print a STRANDED line per done-group carry.
- **The unmodified self-tests at this head:** `roster_lib.py --self-test` 60 checks 0 failed; `roster_edit.py` 145/0; `roster_sync.py` 78/0; `carry_audit.py` 214/0; `r10_roster_ops_mutants.py --self-test` 162/0; `node tools/policy/brief_lint.mjs` `TOTAL: 0 error(s) across 48 file(s)` with `ISSUELESS ok`..

## Figures

All at the head above. Roster read: `origin/handoff/audit-r10-roster` `a4c9fa3d6`. Open issues: the GitHub issue list (state open), 54 issues, read 2026-10-31T15:43Z.

- **Red first** at `ac09e1479`: each of `roster_lib.py`, `roster_edit.py`, `roster_sync.py` and `carry_audit.py --self-test` stops on the missing symbol (`NameError: legacy_carries`, `AttributeError: CARRY_CUTOVER`, `TypeError: derive() takes 2 positional arguments`, `NameError: roster_report`), and `node tools/policy/brief_lint.mjs` prints `ISSUELESS VACUOUS`.
- **Carry 23's control, perturbed.** `roster_report` (the `roster` arm's function) is run over that roster and the open-issue list, then over a copy with `R10-ORCH-ROSTER-SCHEMA`'s stage set to `done`. The perturbed run adds 33 STRANDED lines, one per carry this group holds, every one post-cut-over because the group was `carries-open` at the cut-over. It also adds `ISSUE-STRANDED #2733 listed only by closed group(s): R10-ORCH-ROSTER-SCHEMA, R10-ROUTING-INVARIANTS`. The carry's own figure, 24, is stale (the carry list has grown to 33). Null control: the same perturbation on `R10-RCA-FRICTION-RESIDUE`, already `done` with legacy carries, adds 0 lines.
- **The issue arm at that roster, unperturbed** (rule: every open issue but #201 that no group outside `CARRY_CLOSED` lists): 7 ISSUE-STRANDED (#2248, #2249, #2257, #2492, #2674, #2731, #2942) and 1 ISSUE-UNLISTED (#2998), with 0 STRANDED carries. These are findings for the routing audit to dispose (`## Forward-carry`). The perturbation above is this arm's own null: it moves only the perturbed group's lines.
- **brief_lint over the round-10 roster**: `node tools/policy/brief_lint.mjs <roster>` prints `TOTAL: 0 error(s)` plus one `issues` warning per live group with empty `issues` and `fixes`. The warnings never reach the TOTAL.
- **Mutation**: as `## Mutation proof`.
- **`GATE_SCOPE=auto bash tests/run.sh`**: `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (`tests/closure.py select` names `tests/entities.py`), then `ALL 2493 ENTITY CHECKS PASSED`, `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`, `gate rc=0`. It ran at `2ea6ca6d9`'s tree; the three later commits touch only the two mutant drivers.
- **`python3 tests/structure.py`**: `STRUCTURE RATCHET PASSED`; no budget file touched.
- **`python3 -I tools/audit/archscore/score.py --diff <merge-base> HEAD`**: `Architecture score: dS +0.0000 NULL`.
- **`bash tools/pr/prepr.sh <body>`** at this head: every step `ok` or `skip` except `carry`. That step refused 5 bad destinations because the roster moved this group to `done` during the run (`## Forward-carry`, first item). The carries were re-routed to live owners, and `bash tools/pr/prepr.sh --body-check <body>` then prints `PR-BODY: 0 error(s)`, `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)` and `FIGURES: 7 resolved, 0 not verified, 0 refused`. `origin/main` was still `7539d1675` at 2026-10-31T17:20Z.

## Red checks

none

## Carries

Numbered as the review packet counts them, `Carry N` = the brief's `Carry N-1`.

- Carry 1: design 6.4 predicate 1, gate coverage: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 2: absorbed-edge closure: not built here; it stays on this group's carry list (`## Forward-carry`, #2505). `CARRY_CLOSED` is added beside `DONE_STAGES`, which is unchanged.
- Carry 3: brief pinned at handoff: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 4: stage refused outside the classified set: built by #2880 (`roster_edit._stage_why`).
- Carry 5: the §3 (d) pointer to carry 3 (brief index 2): not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 6: lettered proposal labels in the triage gate: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 7: `cannot lock ref` fetch retry: already on main (`roster_edit.py` `LOCK_RACE_RE`, `fetch_origin`); owed `mark-carry … implemented`.
- Carry 8: 64 briefs naming `handoff_push.sh`: not built here; it stays on this group's carry list (`## Forward-carry`, #2505) (roster data, not code).
- Carry 9: fail-closed survivors M4–M6 of the ops harness: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 10: set-stage leaving a stale note: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 11: #2733 routing invariants: built here, (a) `mark-carry` plus the offline `carry_audit.py roster`, (b) the shared closing rule, (c) the brief_lint warning; except (c)'s tick line (`## Forward-carry`, R10-ORCH-LEDGER) and (d)'s governance.yml scoping, not wired here.
- Carry 12: `bus-nonce:`/`Round:` trailers in carry_audit: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 13: routing audit 1's table as the null control: not re-run, because its scratch files are not in the tree; the cut-over null (`## Null control`) stands in for its NO-OBLIGATION rows.
- Carry 14: measured instances of the three invariants: the instrument is built (`## Figures`, the issue arm's first reading); the tick's default pass is not.
- Carry 15: `absorbed` terminal in DONE_STAGES and replan: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 16: queue-line trailing comment: not built here; it stays on this group's carry list (`## Forward-carry`, #2505) (carry 30, brief index 29, amends it).
- Carry 17: carry_audit's destination check refusing `absorbed`: not built here; it stays on this group's carry list (`## Forward-carry`, #2505); `roster_lib.CARRY_CLOSED` is the one stage set it can read.
- Carry 18: append-carry refusing a closing group: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 19: `roster_lib.blocks` for carries-open dependents: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 20: `set-size` and `set-files`: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 21: `set-resume --field pr`: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 22: `gate_kind` classifier: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 23: the delivery-row name: recorded by #2880's Friction.
- Carry 24: the #2733 remainder: built here, items (1)–(4); (2)'s `Carry: #N` arm is the issue arm (ISSUE-STRANDED/UNLISTED). Control re-measured (`## Figures`): 33 STRANDED for this group set done, not 24.
- Carry 25: #2855 and #2429/#2436/#2437/#2438: void at this roster by the carry's own re-measure clause (`## Figures` intro); the mechanism is built.
- Carry 26: source/hotfix/savings fields: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 27: #2875 unowned: now listed by live `R10-FRICTION-REGRESSION`; the ISSUE-UNLISTED check is built.
- Carry 28: #2855's key: as carry 25 (brief index 24).
- Carry 29: lint-gate refusal line: already on main (`LINT GATE REFUSED` in `write_roster`); owed `mark-carry … implemented`.
- Carry 30: `parse_line` comment stripping: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 31: `roster_queue.py run --mark`: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).
- Carry 32: set-stage done -> carries-open through the shared predicate: built here (`_closing`, mutant K7).
- Carry 33: append-group overlap refusal and phase-branch `group_for_branch`: not built here; it stays on this group's carry list (`## Forward-carry`, #2505).

## Forward-carry

- **This group's own stage is wrong on the roster, and the carries below cannot route to it.** At `origin/handoff/audit-r10-roster` `14bf5664c`, `R10-ORCH-ROSTER-SCHEMA` reads `done`. The orchestrator's re-dispatch set it to `in-progress` at `a396c2a83` (16:43:49 +0100). Ten minutes later `roster_sync` (`52aea59b1`) closed it to `done`, because the reused branch name `handoff/r10-roster-schema` still answers for #2880's merged pull request. With this diff, that same pass writes `carries-open` (33 pending carries, none legacy), which makes it a first live instance of the rule. Two things remain after this merges. First, the stage needs one `set-stage R10-ORCH-ROSTER-SCHEMA carries-open`. Second, a group re-dispatched on a branch name whose earlier pull request merged is still matched to that merge; the matching rule (design 6.4, B13) needs a dispatch-time `resume.commit` or a fresh topic. Carry: #2505
- This group's carries not built here: 0–2, 5, 7–9, 11, 14–21, 25, 29, 30 and 32. Carries 6 and 28 are already on main (`roster_edit.py`'s `LOCK_RACE_RE` retry and the `LINT GATE REFUSED` line) and need `mark-carry … implemented`. 3 and 22 were built or recorded by #2880. 10, 12, 13, 23, 26, 27 and 31 are this pull request, except 10 (c)'s tick line. They stay on this group's carry list once its stage is repaired. Carry: #2505
- Carry 10 (c)'s invariant-3 tick line in the default pass belongs in `orchestrator_tick.py`, which `R10-ORCH-LEDGER` holds. `carry_audit.py roster --open-issues FILE` is the offline instrument it can call. Carry: R10-ORCH-LEDGER
- `r10_roster_sync_mutants.py`'s `M9_carry_dedupe_dropped` survives at `origin/main` `7539d1675` and at this head: `already_carried` subsumes the exact-text dedupe the plant drops, so either the plant needs a fixture the fuzzy match misses or the exact test is dead code. Carry: #2505
- The issue arm's first reading (7 ISSUE-STRANDED, 1 ISSUE-UNLISTED at roster `a4c9fa3d6`) is owed a disposition per issue: close it, or list it under a live group. Carry: R10-ORCH-LEDGER

## Friction

- fixer.md: cost: the brief carries 33 items for one group of "at most five findings" (`fixer.md` preamble). Carry 31 alone said which subset to dispatch, and this pull request follows it. Carry: #2505
