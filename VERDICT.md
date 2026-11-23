Fix review: blocked 625cc2c2aef154c507b37cefb015b1c40b27bde7 main-conflict: merge-tree against origin/main 24e3f37620 conflicts in coordinator.py, pump_arbiter.py and tests/entities.py

bus-nonce: 029b3e735b470abf951b0d72c3fe9b7f

## Block
- `git merge-tree --write-tree origin/main 625cc2c2ae` (origin/main 24e3f37620f8f51022a2f9c82f863c7ba28fc6d4) exits 1 with CONFLICT (content) in `custom_components/heatpump_optimizer/coordinator.py`, `custom_components/heatpump_optimizer/pump_arbiter.py` and `tests/entities.py`. It merged cleanly against the main of about 22:15Z. Main has since landed #3812 (9276ddf6b1), and that merge carries the module-span payment e9922bc1c3, which moves code out of coordinator.py and pump_arbiter.py. That is why these files now conflict. The fixer must re-merge main, resolve the conflict, and re-run fixer.md steps 2-8 over the resolution. The resolution touches `custom_components/`, so the next round reads it. Evidence: ev/merge-tree.txt.

## Review scope
- delta: `git diff 868e00db0b 625cc2c2ae` is 9 new `tests/mutation_ledger/killed_by/*.json` pins and nothing else. d03b02b00e is the bot's 5 pins. c55c713dcd is 4 pins made by `mutation_table.apply_pins`; its parent ce185aeaf9 is an ancestor of 868e00db0b. Merge 625cc2c2ae has an empty `--cc` diff, so it is not an evil merge. The delta has no `custom_components/` change, so the scope is not widened (fix-review.md step 12).

## Evidence
- Previous verdict (merge at 868e00db0b): its 4 notes were dismissed. The ci-unreadable note is settled at this head: `merge_train.py classify 625cc2c2ae --pr 3845` read WAIT (pending: gate) from 22:19Z to 22:51Z, then `GREEN ... pending: none red: none`, rc=0, at 01:03Z (ev/classify.log).
- Pin anchors: the `old` line of all 9 pins is present in its file at the head.
- Pin re-derivation: I reproduced 2 of the 9 pins by hand through tests/features.py.
  - m1, coordinator `_tariff_months` RETURN_DEL → `pass`: rc=1, crash at tests/features.py:18075 (`TypeError: 'NoneType' object is not iterable` on `sorted(_elv_ct.months)`). KILLED. The pin records rc=1 failed=1. Here it crashes, and the unmutated run passes that line.
  - m2, diagnostics `_never_breaks` RETURN_DEL → `pass`: rc=1, `2 of 6041 FEATURE CHECKS FAILED`. The two failures are the diagnostics-view fallback checks ("a view that raises reports unavailable", D1-s3-07). KILLED. The pin records failed=3, a count difference that this host's run does not change.
  - Null control (unmutated head, same host): `1 of 6041 FEATURE CHECKS FAILED`. The one failure is a host-load process-worker flake ("a worker that dies mid-reply is a transport fault": pickle truncated after 0.95 s). It is not among m2's failures, and CI `tests / fast (3.14)` is green at the head.
  - Evidence: ev/m1.diff, ev/m2.diff, ev/feat_*.tail.txt.
- The other 7 pins were not re-derived. CI `tests / mutation` is success at this head.
- No overlaid instrument. The local seat pushes through bus.sh push-verdict in place of the cloud probe ref, as the dispatcher directed.
