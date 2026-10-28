Fix review: blocked 82a6ef4a1004d1c20fb0411bc4bee461a2015006 conflict: dev/audit/config/bugclasses.json conflicts with origin/main b6f6ceca4 (both sides append an _rca entry at the same place; ledgermerge refused), not a claim file

bus-nonce: 882044c3fbae91084e7391f03db3f027

## Scope

This is round 4 of fix review for #2896 (R10-RCA-FRICTION-RESIDUE), and the body presents it as a re-cut (`fixer.md`, past three rounds). I measured at head `82a6ef4a1004d1c20fb0411bc4bee461a2015006`, whose code head is `2ee7cdc38`. The merge base is `beb570c817c4efcae0d5f6f4bba52f3383baf8db`. Origin/main was `beb570c81` when I started and `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa` at 20:24Z, 12 commits on. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty at both, so the contract read is current. I re-read the branch tip with `git ls-remote` before writing, and it is still the head I measured.

`review_packet.py render` refused `host-path: home-directory in the body` and wrote no packet (`ev/packet_refusal.txt`). So I read the body, the check runs and the tree directly. I did not work around the refusal.

The three-dot diff touches five files: the record, its two evidence files, one `bugclasses.json` `_rca` entry, and the orchestrator's delivery row. It touches no production line, claim file, `VERSION`, manifest version or notes heading.

## Block

- **conflict: `dev/audit/config/bugclasses.json`.** Origin/main moved after the head was cut. `80cf79c2c` (R10-RCA-CLOSURE-ARGV, via `3d8fb943b`) appends `_rca."R10-RCA-CLOSURE-ARGV"` at the same place this PR appends `_rca."R10-RCA-FRICTION-RESIDUE"`, right after `R10-N-vocabulary-drift`. `git merge-tree --write-tree origin/main 82a6ef4a1` exits 1 with `CONFLICT (content)` on that file. Its stderr reads `LEDGER-MERGE: refused dev/audit/config/bugclasses.json: a side is not in its writer's own JSON format` (`ev/merge_new_main.txt`). A plain `git merge-file` of the three blobs also conflicts, so the driver is not the only cause. This path is not one of the two claim files, so rule 13 makes it a block.
- The resolution is mechanical. The driver refuses only because base, main and head all lack a trailing newline: `ledger_merge._format` compares against `json.dumps(...) + "\n"`. With a newline appended to each side, the same driver prints `LEDGER-MERGE: resolved` (rc=0), and the merged `_rca` keeps both `R10-RCA-FRICTION-RESIDUE` and `R10-RCA-CLOSURE-ARGV` (`ev/bugclasses_conflict.txt`).
- Repair: merge origin/main into the PR head, keep both `_rca` entries, and write the file with its trailing newline.
- Nothing else I measured blocks. Once the merge brings in nothing else, the record and its evidence files need no change.

## Findings

- Instrument: `dev/audit/config/bugclasses.json` has no trailing newline at the merge base or at origin/main `b6f6ceca4`. `tools/merge/ledger_merge.py`'s `_format` accepts only the writer's form with a newline, so `merge=ledgermerge` refuses every concurrent edit of this ledger instead of merging it key by key. That is what turned this two-append race into a hand conflict. The fix is to restore the newline in the tree, or to have `_format` accept the form without one, with a self-test row. Carry: dismissed: no live roster group owns tools/merge/ledger_merge.py or bugclasses.json at handoff/audit-r10-roster; the orchestrator routes it
- Non-blocking, carried from round 3 and still open: the `rounds.py` friction row routes `Carry: R10-ROUND-PLAYBOOK`, but that group's carry list at `handoff/audit-r10-roster` `be898eaef` still holds no text about `rounds.py --stats` not being a mode. This is the record's own section-3 case 3, and the merge-time fold or an `append-carry` must land it. Carry: R10-ROUND-PLAYBOOK
- Non-blocking: R10-ORCH-ROSTER-SCHEMA carry[24] still names "carry-2733.json's two items (#2875, #2855's key), added by #2896 (origin/handoff/r10-rca-friction-residue 581079f20)" as the first instances for the STRANDED report. That file is deleted at the head, as the body notes. #2855's item is now carry[25], with its control. #2875's own control (listed by no group, null #2860) is readable only at `581079f20`, not in the live brief. The orchestrator should re-point carry[24] at #2875 and #2855 directly. Carry: R10-ORCH-ROSTER-SCHEMA
- Instrument, non-blocking (rounds 1 to 3 reported it too): `review_packet.py`/`ref_privacy.py`'s home-directory test is a bare case-folded substring match. On a seat whose home is `/root`, the body's literal `/root` and `roles/root-cause.md` both trip it, so this seat cannot render the packet. Carry: dismissed: uid-0 seat false positive outside this PR's diff; no live group owns ref_privacy.py or review_packet.py

## Evidence

