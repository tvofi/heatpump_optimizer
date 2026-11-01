R10-FLY-RAISE-REVIEWABLE (S, instrument; triage P345 and its carry P348, batch 95). Every budget raise is red at `budget-raise-gate` until the owner's approval (or a mandated one) names its head, and that approval comes after the verdict. So the reviewer-dispatch readers refused the review that the approval needs (#3045 at 9ef51b82, hand override; #3006's pre-approval reds). This adds `merge_train.approval_owed(train, pr, head, red)` as the single owner of that state, built on `Train.raise_hold` and so on budget_raise_gate's own `raises_between` and `approval`. Every reviewer-dispatch reader now asks it. `classify` itself, the train and the merge state do not change.

- `merge_train.py classify --pr N`: when the head is RED and `approval_owed` returns a reason, it prints `APPROVAL-OWED <sha> <why>` and exits 4. Without `--pr`, the result is the same as before.
- `bus.sh dispatch` passes `--pr "$pr"`, dispatches on rc 4 the same way as on 0 and 3, and prints the line.
- `orchestrator_tick.one_pr` prints `#N: RAISE APPROVAL OWED at <head8>: review it, then approve under the owner or the mandate (0013) -- not its fixer (K15 (d))` in place of NOT REVIEWABLE.
- `review_packet.py render`: when classify `--pr` answers APPROVAL-OWED for a required red, the red becomes the `approval-owed` advisory and is not the `required-red` refusal (that refusal is what made `bus.sh dispatch` die). This reader is the third layer the dispatch measured.
- `cloud_dispatch.py`'s reviewer prompt waits on `classify <head> --pr <pr>` and treats 4 as reviewable. Without that change the reviewer would get a 1 and block.
- Instrument pages updated: merge_train, orchestrator_tick, bus.sh, review_packet.
- `dev/audit/harnesses/r10_fly_raise_reviewable.py` is the real-head control (fixer step 18). It is INERT through `ci_predict.py --apply-inert`.

**One departure from the triage text, and the reason.** P345 says `approval_owed` should get "the red set" in which `classify` "reports `gate` and `budget-raise-gate / budget-raise-gate` red". The `classify` red set is taken over the ruleset's contexts, and the only one is `gate` (`tools/policy/fixtures/required-contexts.json` `contexts`). At #3045, `classify` prints `red: gate` and never names the unit (see Figures F1). If the predicate were fed that set, it would never fire. Every caller therefore passes the red set over `merge_train.gating_names(required)`: the ruleset contexts plus every unit gate.py can owe. That is the same expansion `gating_names` already provides for exactly this purpose. Mutation M5 pins this. The names come from `git diff --no-renames --name-only <merge-base> <head>`: P345's command, with `--no-renames` added because `closure.py selftest`'s RENAME_SITES pin requires it.

