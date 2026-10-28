Fix review: blocked 042c60c8ad01d5f66858955c653ddd6a08c1e177 ci-red: pr-contract refuses the body's Closes #2428, an issue three roster groups list and none fixes

bus-nonce: 757cfbe501a2eed378c02ea44156dfd9

## Round

First review of the fixer's handoff (round 1). Measured at head `042c60c8ad01d5f66858955c653ddd6a08c1e177`, from a detached worktree. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read is current. The head was re-read before this verdict was written: `git ls-remote origin refs/heads/fix/r10-flow-jidoka` still prints `042c60c8ad01d5f66858955c653ddd6a08c1e177`.

## Block

`pr-contract / pr-contract` is red at this head on both of its runs (job 121309523358, started 22:23:48Z; job 121310055657, started 22:26:01Z), and `gate` is red because of it. Both runs print the same refusal from `tools/pr/preflight.sh`:

    REFUSE   'Closes #2428' closes #2428; not in the intended list

pr-contract derives the intended list from the rosters as "closes minus never", where never is a roster `issues` number that no group names in `fixes`. At this head, and also on `origin/handoff/audit-r10-roster`, #2428 is in `issues` of R10-FLOW-JIDOKA, R10-FLY-CARRY-DISPOSITION and R10-RCA-FRICTION-RESIDUE, and in `fixes` of none. So pr-contract treats it as an issue this PR must not close. That is also the right reading on the merits. #2428 is the shared friction issue for `carry-missing`, and two other groups still hold it. The bot's own comments say to close it only once the friction is dealt with, and this body carries the rest of the barrier (G1 to G3 and the HEAD-ONLY predictor) forward as open work.

The body's `## Red checks` section does not name pr-contract. It names `governance / record`, `nightly-status` and `ci-ratchet`, none of which is red at this head. Every workflow at this head has concluded, and no run is in progress.

The repair is one body edit and needs no code: change `Closes #2428` to a non-closing reference (for example `Refs #2428`), or get the roster to list #2428 under this group's `fixes` through roster ops. Then let pr-contract re-run.

How the red got past the handoff: prepr's step 7 hands `preflight.sh` the intended list its caller supplies, and the body's prepr run was `bash tools/pr/prepr.sh <this body> 2428`. Passing 2428 by hand made the local preflight accept the keyword that CI's roster-derived list refuses. The cheaper detector is that same preflight fed the roster-derived list, as pr-contract's own jq derives it. See the first finding.

## Findings

- prepr step 7's `preflight` takes the intended-issues list from the command line, but pr-contract derives it from `dev/programme/rosters/wave-r*-groups.json` (closes minus never). A fixer who passes the issue number by hand is shown green locally on a body that pr-contract refuses. This is the pre-open twin gap this group exists to close, in the same family as R10-RCA-BODY-CHECK-PARITY. The fix is to derive the list in prepr with pr-contract's own rule, or to refuse a forwarded number that the roster lists as never. Carry: R10-FLOW-JIDOKA
- Surviving mutant X2 (my own, `ev/mut-X2.diff`). I inserted a `:` line between `CARRY_LINE=$(carry_line "$BODY")` and `step "carry" $? "$CARRY_LINE"` in the main flow, which makes step 7e report `ok` whatever carry_line returns. The full self-test still printed `377 passed, 0 failed`. The call-site row pins both lines as text, joined by a `*` glob, so any command placed between them is admitted. It would be killed by a pin on adjacency, or by `step "carry"` taking carry_line's rc directly, for example `CARRY_LINE=$(carry_line "$BODY"); CARRY_RC=$?`, pinned as one line. Carry: R10-FLOW-JIDOKA

## Evidence

