`tools/audit/seat/cloud_relay.sh` `carry_fold_arm`, R10-REVIEW-DISPATCH-RESIDUE part 1 of 6: **Carry 14** (P556, S14-CARRY-FOLD-WRONG-CHECKOUT) and **Carry 22** (P580, CARRY-FOLD-ARM-REJUDGES-EVERY-PASS), built as one change to the arm. Carry 17 (same arm, the handoff-wip dispose) is part 6's and is not touched; dispose is not widened to `handoff-wip/`.

- **Carry 14.** At the base the body push ran from `git worktree add --detach "$wt" FETCH_HEAD` (base line 838, `git show a7628041dc:tools/audit/seat/cloud_relay.sh | grep -n FETCH_HEAD`). The worktree is now added at a private ref, `+refs/heads/handoff/<topic>:refs/hpo-relay/fold/<topic>`, deleted after the push. Before `body_push.sh` runs, the worktree's HEAD must equal `handoff/<topic>`'s tip from the arm's own `ls-remote`, which now lists `refs/heads/handoff/*` as well as `refs/heads/handoff-wip/*`. Otherwise the arm prints `OWED carry-fold <topic> worktree at <a>, handoff at <b>`, puts that on the level and pushes nothing, so a failing pass logs the fold worktree's head, as reproduce step (1) asks. `HPO_RELAY_BODYPUSH` now replaces only the `body_push.sh` call inside that worktree. At the base it skipped the worktree entirely, so the self-test never exercised the real checkout. A missing handoff is now on the level; at the base it was only printed, with no level line.
- **Carry 22.** A new state file, `cloud-fold-judged`, holds one line per topic: `<topic> <wip sha> <body sha|-> <outcome> <epoch> [<its OWED level line>]`. The outcome is one of `blocked`, `fold-failed`, `push-failed` or `folded`. Both shas come from the `ls-remote` the arm already makes. A memoed pair is neither fetched nor shown (base line 818 fetched every one), and its stored OWED line goes back into `cloud-level-fold.$$`, because `level_set carry-fold` (base line 849) replaces the whole kind. `fold_memo_stands` lets `fold-failed` and `push-failed` expire after 3600 s, because an ancestry red can clear with no ref moving. Success still appends to `cloud-folded` (base line 843). The memo is rebuilt each pass from the topics listed in that pass.

Alternatives not taken. Storing the OWED line in the level file was rejected: the level is per `--log`, so a pass with another log would silently drop an owed item. An env-tunable TTL was rejected: the self-test ages the memo entry instead, so no knob was added. Moving the worktree check ahead of `carry_fold.py` was also rejected. It would change the order the brief prices as "a failure after the fold", and the cost it would save happens only when no handoff exists.

Carry numbers in this body are 0-based roster indexes, as the part-1 dispatch gives them: "This part: Carries 14, 22 (0-based roster indexes)". The rest of the group's roster carries are other parts' and are not touched here. `review_packet.py handoff` counts carries 1-based over the live roster, so the `Carry <N>: not built in this part; stays open on the roster for a later part` lines are added at the end of this body from what `body_push.sh` prints. The counting defect is already held on the roster as BRIEF-CARRIES-PART-SCOPE (Carry: dismissed: already carried as R10-REVIEW-DISPATCH-RESIDUE carry[25] on handoff/audit-r10-roster).

- Carry 1: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 2: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 3: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 4: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 5: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 6: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 7: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 8: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 9: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 10: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 11: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 12: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 13: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 15: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 16: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 18: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 19: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 20: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 21: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 23: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 24: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 26: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE
- Carry 27: not built in this part; stays open on the roster for a later part. Carry: R10-REVIEW-DISPATCH-RESIDUE

The cause of the observed wrong checkout is still unproven. The private ref removes the FETCH_HEAD candidate. The assertion turns any other cause into an OWED line that names both heads, where at the base the push went through from the wrong head.

## Head