- `ev/HEAD.txt`: the head reviewed. `ev/head_merge.txt`: the merge base, origin/main and branch tip, the empty roles diff, `merge-tree` rc=0 against `beb570c81`, the diff stat, 0 version or claim files touched, and no attribution trailer in any commit message.
- `ev/merge_new_main.txt` and `ev/bugclasses_conflict.txt`: the block's evidence (above).
- Mutation proof (step 1): n/a. The diff writes no production line, so the record's A1/A2 demonstrations are owed by their fixers. I cite CI's `tests / mutation` and did not re-run it.
- Body figures re-derived at this head:
  - `closure.py select`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out` over 5 changed files. The body's "four changed files" is the code head `2ee7cdc38`'s count; the fifth is the orchestrator's delivery row, added by the merge `82a6ef4a1` (`ev/closure_select.txt`).
  - `rosterIssues()`: prints `1 72` at both `beb570c81` and the head, matching the body (`ev/roster_issues_*.txt`).
  - `structure.py`: `STRUCTURE RATCHET PASSED` (`ev/structure.txt`).
  - `carry_audit.py check --body`: `CARRY-AUDIT: 17 finding item(s): 17 routed, 0 unrouted, 0 bad destination(s)` (`ev/carry_audit.txt`).
  - `fold_ledger.py check`: 126 rca entries, 0 violations (`ev/fold_ledger.txt`).
- Record claims checked:
  - Section 1: `rounds.py --stats <tsv>` gives rc=0 with 0 bytes (`ev/rounds_stats.txt`).
  - Section 3, A1's blindness: a planted `carry-2492.json` is accepted at rc=0 with 0 errors under the shipped no-argument index. With `dev/programme/rosters`, 2492 is covered by `R10-SAV-ACTUATION`. The record names `R10-SAV-COMFORT`, its own base `6eb552157`'s owner, and the record labels it as such. Control `carry-999999.json` is accepted and not covered (`ev/perturb_carry.txt`). The plants were removed afterwards.
- Forward-carry (step 10), at `handoff/audit-r10-roster` `be898eaef` (`ev/forward_carry.txt`):
  - A1 and A2 are R10-FLOW-TOOLKIT-MODEL carry[14] (`not-started`), whose acceptance holds the control.
  - #2855's key, and the four sibling issues #2429, #2436, #2437 and #2438 that strand, are R10-ORCH-ROSTER-SCHEMA carry[25] (`carries-open`), which has a control and a re-measure.
  - `carry-2733.json` and its closures entry are gone at the head, so round 3's block is resolved.
  - The record no longer names #2733 as an owner, and sections 3 and 5 name the live groups. Round 2's block is resolved.
- `bugclasses.json` `_rca."R10-RCA-FRICTION-RESIDUE"` is the one register entry, earned by the record. It is the 126th rca entry in `fold_ledger`.
- CI at the head (`ev/check_runs.tsv`, `ev/workflow_runs.tsv`, read with `filter=all` after every run concluded at 20:24Z):
  - 68 check runs, with one non-pass: `gate` 123069364626 in `CI code` run 40750635599, failure at 20:18:47Z. Its log's only verdict line is `FAIL run(s) [40752472986] at this head are still being judged; their gate decides`, a deferral.
  - The edit run's `gate` 123073029922 printed `PASS` (20:23:39Z), and both `CI edit` runs concluded success.
  - `pr-contract` 123075090262 started 20:21:07Z, after the last red concluded. It is green with `clean no refusal` and the same CARRY-AUDIT line. By step 11, that run is the evidence.
  - The body's `## Red checks` answers the earlier `1e917ac2` reds: `pr-contract`'s closes refusal now has its true cause and a cheaper detector, and `prelude`'s rate limit is answered.
- Locally, `tests/entities.py` cannot be parsed by this seat's Python 3.11.17 (a 3.12+ f-string at line 4253; `ev/entities.txt`). CI runs 3.14, and `tests / closures` and `tests / fast (3.14)` are green at the head, so I cite those.
- Not run: the gate, the mutation table and `policy_lint --stats` (669 s). CI's heavy runs are cited, never re-run.

RESULT merge-tree origin/main=b6f6ceca4 rc=1 conflict=dev/audit/config/bugclasses.json driver=refused(format: no trailing newline on any side) driver-with-newline=resolved
RESULT merge-tree origin/main=beb570c81 rc=0
RESULT closure-select MODE=SCOPED run=0 scoped-out=33 changed=5 (4 at code head 2ee7cdc38)
RESULT rosterIssues noarg=1 rosters=72 at beb570c81 and at head
RESULT carry-2492 shipped=accepted rc=0; rosters=covered R10-SAV-ACTUATION; control 999999 accepted, not covered
RESULT carry_audit routed=17/17
RESULT ci checks=68 nonpass=1 (gate deferral 123069364626); edit gate PASS; pr-contract 123075090262 green after last red
RESULT head 82a6ef4a1004d1c20fb0411bc4bee461a2015006 unchanged at write
