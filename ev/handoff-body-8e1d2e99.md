`tools/audit/seat/cloud_relay.sh` `carry_fold_arm`, R10-REVIEW-DISPATCH-RESIDUE part 1 of 6: **Carry 14** (P556, S14-CARRY-FOLD-WRONG-CHECKOUT) and **Carry 22** (P580, CARRY-FOLD-ARM-REJUDGES-EVERY-PASS), built as one change to the arm. Carry 17 (same arm, the handoff-wip dispose) is part 6's and is not touched; dispose is not widened to `handoff-wip/`.

- **Carry 14.** At the base the body push ran from `git worktree add --detach "$wt" FETCH_HEAD` (base line 838, `git show a7628041dc:tools/audit/seat/cloud_relay.sh | grep -n FETCH_HEAD`). The worktree is now added at a private ref, `+refs/heads/handoff/<topic>:refs/hpo-relay/fold/<topic>`, deleted after the push. Before `body_push.sh` runs, the worktree's HEAD must equal `handoff/<topic>`'s tip from the arm's own `ls-remote`, which now lists `refs/heads/handoff/*` as well as `refs/heads/handoff-wip/*`. Otherwise the arm prints `OWED carry-fold <topic> worktree at <a>, handoff at <b>`, puts that on the level and pushes nothing, so a failing pass logs the fold worktree's head, as reproduce step (1) asks. `HPO_RELAY_BODYPUSH` now replaces only the `body_push.sh` call inside that worktree. At the base it skipped the worktree entirely, so the self-test never exercised the real checkout. A missing handoff is now on the level; at the base it was only printed, with no level line.
- **Carry 22.** A new state file, `cloud-fold-judged`, holds one line per topic: `<topic> <wip sha> <body sha|-> <outcome> <epoch> [<its OWED level line>]`. The outcome is one of `blocked`, `fold-failed`, `push-failed` or `folded`. Both shas come from the `ls-remote` the arm already makes. A memoed pair is neither fetched nor shown (base line 818 fetched every one), and its stored OWED line goes back into `cloud-level-fold.$$`, because `level_set carry-fold` (base line 849) replaces the whole kind. `fold_memo_stands` lets `fold-failed` and `push-failed` expire after 3600 s, because an ancestry red can clear with no ref moving. Success still appends to `cloud-folded` (base line 843). The memo is rebuilt each pass from the topics listed in that pass.

Alternatives not taken. Storing the OWED line in the level file was rejected: the level is per `--log`, so a pass with another log would silently drop an owed item. An env-tunable TTL was rejected: the self-test ages the memo entry instead, so no knob was added. Moving the worktree check ahead of `carry_fold.py` was also rejected. It would change the order the brief prices as "a failure after the fold", and the cost it would save happens only when no handoff exists.

Carry numbers in this body are 0-based roster indexes, as the part-1 dispatch gives them: "This part: Carries 14, 22 (0-based roster indexes)". The rest of the group's roster carries are other parts' and are not touched here. `review_packet.py handoff` counts carries 1-based over the live roster, so the `Carry <N>: not built in this part; stays open on the roster for a later part` lines are added at the end of this body from what `body_push.sh` prints. The counting defect is already held on the roster as BRIEF-CARRIES-PART-SCOPE (Carry: dismissed: already carried as R10-REVIEW-DISPATCH-RESIDUE carry[25] on handoff/audit-r10-roster).

