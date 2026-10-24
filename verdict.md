Fix review: merge 583219fa8a44c79e038ae091ce907dafa3e847d0

bus-nonce: 7c3743ba165cbfbf61fab7740ccd4751

Third review of #2689. The earlier verdicts were merge at 44ee0e5f, blocked at 80a62d9a7 (figure-unverified) and merge at this head. This is the second repair round, so no re-cut is owed. I reviewed head `583219fa8a44c79e038ae091ce907dafa3e847d0` in a detached worktree. The merge base is origin/main `50af6174f`. I used the current contract: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty. The diff adds `dev/programme/triage/s6-batch2.md` (P45-P52) and `dev/programme/delivery/2689.md`, and it changes no code, check, budget, claim file, closure or version.

## Findings

- After the merge, append the shared standing-seat carry for P45, P46 and P51 (the text is under "One destination" in s6-batch2.md) to R10-ORCH-BEATD. Use `roster_edit.py append-carry` and cite `#P45`, `#P46` and `#P51`. `roster_edit` reads the ruling only from origin/main or the roster branch, so this op cannot land before the merge. Carry: R10-ORCH-BEATD
- After the merge, append P49's record-chain carry (measure first) to R10-FLOW-RECORD-PITCH, citing `#P49`. Carry: R10-FLOW-RECORD-PITCH
- The title in `dev/programme/delivery/2689.md` still reads "(P45-P51)", but the file and the PR title cover P45-P52. Carry: dismissed: `delivery-status` is green, and the record row is rewritten at merge
- P52's stated command `TZ=UTC git log -1 --format=%cI` prints the committer's +02:00 offset, not UTC. Every UTC time it quotes still re-derives correctly with `--date=iso-strict-local --format=%cd`. Carry: dismissed: the wording of a derivation command; no figure is wrong
- P52 routes the `bugclasses.json` row to the RCA seat's own pull request as an orchestrator ask. Carry: dismissed: no roster group owns R10-RCA-CI-RATCHET-RUN-NAME, and the ruling names the route

## Evidence

- RESULT merge: `git merge-tree --write-tree origin/main(e8a08cf9e) 583219fa8a44c79e038ae091ce907dafa3e847d0` exits 0 with tree 48fe6c63f. There is no conflict and no claim file is involved. `VERSION`, the manifest, `RELEASE_NOTES.md` and the golden fixtures are untouched in the three-dot diff.
- RESULT mutation (step 1): the diff has no production line, so I ran the step on the consumer. `roster_edit.ruling_verdict` at the head returns P45, P46, P49 and P51 ACCEPT; P47 and P48 DEFER; P50 and P52 REJECT; and P53 None. `triage_refusal` passes #P45, #P46, #P49 and #P51 and refuses #P47, #P50 and #P53. Mutant: deleting P45's `Verdict:` line makes #P45 refused as unreadable. The body's null control reproduces, with P53 as the absent pid. I built this harness from the body's description; there is no committed one.
- RESULT figures, re-derived at 50af6174f:
  - Verdict counts are 4 ACCEPT, 2 DEFER and 2 REJECT, over 8 entries.
  - P49: 14 of the 48 first-parent merges since 2026-10-23T00:00Z are record/autofix. The chain #2676-#2686 each add only their own `delivery/<N>.md`, and 2685.md names #2681 and #2684.
  - P52: all five commit times match in UTC.
  - `N-postreview-merge-red` matches as the file now states it: kind instrument, total 0, 15 non_round_instances, barrier null, and `class_rca_on_record` true with the other three trigger fields false.
  - Citations match: `sweep_template.md:61` names `train.sh` (last edited in b16084794), `orchestrator.md:109`, `pulse.py` STANDING at line 91 with no file-liveness arm, `roster_sync.py` `chosen` at line 239 and `DERIVABLE_STAGES` (no `carries-open`), `replan.py` `touches_coordinator` at about line 205, and `standing-tick.md:8` as the only wait/background line.
  - Roster at origin/main: R10-ORCH-BEATD, R10-FLOW-RECORD-PITCH, R10-ORCH-ROSTER-SCHEMA, R10-FLOW-TOOLKIT-MODEL and R10-FLY-PRUNE-REFS are not-started, and R10-FLY-INERT-LOAD-TIME is in-progress. On the roster branch (76fdb35fa), R10-FLY-RELAY-REVIEW-FF is carries-open. R10-FLY-STANDING-SEATS is absent, which matches the file: it names that group only as a possible split.
  - I did not re-derive the out-of-tree session logs (the r10s5/r10s6 ledgers and reports) or P50's token figures; neither is in the tree.
- The previous block is settled. The body's null control now names P53. The P52 times are UTC. The class trigger is stated with `class_rca_on_record` true.
- RESULT red-check trigger: `ref_privacy.py --check` at the head prints 0 refused out of 284 added lines. The body answers the red `instrument-self-tests` at 44ee0e5f by naming the bypassed cheaper detector (`handoff_push.sh`'s guard, 0.5 s).
- RESULT CI at this head (check-runs API, `ev/ci.txt`): all 65 runs have completed, 44 success and 21 skipped, none red. The `gate` runs 120841072885, 120841202397 and 120841210260 are success. `pr-contract` is success, its latest run being 120840986826. The mutation lane is green but drew no mutant, because the diff writes no code line.
- Classification: both files fall under the INERT prefix `dev/programme/` (`tests/closure.py` line 273). I could not run `tests/entities.py` locally because `homeassistant` is missing, so I cite CI's green `gate`.
- Step 6 (class): this PR is a ruling record, not a fix of a seam, so there is no enumeration rule and its class is the one record. Step 12: `git ls-remote` still shows the head at 583219fa8a44c79e038ae091ce907dafa3e847d0 when this verdict was written.
