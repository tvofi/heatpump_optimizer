Fix review: blocked 2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee mutation-vacuous: review_packet.py:847-849,853 handoff wiring and the new part-line base predicate survive; cloud_dispatch.py:681 fetch survives

bus-nonce: 55ce0064265b6ffbf6e084e24ecdd271
pending-ci: governance / instrument-self-tests, governance / policy-docs, governance / env-matrix, governance / wave-script, tests / briefs, tests / closure-scope, arch-score / arch-score, hassfest / hassfest, validate / validate-hacs, budget-raise-gate / budget-raise-gate

Round 1 (first review of #3539). Measured head `2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee`, which is the head the PR body names. Merge base `caacd43b4ee1b1ce849fbc92590e0b2191e6c02c`.

## Block

- mutation-vacuous: carry 25's new predicate in `handoff()` is never run by `review_packet.py --self-test`. At `tools/audit/seat/review_packet.py:849`, `base = " -- demanded by the dispatch PROMPT's part line" if part_carries(prompt) else ""` survives when it is inverted and when it is forced to `""` (both `128 checks, 0 failed`). So do `:848` `carries = handoff_carries(prompt, live)` → `handoff_carries(None, live)` (that drops the part scope from the live handoff path entirely) and the driver's STMT_DEL of `:847`, `:848`, `:849` and `:853`. `handoff()` has no self-test fixture, so nothing pins the wiring this carry exists to change. The body's "Carry 25 base text in the refusal dropped: KILLED" mutant is on `handoff_refusals`'s parameter, not on this predicate. Owed: a self-tested seam for the brief-carries step of `handoff()` (for example, lift lines 847-849 and the `unnamed_carries`/`handoff_refusals` call into one pure function over `(prompt, live, body)` that the self-test drives with a part-line prompt and with a no-part-line prompt), then show both mutants on 848/849 KILLED.
- mutation-vacuous: `tools/audit/seat/cloud_dispatch.py:681` `_git(repo_dir, "fetch", "-q", "origin", vref)` is a changed production line, and deleting it survives (`172 checks, 0 failed`). The fixture's verdict objects are already local, so the fetch is unobservable. The body does not say why the fetch target moved from `vtip[0]` to `vref`.
- Every survivor the driver run at this head reports (`mutant_run.py --diff caacd43b4e...<head>`, per file, each against that file's own `--self-test`; logs in `ev/mut-*.log`):
  - SURVIVED tools/audit/seat/review_packet.py:1133 CONST_SWAP  and unnamed_carries("Carry 2: a\n", handoff_carries(hand, 6)) == [3])
  - SURVIVED tools/audit/seat/review_packet.py:1138 CONST_SWAP  unnamed_carries(two, handoff_carries(hand, 7)) == [])
  - SURVIVED tools/audit/seat/review_packet.py:1141 CONST_SWAP  and unnamed_carries(two, handoff_carries(full5, 6)) == [0, 1, 4] and handoff_carries(None, 5) == 5)
  - SURVIVED tools/audit/seat/review_packet.py:847 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:848 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:849 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:853 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1131 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1134 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1137 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1139 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_packet.py:1142 STMT_DEL  pass
  - SURVIVED tools/audit/seat/cloud_dispatch.py:681 CALL_DEL  pass
  - SURVIVED tools/audit/seat/cloud_dispatch.py:858 STMT_DEL  pass
  - SURVIVED tools/audit/seat/cloud_dispatch.py:869 STMT_DEL  pass
  - SURVIVED tools/audit/seat/cloud_dispatch.py:874 STMT_DEL  pass
  - SURVIVED tools/audit/seat/review_strength.py:586 STMT_DEL  pass
  - Excluded from this block: the 12 survivors on self-test lines (`review_packet.py:1131-1142`, `cloud_dispatch.py:858/869/874`, `review_strength.py:586`). Deleting or re-numbering an assertion is not production behaviour. They are listed above because the driver reported them; the block rests on `review_packet.py:847-849,853` and `cloud_dispatch.py:681`.
- My hand predicate mutants (`ev/hm.py`, `ev/hand-mutants.out`), one per new predicate, against the file's own `--self-test`:
  - SURVIVED: c25 base predicate inverted (849), c25 base always empty (849), c25 handoff ignores prompt (848), c24 fetch deleted (681).
  - KILLED: c25 `assigned or found` → `found` (3 failed), c25 hand branch disabled (2), c25 gen branch disabled (1), c24 range predicate always true (1) and always false (1), c24 render guard off (2), c24 role tuple narrowed to designer (2), c10 isinstance inverted (AttributeError), c10 string branch → None (1).
  - NULL (identical replacement): SURVIVED.