- Carry 1: left for a later part; it stays on the roster.
- Carry 2: left for a later part; it stays on the roster.
- Carry 3: left for a later part; it stays on the roster.
- Carry 4: left for a later part; it stays on the roster.
- Carry 5: left for a later part; it stays on the roster.
- Carry 6: left for a later part; it stays on the roster.
- Carry 7: left for a later part; it stays on the roster.
- Carry 8: left for a later part; it stays on the roster.
- Carry 9: left for a later part; it stays on the roster.
- Carry 10: left for a later part; it stays on the roster.
- Carry 11: left for a later part; it stays on the roster.
- Carry 12: left for a later part; it stays on the roster.
- Carry 13: left for a later part; it stays on the roster.
- Carry 15: left for a later part; it stays on the roster.
- Carry 16: left for a later part; it stays on the roster.
- Carry 18: left for a later part; it stays on the roster.
- Carry 19: left for a later part; it stays on the roster.
- Carry 20: left for a later part; it stays on the roster.
- Carry 21: left for a later part; it stays on the roster.
- Carry 23: left for a later part; it stays on the roster.
- Carry 24: left for a later part; it stays on the roster.
- Carry 26: left for a later part; it stays on the roster.
- Carry 27: left for a later part; it stays on the roster.
- Carry 28: left for a later part; it stays on the roster.

The cause of the observed wrong checkout is still unproven. The private ref removes the FETCH_HEAD candidate. The assertion turns any other cause into an OWED line that names both heads, where at the base the push went through from the wrong head.

## Head

bb3933b18fc35aea81c755dceb5e59eb07d3224d, on merge base f24d107bd7aa170bea7419251a4b7f4f48b732f6; origin/main's tip when measured was ee64358be7eeccaec5178a923cb3b83a18a924a0 (2026-11-11T12:17Z), and `git merge-tree --write-tree origin/main HEAD` reported no conflict, so main was not merged.

## Round 3

Round 2 was blocked `mutation-vacuous` at c562b07972 on two survivors. Both are now closed in `carry_fold_arm` and its self-test; round 2's triage of them is withdrawn.

- `rv-privref-not-deleted` is now KILLED. The body-push stand-in records `git for-each-ref refs/hpo-relay/fold/` from inside the fold worktree. Two checks follow cf-a's fold. The null control asserts `refs/hpo-relay/fold/cf-a` stood while the push ran. The second asserts `git for-each-ref refs/hpo-relay/fold/` prints nothing after the pass.
- `rv-folded-memo-no-entry` no longer has a site, because the reviewer's first cure was taken: the memo write on the `cloud-folded` skip is deleted. That write was redundant. Each pass rebuilds the memo, and the `cloud-folded` grep skips the (topic, body) with no fetch whether or not a memo line exists. The skip is now `[ -f cloud-folded ] && grep -qxF ... && continue`. The arm's comment says a (topic, body) that `cloud-folded` holds is skipped unmemoed, and that the private ref is deleted after the push.
- Rewriting that line exposed a third survivor, `r3-folded-skip-off`: replacing `&& continue` with `&& true` survived the round-2 suite. The skip is the only guard when a folded topic's wip ref moves and its body does not, because the memo is keyed on the wip sha. The self-test now moves `handoff-wip/cf-a` after its fold and asserts that `carry_fold.py` ran once for cf-a. That mutant is KILLED.

The alternative to deleting the memo write was a check that the `cloud-fold-judged` line survives a pass. It lost because nothing reads that line for an already-folded topic: the check would pin a write with no consumer.

## Mutation proof

Command: `python3 tools/audit/seat/mutant_run.py --spec <spec> --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test' --copy-tree`. The round-2 reviewer's spec (`evidence/mutants.json` on `verdict/3448`) was used without `rv-folded-memo-no-entry`, whose `old` text is gone, and with this round's `r3-folded-skip-off` added (`grep -qxF "$topic $bsha" "$state/cloud-folded" && continue` becomes `... && true`).

- At d6a35eb044, the first round-3 commit, all 15 mutants ran. NULL SURVIVED. KILLED: foldref-fetch-head, foldtip-assert-off, foldmemo-drops-line, foldmemo-no-skip, foldttl-never-retry, foldttl-always-retry, foldtip-wide-lsremote, rv-memo-key-ignores-body, rv-blocked-never-stands, rv-memo-not-saved, rv-stub-outside-wt, rv-real-bodypush-outside-wt, rv-privref-not-deleted and rv-nohandoff-not-on-level. SURVIVED: r3-folded-skip-off.
- At bb3933b18f, `rv-privref-not-deleted` and `r3-folded-skip-off` were re-run: both KILLED, NULL SURVIVED.

