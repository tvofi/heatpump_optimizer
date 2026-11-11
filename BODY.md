`tools/audit/seat/cloud_relay.sh` `carry_fold_arm`, R10-REVIEW-DISPATCH-RESIDUE part 1 of 6: **Carry 14** (P556, S14-CARRY-FOLD-WRONG-CHECKOUT) and **Carry 22** (P580, CARRY-FOLD-ARM-REJUDGES-EVERY-PASS), built as one change to the arm. Carry 17 (same arm, the handoff-wip dispose) is part 6's and is not touched; dispose is not widened to `handoff-wip/`.

- **Carry 14.** At the base the body push ran from `git worktree add --detach "$wt" FETCH_HEAD` (base line 838, `git show a7628041dc:tools/audit/seat/cloud_relay.sh | grep -n FETCH_HEAD`). The worktree is now added at a private ref, `+refs/heads/handoff/<topic>:refs/hpo-relay/fold/<topic>`, deleted after the push. Before `body_push.sh` runs, the worktree's HEAD must equal `handoff/<topic>`'s tip from the arm's own `ls-remote`, which now lists `refs/heads/handoff/*` as well as `refs/heads/handoff-wip/*`. Otherwise the arm prints `OWED carry-fold <topic> worktree at <a>, handoff at <b>`, puts that on the level and pushes nothing, so a failing pass logs the fold worktree's head, as reproduce step (1) asks. `HPO_RELAY_BODYPUSH` now replaces only the `body_push.sh` call inside that worktree. At the base it skipped the worktree entirely, so the self-test never exercised the real checkout. A missing handoff is now on the level; at the base it was only printed, with no level line.
- **Carry 22.** A new state file, `cloud-fold-judged`, holds one line per topic: `<topic> <wip sha> <body sha|-> <outcome> <epoch> [<its OWED level line>]`. The outcome is one of `blocked`, `fold-failed`, `push-failed` or `folded`. Both shas come from the `ls-remote` the arm already makes. A memoed pair is neither fetched nor shown (base line 818 fetched every one), and its stored OWED line goes back into `cloud-level-fold.$$`, because `level_set carry-fold` (base line 849) replaces the whole kind. `fold_memo_stands` lets `fold-failed` and `push-failed` expire after 3600 s, because an ancestry red can clear with no ref moving. Success still appends to `cloud-folded` (base line 843). The memo is rebuilt each pass from the topics listed in that pass.

Alternatives not taken. Storing the OWED line in the level file was rejected: the level is per `--log`, so a pass with another log would silently drop an owed item. An env-tunable TTL was rejected: the self-test ages the memo entry instead, so no knob was added. Moving the worktree check ahead of `carry_fold.py` was also rejected. It would change the order the brief prices as "a failure after the fold", and the cost it would save happens only when no handoff exists.

The cause of the observed wrong checkout is still unproven. The private ref removes the FETCH_HEAD candidate. The assertion turns any other cause into an OWED line that names both heads, where at the base the push went through from the wrong head.

## Head

185699076fb42c0082be4e5eaae31ab1abf2c1ad, on merge base a7628041dc02e298c5399003d4c0576391dd5c4e (origin/main's tip when measured, 2026-11-11T07:01:04Z).

## Mutation proof

Seven reviewer-style mutants were re-created as `mutant_run.py --spec` entries, in a `git archive` copy of the handoff head. Each is KILLED, and the automatic NULL mutant SURVIVED. Command: `python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test' --timeout 400` (the spec is quoted at the end of this section). Output, verbatim:

```
SURVIVED NULL
KILLED foldref-fetch-head
KILLED foldtip-assert-off
KILLED foldmemo-drops-line
KILLED foldmemo-no-skip
KILLED foldttl-never-retry
KILLED foldttl-always-retry
KILLED foldtip-wide-lsremote
```

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
- head self-test `433 checks, 0 failed`: `bash tools/audit/seat/cloud_relay.sh --self-test` at the head
- base lines 805 (`carry_fold_arm`), 818 (wip fetch), 838 (`FETCH_HEAD`), 843 (`cloud-folded`), 849 (`level_set carry-fold`): `git show a7628041dc:tools/audit/seat/cloud_relay.sh | grep -n 'carry_fold_arm() {\|FETCH_HEAD\|level_set carry-fold'`
- mutants, 7 KILLED and NULL SURVIVED: `python3 tools/audit/seat/mutant_run.py --spec mutants.json --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test'`
- gate scope `MODE: SCOPED -- 1 script(s) run`, which is `tests/doc_claims.py`: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed `ALL 297 checks PASSED`. All four of `tests/run.sh`'s `run_always` scripts exited 0.
- structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`
- architecture: `python3 tools/audit/archscore/score.py --diff a7628041dc HEAD` printed `Architecture score: dS +0.0000 NULL`

## Red checks

none

## Forward-carry

none

## Friction

none
