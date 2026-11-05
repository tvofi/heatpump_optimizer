Fix review: blocked aca500910b8917fd41516f5f290c6a18f1727b8b ci-red: required gate concluded cancelled at this head (classify RED), and the body's Head and Red checks name stale SHAs, not this head's base

bus-nonce: 29b7d53a28cafa1a1e1c82375a4b0384

Round: this is the second fix review of #3219. The first blocked 140df026 as mutation-vacuous. Round 2 never reached review because prepr refused it. This review covers repair round 3 at head aca500910b8917fd41516f5f290c6a18f1727b8b, merge base 662b29669ec5beb6773fa8b62ac98f2b020be90e. The roles diff against main is empty, so this contract is current. Another repair would be round 4, which per `fixer.md` owes a re-cut, not a repair.

## Block

- CI: `merge_train.py classify aca500910b8917fd41516f5f290c6a18f1727b8b --pr 3219` exits 1 with `RED ... pending: none red: gate` on every run (ev/classify.txt). The required `gate` context concluded `cancelled` in run 41966445820 (job 127046941758) after its `prelude` (127044449071) was cancelled. The earlier gate, 127045288245 in run 41966182433, was also cancelled. Lanes of run 41966183843 were still in progress when read (closures, coverage, fast, replay, mutation-pins, instrument-self-tests, CodeQL python). A red CI never carries, so this head cannot take `merge` until a `gate` concludes green on it.
- `## Head` names three SHAs: aca50091 as the head, plus 2aafd3e3 and 651468bb. It states that the merge base equals `origin/main` at 7c274274830ce553b8faec9574837de91a2be234. At this head the merge base is 662b29669ec5beb6773fa8b62ac98f2b020be90e (`git merge-base origin/main HEAD`). The brief requires `## Head` to name ONE head (step 7). The paragraph about the code head is round-3 history and belongs elsewhere, or should be dropped.
- `## Red checks` is not complete or accurate for this head. It does not name `gate` or `prelude`, both concluded `cancelled` (review_packet REFUSE red-unanswered ×2, required-red: ev/review-packet.md). It also names `tests / mutation-autofix`, which has no check run on this head at all. And it calls `governance / delivery-status` and `tests / nightly-status` inherited "at base 7c274274", which is not this head's base (662b2966). Step 11 cannot be judged until all workflows on this head have concluded and `pr-contract` has re-read the corrected body.

## Findings

- Follow-up: the code change is sound and every mutant claim in the body re-derives at this head (see Evidence). The repair this PR owes is only the body (`## Head` with one SHA and the true merge base, `## Red checks` covering every concluded red, with the inherited reds named against 662b2966) plus a green `gate` on the head. Carry: R10-FLY-REPLAY-MASK
- Follow-up: the brief expected round 3 to add a check that reaches the `_DROP` skip at round-2 `:537`. The fixer deleted the skip instead and argued it was an equivalent mutant. I confirmed this. Re-inserting `if value is _DROP: continue` after the `_entry_shape` call leaves `replay.mask_checks()` at 23/23 (M5). Planting an id-shaped value that `_entry_shape` returns `_DROP` for, inside conf, neither leaks nor refuses at the head (ev/plant_drop.txt). The deletion is the sounder design, and `## Unpinned sites` states truthfully that the site is gone. The orchestrator should record that the brief's "adds the check" was met by deletion. Carry: R10-FLY-REPLAY-MASK
- Follow-up: replay_doc.py:535 (`if conf is not None:`) is killed by one check (`mask:id_in_list_under_an_entities_key_beside_a_non_id_seals_masked`) but has no ledger pin in this diff. The body defers the pin to `mutation-autofix` after the push. The `tests / mutation` red is that unpinned site. It needs the bot pin commit before merge, and that commit moves the head. Carry: R10-FLY-REPLAY-MASK
- Follow-up: the escaped class on the owner's 2026-11-04 live export is still stated by reasoning, not by measurement. The body says this honestly: an id under an entry key off the allowlist. Neither the fixer nor this seat read the export, so the match has not been checked. Carry: R10-FLY-REPLAY-MASK