**Round 2: P348, in the same function.** `bus.sh dispatch --reviewed-head <rh>` refused to mint whenever `review_carry.py` answered CARRY, but `review_carry` reads only the commit range and never what the review at `rh` decided. A blocked review carried leaves nothing to merge, so the refusal blocked the fresh review the block asked for. #3045 round 3 at 9ef51b82 went out only by dropping `--reviewed-head`, which also drops the check for the case it exists for. `verdict_at <pr> <rh>` now prints the latest verdict word naming `rh` on `verdict/<pr>`. It shares the ref read with `blocked_rounds` through one new reader, `verdict_log`, which took the fetch and log that `blocked_rounds` held, so the ref is read the same way in both places and the read is not copied.
- On CARRY, a `merge` verdict still refuses with the existing message (the ruling's case, tvofi 2026-10-27).
- A `blocked` verdict mints and prints `review-carry: <rh> was blocked, so a fresh review is owed`. No verdict at all mints and prints `review-carry: <rh> has no verdict, so a fresh review is owed`.
- An unreadable `verdict/<pr>` refuses (`cannot read verdict/<pr> to learn what the review at <rh> decided`), as `blocked_rounds`' caller does.
- `dev/governance/roles/orchestrator.md` (the carry sentence beside `--reviewed-head`) now reads "over a range clean against a reviewed head whose verdict was merge", P348's clause. **This is a policy change and waits for the owner's approving review, or the mandate, at merge.** `policy_lint.mjs --budgets` passes with the clause in (F7).
- Instrument pages `bus.sh.md` and `review_carry.py.md` state the condition. `dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh` is the real-ref control, INERT through `ci_predict.py --apply-inert`.

Alternatives considered for P348:
- Teach `review_carry.py` to read verdicts. Rejected: its contract is "THE TEST IS A COMMIT RANGE", and `app_approve.sh --carry` asks it the same question; a verdict read there would answer for callers that already hold a merge verdict.
- A second, independent `verdict/<pr>` reader beside `blocked_rounds`. Rejected: two copies of one ref read can drift. `verdict_log` is the one reader.

## Head

75b873248402113a5472780b5f26ac620d4ac1dc, five commits fast-forward on round 1's handoff c7ccdbf7e5a16dabc37a14bb3d26da635f4c5c63 (`git log --oneline c7ccdbf7e..75b873248`). The merge base with origin/main is 2b6bef7453a8bdaf97d42f382a116ce226b35ccc. At 2026-11-01T00:04:42Z origin/main's tip was 8fec54ee2afb5e37687f34bc5fd3aa7280f64e1f, and `git merge-tree --write-tree origin/main HEAD` reported no conflict (`tests/closures.json` resolved by its ledger merge driver). So the head was not merged forward (fixer.md step 6). `git diff --name-only 2b6bef745 8fec54ee2` names no file this diff measures except `tests/closures.json`. Round 1's figures below were taken at c7ccdbf7e. `git diff --stat c7ccdbf7e HEAD -- tools/audit/seat/merge_train.py tools/audit/seat/orchestrator_tick.py tools/audit/seat/review_packet.py tools/audit/seat/cloud_dispatch.py` is empty, and the self-tests of those four were re-taken at this head (F3). The bus.sh mutants M3 and M4 were re-run here because this round edits that file.

## Mutation proof

P348 (this round), each applied to bus.sh at this head, `bash tools/audit/seat/bus.sh --self-test` run, then restored with `git checkout`:
- M7: the verdict test is dropped (`v=$(verdict_at ...) ||` -> `v=merge; true ||`). `FAIL P348: a blocked verdict at the reviewed head over a clean range mints, says why, and records (#3045 r3)`, `FAIL P348: a reviewed head with no verdict at all carries nothing, so it mints` and `FAIL P348: an unreadable verdict/<pr> over a clean range refuses, and records nothing`.
- M8: the oldest verdict naming `rh` wins (`| head -n 1` -> `| tail -n 1`). Fails `P348: a blocked verdict at the reviewed head ... (#3045 r3)`.
- M9: an unreadable ref is read as no verdict (`|| die ...` -> `|| v=""`). Fails `P348: an unreadable verdict/<pr> ...`. The first cut of that row survived this mutant, because `three_rounds`' later read of the same ref also refused. The row now requires the carry's own refusal text (commit b9509cdc9).
- M10: the sha anchor is dropped (`$2` -> `[0-9a-f]*`). Fails `P348: the latest verdict naming the reviewed head decides -- blocked then merge refuses, a blocked verdict at another head aside (#2962)`.
- M11: no verdict refuses (`"") die`). Fails `P348: a reviewed head with no verdict at all carries nothing, so it mints`.
- Re-run at this head: round 1's M3 (bus.sh's `4)` arm deleted) fails `P345: a raise whose only red is its owed approval (classify --pr APPROVAL-OWED) dispatches, records, and prints the line`. Round 1's M4 (`--pr "$pr"` dropped) fails `a head whose required context concluded failure (classify RED) is not dispatched, and nothing is recorded`.
- Failing test first: with the P348 rows added and c7ccdbf7e's `dispatch` unchanged, `bus.sh --self-test` printed 115 checks, 17 failed. Those were the three P348 rows (blocked mints, none mints, unreadable refuses) plus F3's 14 bash-3.2 orphans rows. The merge-verdict null control passed, as it must, because it is the old behaviour.