Failing test first: the head's self-test with merge base f24d107bd7's `carry_fold_arm` spliced in printed `cloud_relay self-test: 443 checks, 15 failed` at d6a35eb044. That is round 2's 14 plus the new null control `the push ran while the private fold ref refs/hpo-relay/fold/cf-a stood`, which fails because the base arm has no private ref.

## Null control

- The unmodified tree's self-test: `bash tools/audit/seat/cloud_relay.sh --self-test` at a7628041dc printed `cloud_relay self-test: 416 checks, 0 failed`. At the head it printed `444 checks, 0 failed`.
- The ref-deletion check has its own null control, `null control: the push ran while the private fold ref refs/hpo-relay/fold/cf-a stood`. Without it, an empty `for-each-ref` could also mean the ref was never made.
- The no-refold check's null controls are the existing `null control: a moved wip ref is judged again` and `... as is a moved body ref`. A moved ref is fetched and judged, so a fold count of 1 for cf-a comes from the `cloud-folded` skip, not from a moved ref going unseen.
- Carry 14's null control is the self-test check `null control (carry 14): a sequential fold pushes the body from a worktree at handoff/cf-a's tip`. Carry 22's are the two moved-ref checks above, plus the `foldmemo-drops-line` mutant, KILLED.
- The cost figures (27-33 s, about 181 s a pass) are the triage's, from the live relay. This seat has no relay state, so they are not re-measured. The self-test pins the mechanism, which is that a memoed pair is not fetched.

## Figures

- base self-test `416 checks, 0 failed`: `bash tools/audit/seat/cloud_relay.sh --self-test` at a7628041dc
- red self-test `443 checks, 15 failed`: the same command on the head (d6a35eb044) tree with f24d107bd7's `carry_fold_arm` spliced over the head's
- head self-test `444 checks, 0 failed`: `bash tools/audit/seat/cloud_relay.sh --self-test` at bb3933b18f
- mutants, round-3 spec, 14 KILLED, 1 SURVIVED (`r3-folded-skip-off`), NULL SURVIVED at d6a35eb044, then `rv-privref-not-deleted` and `r3-folded-skip-off` KILLED, NULL SURVIVED at bb3933b18f: the `mutant_run.py` command above
- base lines 805 (`carry_fold_arm`), 818 (wip fetch), 838 (`FETCH_HEAD`), 843 (`cloud-folded`), 849 (`level_set carry-fold`): `git show a7628041dc:tools/audit/seat/cloud_relay.sh | grep -n 'carry_fold_arm() {\|FETCH_HEAD\|level_set carry-fold'`
- gate scope `MODE: SCOPED -- 1 script(s) run`, which is `tests/doc_claims.py`: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`. `PYTHONPATH=tests/hastub python3 tests/doc_claims.py` printed `ALL 315 checks PASSED`.
- pre-PR: `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh <body>`, under the owner's standing ruling for an interpreter with no `homeassistant` module (`python3 -c "import homeassistant"` raises `ModuleNotFoundError` here). Without the skip, the closures step refused `tests/harness_headers.py` as UNDER-SCOPED, left to CI. `./tests/derive_closures.sh --single tests/harness_headers.py` at bb3933b18f, run in a scratch worktree, left `tests/closures.json` unchanged (`git status --short` printed nothing). `ci_predict` predicted no closures red.
- structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`
- architecture: `python3 tools/audit/archscore/score.py --diff f24d107bd7 HEAD` printed `Architecture score: dS +0.0000 NULL`

## Red checks

none

## Forward-carry

none

## Friction

none