## Evidence

- HEAD reviewed: aca500910b8917fd41516f5f290c6a18f1727b8b (ev/HEAD.txt). It was reviewed from a detached worktree at that SHA.
- No finder's harness is named (packet: "Finder's harness: none named"). The instruments are my own and the round-1 reviewer's: ev/mc.py (round-1 reviewer's), ev/mut.sh, ev/plant2.py, ev/plant3.py. They run `replay.mask_checks()` and the module API with `PYTHONDONTWRITEBYTECODE=1`.
- RESULT null: mask_checks 23 checks, 0 failed (ev/mutants.txt M0). This matches the body's "23 checks, none failed".
- RESULT mutants at head (ev/mutants.txt, ev/mutants_crash.txt):
  - M1 :533 key guard `if False:` fails 4.
  - M1b :533 BOOLOP crashes with TypeError (killed).
  - M2 :535 `if conf is not None:` → `if False:` fails 1 (`mask:id_in_list_under_an_entities_key_beside_a_non_id_seals_masked`), as the body states.
  - M3 :538 `_entry_shape` call → `pass` fails 1 (same check), as the body states.
  - M4 :540 list test `if False:` crashes with TypeError (killed).
  - M5 re-inserting the round-2 `_DROP` skip fails 0 (equivalent, as the body states).
  - M6 `mask_ids` passes None fails 5.
  - M7 `document` drops conf fails 5.
  - M8 deleting `conf=conf` in debugger.py fails 1 (`mask:debugger_replay_document_passes_conf_to_document`).
  - M9 deleting `conf=conf` in tools/replay/export.py fails 1 (`mask:build_export_passes_conf_to_document`).
  - Every file was restored after each mutant (`git checkout`), and the worktree was clean afterwards.
- RESULT plant (ev/plant.txt), base 662b2966 vs head:
  - The list `["abc", <id>]` under the kept non-`_entities` conf keys after_save, away_dhw_min_temperature and away_enabled seals 3 states with no leak at both ends. The round-1 regression is gone.
  - `legacy_probe_entity` off the allowlist and `room_sensor_entities` off the allowlist refuse at the base and seal with no leak at the head (null control holds).
  - No installed conf key makes `_entry_shape` return `_DROP` for a bare id string: 0 of 219 non-secret keys.
- RESULT `_DROP` plant (ev/plant_drop.txt):
  - A scalar id under a conf-kept `_entities` key (synthetic `zone_entities`), alone or beside a later `_entity` role, refuses at the base and seals with no leak at the head.
  - An id with whitespace under after_save seals with no leak at both ends.
  - In every case the `_DROP`-shaped id neither appears in the replay nor is refused at the head.
- RESULT `mask:planted_unmasked_id_still_refused`: true at the head (in the 23/23).
- merge-tree with origin/main 8364e62460f61d68be8073cd1b65e8079aa350a7: rc=0, tree fb8d07e6a2a79105a2d5d57f816a1d8805bc80ca, no conflicts (ev/merge-tree.txt).
- VERSION, manifest.json, RELEASE_NOTES.md, tests/golden and the claim files are not in the three-dot diff (ev/three-dot.diff).
- Every entity id in the diff is synthetic: sensor.hpo_out, sensor.in, sensor.late, sensor.off_list, sensor.planted_unmasked. The body quotes no id.
- Check runs read live, one page of 59 (total_count 59), were the source for the Block. `tests / mutation` failed (127045678304). `governance / delivery-status` failed (127045678404). `tests / nightly-status` failed (127045678253). `gate` was cancelled ×2. `prelude` was cancelled ×2 (127044449071, 127043596901) and succeeded once (127043601434). Not all workflows had concluded.
- Not re-derived: whether `delivery-status` and `nightly-status` are red on main at 662b2966. The body ties them to 7c274274 instead.
- Not re-derived: the body's closure list and `STRUCTURE RATCHET PASSED`. These are CI's heavy checks, and I did not re-run them.
- I did not re-run the gate or the mutation table (step 11, "cite CI's heavy runs").
