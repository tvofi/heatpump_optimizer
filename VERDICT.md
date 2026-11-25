Fix review: merge 086341d6f99a2c031fcf91edfaa5661c47361951

bus-nonce: bc16094da95db343b1c73ec1ff2fcf8e
pending-ci: gate

## Block

None. Delta round 3: reviewed head 6fb0f76ae8f5 (blocked tests-red), now 086341d6f99a.

- The delta (`ev/delta.diff`) is one file, `tests/deployment_shape.py`. It arrives through 2b1b54fa, which is merged in by 086341d6. No main changes fall in the range.
- The note now reads `184 of the 561` and `all 184 among the 435`. It also has a history clause: 182 before R11-OWNER-FLOWCAP's `flow_limit.py` joined main's closures, adding `env_drift.py`/`manual_plan.py` and `golden.py`/`manual_plan.py`.
- Those two pairs are exactly the ones my derivation found at the blocked head, so the clause is accurate.

## Findings

- Prior block (blocked 6fb0f76ae8f5 tests-red, the #1218 selection-cost marker `184 of the 561` missing) is **resolved**. I re-ran entities.py's own pair predicate on `tests/closures.json` (`ev/d308.txt`):
  - head 086341d6: 122 production files, 184 of 561, and the marker is present;
  - the tree from merging the head with origin/main bb6377b4 (34fc218c): 184 of 561, no pair moved, and the marker is present.

  Every other marker the check reads is in the note: `D3-08`, `#1218`, `selection cost`, `all 122 files`, `435 pairs`, and the four empty-closure script names.

  Carry: dismissed: resolved at this head
- The coordinator reports that the local `tests/entities.py` run on 2b1b54fa merged with bb6377b4 failed 1 of 2762, on `hb:positive_control`. That check is a live heartbeat-sampler timing control (`tests/nightly_ha.py` `check_hb_positive_control`), and the host was at load 55+. Neither the delta nor the PR's diff against main touches `tests/entities.py`, `tests/nightly_ha.py` or `tools/`. I did not re-run it on this loaded host; CI's `tests / fast` at this head is the authority, hence `pending-ci: gate`. Carry: dismissed: not this diff's; CI decides

## Evidence

- Head reviewed: 086341d6f99a2c031fcf91edfaa5661c47361951 (`ev/HEAD.txt`), which `refs/pull/3866/head` matches.
- `git merge-tree --write-tree origin/main <head>` at bb6377b4: rc 0, clean (`ev/merge_tree.txt`).
- The code delta was judged in the previous round, and this round leaves it unchanged. Those mutation results (M1103 killed, MCAP/M8 6 of 12, MRESTORE null with no check moving) carry, because `git diff 6fb0f76ae8f5 086341d6f99a` touches no production file.
- CI at the head, read at publication: `tests / fast (3.14)` **success**, which is the job the prior block rested on. `tests / mutation` has concluded. `merge_train.py classify --pr 3866` reads `WAIT ... pending: gate red: none`. The one `gate` failure is a deferral (`run(s) [45608794241] at this head are still being judged; their gate decides`). `tests / nightly-status` is red but not required. The `gate` verdict is owed before merge.
