R10-FLY-RELAY-REVIEW-FF, carries round: the relay, tick loop, bus and carry_audit carries still owed after #2664, with CARRY-DISPOSITION's and RELAY-TOOLS-LEVEL's carries folded in. Part of #201.

**Already on main, not rebuilt.** P15 (`relay_start` passes `--confirm`, `tick_loop-3`), P-O (the confirm arm), and Carry 2's transient retry with `REFUSED <ref> <sha> <reason>`: `cloud_relay.sh` already holds `confirm_arm`, `HPO_RELAY_TRIES` and the `probe-refused` level. `--confirm` replaces the orchestrator's read of the reviewer thread with the relay's nonce, head and dispatch-record checks (decided 2026-10-18).

**Built here, one commit each:**
- `tick_loop.sh` (P14, as Carry 8 reconciles it). Each pass fetches `origin main` and counts `HEAD..origin/main -- tools/audit/seat tools/pr tools/audit/carry_audit.py`.
  - `code=<sha7> behind=<n>` goes on the `TICK-PASS` banner and in the heartbeat message.
  - Past `HPO_TICK_STALE_BOUND` (25), or on any commit touching `tick_loop.sh` or `cloud_relay.sh`, the loop restarts between passes, at most once a pass. It needs the relay lock free and a clean detached tree, and `bash -n` must pass on origin/main's copy. It then checks out origin/main detached and `exec`s it with the same args.
  - Otherwise `TICK-STALE ...: <why>`, the relay and sweep arms are skipped (`relay=stale`), and the board is still written.
  - Never a fast-forward in place, never an exit.