## Evidence

- RESULT self-tests at the head: review_packet 128 checks, 0 failed; cloud_dispatch 172 checks, 0 failed; review_strength 117 checks, 0 failed (`ev/selftests-head.txt`). These match the body's three green figures. I did not re-derive the body's red-at-base FAIL counts (3, 2, NameError).
- RESULT carry 25 hand spelling, real p6 PROMPT `8602c93e58:PROMPT.md`: `prompt_carries` gives [10, 24, 25]. In a 27-carry prompt with the hand line, a body naming 25, 24 and 10 has unnamed [] (passes). A body missing 10 is refused for [10]. A body naming only Carry 3, outside the part, is refused for [10, 24, 25] (`ev/c25.out`).
- RESULT carry 25 generated spelling `Part 2 of 3: build carries 15-17+19-20;`: assigned [15, 16, 17, 19, 20]. The exact body passes. A body naming 18 (outside) in place of 20 is refused for [20]. A round trip of `cloud_dispatch.part_line` for a 20-carry split parses every part to its own runs: 0-4, 5-9, 10-11+13-15, 16-17+19-20+22.
- RESULT carry 25 null: a prompt with no part line demands all 27 (a 3-carry body leaves 24 unnamed). At the merge base, the generated-line prompt demands all 27 (22 unnamed for the 5-carry body), so the fix moves it.
- RESULT carry 25 domain: a body naming its own three carries plus an outside `Carry 3` is not refused (unnamed []). Carry 25 asks only to demand the assigned indexes; "names no other carry" is a fixer-brief rule that no instrument here enforces. I record this as the check's domain, not a defect of this part.
- RESULT the roster-at-dispatch-time base (`rev-list -1 --before`) is not built. The body says so and why. That matches the fixer brief, which made it conditional on a prompt holding no Carry lines.
- RESULT merge with main: `git merge-tree --write-tree origin/main 2e160c0c9b…` (main `b5057b0525`) gives rc=0, tree `87edde0b79`. It is clean, not textual-only (`ev/mergetree.out`).
- RESULT PR #3533: `refs/pull/3533/head` `faf8676984` is already an ancestor of origin/main (merged at `b5057b0525`), so the merge-tree against it is that same clean rc=0. Against the p6 merge base, #3533's `cloud_dispatch.py` hunks are at 934+ and 1147+ in `_group_checks`. p6's hunks are at 362, 577-592, 674-683 and 855-875, so p6 did not edit #3533's lines: clean, not textual-only.
- RESULT scope: the diff touches only `review_packet.py`, `cloud_dispatch.py`, `review_strength.py` and its own delivery row. There is no role or policy file and no `VERSION`, manifest, notes heading, golden or claim file. The body names Carry 25, 24 and 10 and no other carry of the group, which matches the part scope.
- RESULT carry 10: `fixer_of` reads a string model, a dict's `fixer` key, `{}` and None as sonnet / opus / none / none. Both of its predicate mutants are killed.
- RESULT roster destinations: `dev/programme/rosters/wave-r10-groups.json` holds `R10-REVIEW-DISPATCH-RESIDUE` at origin/handoff/audit-r10-roster `d12ffa3aaf` (506 groups) but not at origin/main `b5057b0525` (342 groups) (`ev/roster-dest.out`). A `Carry:` to this group therefore fails the both-rosters rule today, which is why this verdict hands the block back to the PR instead of carrying it.
- RESULT CI: `merge_train.py classify … --pr 3539` printed `WAIT 2e160c0c9b0cb4b00bdbd5f17defd63bfcfbfbee pending: gate red: none` (rc 3) at both reads. Per the dispatch, I did not wait. The packet render refused `introduced-red: unreadable` because `instrument-self-tests` had not concluded, and showed `tests / nightly-status` failure, which is outside `owed-reds` (`ev/review-packet.md`). No red-check answer is owed yet.
- RESULT `env -u BASH_ENV python3 tests/entities.py` could not run in this container: `ModuleNotFoundError: No module named 'homeassistant'` under venv-ci (`ev/entities.out`). It is not verified here; CI's governance lanes run it.