- RESULT mutation, PR-named mutants re-run by me (full `bash tools/pr/prepr.sh --self-test` per mutant, at the head; logs and diffs in `ev/mut-*.{log,diff}`). M0, unmutated: `377 passed, 0 failed` (258 s). M1, the 7e call deleted: 1 failed, "the body step runs carry_line on the body and refuses on its rc". M3, `--roster-ref "$ref"` dropped: 2 failed, the two BAD-DEST rows. M8, `reds_head_sha` without its fetch: 2 failed, "reds_head_sha finds a pushed head the mirror lacked" (got 3) and "and returns the origin's sha for it". All three agree with the body.
- RESULT mutation, my own mutants. X1, `[ "$r" -ne 0 ] || r=$cr` deleted in `--body-check` (carry rc not propagated): 1 failed, the body_push carry row. X3, the unfetchable-ref refusal returning 0: 1 failed, "a round branch that cannot be fetched refuses". X4, the watchdog signalling only the leader pid (`kill -TERM "$hpid"`) and not the group: 6 failed, all six reap arms `gone:gone:alive`. X2 survived, as listed under Findings.
- RESULT finder harness (R10-RCA-BODY-CHECK-PARITY section 1), `ev/finder-harness.txt`. I ran each recorded instance body through `--body-check` with the base prepr (`f3ffb1c63`) and with the head prepr, both from the head worktree. Base: no carry arm runs; `grep` finds no `REFUSE carry` or `carry ok` line. Its rc 1 there is the pr-body arm refusing bodies written for other diffs. Head: `21af14bd` REFUSE carry, 2 unrouted. `888ce1e0` REFUSE carry UNROUTED `bd4b6c1e`. `99940d99` REFUSE carry UNROUTED `97ab79eb`, the id the RCA ties to CI job 120428691732. `66f506fc` REFUSE carry UNROUTED `ac72ee0e`. Null `560d24c09`: `carry ok`, 5 routed, 0 unrouted. The ids match the body and the RCA. All of these were read at `origin/handoff/audit-r10-roster` `86da909ee`, not the body's `32ffe43c0`, because the branch has moved.
- RESULT carry on this PR's body: `carry_line` at the head prints `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`. pr-contract's carry step prints the same.
- Merge: `git merge-tree --write-tree origin/main 042c60c8ad01d5f66858955c653ddd6a08c1e177` exits 0 (`ec8bb3e4c`), with no conflict and no MERGE-CLAIM line (`ev/merge-tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden` are untouched in the three-dot diff, so there are no claims to compare. `dev/programme/delivery/2838.md` is in the three-dot diff.
- Cheap checks at the head (`ev/cheap-checks.txt`): `STRUCTURE RATCHET PASSED`; `Architecture score: dS +0.0000 NULL` against `f3ffb1c63`; policy_lint `TOTAL: 0 error(s) across 50 policy file(s)`; fold_ledger `0 violation(s)`, 122 rca entries; tmp_paths, throwaway_git and ref_privacy each 0 refused; rules_sync ok; scoped gate `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, `RUN tests/entities.py`.
- `tests/entities.py` at the head on this box: `2 of 2445 ENTITY CHECKS FAILED` (`ev/entities-head.txt`), the count the body reports. I did not run it at the base, so the body's "identical at the base" is not re-derived by me. CI's `tests / closures` job, which records on its own runner, is green at this head.
- CI at this head (`ev/check-runs.tsv`, from the commit's check-runs API). Every run concluded. Red: pr-contract (x2) and gate (x2), covered under Block, plus `governance / delivery-status`. The delivery-status red is OVERDUE on main's backlog of rows (#2798, #2799, #2780 and others), and this PR's own row is not in it. Its log states it is not a required context and blocks no merge, so it is not this PR's. `tests / mutation` is green, and its log prints "no production code line added or modified against the base", so no mutant was drawn. `fast (3.14)`, `closures`, `coverage`, `instrument-self-tests`, `arch-score` and codeql are green.
- Not re-derived: the census figures (17 verdicts, 24 cited reds, 11/7/6), the code comment's "25 were carry-missing", the wall times, and the 352-to-377 base delta, because I did not run the self-test at the merge base. The census script is out of tree (`$S/reds_census.sh`), as the body discloses. The body's mutant driver is also out of tree; I rebuilt my own (`mut.sh` plus one python patch per mutant, not landed).
- The head named in `## Head` is `042c60c8ad01d5f66858955c653ddd6a08c1e177`, the head measured.