- `cloud_relay.sh`:
  - review_freeze holds only on a dispatch record of the PR at its head, and HELD-REVIEW names `dispatch=<nonce8> at=<utc>` (P288). The detached-worktree arm is removed.
  - `update_pr.sh` runs from `<state>/relay-tools`, a tools tree the relay levels to origin/main when clean. A dirty tree is refused by name and owed; a busy one (a live pid's `relay-tools.lock`) waits (P283).
  - The no-return line `SEAT ENDED NO RETURN <topic>` is `seat-no-return` on the level (P-E, below).
  - The confirm arm skips a relayed review whose PR is not in the pass's open-PR listing, once, owing nothing; a failed listing skips nothing (P332, Carry 18, landed on the roster after the dispatch).
- `bus.sh`:
  - push-verdict refuses before `review/<pr>` moves:
    - a line its post would refuse (`ref_privacy.py body-lines`, naming the line, P76);
    - a finding item with no valid `Carry:` (`carry_audit.py check`, P40/P207).
  - Its push carries `-c http.postBuffer=524288000` (#2563's HTTP 400).
  - dispatch reads a dependabot-only head's row at origin/main (P100), and refuses a body carry its group does not hold, printing the `roster_edit.py append-carry` op (CARRY 0, P310). `watch` holds a single-instance lock (P102).
- `carry_audit.py`:
  - `## Evidence`, and every section of a merge verdict but a findings section, is read by shape: a finding only when it opens with LEAD, sits under a lead, or carries `Carry:` (P308, P314). A findings section is a heading opening with a declared word (CARRY 5), or a block heading.
  - The owner-approval merge condition, with its one bare sentence after it, and a negated deferral ("nothing is deferred") read no NONBLOCK (P329).
  - A lead's bullets end at its section (CARRY 3).
  - `(item <id>, supersedes <old>)` retires a bad token for that item only, printed as a NOTE; one naming a valid destination is refused (P296).
  - `load_dests` reads the round's roster on the explicit-ref path (P319), and unions an extra ref's carry files (P43).
  - `landed` and `land-ops` (CARRY 0, P310): a carry lands when its group's brief or carries hold the item id or the source `#<pr>`/topic, as whole tokens.
  - `NOT_REQUIRED` and `DEFERRED` are deleted; nothing read them after P308.
- `queue_pre_flight.py` reads each PR's destinations with its head as the extra ref, uncached (P43).
- `body_push.sh` runs `landed` at the handoff: rc 1 refuses, rc 3 is said (CARRY 11).
- `cloud_dispatch.py`'s reviewer prompt states the shape reading and caps `ev/` at 25 MB (Carry 2's payload cap).
- `standing-dispatch.md` (policy, code-owned): the relay half retires to a beat job once one cycle's job log agrees with the seat, never inline (card 1, Carry 9). BEATD (#2916) merged first, so this group owns the edit.

**P-E's open point, closed.** No `cloud-sessions.tsv` is written anywhere in the tree: `git grep -n cloud-sessions -- tools` at the merge base prints nothing. The detector therefore keys on the dispatch ref, and reports a `dispatch/fixer-<topic>` tip older than 2 h and younger than 48 h with no `handoff-wip/`, `handoff/`, `handoff-body/<topic>`, `fix/<topic>-pr` or `fix/<topic>` commit newer than it. The session id is not named, since git does not hold it.

**CARRY 2 (from #2545), closed by P319.** pr-contract's `carry_audit.py pr` (no `--roster-ref`), the pre-flight's explicit `origin/main`, push-verdict and dispatch now all read main's roster plus the round's branch, so the rule and the check read the same roster.

## Carries

Numbered as the roster lists them (`Carry N`, 1-based). The folded groups' own `CARRY n` keep their numbering.
- Carry 1 (P15 `--confirm` in `relay_start`): on main before this branch (`tick_loop-3` pins it); not rebuilt.
- Carry 2 (#2563): `http.postBuffer` on the verdict push (`bus-6`), and the `ev/` cap in the reviewer prompt, built. The transient retry and the logged `REFUSED <ref> <sha> <reason>` were on main already.
- Carry 3 (P-B), Carry 6 and Carry 8 (the stale checkout, Carry 8 binding): built in `tick_loop.sh`, `tick_loop-4..11`.
- Carry 4 (P-C): `--confirm` was on main. The self-test row "a posted review is not confirmed again" is the never-twice case, and `tick_loop-3` drops `--confirm`.
- Carry 5 (P-E): built as the git-only no-return line; its open point is closed above.
- Carry 7 (P-O): the confirm arm was on main (#2664); not rebuilt.
- Carry 9 (card 1): the `standing-dispatch.md` edit, under `## Approval`.
- Carry 10 (CARRY-DISPOSITION folded):
  - built: CARRY 0, 7 and 11 (`landed`, `land-ops`, dispatch and handoff), CARRY 3 (lead section), CARRY 4 and 10 (push-verdict's carry check), CARRY 5 (the findings-heading grammar), CARRY 6 (P43), CARRY 8 (body lines), CARRY 9 (P100) and CARRY 12 (supersedes);
  - CARRY 13 and 14: superseded by P308 (Carry 11), as Carry 11 states;
  - CARRY 2: closed by P319 (above);
  - CARRY 1: not built (below).
- Carry 11 (P308), Carry 12 (P310), Carry 13 (P314), Carry 14 (P319), Carry 16 (P329) and Carry 18 (P332): built.
- Carry 15 (RELAY-TOOLS-LEVEL folded): the levelled tools tree (P283) and its CARRY 0, the dispatch-record freeze (P288). Both built.
- Carry 17 (P102): the `watch` lock, built.

## Not built here

CARRY 1 of CARRY-DISPOSITION, the lost-ask fold count (a closing PR answering an issue's (a)-(e) fold list item by item), is not built. It needs a fold grammar no issue declares today and an issue read inside a required check, so a wrong reading would refuse merges. Its brief names no grammar to build against. The orchestrator re-homes it or rules on the grammar; the group stays `carries-open` for it.

## Approval

Owed, not yet given. `dev/governance/roles/standing-dispatch.md` changes what the dispatch/relay seat must do: its relay half retires to a beat job, once one cycle agrees and never inline. That is the owner's card 1 ruling (tvofi, 2026-10-24), carried into the contract as Carry 9 instructs. It merges only on the owner's approving review (the code-owner rule of `main-protect-checks`), or under the mandate the roster names for this group (6319294694) if that mandate covers policy.

## Head

36692240baf8b8b068e5eaec96b78c7ac5584d64. The branch was cut at 7539d1675; origin/main moved to a7dd7f50d during the work and was merged in fa8a7473d (only `tests/closures.json` overlapped, resolved by the ledger merge driver). The self-tests, mutants, predictor and prepr below were re-run after that merge.

## Mutation proof

The seat harness plants each mutant in its file, outside the self-test function, and runs the CI step naming the file. Every new id was killed: `RESULT survivors=0`.
- `tick_loop-4..11`: drop the path filter, the bound test, the lock test, the dirty test or the `bash -n` guard; drop the exec, the relay skip or the once-per-pass guard.
- `cloud_relay-39`: restore the worktree arm. `cloud_relay-40`: drop the HELD evidence. `cloud_relay-41`: run `$HERE/update_pr.sh` again; the row runs a copy of the relay whose `update_pr.sh` refuses STALE, so no route reaches the real script. `cloud_relay-42..44`: no dirty test, no busy test, no levelling. `cloud_relay-45..48`: the no-return age bound, window and moved test, and its wiring into `pass`. `cloud_relay-33` is re-keyed to the new pass line. `cloud_relay-49`: the closed-PR skip removed (P332).
- `bus-4`: carry_gate call removed. `bus-5`: body-lines call removed. `bus-6`: postBuffer dropped. `bus-7`: the all-bot test reduced to non-empty. `bus-8`: the watch lock's live-pid test. `bus-9`: the landing's rc ignored.
- `carry_audit-1` (graded by bus.sh's step): `check` reads the roster with no finding item.
- `queue_pre_flight-1`: `extra_ref=None`.
- `body_push-4` (graded by prepr.sh's step): rc 1 not refused.

The carry parser harness generates one mutant per regex alternative and per site, and reports `RESULT sites=193 unmapped=0 mutants=264 survived=0`. The new written mutants are `P308-restore` (the four field rows and #2441/#2465 fail), `P314-merge-only` (the Summary row and the #2683 rows fail), `P329-*` (the three fixture rows fail), `P296-*`, `C3-*`, `L-*`, `P43-extra` and `P319-ref-path`.

## Null control

Each arm has its unmutated twin as a self-test row:
- tick_loop: behind 0 is silent and does not exec. A commit outside the code paths counts 0. Behind 1 within the bound relays.
- cloud_relay: a detached worktree with no dispatch record updates (the #2953 shape), and the same with a record holds. A dirty tools tree is left untouched. A seat whose `handoff-wip` or PR head moved after dispatch is not reported.
- bus: the routed verdict, the `~/`-written path and a dependabot head with its row on main all pass. A non-bot head reading main is refused.
- carry_audit: the same #2465 sentence under `## Findings` and a Summary `Follow-up:` are findings; the approval sentence followed by a defect stays one. A supersede of a valid destination, or of another item's id, stays bad. `#25581` does not land `#2558`.
- The merge base: `r10_carry_field_figures.py 7539d1675` prints 17/17 field items flagged.

## Figures

- `bash tools/audit/seat/tick_loop.sh --self-test`: 26 checks, 0 failed.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: 316 checks, 0 failed.
- `bash tools/audit/seat/bus.sh --self-test`: 123 checks, 0 failed.
- `python3 tools/audit/carry_audit.py --self-test`: 292 checks, 0 failed.
- `python3 tools/audit/seat/ref_privacy.py --self-test`: 100 checks, 0 failed.
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: 45 checks, 0 failed.
- `python3 tools/audit/seat/cloud_dispatch.py --self-test`: 125 checks, 0 failed.
- `python3 tools/audit/seat/ledger.py --self-test`: 77 checks, 0 failed.
- `bash tools/pr/prepr.sh --self-test`: EXIT 0.
- `bash tools/pr/prepr.sh <this body>` at 36692240b after the merge: every step ok or skip except `pr-body`, which wanted `## Approval`. After that section was added, `bash tools/pr/prepr.sh --body-check <this body>` printed `PR-BODY: 0 error(s)` with rc 0, and origin/main was still a7dd7f50d.
- `python3 dev/audit/harnesses/r10_carry_field_figures.py 7539d1675 HEAD`: `field_flagged=17/17 v2645_flagged=8` at the base, `field_flagged=0/17 v2645_flagged=1` at the head. The rule: each verbatim item in `dev/audit/harnesses/r10_carry_field_verdicts.json`, alone under its own verdict word and heading, and #2645's round-1 VERDICT.md whole, through `items()` at each revision. The one item left on #2645 is `95bcfcd0`, a genuine NONBLOCK word (the carry's residual, declined).
- `python3 dev/audit/harnesses/r10_carry_parser_mutants.py`: `RESULT sites=193 unmapped=0 mutants=264 survived=0`.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py <the ids above>`: `RESULT survivors=0`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: no closures, fast, governance or instrument red predicted, after `--apply-inert` wrote the field-figures harness's `inert_reads` entry.
- `tests/closure.py select` at the merge base: `MODE: SCOPED -- 2 script(s) run`. `tests/doc_claims.py` printed `ALL 255 checks PASSED`; `tests/entities.py` printed `ALL 2493 ENTITY CHECKS PASSED`; at 3d8caf003 it had refused the over-cap standing-dispatch.md through policy_lint's template acceptance, repaired in ccf694234. The `run_always` lines (`env_drift.py --claims-only`, `closure.py selftest`, `layout.py`) are green.

## Red checks

none

## Forward-carry

none

## Friction

- fixer.md: cost: the seat mutant harness edits the committed file in place, and a commit made while it ran captured mutant bus-5; `git status` showed it and the commit was amended back to the unmutated bus.sh before any push. Carry: dismissed: the harness already refuses a dirty file, and a seat that commits during its run is the defect