30277114cd6436232f653a800045abd79859f474, on merge base f24d107bd7aa170bea7419251a4b7f4f48b732f6 (origin/main's tip when measured, 2026-11-11T09:34Z).

## Round 2

Round 1 was blocked `mutation-vacuous` at 185699076f on four survivors. Two get an arm in the self-test (`carry_fold_arm` is unchanged):

- `rv-real-bodypush-outside-wt`: one arm unsets `HPO_RELAY_BODYPUSH` and sets `HERE` to a directory holding a stand-in `body_push.sh`, so the production `(cd "$wt" && bash "$HERE/body_push.sh" ...)` line runs. It asserts the stand-in ran on the kept body, at `handoff/cf-i`'s tip and never at main's.
- `rv-nohandoff-not-on-level`: one arm makes a CARRY-LANDED topic `cf-h` with no `handoff/cf-h` ref. It asserts the `OWED carry-fold cf-h ... no handoff/cf-h` line, its line on the level, no `cloud-folded` entry, no `FOLDED` announce and no `body_push.sh` run.
- Triaged survivors, no test owed: `rv-folded-memo-no-entry` is equivalent, because the `cloud-folded` grep that follows also skips with no fetch; `rv-privref-not-deleted` is cleanup only, because the fetch refspec is forced (`+`), so a stale private ref cannot become the next worktree's head.

## Mutation proof

The reviewer's 15-entry spec (`ev/mutants.json` on `probe/revt-r10-review-dispatch-residue-p1-dd078352`) was run, one mutant at a time with `bash tools/audit/seat/cloud_relay.sh --self-test` as the command, against the head. Result: the seven named mutants below, the reviewer's `rv-memo-key-ignores-body`, `rv-blocked-never-stands`, `rv-memo-not-saved`, `rv-stub-outside-wt` and the two new targets `rv-real-bodypush-outside-wt` and `rv-nohandoff-not-on-level` are KILLED; `rv-folded-memo-no-entry` and `rv-privref-not-deleted` SURVIVE (triaged above); NULL SURVIVED. The seven named mutants (spec quoted below):

Spec (name: old -> new, all in `tools/audit/seat/cloud_relay.sh`):

- `foldref-fetch-head`: the worktree is added at `FETCH_HEAD` instead of `refs/hpo-relay/fold/$topic`. Carry 14's mutant on the private ref.
- `foldtip-assert-off`: `[ "$head" != "$htip" ]` becomes `false`. Carry 14's mutant on the assertion.
- `foldmemo-drops-line`: a memo hit re-sets `""` instead of `"$ml"`. Carry 22's null control: a memo that drops the line must fail the check.
- `foldmemo-no-skip`: `if [ -n "$mo" ] && ...` becomes `if false && ...`.
- `foldttl-never-retry` and `foldttl-always-retry`: `-lt 3600` becomes `-lt 99999999` and `-lt 0`.
- `foldtip-wide-lsremote`: the `ls-remote` lists `refs/heads/handoff-wip/*` alone.

Failing test first: with the new self-test arms on the unfixed arm, `bash tools/audit/seat/cloud_relay.sh --self-test` printed `cloud_relay self-test: 433 checks, 9 failed`. The nine FAIL names include `a fold with a concurrent fetch of main before its worktree add still pushes from handoff/cf-e's tip (carry 14)`, `a fold worktree that lands off the handoff tip is OWED with both heads (carry 14)`, `an unchanged nothing-folded ref is not fetched again (carry 22)` and `... and not retried before its memo entry is an hour old`.

## Null control

- The unmodified tree's self-test: `bash tools/audit/seat/cloud_relay.sh --self-test` at a7628041dc printed `cloud_relay self-test: 416 checks, 0 failed`. At the head it printed `433 checks, 0 failed`.
- Carry 14's null control is the self-test check `null control (carry 14): a sequential fold pushes the body from a worktree at handoff/cf-a's tip`, with no planted fetch.
- Carry 22's null controls are the self-test checks `null control: a moved wip ref is judged again` and `... as is a moved body ref`. Each shows that the fetch logger which reads "not fetched" for an unchanged ref does record a fetch when the ref moved. A memo that drops the stored line is the `foldmemo-drops-line` mutant, KILLED above.
- The planted concurrent fetch is a `git` shell function in the self-test that runs `git fetch -q origin main` immediately before the arm's `git worktree add`. The cost figures (27-33 s, about 181 s a pass) are the triage's, from the live relay. This seat has no relay state, so they are not re-measured here. The self-test pins the mechanism, which is that a memoed pair is not fetched.

## Figures

- base self-test `cloud_relay self-test: 416 checks, 0 failed`: `bash tools/audit/seat/cloud_relay.sh --self-test` at a7628041dc
- red self-test `433 checks, 9 failed`: `bash tools/audit/seat/cloud_relay.sh --self-test` with the new arms on the unfixed arm
- head self-test `441 checks, 0 failed`: `bash tools/audit/seat/cloud_relay.sh --self-test`
- base lines 805 (`carry_fold_arm`), 818 (wip fetch), 838 (`FETCH_HEAD`), 843 (`cloud-folded`), 849 (`level_set carry-fold`): `git show a7628041dc:tools/audit/seat/cloud_relay.sh | grep -n 'carry_fold_arm() {\|FETCH_HEAD\|level_set carry-fold'`
- mutants, 13 KILLED, 2 triaged survivors and NULL SURVIVED: `python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test'`
- gate scope `MODE: SCOPED -- 1 script(s) run`, which is `tests/doc_claims.py`: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed `ALL 297 checks PASSED`. All four of `tests/run.sh`'s `run_always` scripts exited 0.
- structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`
- architecture: `python3 tools/audit/archscore/score.py --diff a7628041dc HEAD` printed `Architecture score: dS +0.0000 NULL`

## Red checks

none

## Forward-carry

none

## Friction

none
