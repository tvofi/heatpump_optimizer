Fix review: blocked 5356706e02cd174793004a041059c090eb15efba mutation-survivor: P657 merge-verdict guard in Tick._bucket is unpinned

bus-nonce: 6379a5c9085a0db44530aa93851d5925

Round 1 (first review of #3689; no earlier verdict).

## Block

The P657 arm added to `tools/audit/seat/orchestrator_tick.py` `Tick._bucket` buckets a PR as `verdicted` when `m.group(1) == "merge" and m.group(2) != head and self._carries(...)`. Deleting the `m.group(1) == "merge" and` conjunct leaves `orchestrator_tick.py --self-test` at 374 checks, 0 failed. With that conjunct gone, a red PR whose last verdict is a *blocked* one at an older head that the carry predicate accepts is bucketed `verdicted` and its `OWED red-unowned` line disappears, which hides exactly the owed red this tick exists to show. A reviewer probe arm (`oboard2` with last line `Fix review: blocked <h(1095)> x: y`, `carries=lambda v, hd: True`; expect not verdicted and an OWED line) passes at the head (375 checks, 0 failed) and fails with the conjunct deleted (375 checks, 1 failed). Repair: land that arm, or an equivalent one, next to the existing P657 arm and its null control, and add it to the body's mutation proof. Evidence: ev/mutants.txt.

## Findings

- The `m.group(2) != head and` conjunct of the same arm also survives deletion (374 checks, 0 failed). This mutant is equivalent in outcome: a merge verdict at the head is bucketed `verdicted` by the later arm anyway, and the only cost is one needless fetch inside `_carries`. Carry: dismissed: equivalent mutant, no behaviour differs

## Evidence

- CI at this head: `merge_train.py classify 5356706e02cd174793004a041059c090eb15efba --pr 3689` prints `GREEN 5356706e02cd174793004a041059c090eb15efba pending: none red: none`, rc 0 (ev/ci-and-merge.txt). `tests / nightly-status` is red in the packet digest, but it is not in the `merge_train.py owed-reds` set, so it is owed no answer.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0, tree a4a91c3dff. The base equals origin/main b98c78e0f6, so the role-contract diff is empty and the contract is current.
- Mutation proof as the body names it, re-run by the reviewer: all five mutants were killed (carry 8 STAMP, carry 6 cap prefix, carry 9 `mut:carriedverdict`, carry 5 `mut:redlog`, and the reviewer's ANSI-strip deletion). Details in ev/mutants.txt.
- Null controls as the body names them: each is present in the self-test and green at the head.
- Body figures re-derived at the head: orchestrator_tick 374 checks, 0 failed; verdict_audit 18, 0 failed; owed_unactioned 60, 0 failed; `tests/structure.py` STRUCTURE RATCHET PASSED. `tests/entities.py` was still running locally at verdict time, so this review cites CI's green `gate` and `tests / closures` for it rather than a local run.
- The three-dot diff touches no VERSION, manifest, RELEASE_NOTES, golden or claim file, and nothing under `custom_components/`.
- The body names this head, 5356706e02cd174793004a041059c090eb15efba. Its prepr ran at e88651b697, the pre-main-merge tip; the delta from there is the clean main merge plus the delivery row.
- Finder's harness: none is named. The carries' own triage pins are the harnesses, and each is present in the self-tests. No enumeration rule is named; each carry states one seam, so these are one-seam classes and the absence of a rule is not read as compliance.
- Carry 6 design: removing the reader-side `CAP_NOTICE` skip follows the carry's ruling (P574: "Do not add a reader-side skip"). A board written by a pre-merge tick, with the old `OWED handoffs capped` line, reads UNREADABLE again until the tick is updated. The self-test's null control asserts that on purpose.