P345 (round 1, at c7ccdbf7e; M3 and M4 re-taken above):
Each mutant was applied to the head, the named self-test was run, and the tree was restored.
- M1: approval_owed's test (b) is dropped (`return why if raises and not held else None` -> `return why`). `merge_train.py --self-test`: `FAIL P345 row 3 (null): budget-raise-gate red with no raise in the diff ... stays RED, rc 1` and `FAIL P345 (null): a raise the owner's mandated approval already holds at the head owes nothing`; 388 checks, 2 failed.
- M2: test (a)'s "only gate units" is dropped (`if RAISE_GATE not in red or red - {GATE, RAISE_GATE}` -> `if RAISE_GATE not in red`). `FAIL P345 row 2 (null): the same plus tests / fast (3.14) red stays RED, rc 1`; 388 checks, 1 failed.
- M3: bus.sh's `4)` arm is deleted. `bus.sh --self-test`: `FAIL P345: a raise whose only red is its owed approval (classify --pr APPROVAL-OWED) dispatches, records, and prints the line`; 111 checks, 2 failed.
- M4: bus.sh's `--pr "$pr"` is dropped. `FAIL a head whose required context concluded failure (classify RED) is not dispatched, and nothing is recorded` (the argv pin); 111 checks, 1 failed.
- M5: the tick's owed call is set to `owed = None`, and separately its red set is changed from `gating_names(req)` to `req`. `orchestrator_tick.py --self-test`, both mutants: `FAIL P345 PRS #3045 shape: RAISE APPROVAL OWED present, naming the raise` and `... NOT REVIEWABLE absent`; 241 checks, 2 failed.
- M6: review_packet's `if owed:` -> `if False:`. `review_packet.py --self-test`: `FAIL P345: a required red that is only a raise's owed approval renders`; 53 checks, 1 failed. `approval_owed_line`'s `r.returncode == 4 and` is dropped: `FAIL P345: the reason is classify --pr's own APPROVAL-OWED line at rc 4`; 53 checks, 1 failed.
- Survivor, equivalent: in `return why if raises and not held else None`, dropping only `raises and` survives. On each of its three no-raise returns, `raise_hold` returns `held=True` (`no budget file changed`, the `#2401` `raises_between: 0` path, both `[], True, ...`), so `not held` already implies a raise. The conjunct is kept because it states P345's test (b) in its own words.

## Null control

P348 (this round):
- Self-test, the ruling's own case: a merge verdict at `rh` over a clean range still refuses (CARRY), records nothing and closes no `reviewer-fire` (`null control (P348): ...`). A merge verdict newer than a blocked one at the same head refuses too, with a blocked verdict at another head pushed on top (`P348: the latest verdict naming the reviewed head decides ...`).
- Real refs, through `dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh` (F6), which drives `dispatch` against the live `verdict/<pr>` on origin, with scratch state and only the classifier and packet renderer stubbed:
  - Control #3045, `rh` = head = 9ef51b82 (the latest verdict naming it is `blocked`): at c7ccdbf7e `REFUSED rc=1 review_carry: CARRY`; at this head `review-carry: 9ef51b8215dd7216950f177386fb2f5a8f010a47 was blocked, so a fresh review is owed`, `MINTS rc=0`.
  - Null #2962, `rh` = head = 9ce0179f (blocked three times, then the latest is `merge`): `REFUSED rc=1 review_carry: CARRY` at both ends.

P345 (round 1, at c7ccdbf7e):
- Real heads, through `dev/audit/harnesses/r10_fly_raise_reviewable.py`. Its only change to the classifier is a transport shim: a `gh api --paginate --slurp P` call is read as one page, because this cloud seat's proxy refuses `--paginate`'s numeric-id follow-up links. Without the shim, `raise_hold` Stops here and `approval_owed` fails closed (RED rc 1), which is the designed answer.
  - #3045 at 9ef51b82: at the base (f3c9144 checkout, no `--pr` there) `RED ... red: gate` rc=1. At the head with `--pr 3045`: `APPROVAL-OWED 9ef51b82... 1 budget raise(s), first tests/ci_budgets.json: critical_path_minutes_band: None -> 1.3 (a pinned value the gate cannot sign as routine): a raise is the owner's (0013): tvofi's approval is on b02ffd170d50, not this head 9ef51b8215dd ...` rc=4.
  - Null #3055 at 6a988a23: `RED ... red: gate` rc=1 at both ends.
  - The merge state is unchanged: at the head, without `--pr`, #3045 still reads `RED ... red: gate` rc=1 (F1).
