Fix review: merge 40cc860dd82b1e81ae8f2492a2796bf2797bc911

bus-nonce: 3674812515c5cf5cb78ee6f288eefe08

## Scope

Round 1 (no earlier verdict on #3648), full review of `git diff 921214bf...40cc860d` (10 files, no `custom_components/` path). Reviewed in detached worktrees at the head and at the merge base `921214bf4246338c1a83fbc5269eaa0bfe91b7d5`. The PR body's `## Head` names `40cc860dd82b1e81ae8f2492a2796bf2797bc911`, the head measured here.

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main 40cc860d` (origin/main `6aa7ddc7`) rc=0; its only driver line is `LEDGER-MERGE: resolved tests/closures.json`. No conflict.
- RESULT harness (the fixer's `dev/audit/harnesses/r11_relay_3358_skip.py`, run from the head tree): with `--seat` set to the merge-base `tools/audit/seat` it prints `defect_updated=0 defect_owed=0` and `null_updated=0 null_owed=0`. With the head seat it prints `defect_updated=1 defect_owed=0` and `null_updated=0 null_owed=0`. Both match the body's `## Figures`. The body's base worktree was `98847b99`; mine was `921214bf`, which contains `98847b99`. Files: ev/harness-base.txt, ev/harness-head.txt.
- RESULT harness under mutant `handoff-topics` -> `pr-topic` (the base's rule): `defect_updated=0 defect_owed=0`, so the harness moves under its own perturbation (ev/harness-mut-handofftopics.txt).
- Harness provenance (step 9): the finding (roster carry 0, #3358) came with no committed harness. This harness is the fixer's, built for this PR and landed by it, and the body presents it that way. Its null case (`d07f8e9e`, a head that holds the handoff) is flat at both ends, as the carry's control requires.
- RESULT mutation proof: these are my own mutants, each applied by perl in its own worktree at the head, and the named self-test re-run. All 10 were killed (ev/mut-*.txt):
  - `handofftopics` (handoff-topics -> pr-topic): cloud_relay 1 failed.
  - `nobody` (NOBODY level line dropped): 1 failed.
  - `reviewrelease` (predicate `false`): 3 failed.
  - `owedred` (PREDICTOR case emptied): 2 failed.
  - `skipbusy` (BUSY skip_owed removed): 1 failed.
  - `branchrestart` (`-B <br>` -> `--detach`): tick_loop 8 failed.
  - `gapstart` (in-sleep relay_start removed): 1 failed.
  - `staleowed` (`-lt 2` -> `-lt 99`): 8 failed.
  - `tgorder` (handoff_topics order reversed, `<t>` before `<t>-pr`, which is #3358's first-with-a-ref shape): topic_grammar 2 failed plus cloud_relay's #3358-shape row.
  - `tgstrip` (handoff_topics reduced to the stripped topic): the same 3 rows.
- RESULT self-tests at the head:
  - `cloud_relay self-test: 515 checks, 0 failed`.
  - `tick_loop self-test: 48 checks, 0 failed`. The same command on the `origin/main` 6aa7ddc7 checkout gives 42 checks, 0 failed (ev/tick_loop-selftest-base.txt).
  - `ledger self-test: 104 checks, 0 failed`.
  - `topic_grammar self-test: ok`.
  - `review_packet self-test: 133 checks, 0 failed`.
  - `STRUCTURE RATCHET PASSED`.
- RESULT class (step 6): the body's rule, `awk '/^handoff_arm\(\) \{/,/^}$/' tools/audit/seat/cloud_relay.sh | grep -n continue`, returns 21 sites at the head (ev/class-rule-continue.txt). I read each one against the body's list. Every site that skips a handoff the head lacks either writes a level line (`handoff-held`, `handoff-skipped`, `handoff-update`, `handoff-body-stale`, `handoff-body-unapplied`) or is the ledger's `dispatch`. The remaining sites are "no PR", "no handoff ref" and the three in-head sites (no body, body applied, seed). No open seam.
- RESULT topic rule readers: `git grep` for pr_topic and handoff_topics across tools/, tests/, harnesses and .claude finds the handoff-ref readers as `cloud_relay.sh:607`, `cloud_relay.sh:646` and `review_packet.py:330/408/783`, all on `handoff_topics` (ev/class-enum.txt). `bus.sh:257` (`mut:landtopic`) keeps `pr-topic`. It derives the group topic for the carry-landing own-carry exemption, not a `handoff/` ref, so it is outside this class.
- Claim files: `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical over the three-dot diff. No golden path is touched. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (step 5).
- Metrics (step 14): the only moved instrument is `tests/closures.json`, which gains one line, the new harness. That is a classification the new file requires, so the movement is earned. CI `arch-score` is success, and the body quotes `dS +0.0000 NULL`.
- Own-group carries 5-12 (step 10): each is `Carry: R11-PRE-RELAY-REBUILD`. The original fixer dispatch `dispatch/fixer-r11-pre-relay-rebuild` 367dc03c90 PROMPT.md ends `Part 1 of 3: build carries 0-4; the others are later parts dispatched at this part's handoff; answer none of them` (copy in ev/fixer-dispatch-367dc03c90-PROMPT.md). That is the orchestrator-named split part that fixer.md's exception allows. The roster's R11-PRE-RELAY-REBUILD entry on `handoff/audit-r10-roster` (`wave-r11-groups.json`) holds those 13 carries and `pr: 3648`. The group's core P12 brief (verdict posting never queues behind an update) is also not built in this part, and the body does not claim it.
- Red checks (step 11): `tests / fast (3.14)` was red at `16945f40` and is in the owed-reds set. The body answers it under `## Red checks`: the cheaper detector exists (`tests/harness_headers.py`, run_always, about 0.5 s for the depth-seam arm), and the process state is (b). `pr-contract` and `gate` are answered as downstream of it.
- Figures not re-derived: the tick_loop wall times (1m47s / 2m00s), the `prepr.sh` step 6d survivor list and the `closure.py select` line are taken from the body unverified. CI's `tests / mutation` is success at this head, and I did not re-run the gate or the mutation table.
- RESULT CI: `merge_train.py classify 40cc860dd82b1e81ae8f2492a2796bf2797bc911 --pr 3648` -> `GREEN 40cc860dd82b1e81ae8f2492a2796bf2797bc911 pending: none red: none` (rc 0, 03:18:11Z; ev/classify-poll.log). The `gate` failure in the packet digest was an earlier run that finished before `pr-contract` re-ran. The packet's `introduced-red` refusal said `governance / instrument-self-tests` was still in progress; classify reads it concluded with no red.
- RESULT head re-read before return: `fix/r11-pre-relay-rebuild` is still `40cc860dd82b1e81ae8f2492a2796bf2797bc911`.