- Self-test rows, each against its null: P345 rows 1-5 in `merge_train.py --self-test`, plus a held raise (an owner's mandated approval at the head) staying RED, and a red gate without the raise unit staying RED. In bus.sh, RED/GREEN/WAIT/unreadable are unchanged, and APPROVAL-OWED dispatches. In the tick, the #3045 shape prints RAISE APPROVAL OWED, while `tests / fast (3.14)` red too, or no raise in the diff, still prints NOT REVIEWABLE. In review_packet, the advisory replaces the refusal only at rc 4 with the head's own line.

## Figures

Round 2, at 75b873248:
- F3 (re-taken): `python3 tools/audit/seat/merge_train.py --self-test` (388 checks, 0 failed); `python3 tools/audit/seat/orchestrator_tick.py --self-test` (241, 0 failed); `python3 -I tools/audit/seat/review_packet.py --self-test` (53, 0 failed); `python3 tools/audit/seat/cloud_dispatch.py --self-test` (124, 0 failed); `python3 -I tools/audit/seat/review_carry.py --self-test` (26, 0 failed). `bash tools/audit/seat/bus.sh --self-test`: 115 checks, 14 failed on this seat's macOS `/bin/bash` 3.2, against 111 checks and 14 failed at c7ccdbf7e. The 14 are the same named orphans rows at both ends, each failing on `arms[@]: unbound variable` (bash 3.2 under `set -u` with an empty array, in `orphans`' `ledger.py landed "${arms[@]}"` call). The four added checks are P348's rows, and all pass. CI's Linux bash is the authority for the 115.
- F4 (scope, re-taken): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, naming `tests/doc_claims.py` and `tests/entities.py`. With `PYTHONPATH=tests/hastub` at this head: `ALL 255 checks PASSED` (doc_claims); `claims hygiene: 2b6bef7453a8... ok`; `ALL 117 closure shrink pins PASSED`; `layout self-test: ok`; `STRUCTURE RATCHET PASSED`; `ALL 112 HARNESS HEADER CHECKS PASSED`. On this macOS seat, `tests/entities.py` exits 1 with 44 FAIL lines. That set is byte-identical to the set at c7ccdbf7e (`diff` of the sorted FAIL names, run at both ends), and the run ends in `PermissionError: Cannot get task port` at both ends. One more row, the gate-lease row, failed once at this head and passed on the re-run (the gate slots are contended). CI is the authority for entities.
- F5 (the class's seams for P348). The rule is `git grep -nE "review_carry(\.py)?|--carry\b" -- 'tools/**/*.py' 'tools/**/*.sh'` (self-test lines excluded). The verdict-carry deciders it returns, each with its disposition:
  - `bus.sh dispatch --reviewed-head`: the only caller of `review_carry.py`; closed here.
  - `tools/pr/app_approve.sh --carry`, and its callers `merge_train.py` step 3, `queue_pre_flight.py`, `ledger.py` REVIEW OWED and `orchestrator_tick._carries`: already guarded. Each takes a verdict, and app_approve accepts only `Fix review: merge <sha>` (its `vline` test), so a blocked verdict never carries there.
  - The rest are prose or self-test fixtures (`cloud_relay.sh`'s `carry-missing` verdict subjects, `cloud_dispatch.py`'s roster-carry docstring).
- F6 (the real-ref control): `bash dev/audit/harnesses/r10_fly_raise_reviewable_carry.sh <checkout> <pr> <rh>`, with `<checkout>` a c7ccdbf7e worktree and this head. #3045 9ef51b82: REFUSED -> MINTS. #2962 9ce0179f: REFUSED -> REFUSED.
- F7 (policy budget): `node tools/policy/policy_lint.mjs --budgets` rc 0; orchestrator.md's row reads 294 lines (cap 295) and ~4245 tokens (cap 4251), after the clause. `node tools/policy/policy_lint.mjs` rc 0; `node tools/policy/rules_sync.mjs --check` prints `RULES-SYNC ok`.
- F8 (architecture): `python3 tools/audit/archscore/score.py --diff 2b6bef7453a8 HEAD` (three-dot base) prints `Architecture score: dS +0.0000 NULL`, and so does `--diff c7ccdbf7e HEAD` (round 2 alone). archscore reads none of the shell instruments changed here, so no improvement is claimed. The `verdict_log` extraction is argued on its own (one reader of the ref) and not on the score.

Round 1, at c7ccdbf7e (F3 and F4 superseded by round 2's re-take above):
- F1 (the departure's evidence): `python3 tools/audit/seat/merge_train.py classify 9ef51b8215dd7216950f177386fb2f5a8f010a47 --repo tvofi/heatpump_optimizer` at f3c9144 prints `RED 9ef51b82... pending: none red: gate`, rc 1. The gating red set (`classify(latest_runs(runs), gating_names(required))[2]`, read live) is `['budget-raise-gate / budget-raise-gate', 'gate']`.
- F2 (the real-head control above): `python3 dev/audit/harnesses/r10_fly_raise_reviewable.py <checkout> classify <sha> --repo tvofi/heatpump_optimizer [--pr N]`, with <checkout> a merge-base worktree and the head. #3045: rc 1 -> 4. #3055: rc 1 -> 1.
- F3 (self-tests at the head): `python3 tools/audit/seat/merge_train.py --self-test` (388 checks, 0 failed); `bash tools/audit/seat/bus.sh --self-test` (111, 0 failed); `python3 tools/audit/seat/orchestrator_tick.py --self-test` (241, 0 failed); `python3 -I tools/audit/seat/review_packet.py --self-test` (53, 0 failed); `python3 tools/audit/seat/cloud_dispatch.py --self-test` (124, 0 failed).
- F4 (scope): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run`, naming `tests/doc_claims.py` and `tests/entities.py`. Both were run with `PYTHONPATH=tests/hastub`, together with the `run_always` lines (`env_drift.py --claims-only`, `closure.py selftest`, `layout.py`) and `tests/structure.py`, at the head: `ALL 2493 ENTITY CHECKS PASSED`, `ALL 255 checks PASSED`, `claims hygiene: f3c9144b8088... ok`, `ALL 117 closure shrink pins PASSED`, `layout self-test: ok`, `STRUCTURE RATCHET PASSED`. The first closure run refused `no rename-detecting --name-only diff under RENAME_SITES` at approval_owed's diff and the two stubs; the diff is `--no-renames` now, because a rename-detecting `--name-only` would name a renamed budget file by its new path alone.
- F5 (the class's seams). The rule is `git grep -nE "classify\(|merge_train.py\"?\}? classify|merge_train.py classify|& set\(REQUIRED\)|req_red|req_bad" -- 'tools/audit/seat/*.py' 'tools/audit/seat/*.sh'` (self-test lines excluded). The gate-conclusion readers it returns, each with its disposition:
  - `bus.sh` dispatch's classify: closed here.
  - `cloud_dispatch.py` reviewer wait: closed here.
  - `review_packet.py` required-red (`& set(REQUIRED)`): closed here.
  - `orchestrator_tick.one_pr` `req_red`: closed here.
  - `orchestrator_tick` main-tip `req_bad`: main's tip, not a review, left alone.
  - `merge_train` `wait_ci` / `main_green` `classify(` and `proof_watch.required_state`: the merge judgement, deliberately unchanged (P345: "the merge state, the train and main stay as they are").
  - The other `classify(` hits are homonyms that read no check run: `ledger.py`, `prune_refs.py`, `row_position.py`, `run_twins.py`, `tmp_paths.py`, and `review_carry.py`. The dispatch named "the review-carry check" as a layer, but `review_carry.classify(repo, reviewed, new, main)` reads only the commit range and never the gate, so it holds no seam.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Awaiting approval at the head. This diff changes policy (`dev/governance/roles/orchestrator.md`, the carry sentence beside `--reviewed-head`), so it merges only on an approving review at its head: the owner's, or the orchestrator's under mandate 6329234399 (scope all). The change narrows when the carry refusal applies, to a reviewed head whose verdict was merge, as triage P348 rules. A blocked review is no longer "the error" to re-dispatch. No other obligation moves, and no budget is raised (F7).
